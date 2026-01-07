"""测试配置模块"""
import pytest

def test_ensure_config():
    """测试配置目录创建"""
    from aiw.config import ensure_config, CONFIG_DIR, CONFIG_FILE, SESSIONS_FILE
    
    ensure_config()
    
    assert CONFIG_DIR.exists()
    assert CONFIG_FILE.exists()
    assert SESSIONS_FILE.exists()

def test_load_default_config():
    """测试加载默认配置"""
    from aiw.config import load_config, ensure_config
    
    ensure_config()
    config = load_config()
    
    assert "default_tool" in config
    assert "tools" in config
    assert "gemini" in config["tools"]
    assert "kiro" in config["tools"]
    assert "claude" in config["tools"]

def test_save_and_load_config():
    """测试保存和加载配置"""
    from aiw.config import save_config, load_config, ensure_config
    
    ensure_config()
    
    test_config = {
        "default_tool": "test_tool",
        "tools": {
            "test_tool": {
                "cmd": "test_cmd",
                "default_model": "test_model",
                "models": ["model1", "model2"]
            }
        }
    }
    
    save_config(test_config)
    loaded = load_config()
    
    assert loaded["default_tool"] == "test_tool"
    assert "test_tool" in loaded["tools"]

def test_sessions_save_load():
    """测试会话元数据保存和加载"""
    from aiw.config import save_sessions, load_sessions, ensure_config
    
    ensure_config()
    
    test_sessions = {
        "test-ws": {
            "tool": "gemini",
            "model": "flash",
            "dir": "/tmp/test",
            "desc": "测试工作空间"
        }
    }
    
    save_sessions(test_sessions)
    loaded = load_sessions()
    
    assert "test-ws" in loaded
    assert loaded["test-ws"]["tool"] == "gemini"

def test_get_tool_cmd():
    """测试获取工具命令"""
    from aiw.config import get_tool_cmd, ensure_config
    
    ensure_config()
    
    # 测试默认模型
    cmd = get_tool_cmd("gemini")
    assert "gemini" in cmd
    
    # 测试指定模型
    cmd = get_tool_cmd("kiro", "opus")
    assert "kiro" in cmd
    assert "opus" in cmd

def test_get_default_tool():
    """测试获取默认工具"""
    from aiw.config import get_default_tool, ensure_config
    
    ensure_config()
    
    default = get_default_tool()
    assert default == "gemini"

def test_get_all_tools():
    """测试获取所有工具"""
    from aiw.config import get_all_tools, ensure_config
    
    ensure_config()
    
    tools = get_all_tools()
    assert isinstance(tools, dict)
    assert len(tools) >= 3
