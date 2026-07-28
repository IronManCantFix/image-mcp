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
