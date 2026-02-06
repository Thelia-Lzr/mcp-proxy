"""
Example: Basic usage of the MCP Proxy Client

This example demonstrates how to use the MCP proxy to list and call tools.
"""

import httpx
import asyncio
import json

# Configuration
PROXY_URL = "http://localhost:8000"
PROXY_TOKEN = "your_secure_proxy_token_here"
MCP_SERVER_URL = "http://your-mcp-server.com"
MCP_TOKEN = "optional_mcp_token"  # Optional


async def list_tools():
    """List available tools from the MCP server"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PROXY_URL}/proxy",
            headers={
                "Content-Type": "application/json",
                "X-Proxy-Token": PROXY_TOKEN,
            },
            json={
                "mcp_server_url": MCP_SERVER_URL,
                "mcp_token": MCP_TOKEN,
                "method": "tools/list",
                "params": {},
                "jsonrpc": "2.0",
                "id": 1,
            },
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return None
        
        return result.get("result", {}).get("tools", [])


async def call_tool(tool_name: str, arguments: dict):
    """Call a specific tool"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PROXY_URL}/proxy",
            headers={
                "Content-Type": "application/json",
                "X-Proxy-Token": PROXY_TOKEN,
            },
            json={
                "mcp_server_url": MCP_SERVER_URL,
                "mcp_token": MCP_TOKEN,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                },
                "jsonrpc": "2.0",
                "id": 2,
            },
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return None
        
        return result.get("result")


async def main():
    print("=" * 60)
    print("MCP Proxy Client - Python Example")
    print("=" * 60)
    
    # List tools
    print("\n1. Listing available tools...")
    tools = await list_tools()
    
    if tools:
        print(f"\nFound {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description', 'No description')}")
    else:
        print("No tools found or error occurred")
        return
    
    # Call a tool (example)
    if tools:
        tool_name = tools[0].get("name")
        print(f"\n2. Calling tool: {tool_name}")
        
        # Adjust arguments based on your tool's schema
        result = await call_tool(tool_name, {})
        
        if result:
            print(f"\nTool result:")
            print(json.dumps(result, indent=2))
        else:
            print("Tool call failed or returned no result")


if __name__ == "__main__":
    asyncio.run(main())
