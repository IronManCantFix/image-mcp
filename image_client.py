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
