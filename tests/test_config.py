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
    assert config.model == "gpt-image-2"  # 默认值

def test_load_config_from_file(tmp_path):
    """测试从配置文件加载"""
    config_data = {
        "api_url": "https://file.api.com/v1",
        "api_key": "file-key-456",
        "model": "gpt-image-1"
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    
    from config import load_config
    config = load_config(config_path=str(config_file))
    
    assert config.api_url == "https://file.api.com/v1"
    assert config.api_key == "file-key-456"
    assert config.model == "gpt-image-1"

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

def test_model_override(monkeypatch):
    """测试模型名称可通过环境变量覆盖"""
    monkeypatch.setenv("IMAGE_API_URL", "https://test.api.com/v1")
    monkeypatch.setenv("IMAGE_API_KEY", "test-key")
    monkeypatch.setenv("IMAGE_MODEL", "gpt-image-1")
    
    from config import load_config
    config = load_config()
    
    assert config.model == "gpt-image-1"
