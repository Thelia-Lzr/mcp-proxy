"""
Integration test for MCP Proxy Server

This test verifies basic functionality of the proxy server.
"""

import asyncio
import httpx
import pytest

# Test configuration
PROXY_URL = "http://localhost:8000"
PROXY_TOKEN = "test_token_123"

# Note: These tests require the server to be running
# Start the server with: PROXY_TOKEN=test_token_123 python server.py


async def test_health_endpoint():
    """Test the health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PROXY_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


async def test_root_endpoint():
    """Test the root endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PROXY_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "MCP Proxy Server"


async def test_proxy_without_token():
    """Test proxy endpoint without authentication token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PROXY_URL}/proxy",
            json={
                "mcp_server_url": "http://example.com",
                "method": "test",
                "jsonrpc": "2.0",
                "id": 1,
            },
        )
        assert response.status_code == 401


async def test_proxy_with_invalid_token():
    """Test proxy endpoint with invalid token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PROXY_URL}/proxy",
            headers={"X-Proxy-Token": "invalid_token"},
            json={
                "mcp_server_url": "http://example.com",
                "method": "test",
                "jsonrpc": "2.0",
                "id": 1,
            },
        )
        assert response.status_code == 401


if __name__ == "__main__":
    print("Running basic integration tests...")
    print("Note: Server must be running with PROXY_TOKEN=test_token_123")
    
    # Run tests
    asyncio.run(test_health_endpoint())
    print("✓ Health endpoint test passed")
    
    asyncio.run(test_root_endpoint())
    print("✓ Root endpoint test passed")
    
    asyncio.run(test_proxy_without_token())
    print("✓ Proxy without token test passed")
    
    asyncio.run(test_proxy_with_invalid_token())
    print("✓ Proxy with invalid token test passed")
    
    print("\nAll tests passed!")
