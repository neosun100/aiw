"""测试 Tmux 模块"""
import pytest
from unittest.mock import patch

def test_list_workspaces_empty():
    """测试列出空工作空间"""
    from aiw.tmux import list_workspaces
    
    with patch('aiw.tmux._run') as mock_run:
        mock_run.return_value = (1, "", "no server running")
        
        result = list_workspaces()
        assert result == []

def test_list_workspaces_with_sessions():
    """测试列出有工作空间的情况"""
    from aiw.tmux import list_workspaces
    from aiw.config import save_sessions, ensure_config
    
    ensure_config()
    save_sessions({
        "test-ws": {
            "tool": "gemini",
            "model": "flash",
            "dir": "/tmp/test",
            "desc": "测试"
        }
    })
    
    with patch('aiw.tmux._run') as mock_run:
        mock_run.return_value = (0, "aiw-test-ws|1234567890", "")
        
        result = list_workspaces()
        assert len(result) == 1
        assert result[0]["name"] == "test-ws"
        assert result[0]["tool"] == "gemini"

def test_workspace_exists():
    """测试检查工作空间是否存在"""
    from aiw.tmux import workspace_exists
    
    with patch('aiw.tmux._run') as mock_run:
        mock_run.return_value = (0, "", "")
        assert workspace_exists("test") == True
        
        mock_run.return_value = (1, "", "session not found")
        assert workspace_exists("nonexistent") == False

def test_create_workspace():
    """测试创建工作空间"""
    from aiw.tmux import create_workspace
    from aiw.config import ensure_config
    
    ensure_config()
    
    with patch('aiw.tmux._run') as mock_run:
        with patch('aiw.tmux.workspace_exists') as mock_exists:
            mock_exists.return_value = False
            mock_run.return_value = (0, "", "")
            
            result = create_workspace("test-ws", "gemini", "flash", "/tmp/test", "测试")
            
            assert result["success"] == True
            assert result["name"] == "test-ws"
            assert result["tool"] == "gemini"

def test_create_workspace_already_exists():
    """测试创建已存在的工作空间"""
    from aiw.tmux import create_workspace
    
    with patch('aiw.tmux.workspace_exists') as mock_exists:
        mock_exists.return_value = True
        
        result = create_workspace("existing-ws")
        
        assert result["success"] == False
        assert "already exists" in result["error"]

def test_create_workspace_default_dir():
    """测试创建工作空间时使用默认目录"""
    from aiw.tmux import create_workspace
    from aiw.config import ensure_config
    import os
    
    ensure_config()
    
    with patch('aiw.tmux._run') as mock_run:
        with patch('aiw.tmux.workspace_exists') as mock_exists:
            mock_exists.return_value = False
            mock_run.return_value = (0, "", "")
            
            result = create_workspace("test-ws")
            
            assert result["success"] == True
            assert result["dir"] == os.getcwd()

def test_kill_workspace():
    """测试关闭工作空间"""
    from aiw.tmux import kill_workspace
    from aiw.config import ensure_config
    
    ensure_config()
    
    with patch('aiw.tmux._run') as mock_run:
        with patch('aiw.tmux.workspace_exists') as mock_exists:
            mock_exists.return_value = True
            mock_run.return_value = (0, "", "")
            
            result = kill_workspace("test-ws")
            
            assert result["success"] == True

def test_kill_workspace_not_found():
    """测试关闭不存在的工作空间"""
    from aiw.tmux import kill_workspace
    
    with patch('aiw.tmux.workspace_exists') as mock_exists:
        mock_exists.return_value = False
        
        result = kill_workspace("nonexistent")
        
        assert result["success"] == False

def test_kill_all_workspaces():
    """测试关闭所有工作空间"""
    from aiw.tmux import kill_workspace
    from aiw.config import ensure_config
    
    ensure_config()
    
    with patch('aiw.tmux.list_workspaces') as mock_list:
        with patch('aiw.tmux._run') as mock_run:
            mock_list.return_value = [{"name": "ws1"}, {"name": "ws2"}]
            mock_run.return_value = (0, "", "")
            
            result = kill_workspace("all")
            
            assert result["success"] == True
            assert result["killed"] == 2

def test_get_log():
    """测试获取日志"""
    from aiw.tmux import get_log
    
    with patch('aiw.tmux.workspace_exists') as mock_exists:
        with patch('aiw.tmux._run') as mock_run:
            mock_exists.return_value = True
            mock_run.return_value = (0, "line1\nline2\nline3", "")
            
            result = get_log("test-ws", 10)
            
            assert "line1" in result

def test_get_log_not_found():
    """测试获取不存在工作空间的日志"""
    from aiw.tmux import get_log
    
    with patch('aiw.tmux.workspace_exists') as mock_exists:
        mock_exists.return_value = False
        
        result = get_log("nonexistent")
        
        assert result == ""

def test_send_keys():
    """测试发送按键"""
    from aiw.tmux import send_keys
    
    with patch('aiw.tmux.workspace_exists') as mock_exists:
        with patch('aiw.tmux._run') as mock_run:
            mock_exists.return_value = True
            mock_run.return_value = (0, "", "")
            
            result = send_keys("test-ws", "hello")
            
            assert result["success"] == True

def test_send_keys_not_found():
    """测试发送到不存在的工作空间"""
    from aiw.tmux import send_keys
    
    with patch('aiw.tmux.workspace_exists') as mock_exists:
        mock_exists.return_value = False
        
        result = send_keys("nonexistent", "hello")
        
        assert result["success"] == False

def test_send_to_all():
    """测试发送到所有工作空间"""
    from aiw.tmux import send_to_all
    
    with patch('aiw.tmux.list_workspaces') as mock_list:
        with patch('aiw.tmux.send_keys') as mock_send:
            mock_list.return_value = [{"name": "ws1"}, {"name": "ws2"}]
            mock_send.return_value = {"success": True}
            
            result = send_to_all("hello")
            
            assert result["success"] == True
            assert result["count"] == 2

def test_get_workspace_count():
    """测试获取工作空间数量"""
    from aiw.tmux import get_workspace_count
    
    with patch('aiw.tmux.list_workspaces') as mock_list:
        mock_list.return_value = [{"name": "ws1"}, {"name": "ws2"}]
        
        count = get_workspace_count()
        
        assert count == 2
