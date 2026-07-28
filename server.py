"""GPT-Image MCP Server"""
import asyncio
import sys
import json
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
            text=json.dumps({"success": False, "error": "API 客户端未初始化，请检查配置"}, ensure_ascii=False)
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
