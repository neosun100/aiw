"""共享测试 fixtures"""
import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, tmp_path):
    """为每个测试设置临时配置目录"""
    import aiw.config as config_module
    
    config_dir = tmp_path / "aiw_config"
    config_file = config_dir / "config.toml"
    sessions_file = config_dir / "sessions.json"
    
    monkeypatch.setattr(config_module, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_module, "SESSIONS_FILE", sessions_file)
    
    # 确保目录存在
    config_dir.mkdir(parents=True, exist_ok=True)
    
    yield
