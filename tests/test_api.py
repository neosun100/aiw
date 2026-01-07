"""测试 API 模块"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture
def client():
    """创建测试客户端"""
    from aiw.api import app
    return TestClient(app)

def test_api_list_workspaces_empty(client):
    """测试列出空工作空间"""
    with patch('aiw.api.tmux.list_workspaces') as mock_list:
        with patch('aiw.api.tmux.get_workspace_count') as mock_count:
            mock_list.return_value = []
            mock_count.return_value = 0
            
            response = client.get("/api/workspaces")
            
            assert response.status_code == 200
            data = response.json()
            assert data["workspaces"] == []
            assert data["count"] == 0

def test_api_list_workspaces(client):
    """测试列出工作空间"""
    with patch('aiw.api.tmux.list_workspaces') as mock_list:
        with patch('aiw.api.tmux.get_workspace_count') as mock_count:
            mock_list.return_value = [
                {"name": "test-ws", "tool": "gemini", "model": "flash", "dir": "/tmp", "desc": ""}
            ]
            mock_count.return_value = 1
            
            response = client.get("/api/workspaces")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["workspaces"]) == 1

def test_api_get_workspace(client):
    """测试获取单个工作空间"""
    with patch('aiw.api.tmux.get_workspace') as mock_get:
        mock_get.return_value = {"name": "test-ws", "tool": "gemini", "model": "flash", "dir": "/tmp", "desc": ""}
        
        response = client.get("/api/workspaces/test-ws")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-ws"

def test_api_get_workspace_not_found(client):
    """测试获取不存在的工作空间"""
    with patch('aiw.api.tmux.get_workspace') as mock_get:
        mock_get.return_value = None
        
        response = client.get("/api/workspaces/nonexistent")
        
        assert response.status_code == 404

def test_api_create_workspace(client):
    """测试创建工作空间"""
    with patch('aiw.api.tmux.create_workspace') as mock_create:
        mock_create.return_value = {"success": True, "name": "new-ws", "tool": "gemini", "model": "flash", "dir": "/tmp"}
        
        response = client.post("/api/workspaces", json={"name": "new-ws", "tool": "gemini", "model": "flash", "dir": "/tmp"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

def test_api_create_workspace_already_exists(client):
    """测试创建已存在的工作空间"""
    with patch('aiw.api.tmux.create_workspace') as mock_create:
        mock_create.return_value = {"success": False, "error": "Workspace already exists"}
        
        response = client.post("/api/workspaces", json={"name": "existing-ws"})
        
        assert response.status_code == 400

def test_api_delete_workspace(client):
    """测试删除工作空间"""
    with patch('aiw.api.tmux.kill_workspace') as mock_kill:
        mock_kill.return_value = {"success": True, "name": "test-ws"}
        
        response = client.delete("/api/workspaces/test-ws")
        
        assert response.status_code == 200

def test_api_delete_workspace_not_found(client):
    """测试删除不存在的工作空间"""
    with patch('aiw.api.tmux.kill_workspace') as mock_kill:
        mock_kill.return_value = {"success": False, "error": "Workspace not found"}
        
        response = client.delete("/api/workspaces/nonexistent")
        
        assert response.status_code == 404

def test_api_get_log(client):
    """测试获取日志"""
    with patch('aiw.api.tmux.workspace_exists') as mock_exists:
        with patch('aiw.api.tmux.get_log') as mock_log:
            mock_exists.return_value = True
            mock_log.return_value = "line1\nline2\nline3"
            
            response = client.get("/api/workspaces/test-ws/log")
            
            assert response.status_code == 200
            data = response.json()
            assert "line1" in data["log"]

def test_api_get_log_not_found(client):
    """测试获取不存在工作空间的日志"""
    with patch('aiw.api.tmux.workspace_exists') as mock_exists:
        mock_exists.return_value = False
        
        response = client.get("/api/workspaces/nonexistent/log")
        
        assert response.status_code == 404

def test_api_send_command(client):
    """测试发送命令"""
    with patch('aiw.api.tmux.send_keys') as mock_send:
        mock_send.return_value = {"success": True}
        
        response = client.post("/api/workspaces/test-ws/send", json={"text": "hello"})
        
        assert response.status_code == 200

def test_api_send_command_to_all(client):
    """测试发送命令到所有工作空间"""
    with patch('aiw.api.tmux.send_to_all') as mock_send:
        mock_send.return_value = {"success": True, "count": 3}
        
        response = client.post("/api/workspaces/all/send", json={"text": "hello"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3

def test_api_list_tools(client):
    """测试列出工具"""
    response = client.get("/api/tools")
    
    assert response.status_code == 200
    data = response.json()
    assert "default" in data
    assert "tools" in data

def test_api_status(client):
    """测试获取状态"""
    with patch('aiw.api.tmux.list_workspaces') as mock_list:
        with patch('aiw.api.tmux.get_log') as mock_log:
            mock_list.return_value = [{"name": "test-ws", "tool": "gemini", "model": "flash", "dir": "/tmp", "desc": ""}]
            mock_log.return_value = "test log"
            
            response = client.get("/api/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 1

def test_api_index_html(client):
    """测试首页 HTML"""
    response = client.get("/")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI WORKSPACE" in response.text
