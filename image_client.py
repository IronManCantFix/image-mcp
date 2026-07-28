"""GPT-Image API 客户端"""
import base64
import httpx
import sys
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
        """文生图"""
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
        """图生图"""
        input_path = Path(input_image)
        if not input_path.exists():
            return {"success": False, "error": f"输入图片不存在: {input_image}"}
        
        try:
            with open(input_path, "rb") as f:
                image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode()
        except Exception as e:
            return {"success": False, "error": f"读取输入图片失败: {e}"}
        
        suffix = input_path.suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
        mime_type = mime_map.get(suffix, "image/png")
        image_url = f"data:{mime_type};base64,{image_b64}"
        
        return await self._generate(prompt=prompt, save_path=save_path, size=size, quality=quality, image=image_url)
    
    async def _generate(
        self,
        prompt: str,
        save_path: str,
        size: str = "1024x1024",
        quality: str = "medium",
        image: Optional[str] = None
    ) -> dict:
        """调用 API 生成图片"""
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "n": 1,
            "size": size
        }
        
        if image:
            payload["image"] = image
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        print(f"[INFO] 正在调用 API 生成图片...", file=sys.stderr)
        print(f"[INFO] 模型: {self.config.model}", file=sys.stderr)
        print(f"[INFO] 尺寸: {size}", file=sys.stderr)
        print(f"[INFO] Prompt: {prompt[:50]}...", file=sys.stderr)
        
        try:
            # 图片生成可能需要很长时间，设置较长的超时
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5分钟超时
                print(f"[INFO] 发送请求到: {self.config.api_url}", file=sys.stderr)
                
                response = await client.post(
                    self.config.api_url,
                    json=payload,
                    headers=headers
                )
                
                print(f"[INFO] 收到响应，状态码: {response.status_code}", file=sys.stderr)
                
                response.raise_for_status()
                
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    image_data = data["data"][0]
                    
                    if "b64_json" in image_data:
                        img_bytes = base64.b64decode(image_data["b64_json"])
                    elif "url" in image_data:
                        print(f"[INFO] 下载图片: {image_data['url'][:100]}...", file=sys.stderr)
                        img_response = await client.get(image_data["url"])
                        img_bytes = img_response.content
                    else:
                        return {"success": False, "error": "API 响应中没有图片数据"}
                    
                    save_dir = Path(save_path).parent
                    save_dir.mkdir(parents=True, exist_ok=True)
                    
                    with open(save_path, "wb") as f:
                        f.write(img_bytes)
                    
                    print(f"[INFO] 图片已保存到: {save_path}", file=sys.stderr)
                    
                    return {
                        "success": True,
                        "file_path": str(Path(save_path).resolve()),
                        "message": "图片已保存"
                    }
                else:
                    return {"success": False, "error": f"API 响应格式异常: {response.text[:200]}"}
        
        except httpx.TimeoutException as e:
            print(f"[ERROR] 请求超时: {e}", file=sys.stderr)
            return {"success": False, "error": "请求超时（超过5分钟），图片生成需要较长时间，请稍后重试或使用更小的尺寸"}
        except httpx.HTTPStatusError as e:
            print(f"[ERROR] HTTP错误: {e.response.status_code} - {e.response.text[:200]}", file=sys.stderr)
            return {
                "success": False,
                "error": f"API 请求失败 (HTTP {e.response.status_code})",
                "details": e.response.text[:500]
            }
        except httpx.RequestError as e:
            print(f"[ERROR] 请求错误: {e}", file=sys.stderr)
            return {"success": False, "error": f"网络请求失败: {e}"}
        except Exception as e:
            print(f"[ERROR] 未知错误: {type(e).__name__}: {e}", file=sys.stderr)
            return {"success": False, "error": f"生成图片失败: {type(e).__name__}: {e}"}
