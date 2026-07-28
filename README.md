# GPT-Image MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-brightgreen.svg)](https://modelcontextprotocol.io)

一个用于调用 GPT-Image API 生成图片的 MCP 服务器，支持文生图和图生图功能。

## ✨ 功能特性

- 🎨 **文生图**：根据文本描述生成图片
- 🖼️ **图生图**：基于参考图片和描述生成新图片
- ⚙️ **灵活配置**：支持环境变量和配置文件，环境变量优先
- 🔌 **标准协议**：基于 MCP 协议，可集成到各种 AI 工具
- 📁 **自动创建目录**：保存图片时自动创建不存在的目录

## 📦 安装

### 方式一：使用 uvx 直接运行（推荐）

无需安装，直接运行：

```bash
uvx image-mcp
```

### 方式二：使用 pip 安装

```bash
pip install git+https://github.com/IronManCantFix/image-mcp.git
```

安装后可直接使用 `image-mcp` 命令。

### 方式三：从源码安装

```bash
git clone https://github.com/IronManCantFix/image-mcp.git
cd image-mcp
pip install .
```

## ⚙️ 配置

### 方式一：环境变量

```bash
export IMAGE_API_URL="https://api.openai.com/v1/images/generations"
export IMAGE_API_KEY="sk-your-api-key"
export IMAGE_MODEL="gpt-image-1"  # 可选，默认 gpt-image-1
```

### 方式二：配置文件

1. 下载配置文件模板：

```bash
mkdir -p ~/.config/image-mcp
curl -o ~/.config/image-mcp/config.json https://raw.githubusercontent.com/IronManCantFix/image-mcp/main/config.example.json
```

2. 编辑 `~/.config/image-mcp/config.json`，填入你的配置：

```json
{
  "api_url": "https://api.openai.com/v1/images/generations",
  "api_key": "sk-your-api-key",
  "model": "gpt-image-1"
}
```

> 💡 **提示**：配置文件路径可通过 `IMAGE_CONFIG_PATH` 环境变量覆盖。

### 配置优先级

环境变量 > 配置文件 > 默认值

## 🚀 使用方法

### 启动 MCP 服务器

```bash
# 使用 uvx
uvx image-mcp

# 使用 pip 安装后
image-mcp

# 从源码运行
python server.py
```

### 集成到 Cursor

在项目根目录创建 `.cursor/mcp.json` 文件：

```json
{
  "mcpServers": {
    "image-mcp": {
      "command": "uvx",
      "args": ["image-mcp"],
      "env": {
        "IMAGE_API_URL": "https://api.openai.com/v1/images/generations",
        "IMAGE_API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

或者使用 pip 安装后：

```json
{
  "mcpServers": {
    "image-mcp": {
      "command": "image-mcp",
      "env": {
        "IMAGE_API_URL": "https://api.openai.com/v1/images/generations",
        "IMAGE_API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

### 集成到 Claude Desktop

在 Claude Desktop 配置文件中添加：

```json
{
  "mcpServers": {
    "image-mcp": {
      "command": "uvx",
      "args": ["image-mcp"],
      "env": {
        "IMAGE_API_URL": "https://api.openai.com/v1/images/generations",
        "IMAGE_API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

## 🛠️ 工具说明

### text_to_image

根据文本描述生成图片。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt` | string | ✅ | 图片描述文本 |
| `save_path` | string | ✅ | 保存的本地文件路径 |
| `size` | string | ❌ | 图片尺寸，如 `1024x1024`，默认 `1024x1024` |
| `quality` | string | ❌ | 图片质量：`low` / `medium` / `high`，默认 `medium` |

**示例：**
```json
{
  "prompt": "a cute cat sitting on a windowsill",
  "save_path": "/Users/me/images/cat.png",
  "size": "1024x1024",
  "quality": "high"
}
```

### image_to_image

基于参考图片和文本描述生成新图片。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt` | string | ✅ | 变换描述文本 |
| `input_image` | string | ✅ | 输入图片的本地文件路径 |
| `save_path` | string | ✅ | 保存的本地文件路径 |
| `size` | string | ❌ | 输出图片尺寸 |
| `quality` | string | ❌ | 图片质量 |

**示例：**
```json
{
  "prompt": "make it in anime style",
  "input_image": "/Users/me/images/original.png",
  "save_path": "/Users/me/images/anime_version.png",
  "size": "1024x1024",
  "quality": "high"
}
```

## 📤 返回格式

所有工具返回统一的 JSON 格式：

### 成功

```json
{
  "success": true,
  "file_path": "/absolute/path/to/image.png",
  "message": "图片已保存"
}
```

### 失败

```json
{
  "success": false,
  "error": "错误描述"
}
```

## ❓ 常见问题

### Q: 如何获取 API Key？

A: 前往 [OpenAI Platform](https://platform.openai.com/api-keys) 创建 API Key。

### Q: 支持哪些图片格式？

A: 输出格式为 PNG。图生图输入支持 PNG、JPG、JPEG、GIF、WebP 格式。

### Q: 可以使用其他兼容的 API 吗？

A: 可以，只需将 `IMAGE_API_URL` 设置为对应的 API 端点地址即可。

### Q: 图片保存在哪里？

A: 由调用时的 `save_path` 参数决定，可以是任意路径。如果目录不存在会自动创建。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [MCP 协议官网](https://modelcontextprotocol.io)
- [OpenAI GPT-Image API 文档](https://platform.openai.com/docs/api-reference/images)
- [GitHub 仓库](https://github.com/IronManCantFix/image-mcp)
