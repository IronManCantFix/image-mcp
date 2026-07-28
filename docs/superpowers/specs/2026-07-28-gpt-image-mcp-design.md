# GPT-Image MCP Server 设计文档

## 概述

创建一个 MCP（Model Context Protocol）服务器，用于调用 GPT-Image API 生成图片并保存到本地。支持文生图和图生图功能，配置灵活，可通过 MCP 协议集成到其他 AI 工具中。

## 目标用户

- 个人本地使用
- 需要导入其他 AI 软件（如 Cursor、Claude Desktop 等）作为 MCP 工具

## 技术栈

- **语言**：Python 3.10+
- **MCP SDK**：`mcp` Python SDK
- **HTTP 客户端**：`httpx`（支持异步）
- **图片处理**：`Pillow`

## 项目结构

```
image-mcp/
├── server.py          # MCP 服务主入口，定义工具
├── config.py          # 配置管理模块
├── image_client.py    # GPT-Image API 调用封装
├── requirements.txt   # Python 依赖
├── config.example.json # 配置文件示例
└── README.md          # 使用说明
```

## 配置管理

### 配置优先级

1. **环境变量**（最高优先级）
2. **配置文件**
3. **默认值**

### 环境变量

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| `IMAGE_API_URL` | API 端点地址 | 是 | 无 |
| `IMAGE_API_KEY` | API 密钥 | 是 | 无 |
| `IMAGE_MODEL` | 模型名称 | 否 | `gpt-image-1` |
| `IMAGE_CONFIG_PATH` | 配置文件路径 | 否 | `~/.config/image-mcp/config.json` |

### 配置文件

默认路径：`~/.config/image-mcp/config.json`

```json
{
  "api_url": "https://api.openai.com/v1/images/generations",
  "api_key": "sk-xxx",
  "model": "gpt-image-1"
}
```

### 配置加载逻辑

```python
def load_config():
    # 1. 尝试加载配置文件
    # 2. 环境变量覆盖配置文件
    # 3. 验证必填配置
    # 4. 返回配置对象
```

## MCP 工具定义

### 1. `text_to_image` - 文生图

**描述**：根据文本描述生成图片

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `prompt` | string | 是 | 图片描述文本 |
| `save_path` | string | 是 | 保存的本地文件路径 |
| `size` | string | 否 | 图片尺寸，如 `1024x1024`，默认 `1024x1024` |
| `quality` | string | 否 | 质量：`low`/`medium`/`high`，默认 `medium` |

**返回值**：
```json
{
  "success": true,
  "file_path": "/path/to/saved/image.png",
  "message": "图片已保存"
}
```

### 2. `image_to_image` - 图生图

**描述**：基于参考图片和文本描述生成新图片

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `prompt` | string | 是 | 变换描述文本 |
| `input_image` | string | 是 | 输入图片的本地文件路径 |
| `save_path` | string | 是 | 保存的本地文件路径 |
| `size` | string | 否 | 输出图片尺寸 |
| `quality` | string | 否 | 质量 |

**返回值**：
```json
{
  "success": true,
  "file_path": "/path/to/saved/image.png",
  "message": "图片已保存"
}
```

## 错误处理

### 错误类型

1. **配置错误**
   - 缺少必填配置 → 提示用户设置对应的环境变量或配置文件
   - 配置文件格式错误 → 提示具体错误位置

2. **文件错误**
   - 输入图片路径不存在 → 提示文件不存在
   - 保存路径目录不存在 → 自动创建目录
   - 权限不足 → 提示权限错误

3. **API 错误**
   - 网络连接失败 → 提示检查网络
   - 认证失败 → 提示检查 API Key
   - 请求被拒绝 → 返回 API 错误信息

### 错误返回格式

```json
{
  "success": false,
  "error": "错误描述",
  "details": "详细错误信息（可选）"
}
```

## API 调用流程

### 文生图流程

1. 验证配置（API URL、API Key）
2. 验证保存路径
3. 构造请求体（prompt、size、quality）
4. 调用 API
5. 解析响应，提取 base64 图片数据
6. 解码并保存到本地
7. 返回结果

### 图生图流程

1. 验证配置
2. 验证输入图片路径存在
3. 读取输入图片，转换为 base64
4. 构造请求体（prompt、image、size、quality）
5. 调用 API
6. 解析响应，提取 base64 图片数据
7. 解码并保存到本地
8. 返回结果

## 依赖列表

```
mcp>=1.0.0
httpx>=0.25.0
Pillow>=10.0.0
```

## 使用方式

### 安装

```bash
cd image-mcp
pip install -r requirements.txt
```

### 配置

1. 复制配置文件示例：
   ```bash
   mkdir -p ~/.config/image-mcp
   cp config.example.json ~/.config/image-mcp/config.json
   ```

2. 编辑配置文件，填入 API URL 和 API Key

3. 或者设置环境变量：
   ```bash
   export IMAGE_API_URL="https://api.openai.com/v1/images/generations"
   export IMAGE_API_KEY="sk-xxx"
   ```

### 启动 MCP 服务

```bash
python server.py
```

### 集成到其他工具

在 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "image-mcp": {
      "command": "python",
      "args": ["/path/to/image-mcp/server.py"],
      "env": {
        "IMAGE_API_URL": "https://api.openai.com/v1/images/generations",
        "IMAGE_API_KEY": "sk-xxx"
      }
    }
  }
}
```

## 设计决策

1. **选择 stdio 模式**：最通用，兼容几乎所有 MCP 客户端
2. **配置文件路径可配置**：通过环境变量 `IMAGE_CONFIG_PATH` 可以覆盖默认路径
3. **自动创建目录**：保存图片时如果目录不存在会自动创建
4. **返回统一格式**：所有工具返回统一的 JSON 格式，便于客户端处理

## 未来扩展（可选）

- 支持批量生成
- 支持图片编辑（inpainting）
- 支持多张图片生成
- 支持自定义 API 请求头

## 验收标准

1. 能够通过 stdio 模式启动 MCP 服务
2. `text_to_image` 工具能够生成图片并保存到指定路径
3. `image_to_image` 工具能够基于参考图生成新图片
4. 配置文件和环境变量都能正确加载，环境变量优先
5. 错误情况能返回清晰的错误信息
6. 能够集成到 Cursor 或 Claude Desktop 中使用
