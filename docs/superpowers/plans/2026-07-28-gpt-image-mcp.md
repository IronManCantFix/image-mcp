# GPT-Image MCP Server 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个 Python MCP 服务器，支持调用 GPT-Image API 进行文生图和图生图，配置灵活，可集成到其他 AI 工具。

**Architecture:** 使用 Python MCP SDK 实现 stdio 模式的 MCP 服务器，通过 httpx 调用 GPT-Image API，支持环境变量和配置文件两种配置方式。

**Tech Stack:** Python 3.10+, mcp, httpx, Pillow

---

## 文件结构

```
image-mcp/
├── server.py          # MCP 服务主入口，定义工具和启动逻辑
├── config.py          # 配置管理模块，加载环境变量和配置文件
├── image_client.py    # GPT-Image API 调用封装
├── requirements.txt   # Python 依赖
├── config.example.json # 配置文件示例
├── tests/
│   ├── test_config.py     # 配置管理测试
│   └── test_image_client.py # API 客户端测试
└── README.md          # 使用说明
```

---

### Task 1: 初始化项目结构和依赖

**Files:**
- Create: `requirements.txt`
- Create: `config.example.json`

- [ ] **Step 1: 创建 requirements.txt**

```
mcp>=1.0.0
httpx>=0.25.0
Pillow>=10.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

- [ ] **Step 2: 创建配置文件示例**

```json
{
  "api_url": "https://api.openai.com/v1/images/generations",
  "api_key": "sk-your-api-key-here",
  "model": "gpt-image-1"
}
```

- [ ] **Step 3: 安装依赖**

Run: `pip install -r requirements.txt`
Expected: 成功安装所有依赖

---

### Task 2: 实现配置管理模块

**Files:**
- Create: `config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 编写配置管理测试**

```python
import pytest
import os
import json
import tempfile
from pathlib import Path

def test_load_config_from_env(monkeypatch):
    """测试从环境变量加载配置"""
    monkeypatch.setenv("IMAGE_API_URL", "https://test.api.com/v1")
    monkeypatch.setenv("IMAGE_API_KEY", "test-key-123")
    
    from config import load_config
    config = load_config()
    
    assert config.api_url == "https://test.api.com/v1"
    assert config.api_key == "test-key-123"
    assert config.model == "gpt-image-1"  # 默认值

def test_load_config_from_file(tmp_path):
    """测试从配置文件加载"""
    config_data = {
        "api_url": "https://file.api.com/v1",
        "api_key": "file-key-456",
        "model": "gpt-image-2"
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    
    from config import load_config
    config = load_config(config_path=str(config_file))
    
    assert config.api_url == "https://file.api.com/v1"
    assert config.api_key == "file-key-456"
    assert config.model == "gpt-image-2"

def test_env_overrides_file(tmp_path, monkeypatch):
    """测试环境变量覆盖配置文件"""
    config_data = {
        "api_url": "https://file.api.com/v1",
        "api_key": "file-key"
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    
    monkeypatch.setenv("IMAGE_API_URL", "https://env.api.com/v1")
    
    from config import load_config
    config = load_config(config_path=str(config_file))
    
    assert config.api_url == "https://env.api.com/v1"
    assert config.api_key == "file-key"

def test_missing_required_config(monkeypatch):
    """测试缺少必填配置时报错"""
    monkeypatch.delenv("IMAGE_API_URL", raising=False)
    monkeypatch.delenv("IMAGE_API_KEY", raising=False)
    
    from config import load_config, ConfigError
    with pytest.raises(ConfigError):
        load_config()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_config.py -v`
Expected: FAIL - 模块 config 不存在

- [ ] **Step 3: 实现配置管理模块**

```python
"""配置管理模块"""
import os
import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = "~/.config/image-mcp/config.json"

@dataclass
class ImageConfig:
    """图片生成配置"""
    api_url: str
    api_key: str
    model: str = "gpt-image-1"

class ConfigError(Exception):
    """配置错误"""
    pass

def load_config(config_path: str = None) -> ImageConfig:
    """加载配置
    
    优先级：环境变量 > 配置文件 > 默认值
    """
    config_data = {}
    
    # 尝试加载配置文件
    if config_path is None:
        config_path = os.environ.get("IMAGE_CONFIG_PATH", DEFAULT_CONFIG_PATH)
    
    config_path = Path(config_path).expanduser()
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件格式错误: {e}")
    
    # 环境变量覆盖
    api_url = os.environ.get("IMAGE_API_URL", config_data.get("api_url"))
    api_key = os.environ.get("IMAGE_API_KEY", config_data.get("api_key"))
    model = os.environ.get("IMAGE_MODEL", config_data.get("model", "gpt-image-1"))
    
    # 验证必填配置
    if not api_url:
        raise ConfigError("缺少 API URL，请设置环境变量 IMAGE_API_URL 或在配置文件中配置 api_url")
    if not api_key:
        raise ConfigError("缺少 API Key，请设置环境变量 IMAGE_API_KEY 或在配置文件中配置 api_key")
    
    return ImageConfig(
        api_url=api_url,
        api_key=api_key,
        model=model
    )
```

