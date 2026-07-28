# GPT-Image MCP Server

一个用于调用 GPT-Image API 生成图片的 MCP 服务器，支持文生图和图生图。

## 功能特性

- ✅ 文生图：根据文本描述生成图片
- ✅ 图生图：基于参考图片和描述生成新图片
- ✅ 灵活配置：支持环境变量和配置文件
- ✅ 标准 MCP 协议：可集成到各种 AI 工具

## 安装

```bash
git clone <repo-url>
cd image-mcp
pip install -r requirements.txt
```

## 配置

### 方式一：环境变量

```bash
export IMAGE_API_URL="https://api.openai.com/v1/images/generations"
export IMAGE_API_KEY="sk-your-api-key"
export IMAGE_MODEL="gpt-image-1"  # 可选，默认 gpt-image-1
```

### 方式二：配置文件

```bash
mkdir -p ~/.config/image-mcp
cp config.example.json ~/.config/image-mcp/config.json
# 编辑 config.json 填入你的配置
```

配置文件路径可通过 `IMAGE_CONFIG_PATH` 环境变量覆盖。

## 使用方法

### 作为 MCP 服务器启动

```bash
python server.py
```

### 集成到 Cursor

在 `.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "image-mcp": {
      "command": "python",
      "args": ["/path/to/image-mcp/server.py"],
      "env": {
        "IMAGE_API_URL": "https://api.openai.com/v1/images/generations",
        "IMAGE_API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

### 集成到 Claude Desktop

在 Claude Desktop 配置文件中添加类似配置。

## 工具说明

### text_to_image

根据文本描述生成图片。

**参数：**
- `prompt` (必填): 图片描述
- `save_path` (必填): 保存路径
- `size` (可选): 尺寸，如 `1024x1024`
- `quality` (可选): 质量 `low`/`medium`/`high`

### image_to_image

基于参考图片生成新图片。

**参数：**
- `prompt` (必填): 变换描述
- `input_image` (必填): 输入图片路径
- `save_path` (必填): 保存路径
- `size` (可选): 输出尺寸
- `quality` (可选): 质量

## 错误处理

所有工具返回统一格式：

```json
{
  "success": true,
  "file_path": "/path/to/image.png",
  "message": "图片已保存"
}
```

或

```json
{
  "success": false,
  "error": "错误描述"
}
```

## 许可证

MIT
