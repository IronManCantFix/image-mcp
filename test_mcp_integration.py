"""MCP 集成测试"""
import asyncio
import os
import sys

# 设置环境变量
os.environ["IMAGE_API_URL"] = "https://apihub.agnes-ai.com/v1/images/generations"
os.environ["IMAGE_API_KEY"] = "sk-9bGIhBk7Zoocq1AgF5y9TLHMux5h2zgs14wVrtINr4nvnQPg"
os.environ["IMAGE_MODEL"] = "agnes-image-2.0-flash"

from image_client import ImageClient
from config import load_config

async def test_text_to_image():
    """测试文生图功能"""
    print("=" * 60)
    print("测试 MCP ImageClient - 文生图功能")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    print(f"✓ 配置加载成功")
    print(f"  - API URL: {config.api_url}")
    print(f"  - Model: {config.model}")
    
    # 创建客户端
    client = ImageClient(config)
    print(f"✓ 客户端创建成功")
    
    # 测试生成图片
    save_path = "/tmp/mcp_test_output.png"
    print(f"\n开始生成图片...")
    print(f"  - Prompt: 'a cute orange cat sitting on a windowsill'")
    print(f"  - 保存路径: {save_path}")
    print(f"  - 尺寸: 1024x1024")
    
    result = await client.text_to_image(
        prompt="a cute orange cat sitting on a windowsill, digital art style",
        save_path=save_path,
        size="1024x1024",
        quality="medium"
    )
    
    print(f"\n结果: {result}")
    
    if result.get("success"):
        print(f"\n✅ 测试成功！")
        print(f"   图片已保存到: {result.get('file_path')}")
        
        # 验证文件
        if os.path.exists(save_path):
            size = os.path.getsize(save_path)
            print(f"   文件大小: {size / 1024:.1f} KB")
        else:
            print(f"   ❌ 文件不存在!")
    else:
        print(f"\n❌ 测试失败: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_text_to_image())
    sys.exit(0 if result.get("success") else 1)
