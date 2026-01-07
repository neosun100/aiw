"""测试 CLI 模块"""
import pytest
from click.testing import CliRunner
from unittest.mock import patch

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_ls_empty(runner):
    """测试列出空工作空间"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.list_workspaces') as mock_list:
        mock_list.return_value = []
        
        result = runner.invoke(main, ['ls'])
        
        assert result.exit_code == 0
        assert "没有运行中的工作空间" in result.output

def test_cli_ls_with_workspaces(runner):
    """测试列出工作空间"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.list_workspaces') as mock_list:
        mock_list.return_value = [
            {"name": "test-ws", "tool": "gemini", "model": "flash", "dir": "/tmp", "desc": "测试", "active": True}
        ]
        
        result = runner.invoke(main, ['ls'])
        
        assert result.exit_code == 0
        assert "test-ws" in result.output

def test_cli_new(runner):
    """测试创建工作空间"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.create_workspace') as mock_create:
        mock_create.return_value = {"success": True, "name": "new-ws", "tool": "gemini", "model": "flash", "dir": "/tmp"}
        
        result = runner.invoke(main, ['new', 'new-ws', '-t', 'gemini', '-m', 'flash'])
        
        assert result.exit_code == 0
        assert "new-ws" in result.output

def test_cli_new_with_dir(runner):
    """测试创建工作空间并指定目录"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.create_workspace') as mock_create:
        mock_create.return_value = {"success": True, "name": "new-ws", "tool": "gemini", "model": "flash", "dir": "/home/user/project"}
        
        result = runner.invoke(main, ['new', 'new-ws', '-d', '/home/user/project'])
        
        assert result.exit_code == 0
        mock_create.assert_called_once()

def test_cli_new_already_exists(runner):
    """测试创建已存在的工作空间"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.create_workspace') as mock_create:
        mock_create.return_value = {"success": False, "error": "Workspace already exists"}
        
        result = runner.invoke(main, ['new', 'existing-ws'])
        
        assert result.exit_code == 0

def test_cli_log(runner):
    """测试查看日志"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.workspace_exists') as mock_exists:
        with patch('aiw.cli.tmux.get_log') as mock_log:
            mock_exists.return_value = True
            mock_log.return_value = "line1\nline2\nline3"
            
            result = runner.invoke(main, ['log', 'test-ws'])
            
            assert result.exit_code == 0
            assert "line1" in result.output

def test_cli_log_not_found(runner):
    """测试查看不存在工作空间的日志"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.workspace_exists') as mock_exists:
        mock_exists.return_value = False
        
        result = runner.invoke(main, ['log', 'nonexistent'])
        
        assert result.exit_code == 0
        assert "不存在" in result.output

def test_cli_send(runner):
    """测试发送命令"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.send_keys') as mock_send:
        mock_send.return_value = {"success": True}
        
        result = runner.invoke(main, ['send', 'test-ws', 'hello'])
        
        assert result.exit_code == 0
        assert "已发送" in result.output

def test_cli_send_to_all(runner):
    """测试发送命令到所有工作空间"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.send_to_all') as mock_send:
        mock_send.return_value = {"success": True, "count": 3}
        
        result = runner.invoke(main, ['send', 'all', 'hello'])
        
        assert result.exit_code == 0
        assert "3" in result.output

def test_cli_kill(runner):
    """测试关闭工作空间"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.kill_workspace') as mock_kill:
        mock_kill.return_value = {"success": True, "name": "test-ws"}
        
        result = runner.invoke(main, ['kill', 'test-ws'])
        
        assert result.exit_code == 0
        assert "已关闭" in result.output

def test_cli_kill_all(runner):
    """测试关闭所有工作空间"""
    from aiw.cli import main
    
    with patch('aiw.cli.tmux.kill_workspace') as mock_kill:
        mock_kill.return_value = {"success": True, "killed": 3}
        
        result = runner.invoke(main, ['kill', 'all'])
        
        assert result.exit_code == 0
        assert "3" in result.output

def test_cli_tool_list(runner):
    """测试列出工具"""
    from aiw.cli import main
    
    result = runner.invoke(main, ['tool', 'list'])
    
    assert result.exit_code == 0
    assert "gemini" in result.output

def test_cli_tool_default(runner):
    """测试设置默认工具"""
    from aiw.cli import main
    
    result = runner.invoke(main, ['tool', 'default', 'kiro'])
    
    assert result.exit_code == 0
    assert "kiro" in result.output

def test_cli_tool_default_not_found(runner):
    """测试设置不存在的默认工具"""
    from aiw.cli import main
    
    result = runner.invoke(main, ['tool', 'default', 'nonexistent'])
    
    assert result.exit_code == 0
    assert "不存在" in result.output

def test_cli_tool_add(runner):
    """测试添加工具"""
    from aiw.cli import main
    
    result = runner.invoke(main, ['tool', 'add', 'cursor', 'cursor', '-m', 'default'])
    
    assert result.exit_code == 0
    assert "已添加" in result.output
