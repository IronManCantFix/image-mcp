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
        
        save_path = "/tmp/test_output.png"
        result = await client.text_to_image(
            prompt="a cute cat",
            save_path=save_path
        )
        
        assert result["success"] is True
        assert result["file_path"] == str(Path(save_path).resolve())

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