- [ ] **Step 4: 创建 tests 目录和 __init__.py**

Run: `mkdir -p tests && touch tests/__init__.py`

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_config.py -v`
Expected: PASS - 所有测试通过

- [ ] **Step 6: 提交配置模块**

```bash
git add config.py tests/test_config.py
git commit -m "feat: add config management module"
```

---

### Task 3: 实现 GPT-Image API 客户端

**Files:**
- Create: `image_client.py`
- Create: `tests/test_image_client.py`

- [ ] **Step 1: 编写 API 客户端测试**

```python
import pytest
import base64
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

@pytest.fixture
def mock_config():
    """模拟配置"""
    from config import ImageConfig
    return ImageConfig(
        api_url="https://api.test.com/v1/images/generations",
        api_key="test-key",
        model="gpt-image-1"
    )

@pytest.mark.asyncio
async def test_text_to_image_success(mock_config):
    """测试文生图成功"""
    # 模拟 API 响应
    fake_image_data = b"fake image data"
    fake_b64 = base64.b64encode(fake_image_data).decode()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"b64_json": fake_b64}]
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        from image_client import ImageClient
        client = ImageClient(mock_config)
        
        result = await client.text_to_image(
            prompt="a cute cat",
            save_path="/tmp/test_output.png"
        )
        
        assert result["success"] is True
        assert result["file_path"] == "/tmp/test_output.png"

@pytest.mark.asyncio
async def test_text_to_image_api_error(mock_config):
    """测试文生图 API 错误"""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        from image_client import ImageClient
        client = ImageClient(mock_config)
        
        result = await client.text_to_image(
            prompt="a cute cat",
            save_path="/tmp/test_output.png"
        )
        
        assert result["success"] is False
        assert "error" in result

@pytest.mark.asyncio
async def test_image_to_image_input_not_found(mock_config):
    """测试图生图输入文件不存在"""
    from image_client import ImageClient
    client = ImageClient(mock_config)
    
    result = await client.image_to_image(
        prompt="make it blue",
        input_image="/nonexistent/image.png",
        save_path="/tmp/test_output.png"
    )
    
    assert result["success"] is False
    assert "不存在" in result["error"]
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_image_client.py -v`
Expected: FAIL - 模块 image_client 不存在

- [ ] **Step 3: 实现 API 客户端**

```python
"""GPT-Image API 客户端"""
import base64
import httpx
from pathlib import Path
from typing import Optional

from config import ImageConfig

class ImageClient:
    """GPT-Image API 客户端"""
    
    def __init__(self, config: ImageConfig):
        self.config = config
    
    async def text_to_image(
        self,
        prompt: str,
        save_path: str,
        size: str = "1024x1024",
        quality: str = "medium"
    ) -> dict:
        """文生图
        
        Args:
            prompt: 图片描述
            save_path: 保存路径
            size: 图片尺寸
            quality: 质量 (low/medium/high)
            
        Returns:
            dict: {"success": bool, "file_path": str, "message": str} 或 {"success": bool, "error": str}
        """
        return await self._generate(
            prompt=prompt,
            save_path=save_path,
            size=size,
            quality=quality
        )
    
    async def image_to_image(
        self,
        prompt: str,
        input_image: str,
        save_path: str,
        size: str = "1024x1024",
        quality: str = "medium"
    ) -> dict:
        """图生图
        
        Args:
            prompt: 变换描述
            input_image: 输入图片路径
            save_path: 保存路径
            size: 输出尺寸
            quality: 质量
            
        Returns:
            dict: 操作结果
        """
        # 检查输入文件是否存在
        input_path = Path(input_image)
        if not input_path.exists():
            return {
                "success": False,
                "error": f"输入图片不存在: {input_image}"
            }
        
        # 读取图片并转为 base64
        try:
            with open(input_path, "rb") as f:
                image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode()
        except Exception as e:
            return {
                "success": False,
                "error": f"读取输入图片失败: {e}"
            }
        
        # 获取 MIME 类型
        suffix = input_path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        mime_type = mime_map.get(suffix, "image/png")
        image_url = f"data:{mime_type};base64,{image_b64}"
        
        return await self._generate(
            prompt=prompt,
            save_path=save_path,
            size=size,
            quality=quality,
            image=image_url
        )
    
    async def _generate(
        self,
        prompt: str,
        save_path: str,
        size: str = "1024x1024",
        quality: str = "medium",
        image: Optional[str] = None
    ) -> dict:
        """调用 API 生成图片"""
        # 构造请求体
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1
        }
        
        # 如果有参考图片，添加到请求
        if image:
            payload["image"] = image
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.config.api_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                # 提取图片数据
                if "data" in data and len(data["data"]) > 0:
                    image_data = data["data"][0]
                    
                    # 支持 b64_json 和 url 两种响应格式
                    if "b64_json" in image_data:
                        img_bytes = base64.b64decode(image_data["b64_json"])
                    elif "url" in image_data:
                        # 下载图片
                        img_response = await client.get(image_data["url"])
                        img_bytes = img_response.content
                    else:
                        return {"success": False, "error": "API 响应中没有图片数据"}
                    
                    # 确保保存目录存在
                    save_dir = Path(save_path).parent
                    save_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 保存图片
                    with open(save_path, "wb") as f:
                        f.write(img_bytes)
                    
                    return {
                        "success": True,
                        "file_path": str(Path(save_path).resolve()),
                        "message": "图片已保存"
                    }
                else:
                    return {"success": False, "error": "API 响应格式异常"}
        
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"API 请求失败 (HTTP {e.response.status_code})",
                "details": e.response.text
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"网络请求失败: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"生成图片失败: {e}"
            }
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_image_client.py -v`
Expected: PASS - 所有测试通过

- [ ] **Step 5: 提交 API 客户端**

```bash
git add image_client.py tests/test_image_client.py
git commit -m "feat: add GPT-Image API client"
```

---

### Task 4: 实现 MCP 服务器主模块

**Files:**
- Create: `server.py`

- [ ] **Step 1: 实现 MCP 服务器**

```python
"""GPT-Image MCP Server"""
import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from config import load_config, ConfigError
from image_client import ImageClient

