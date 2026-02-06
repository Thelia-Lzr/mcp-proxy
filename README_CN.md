# MCP 代理服务器

这是一个代理服务器，可以将前端应用的 MCP（模型上下文协议）请求转发到 MCP 服务器，提供身份验证和 CORS 支持。

⚠️ **安全提示**: 该代理会将请求转发到用户指定的 URL。部署前请查看 [SECURITY.md](SECURITY.md) 了解重要的安全注意事项。

## 功能特性

- 🔒 **身份验证**: 安全的代理令牌系统控制访问
- 🛡️ **SSRF 防护**: URL 验证防止访问内部网络
- 🔄 **请求转发**: 转发 HTTP 和 WebSocket MCP 请求
- 🌐 **CORS 支持**: 支持前端应用的跨域请求
- 📡 **WebSocket 支持**: 实时双向通信
- 🎯 **TypeScript 客户端**: 完整类型定义的前端集成库
- 🚀 **易于部署**: 基于 FastAPI 的简单 Python 服务器

## 快速开始

### 方法一：自动化安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/Thelia-Lzr/mcp-proxy.git
cd mcp-proxy

# 2. 运行自动化安装脚本
./setup.sh

# 3. 启动服务器
python server.py
```

安装脚本会自动：
- 安装 Python 依赖
- 创建 `.env` 配置文件
- 生成安全的代理令牌
- 构建 TypeScript 客户端

### 方法二：手动安装

#### 1. 服务器端安装

```bash
# 克隆仓库
git clone https://github.com/Thelia-Lzr/mcp-proxy.git
cd mcp-proxy

# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 PROXY_TOKEN
nano .env  # 或使用其他编辑器

# 启动服务器
python server.py
```

服务器将在 `http://0.0.0.0:8000` 启动。

#### 2. 客户端安装（可选）

```bash
cd client
npm install
npm run build
```

### 方法三：Docker 部署

```bash
# 设置代理令牌
export PROXY_TOKEN=你的安全令牌

# 使用 docker-compose 启动
docker-compose up -d

# 或手动运行
docker build -t mcp-proxy .
docker run -p 8000:8000 -e PROXY_TOKEN=你的安全令牌 mcp-proxy
```

## 使用方法

### 1. TypeScript/JavaScript 客户端使用

```typescript
import MCPProxyClient from 'mcp-proxy-client';

// 创建客户端实例
const client = new MCPProxyClient({
  proxyUrl: 'http://localhost:8000',        // 代理服务器地址
  proxyToken: '你的代理令牌',                // 在 .env 中配置的令牌
  mcpServerUrl: 'http://你的mcp服务器.com',  // 目标 MCP 服务器地址
  mcpToken: 'mcp服务器令牌',                 // 可选，MCP 服务器的认证令牌
});

// 初始化连接
await client.initialize();

// 获取工具列表
const tools = await client.listTools();
console.log('可用工具:', tools);

// 调用工具
const result = await client.callTool('工具名称', {
  参数1: '值1',
  参数2: '值2',
});
console.log('工具结果:', result);

// 获取资源列表
const resources = await client.listResources();

// 读取资源
const resource = await client.readResource('resource://示例');

// 使用 WebSocket 进行实时通信
const ws = client.connectWebSocket();
ws.onmessage = (event) => {
  console.log('收到消息:', event.data);
};
```

### 2. 在浏览器中直接使用（无需客户端库）

```javascript
// 使用 fetch API 直接调用
const response = await fetch('http://localhost:8000/proxy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Proxy-Token': '你的代理令牌',
  },
  body: JSON.stringify({
    mcp_server_url: 'http://你的mcp服务器.com',
    mcp_token: 'mcp服务器令牌',  // 可选
    method: 'tools/list',
    params: {},
    jsonrpc: '2.0',
    id: 1,
  }),
});

const data = await response.json();
console.log(data);
```

### 3. Python 客户端使用

```python
import httpx
import asyncio

async def list_tools():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/proxy",
            headers={
                "Content-Type": "application/json",
                "X-Proxy-Token": "你的代理令牌",
            },
            json={
                "mcp_server_url": "http://你的mcp服务器.com",
                "mcp_token": "mcp服务器令牌",  # 可选
                "method": "tools/list",
                "params": {},
                "jsonrpc": "2.0",
                "id": 1,
            },
        )
        return response.json()

# 运行
result = asyncio.run(list_tools())
print(result)
```

### 4. React 集成示例

```typescript
import React, { useEffect, useState } from 'react';
import MCPProxyClient from 'mcp-proxy-client';

function MCPTools() {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const client = new MCPProxyClient({
      proxyUrl: 'http://localhost:8000',
      proxyToken: '你的代理令牌',
      mcpServerUrl: 'http://你的mcp服务器.com',
    });

    async function fetchTools() {
      try {
        await client.initialize();
        const toolList = await client.listTools();
        setTools(toolList);
      } catch (error) {
        console.error('获取工具失败:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchTools();
  }, []);

  if (loading) return <div>加载中...</div>;

  return (
    <div>
      <h2>可用工具</h2>
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

## 配置说明

### 环境变量配置（.env 文件）

```env
# 必需：代理服务器的认证令牌
# 只有提供正确令牌的请求才能使用代理
PROXY_TOKEN=你的安全令牌

