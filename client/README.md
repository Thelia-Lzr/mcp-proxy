# MCP Proxy Client

TypeScript/JavaScript client library for communicating with MCP servers through the MCP Proxy.

## Installation

### From Source

```bash
npm install
npm run build
```

### In Your Project

```bash
# If published to npm
npm install mcp-proxy-client

# Or use it locally
npm install /path/to/mcp-proxy/client
```

## Quick Start

```typescript
import MCPProxyClient from 'mcp-proxy-client';

const client = new MCPProxyClient({
  proxyUrl: 'http://localhost:8000',
  proxyToken: 'your_proxy_token',
  mcpServerUrl: 'http://mcp-server.example.com',
  mcpToken: 'optional_mcp_token',
});

// Initialize and use
await client.initialize();
const tools = await client.listTools();
```

## API Reference

### Constructor

```typescript
new MCPProxyClient(config: MCPProxyConfig)
```

**Config Parameters:**
- `proxyUrl`: URL of the proxy server (e.g., 'http://localhost:8000')
- `proxyToken`: Authentication token for the proxy
- `mcpServerUrl`: URL of the target MCP server
- `mcpToken` (optional): Authentication token for the MCP server

### Methods

#### `initialize(): Promise<any>`
Initialize the MCP connection.

#### `listTools(): Promise<MCPTool[]>`
Get list of available tools from the MCP server.

**Returns:** Array of tool definitions with name, description, and input schema.

#### `callTool(name: string, args?: Record<string, any>): Promise<any>`
Call a specific tool with arguments.

**Parameters:**
- `name`: Tool name
- `args`: Tool arguments object

#### `listResources(): Promise<any[]>`
List available resources.

#### `readResource(uri: string): Promise<any>`
Read a specific resource.

#### `listPrompts(): Promise<any[]>`
List available prompts.

#### `getPrompt(name: string, args?: Record<string, any>): Promise<any>`
Get a specific prompt.

#### `ping(): Promise<void>`
Ping the MCP server.

#### `connectWebSocket(): WebSocket`
Create a WebSocket connection for real-time communication.

## Examples

### Basic Tool Usage

```typescript
const client = new MCPProxyClient({
  proxyUrl: 'http://localhost:8000',
  proxyToken: 'my-secure-token',
  mcpServerUrl: 'http://mcp.example.com',
});

// List and call tools
const tools = await client.listTools();
console.log('Available tools:', tools.map(t => t.name));

const result = await client.callTool('search', {
  query: 'typescript MCP',
  limit: 10,
});
console.log('Search results:', result);
```

### WebSocket Communication

```typescript
const client = new MCPProxyClient({
  proxyUrl: 'http://localhost:8000',
  proxyToken: 'my-secure-token',
  mcpServerUrl: 'ws://mcp.example.com',
});

const ws = client.connectWebSocket();

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list',
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### React Integration

```typescript
import React, { useEffect, useState } from 'react';
import MCPProxyClient from 'mcp-proxy-client';

function MCPToolList() {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const client = new MCPProxyClient({
      proxyUrl: process.env.REACT_APP_PROXY_URL,
      proxyToken: process.env.REACT_APP_PROXY_TOKEN,
      mcpServerUrl: process.env.REACT_APP_MCP_SERVER_URL,
    });

    async function fetchTools() {
      try {
        await client.initialize();
        const toolList = await client.listTools();
        setTools(toolList);
      } catch (error) {
        console.error('Error fetching tools:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchTools();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Available Tools</h2>
      <ul>
        {tools.map((tool) => (
          <li key={tool.name}>
            <strong>{tool.name}</strong>: {tool.description}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Vue Integration

```vue
<template>
  <div>
    <h2>MCP Tools</h2>
    <ul v-if="tools.length">
      <li v-for="tool in tools" :key="tool.name">
        <strong>{{ tool.name }}</strong>: {{ tool.description }}
      </li>
    </ul>
    <p v-else>Loading...</p>
  </div>
</template>

<script>
import MCPProxyClient from 'mcp-proxy-client';

export default {
  data() {
    return {
      tools: [],
      client: null,
    };
  },
  async mounted() {
    this.client = new MCPProxyClient({
      proxyUrl: process.env.VUE_APP_PROXY_URL,
      proxyToken: process.env.VUE_APP_PROXY_TOKEN,
      mcpServerUrl: process.env.VUE_APP_MCP_SERVER_URL,
    });

    await this.client.initialize();
    this.tools = await this.client.listTools();
  },
};
</script>
```

## Error Handling

```typescript
try {
  const result = await client.callTool('my-tool', { param: 'value' });
  console.log(result);
} catch (error) {
  if (error.message.includes('401')) {
    console.error('Authentication failed - check your proxy token');
  } else if (error.message.includes('MCP Error')) {
    console.error('MCP server error:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## TypeScript Types

The client provides full TypeScript support with the following types:

```typescript
interface MCPProxyConfig {
  proxyUrl: string;
  proxyToken: string;
  mcpServerUrl: string;
  mcpToken?: string;
}

interface MCPTool {
  name: string;
  description?: string;
  inputSchema: {
    type: string;
    properties?: Record<string, any>;
    required?: string[];
  };
}

interface MCPResponse<T = any> {
  jsonrpc: string;
  id: number;
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}
```

## License

MIT
