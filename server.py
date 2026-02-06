"""
MCP Proxy Server

A proxy server that forwards MCP requests from frontend to MCP servers
with authentication using proxy_token.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import asyncio
import websockets

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="MCP Proxy Server", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PROXY_TOKEN = os.getenv("PROXY_TOKEN", "")
if not PROXY_TOKEN:
    logger.warning("PROXY_TOKEN not set in environment variables!")

# Security: Allowed URL schemes for MCP servers
ALLOWED_SCHEMES = {"http", "https", "ws", "wss"}

# Security: Blocked hosts to prevent SSRF attacks (internal/private networks)
BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0",
    "169.254.169.254",  # AWS metadata service
    "[::1]",  # IPv6 localhost
}

# Security: Blocked network ranges (private networks)
def is_private_ip(ip_str: str) -> bool:
    """Check if IP address is in private range"""
    try:
        import ipaddress
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False

# Request Models
class MCPRequest(BaseModel):
    """MCP request model"""
    mcp_server_url: str
    mcp_token: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"
    id: Optional[int] = 1


# Authentication helper
def verify_proxy_token(proxy_token: Optional[str]) -> bool:
    """Verify the proxy token"""
    if not PROXY_TOKEN:
        logger.warning("No PROXY_TOKEN configured, allowing all requests")
        return True
    return proxy_token == PROXY_TOKEN


# Security helper
def validate_url(url: str) -> bool:
    """
    Validate URL to prevent SSRF attacks
    
    Note: This is a proxy server designed to forward requests to external MCP servers.
    URL validation helps prevent access to internal/private networks, but cannot
    completely eliminate SSRF risks. Only allow trusted users to access this proxy.
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            logger.warning(f"Blocked URL with invalid scheme: {parsed.scheme}")
            return False
        
        # Check for blocked hosts
        hostname = parsed.hostname
        if not hostname:
            return False
        
        hostname_lower = hostname.lower()
        
        # Check explicit blocked hosts
        if hostname_lower in BLOCKED_HOSTS:
            logger.warning(f"Blocked access to restricted host: {hostname}")
            return False
        
        # Check if hostname resolves to private IP
        if is_private_ip(hostname):
            logger.warning(f"Blocked access to private IP: {hostname}")
            return False
        
        # Additional check: block common internal domains
        if any(keyword in hostname_lower for keyword in ["internal", "local", "intranet"]):
            logger.warning(f"Blocked access to internal domain: {hostname}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating URL: {str(e)}")
        return False


# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MCP Proxy Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/proxy")
async def proxy_request(
    request: MCPRequest,
    proxy_token: Optional[str] = Header(None, alias="X-Proxy-Token")
):
    """
    Proxy MCP requests to the target MCP server
    
    Args:
        request: MCP request containing server URL, token, method, and params
        proxy_token: Authentication token for the proxy (from header)
    
    Returns:
        Response from the MCP server
    """
    # Verify proxy token
    if not verify_proxy_token(proxy_token):
        logger.warning("Invalid proxy token provided")
        raise HTTPException(status_code=401, detail="Invalid proxy token")
    
    # Validate MCP server URL for security
    if not validate_url(request.mcp_server_url):
        logger.warning(f"Invalid or blocked MCP server URL: {request.mcp_server_url}")
        raise HTTPException(
            status_code=400,
            detail="Invalid MCP server URL: URL scheme must be http/https and cannot target private/internal networks"
        )
    
    # Prepare the request to the MCP server
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add MCP token if provided
    if request.mcp_token:
        headers["Authorization"] = f"Bearer {request.mcp_token}"
    
    # Prepare JSON-RPC request
    json_rpc_request = {
        "jsonrpc": request.jsonrpc,
        "id": request.id,
        "method": request.method,
    }
    
    if request.params:
        json_rpc_request["params"] = request.params
    
    # Forward the request to the MCP server
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Forwarding request to {request.mcp_server_url}: {request.method}")
            response = await client.post(
                request.mcp_server_url,
                json=json_rpc_request,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Received response from MCP server")
            return result
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from MCP server: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"MCP server error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to MCP server: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.websocket("/ws")
async def websocket_proxy(websocket: WebSocket):
    """
    WebSocket proxy for MCP protocol
    Handles bidirectional communication between client and MCP server
    """
    await websocket.accept()
    
    # Get proxy token from query params
    proxy_token = websocket.query_params.get("proxy_token")
    
    if not verify_proxy_token(proxy_token):
        await websocket.close(code=1008, reason="Invalid proxy token")
        return
    
    # Get MCP server URL from query params
    mcp_server_url = websocket.query_params.get("mcp_server_url")
    mcp_token = websocket.query_params.get("mcp_token")
    
    if not mcp_server_url:
        await websocket.close(code=1002, reason="MCP server URL required")
        return
    
    # Validate MCP server URL for security
    if not validate_url(mcp_server_url):
        logger.warning(f"Invalid or blocked WebSocket MCP server URL: {mcp_server_url}")
        await websocket.close(code=1002, reason="Invalid MCP server URL")
        return
    
    # Convert http/https to ws/wss
    ws_url = mcp_server_url.replace("http://", "ws://").replace("https://", "wss://")
    
    try:
        # Connect to MCP server
        headers = {}
        if mcp_token:
            headers["Authorization"] = f"Bearer {mcp_token}"
        
        async with websockets.connect(ws_url, extra_headers=headers) as mcp_ws:
            # Create tasks for bidirectional forwarding
            async def forward_to_mcp():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await mcp_ws.send(data)
                except WebSocketDisconnect:
                    logger.info("Client disconnected")
                except Exception as e:
                    logger.error(f"Error forwarding to MCP: {str(e)}")
            
            async def forward_to_client():
                try:
                    async for message in mcp_ws:
                        await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error forwarding to client: {str(e)}")
            
            # Run both forwarding tasks concurrently
            await asyncio.gather(
                forward_to_mcp(),
                forward_to_client(),
                return_exceptions=True
            )
    
    except Exception as e:
        logger.error(f"WebSocket proxy error: {str(e)}")
        await websocket.close(code=1011, reason=str(e))


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting MCP Proxy Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
