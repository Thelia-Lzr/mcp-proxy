# MCP Proxy

A proxy server that forwards MCP (Model Context Protocol) requests from frontend applications to MCP servers, with authentication and CORS support.

## Features

- 🔒 **Authentication**: Secure proxy token system to control access
- 🔄 **Request Forwarding**: Forward HTTP and WebSocket MCP requests
- 🌐 **CORS Support**: Enable cross-origin requests from frontend applications
- 📡 **WebSocket Support**: Real-time bidirectional communication
- 🎯 **TypeScript Client**: Fully typed client library for frontend integration
- 🚀 **Easy to Deploy**: Simple Python server with FastAPI

## Architecture

```
Frontend (TypeScript) → MCP Proxy Server (Python) → MCP Server
                   ↑                           ↑
              X-Proxy-Token              MCP Token
```

## Installation

### Server Setup

1. Clone the repository:
```bash
git clone https://github.com/Thelia-Lzr/mcp-proxy.git
cd mcp-proxy
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and set your PROXY_TOKEN
```

4. Start the server:
```bash
python server.py
```

The server will start on `http://0.0.0.0:8000` by default.

### Client Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Build the TypeScript client:
```bash
npm run build
```

## Usage

### Server Configuration

Edit `.env` file:

```env
# Required: Your secure proxy token
PROXY_TOKEN=your_secure_proxy_token_here

# Optional: Server configuration
HOST=0.0.0.0
PORT=8000
```

### TypeScript Client Usage

```typescript
import MCPProxyClient from 'mcp-proxy-client';

// Initialize the client
const client = new MCPProxyClient({
  proxyUrl: 'http://localhost:8000',
  proxyToken: 'your_secure_proxy_token_here',
  mcpServerUrl: 'http://your-mcp-server.com',
  mcpToken: 'optional_mcp_server_token', // Optional
});

// Initialize connection
await client.initialize();

// List available tools
const tools = await client.listTools();
console.log('Available tools:', tools);

// Call a tool
const result = await client.callTool('tool_name', {
  param1: 'value1',
  param2: 'value2',
});
console.log('Tool result:', result);

// List resources
const resources = await client.listResources();

// Read a resource
const resource = await client.readResource('resource://example');

// Use WebSocket for real-time communication
const ws = client.connectWebSocket();
ws.onmessage = (event) => {
  console.log('Received:', event.data);
};
ws.send(JSON.stringify({ method: 'ping' }));
```

### JavaScript/Browser Usage

```javascript
// Using fetch API directly
const response = await fetch('http://localhost:8000/proxy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Proxy-Token': 'your_secure_proxy_token_here',
  },
  body: JSON.stringify({
    mcp_server_url: 'http://your-mcp-server.com',
    mcp_token: 'optional_mcp_server_token',
    method: 'tools/list',
    params: {},
    jsonrpc: '2.0',
    id: 1,
  }),
});

const data = await response.json();
console.log(data);
```

## API Endpoints

### HTTP Endpoints

#### `GET /`
Root endpoint - returns server information.

#### `GET /health`
Health check endpoint.

#### `POST /proxy`
Main proxy endpoint for forwarding MCP requests.

**Headers:**
- `X-Proxy-Token`: Your proxy authentication token (required)
- `Content-Type`: application/json

**Request Body:**
```json
{
  "mcp_server_url": "http://your-mcp-server.com",
  "mcp_token": "optional_mcp_token",
  "method": "tools/list",
  "params": {},
  "jsonrpc": "2.0",
  "id": 1
}
```

### WebSocket Endpoint

#### `WS /ws`
WebSocket proxy for real-time bidirectional communication.

**Query Parameters:**
- `proxy_token`: Your proxy authentication token (required)
- `mcp_server_url`: Target MCP server URL (required)
- `mcp_token`: MCP server authentication token (optional)

## MCP Protocol Methods

The client supports all standard MCP protocol methods:

### Tools
- `tools/list`: List available tools
- `tools/call`: Call a specific tool

### Resources
- `resources/list`: List available resources
- `resources/read`: Read a specific resource

### Prompts
- `prompts/list`: List available prompts
- `prompts/get`: Get a specific prompt

### Other
- `initialize`: Initialize the MCP connection
- `ping`: Ping the server
- `completion/complete`: Get completions

## Security

⚠️ **Important Security Notes:**

1. **Keep your PROXY_TOKEN secure**: This token controls access to your proxy server.
2. **Use HTTPS in production**: Never send tokens over unencrypted HTTP in production.
3. **Configure CORS properly**: Update the CORS settings in `server.py` for production use.
4. **Validate MCP tokens**: Ensure MCP server tokens are properly secured.

## Development

### Running Tests

```bash
# Server tests (if available)
python -m pytest

# Client tests (if available)
cd client
npm test
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
