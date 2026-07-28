"""API 测试脚本"""
import asyncio
import httpx
import os

async def test_api():
    """测试 API 连接"""
    api_url = os.environ.get("IMAGE_API_URL", "")
    api_key = os.environ.get("IMAGE_API_KEY", "")
    model = os.environ.get("IMAGE_MODEL", "gpt-image-1")
    
    print("=" * 50)
    print("API 配置信息:")
    print(f"  URL: {api_url or '❌ 未设置'}")
    print(f"  Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '❌ 太短或未设置'}")
    print(f"  Model: {model}")
    print("=" * 50)
    
    if not api_url:
        print("\n❌ 错误: IMAGE_API_URL 未设置")
        return
    if not api_key:
        print("\n❌ 错误: IMAGE_API_KEY 未设置")
        return
    
    print("\n正在测试 API 连接...")
    
    payload = {
        "model": model,
        "prompt": "a red circle",
        "n": 1,
        "size": "1024x1024"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"\n响应内容 (前500字符):")
            print(response.text[:500])
            
            if response.status_code == 200:
                print("\n✅ API 测试成功!")
            else:
                print(f"\n❌ API 返回错误状态码: {response.status_code}")
                
    except httpx.ConnectError as e:
        print(f"\n❌ 连接失败: {e}")
        print("   请检查 API URL 是否正确")
    except httpx.TimeoutException:
        print("\n❌ 请求超时")
    except Exception as e:
        print(f"\n❌ 发生错误: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
