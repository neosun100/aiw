"""测试 MCP Server 模块"""
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_mcp_list_tools():
    """测试 MCP 列出工具"""
    from aiw.mcp_server import list_tools
    
    tools = await list_tools()
    
    assert len(tools) >= 7
    tool_names = [t.name for t in tools]
    assert "aiw_list" in tool_names
    assert "aiw_create" in tool_names

@pytest.mark.asyncio
async def test_mcp_aiw_list_empty():
    """测试 MCP aiw_list 空结果"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.list_workspaces') as mock_list:
        mock_list.return_value = []
        
        result = await call_tool("aiw_list", {})
        
        assert len(result) == 1
        assert "没有运行中的工作空间" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_list_with_workspaces():
    """测试 MCP aiw_list 有结果"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.list_workspaces') as mock_list:
        mock_list.return_value = [
            {"name": "test-ws", "tool": "gemini", "model": "flash", "dir": "/tmp", "desc": "测试"}
        ]
        
        result = await call_tool("aiw_list", {})
        
        assert len(result) == 1
        assert "test-ws" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_create():
    """测试 MCP aiw_create"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.create_workspace') as mock_create:
        mock_create.return_value = {"success": True, "name": "new-ws", "tool": "gemini", "model": "flash", "dir": "/tmp"}
        
        result = await call_tool("aiw_create", {"name": "new-ws", "tool": "gemini", "model": "flash", "dir": "/tmp"})
        
        assert len(result) == 1
        assert "已创建" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_create_failed():
    """测试 MCP aiw_create 失败"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.create_workspace') as mock_create:
        mock_create.return_value = {"success": False, "error": "Workspace already exists"}
        
        result = await call_tool("aiw_create", {"name": "existing-ws"})
        
        assert len(result) == 1
        assert "失败" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_log():
    """测试 MCP aiw_log"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.workspace_exists') as mock_exists:
        with patch('aiw.mcp_server.tmux.get_log') as mock_log:
            mock_exists.return_value = True
            mock_log.return_value = "line1\nline2\nline3"
            
            result = await call_tool("aiw_log", {"name": "test-ws", "lines": 10})
            
            assert len(result) == 1
            assert "line1" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_log_not_found():
    """测试 MCP aiw_log 不存在"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.workspace_exists') as mock_exists:
        mock_exists.return_value = False
        
        result = await call_tool("aiw_log", {"name": "nonexistent"})
        
        assert len(result) == 1
        assert "不存在" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_send():
    """测试 MCP aiw_send"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.send_keys') as mock_send:
        mock_send.return_value = {"success": True}
        
        result = await call_tool("aiw_send", {"name": "test-ws", "text": "hello"})
        
        assert len(result) == 1
        assert "已发送" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_send_to_all():
    """测试 MCP aiw_send 到所有"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.send_to_all') as mock_send:
        mock_send.return_value = {"success": True, "count": 3}
        
        result = await call_tool("aiw_send", {"name": "all", "text": "hello"})
        
        assert len(result) == 1
        assert "3" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_kill():
    """测试 MCP aiw_kill"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.kill_workspace') as mock_kill:
        mock_kill.return_value = {"success": True, "name": "test-ws"}
        
        result = await call_tool("aiw_kill", {"name": "test-ws"})
        
        assert len(result) == 1
        assert "已关闭" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_kill_all():
    """测试 MCP aiw_kill 所有"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.kill_workspace') as mock_kill:
        mock_kill.return_value = {"success": True, "killed": 3}
        
        result = await call_tool("aiw_kill", {"name": "all"})
        
        assert len(result) == 1
        assert "3" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_status():
    """测试 MCP aiw_status"""
    from aiw.mcp_server import call_tool
    
    with patch('aiw.mcp_server.tmux.list_workspaces') as mock_list:
        with patch('aiw.mcp_server.tmux.get_log') as mock_log:
            mock_list.return_value = [{"name": "test-ws", "tool": "gemini", "model": "flash", "dir": "/tmp", "desc": ""}]
            mock_log.return_value = "test output"
            
            result = await call_tool("aiw_status", {})
            
            assert len(result) == 1
            assert "test-ws" in result[0].text

@pytest.mark.asyncio
async def test_mcp_aiw_tools():
    """测试 MCP aiw_tools"""
    from aiw.mcp_server import call_tool
    
    result = await call_tool("aiw_tools", {})
    
    assert len(result) == 1
    assert "gemini" in result[0].text

@pytest.mark.asyncio
async def test_mcp_unknown_tool():
    """测试 MCP 未知工具"""
    from aiw.mcp_server import call_tool
    
    result = await call_tool("unknown_tool", {})
    
    assert len(result) == 1
    assert "未知" in result[0].text
