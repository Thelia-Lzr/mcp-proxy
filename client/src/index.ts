/**
 * MCP Proxy Client
 * 
 * TypeScript client for communicating with MCP servers through a proxy
 */

export interface MCPProxyConfig {
  proxyUrl: string;
  proxyToken: string;
  mcpServerUrl: string;
  mcpToken?: string;
}

export interface MCPTool {
  name: string;
  description?: string;
  inputSchema: {
    type: string;
    properties?: Record<string, any>;
    required?: string[];
  };
}

export interface MCPRequest {
  method: string;
  params?: Record<string, any>;
}

export interface MCPResponse<T = any> {
  jsonrpc: string;
  id: number;
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export class MCPProxyClient {
  private config: MCPProxyConfig;
  private requestId: number = 1;

  constructor(config: MCPProxyConfig) {
    this.config = config;
  }

  /**
   * Send a request to the MCP server through the proxy
   */
  private async sendRequest<T = any>(
    method: string,
    params?: Record<string, any>
  ): Promise<T> {
    const response = await fetch(`${this.config.proxyUrl}/proxy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Proxy-Token': this.config.proxyToken,
      },
      body: JSON.stringify({
        mcp_server_url: this.config.mcpServerUrl,
        mcp_token: this.config.mcpToken,
        method,
        params,
        jsonrpc: '2.0',
        id: this.requestId++,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const result: MCPResponse<T> = await response.json();

    if (result.error) {
      throw new Error(
        `MCP Error ${result.error.code}: ${result.error.message}`
      );
    }

    return result.result as T;
  }

  /**
   * Initialize the MCP connection
   */
  async initialize(): Promise<any> {
    return this.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {
        roots: { listChanged: true },
        sampling: {},
      },
      clientInfo: {
        name: 'mcp-proxy-client',
        version: '1.0.0',
      },
    });
  }

  /**
   * List available tools from the MCP server
   */
  async listTools(): Promise<MCPTool[]> {
    const result = await this.sendRequest<{ tools: MCPTool[] }>('tools/list');
    return result.tools || [];
  }

  /**
   * Call a specific tool with arguments
   */
  async callTool(name: string, args?: Record<string, any>): Promise<any> {
    return this.sendRequest('tools/call', {
      name,
      arguments: args || {},
    });
  }

  /**
   * List available resources
   */
  async listResources(): Promise<any[]> {
    const result = await this.sendRequest<{ resources: any[] }>('resources/list');
    return result.resources || [];
  }

  /**
   * Read a resource
   */
  async readResource(uri: string): Promise<any> {
    return this.sendRequest('resources/read', { uri });
  }

  /**
   * List available prompts
   */
  async listPrompts(): Promise<any[]> {
    const result = await this.sendRequest<{ prompts: any[] }>('prompts/list');
    return result.prompts || [];
  }

  /**
   * Get a specific prompt
   */
  async getPrompt(name: string, args?: Record<string, any>): Promise<any> {
    return this.sendRequest('prompts/get', {
      name,
      arguments: args || {},
    });
  }

  /**
   * Send a completion request
   */
  async complete(
    ref: { type: string; name: string },
    argument: { name: string; value: string }
  ): Promise<any> {
    return this.sendRequest('completion/complete', {
      ref,
      argument,
    });
  }

  /**
   * Ping the MCP server
   */
  async ping(): Promise<void> {
    await this.sendRequest('ping');
  }

  /**
   * Create a WebSocket connection to the MCP server through the proxy
   * This allows for real-time bidirectional communication
   */
  connectWebSocket(): WebSocket {
    const wsUrl = this.config.proxyUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    const params = new URLSearchParams({
      proxy_token: this.config.proxyToken,
      mcp_server_url: this.config.mcpServerUrl,
    });
    
    if (this.config.mcpToken) {
      params.append('mcp_token', this.config.mcpToken);
    }

    return new WebSocket(`${wsUrl}/ws?${params.toString()}`);
  }
}

export default MCPProxyClient;