# 创建 MCP 服务器实例
server = Server("image-mcp")

# 全局客户端实例
image_client = None

def init_client():
    """初始化 API 客户端"""
    global image_client
    try:
        config = load_config()
        image_client = ImageClient(config)
        return True
    except ConfigError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        return False

@server.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="text_to_image",
            description="根据文本描述生成图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "图片描述文本"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "保存的本地文件路径"
                    },
                    "size": {
                        "type": "string",
                        "description": "图片尺寸，如 1024x1024",
                        "default": "1024x1024"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "图片质量",
                        "default": "medium"
                    }
                },
                "required": ["prompt", "save_path"]
            }
        ),
        Tool(
            name="image_to_image",
            description="基于参考图片和文本描述生成新图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "变换描述文本"
                    },
                    "input_image": {
                        "type": "string",
                        "description": "输入图片的本地文件路径"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "保存的本地文件路径"
                    },
                    "size": {
                        "type": "string",
                        "description": "输出图片尺寸",
                        "default": "1024x1024"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "图片质量",
                        "default": "medium"
                    }
                },
                "required": ["prompt", "input_image", "save_path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """处理工具调用"""
    if image_client is None:
        return [TextContent(
            type="text",
            text='{"success": false, "error": "API 客户端未初始化，请检查配置"}'
        )]
    
    if name == "text_to_image":
        result = await image_client.text_to_image(
            prompt=arguments["prompt"],
            save_path=arguments["save_path"],
            size=arguments.get("size", "1024x1024"),
            quality=arguments.get("quality", "medium")
        )
    elif name == "image_to_image":
        result = await image_client.image_to_image(
            prompt=arguments["prompt"],
            input_image=arguments["input_image"],
            save_path=arguments["save_path"],
            size=arguments.get("size", "1024x1024"),
            quality=arguments.get("quality", "medium")
        )
    else:
        result = {"success": False, "error": f"未知工具: {name}"}
    
    import json
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False)
    )]

async def main():
    """主函数"""
    # 初始化客户端
    if not init_client():
        sys.exit(1)
    
    # 启动 stdio 服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: 验证语法正确**

Run: `python -c "import server; print('Import OK')"`
Expected: Import OK

- [ ] **Step 3: 提交 MCP 服务器**

```bash
git add server.py
git commit -m "feat: add MCP server with text_to_image and image_to_image tools"
```

---

### Task 5: 创建 README 文档

**Files:**
- Create: `README.md`

- [ ] **Step 1: 编写 README**

```markdown
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
```

- [ ] **Step 2: 提交 README**

```bash
git add README.md
git commit -m "docs: add README with usage instructions"
```

---

### Task 6: 初始化 Git 仓库并最终验证

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: 创建 .gitignore**

```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
dist/
build/
.env
```

- [ ] **Step 2: 初始化 Git 仓库**

```bash
git init
git add .
git commit -m "init: project setup"
```

- [ ] **Step 3: 运行所有测试**

Run: `pytest tests/ -v`
Expected: PASS - 所有测试通过

- [ ] **Step 4: 语法检查**

Run: `python -m py_compile config.py image_client.py server.py`
Expected: 无错误输出

---

## 验收检查清单

- [ ] 能够通过 `python server.py` 启动 MCP 服务
- [ ] 配置文件和环境变量都能正确加载
- [ ] 环境变量优先级高于配置文件
- [ ] `text_to_image` 工具能够生成图片
- [ ] `image_to_image` 工具能够基于参考图生成图片
- [ ] 保存图片时自动创建目录
- [ ] 错误情况返回清晰的错误信息
- [ ] 能够集成到 MCP 客户端使用