# 可选：服务器配置
HOST=0.0.0.0  # 监听地址
PORT=8000     # 监听端口
```

**重要提示**：
- `PROXY_TOKEN` 必须是强密码（建议 32 个字符以上）
- 不要将 `.env` 文件提交到版本控制系统
- 定期更换令牌以提高安全性

## API 端点说明

### HTTP 端点

#### `GET /` - 根端点
返回服务器信息

#### `GET /health` - 健康检查
检查服务器状态

#### `POST /proxy` - 主要代理端点
转发 MCP 请求到目标服务器

**请求头：**
- `X-Proxy-Token`: 代理认证令牌（必需）
- `Content-Type`: application/json

**请求体：**
```json
{
  "mcp_server_url": "http://你的mcp服务器.com",
  "mcp_token": "可选的mcp令牌",
  "method": "tools/list",
  "params": {},
  "jsonrpc": "2.0",
  "id": 1
}
```

### WebSocket 端点

#### `WS /ws` - WebSocket 代理
实时双向通信

**查询参数：**
- `proxy_token`: 代理认证令牌（必需）
- `mcp_server_url`: 目标 MCP 服务器 URL（必需）
- `mcp_token`: MCP 服务器认证令牌（可选）

## MCP 协议方法

客户端支持所有标准 MCP 协议方法：

### 工具相关
- `tools/list` - 获取可用工具列表
- `tools/call` - 调用特定工具

### 资源相关
- `resources/list` - 获取可用资源列表
- `resources/read` - 读取特定资源

### 提示词相关
- `prompts/list` - 获取可用提示词列表
- `prompts/get` - 获取特定提示词

### 其他
- `initialize` - 初始化 MCP 连接
- `ping` - ping 服务器
- `completion/complete` - 获取补全

## 示例文件

项目包含多个示例文件帮助你快速上手：

- `examples/python_client_example.py` - Python 客户端完整示例
- `examples/typescript_example.ts` - TypeScript/Node.js 示例
- `examples/browser_example.html` - 浏览器交互式界面示例

运行示例：

```bash
# Python 示例
python examples/python_client_example.py

# TypeScript 示例（需要先构建）
cd examples
npx ts-node typescript_example.ts

# 浏览器示例（在浏览器中打开）
open examples/browser_example.html
```

## 常见问题

### 1. 服务器启动失败

**问题**：`PROXY_TOKEN not set in environment variables!`

**解决**：确保 `.env` 文件存在并设置了 `PROXY_TOKEN`：
```bash
cp .env.example .env
nano .env  # 编辑并设置 PROXY_TOKEN
```

### 2. 认证失败

**问题**：收到 `401 Invalid proxy token` 错误

**解决**：检查客户端使用的令牌是否与 `.env` 中的 `PROXY_TOKEN` 一致

### 3. 连接 MCP 服务器失败

**问题**：`Failed to connect to MCP server`

**解决**：
- 检查 MCP 服务器 URL 是否正确
- 确认 MCP 服务器正在运行
- 检查网络连接和防火墙设置
- 如果 MCP 服务器需要认证，提供正确的 `mcp_token`

### 4. CORS 错误

**问题**：浏览器控制台显示 CORS 错误

**解决**：代理服务器已配置 CORS 支持。如果仍有问题：
- 确保使用正确的代理服务器地址
- 检查浏览器是否阻止了混合内容（HTTP/HTTPS）
- 在生产环境中配置适当的 CORS 策略（编辑 `server.py` 中的 CORS 设置）

## 安全注意事项

⚠️ **重要**：请阅读 [SECURITY.md](SECURITY.md) 了解详细的安全考虑

**基本安全措施**：
1. 使用强密码作为 `PROXY_TOKEN`（至少 32 个字符）
2. 生产环境中使用 HTTPS
3. 定期更换令牌
4. 限制代理服务器的网络访问
5. 监控日志以发现可疑活动
6. 只允许信任的用户访问代理服务器

## 开发和测试

### 运行测试

```bash
# 启动服务器（在一个终端）
PROXY_TOKEN=test_token python server.py

# 运行测试（在另一个终端）
python test_server.py
```

### 客户端开发

```bash
cd client
npm install
npm run build  # 构建 TypeScript
```

## 获取帮助

- 查看完整英文文档：[README.md](README.md)
- 安全文档：[SECURITY.md](SECURITY.md)
- 客户端文档：[client/README.md](client/README.md)
- 提交问题：[GitHub Issues](https://github.com/Thelia-Lzr/mcp-proxy/issues)

## 许可证

MIT
