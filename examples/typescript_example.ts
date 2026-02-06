/**
 * TypeScript Example for MCP Proxy Client
 * 
 * This example demonstrates how to use the MCP Proxy Client in a TypeScript application.
 */

import MCPProxyClient, { MCPTool } from '../client/src/index';

// Configuration
const config = {
  proxyUrl: 'http://localhost:8000',
  proxyToken: 'your_secure_proxy_token_here',
  mcpServerUrl: 'http://your-mcp-server.com',
  mcpToken: 'optional_mcp_token', // Optional
};

async function main() {
  console.log('='.repeat(60));
  console.log('MCP Proxy Client - TypeScript Example');
  console.log('='.repeat(60));

  // Create client instance
  const client = new MCPProxyClient(config);

  try {
    // 1. Initialize connection
    console.log('\n1. Initializing connection...');
    const initResult = await client.initialize();
    console.log('✓ Connection initialized');
    console.log('Server info:', initResult);

    // 2. Ping the server
    console.log('\n2. Pinging server...');
    await client.ping();
    console.log('✓ Ping successful');

    // 3. List available tools
    console.log('\n3. Listing available tools...');
    const tools: MCPTool[] = await client.listTools();
    console.log(`✓ Found ${tools.length} tools:`);
    
    tools.forEach((tool, index) => {
      console.log(`\n  ${index + 1}. ${tool.name}`);
      console.log(`     Description: ${tool.description || 'N/A'}`);
      if (tool.inputSchema.properties) {
        console.log(`     Parameters:`, Object.keys(tool.inputSchema.properties));
      }
    });

    // 4. List resources
    console.log('\n4. Listing available resources...');
    const resources = await client.listResources();
    console.log(`✓ Found ${resources.length} resources`);

    // 5. List prompts
    console.log('\n5. Listing available prompts...');
    const prompts = await client.listPrompts();
    console.log(`✓ Found ${prompts.length} prompts`);

    // 6. Call a tool (example)
    if (tools.length > 0) {
      const firstTool = tools[0];
      console.log(`\n6. Calling tool: ${firstTool.name}`);
      
      // Build arguments based on tool schema
      const args: Record<string, any> = {};
      if (firstTool.inputSchema.properties) {
        // Fill in required parameters with example values
        Object.entries(firstTool.inputSchema.properties).forEach(([key, schema]: [string, any]) => {
          if (schema.type === 'string') {
            args[key] = 'example';
          } else if (schema.type === 'number') {
            args[key] = 42;
          } else if (schema.type === 'boolean') {
            args[key] = true;
          }
        });
      }

      try {
        const result = await client.callTool(firstTool.name, args);
        console.log('✓ Tool result:');
        console.log(JSON.stringify(result, null, 2));
      } catch (error) {
        console.log(`⚠ Tool call failed: ${error}`);
      }
    }

    console.log('\n' + '='.repeat(60));
    console.log('Example completed successfully!');
    console.log('='.repeat(60));

  } catch (error) {
    console.error('\n❌ Error:', error);
    process.exit(1);
  }
}

// WebSocket example
async function websocketExample() {
  console.log('\n' + '='.repeat(60));
  console.log('WebSocket Example');
  console.log('='.repeat(60));

  const client = new MCPProxyClient(config);
  const ws = client.connectWebSocket();

  ws.onopen = () => {
    console.log('✓ WebSocket connected');
    
    // Send a request
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/list',
    }));
  };

  ws.onmessage = (event) => {
    console.log('✓ Received message:');
    const data = JSON.parse(event.data);
    console.log(JSON.stringify(data, null, 2));
  };

  ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
  };

  // Keep the connection open for a few seconds
  setTimeout(() => {
    ws.close();
  }, 5000);
}

// Run examples
if (require.main === module) {
  main().catch(console.error);
  
  // Uncomment to run WebSocket example
  // websocketExample().catch(console.error);
}

export { main, websocketExample };
