"""API 服务 + Web UI"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import asyncio

from . import tmux
from .config import load_config, get_all_tools, get_default_tool

app = FastAPI(title="AIW - AI Workspace Manager", version="0.1.0")

# === Models ===
class CreateWorkspace(BaseModel):
    name: str
    tool: Optional[str] = None
    model: Optional[str] = None
    dir: Optional[str] = None
    desc: str = ""

class SendCommand(BaseModel):
    text: str

# === API Routes ===
@app.get("/api/workspaces")
def api_list_workspaces():
    """列出所有工作空间"""
    return {"workspaces": tmux.list_workspaces(), "count": tmux.get_workspace_count()}

@app.get("/api/workspaces/{name}")
def api_get_workspace(name: str):
    """获取单个工作空间"""
    ws = tmux.get_workspace(name)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws

@app.post("/api/workspaces")
def api_create_workspace(data: CreateWorkspace):
    """创建工作空间"""
    result = tmux.create_workspace(data.name, data.tool, data.model, data.dir, data.desc)
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result

@app.delete("/api/workspaces/{name}")
def api_kill_workspace(name: str):
    """关闭工作空间"""
    result = tmux.kill_workspace(name)
    if not result["success"]:
        raise HTTPException(404, result["error"])
    return result

@app.get("/api/workspaces/{name}/log")
def api_get_log(name: str, lines: int = 50):
    """获取工作空间日志"""
    if not tmux.workspace_exists(name):
        raise HTTPException(404, "Workspace not found")
    return {"name": name, "log": tmux.get_log(name, lines)}

@app.post("/api/workspaces/{name}/send")
def api_send_command(name: str, data: SendCommand):
    """发送命令到工作空间"""
    if name == "all":
        return tmux.send_to_all(data.text)
    result = tmux.send_keys(name, data.text)
    if not result["success"]:
        raise HTTPException(404, result["error"])
    return result

@app.get("/api/tools")
def api_list_tools():
    """列出所有 AI 工具"""
    return {"default": get_default_tool(), "tools": get_all_tools()}

@app.get("/api/status")
def api_status():
    """获取整体状态（用于 UI 轮询）"""
    workspaces = tmux.list_workspaces()
    return {
        "workspaces": [{**ws, "log": tmux.get_log(ws["name"], 10)} for ws in workspaces],
        "count": len(workspaces),
        "tools": get_all_tools(),
        "default_tool": get_default_tool(),
    }

# === WebSocket ===
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """实时日志推送"""
    await websocket.accept()
    try:
        while True:
            workspaces = tmux.list_workspaces()
            data = {
                "workspaces": [{**ws, "log": tmux.get_log(ws["name"], 15)} for ws in workspaces],
                "count": len(workspaces),
            }
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

# === Web UI ===
@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIW · AI Workspace Manager</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0e27;
            color: #fff;
            min-height: 100vh;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: 
                radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        
        .container { 
            max-width: 1600px;
            margin: 0 auto; 
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            animation: slideDown 0.8s ease-out;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        .logo-icon {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
            animation: float 3s ease-in-out infinite;
        }
        
        .header h1 {
            font-size: 3.5em;
            font-weight: 800;
            letter-spacing: -2px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header .subtitle {
            font-size: 1.1em;
            color: rgba(255,255,255,0.6);
            margin-top: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        .live-time {
            font-size: 1.2em;
            color: #667eea;
            font-weight: 600;
            margin-top: 15px;
            padding: 12px 24px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            display: inline-block;
            border: 1px solid rgba(102, 126, 234, 0.3);
            font-family: monospace;
        }
        
        .controls-panel {
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 25px 35px;
            margin-bottom: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            animation: slideUp 0.8s ease-out;
        }
        
        .control-group {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            box-shadow: none;
        }
        
        .btn-secondary:hover {
            background: rgba(255,255,255,0.2);
            box-shadow: 0 4px 20px rgba(255,255,255,0.1);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
        }
        
        .stats-badges {
            display: flex;
            gap: 15px;
        }
        
        .stat-badge {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            box-shadow: 0 4px 20px rgba(245, 87, 108, 0.3);
        }
        
        .workspace-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .workspace-card {
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.4s;
            animation: fadeIn 0.6s ease-out backwards;
        }
        
        .workspace-card:hover {
            transform: translateY(-8px);
            border-color: rgba(102, 126, 234, 0.5);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        }
        
        .card-header {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .card-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .card-title h3 {
            font-size: 1.3em;
            font-weight: 700;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .card-meta {
            display: flex;
            gap: 10px;
        }
        
        .meta-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .meta-badge.model {
            background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        }
        
        .card-info {
            padding: 15px 20px;
            background: rgba(255,255,255,0.02);
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 0.9em;
            color: rgba(255,255,255,0.6);
        }
        
        .card-info code {
            background: rgba(255,255,255,0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
        }
        
        .card-log {
            padding: 15px 20px;
            height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            color: rgba(255,255,255,0.8);
            white-space: pre-wrap;
            word-break: break-all;
            background: rgba(0,0,0,0.2);
        }
        
        .card-actions {
            padding: 15px 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .action-btn {
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.2s;
            color: white;
        }
        
        .action-btn:hover {
            transform: translateY(-2px);
        }
        
        .btn-send { background: linear-gradient(135deg, #3b82f6, #60a5fa); }
        .btn-kill { background: linear-gradient(135deg, #ef4444, #f87171); }
        
        .empty-state {
            text-align: center;
            padding: 80px 20px;
            color: rgba(255,255,255,0.5);
        }
        
        .empty-state h2 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal.show { display: flex; }
        
        .modal-content {
            background: #16213e;
            padding: 30px;
            border-radius: 20px;
            min-width: 400px;
            max-width: 500px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .modal-content h3 {
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: rgba(255,255,255,0.7);
            font-weight: 500;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            background: rgba(255,255,255,0.05);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
            padding: 12px 15px;
            border-radius: 10px;
            font-size: 15px;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .modal-actions {
            display: flex;
            gap: 10px;
            margin-top: 25px;
        }
        
        .modal-actions .btn {
            flex: 1;
        }
        
        /* Send Modal */
        .send-input {
            display: flex;
            gap: 10px;
        }
        
        .send-input input {
            flex: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-section">
                <div class="logo-icon">🤖</div>
                <h1>AI WORKSPACE</h1>
            </div>
            <p class="subtitle">Multi-Agent Management Platform</p>
            <div class="live-time" id="liveTime">Loading...</div>
        </div>
        
        <div class="controls-panel">
            <div class="control-group">
                <button class="btn" onclick="showNewModal()">
                    <span>➕</span>
                    <span>New Workspace</span>
                </button>
                <button class="btn btn-secondary" onclick="refresh()">
                    <span>🔄</span>
                    <span>Refresh</span>
                </button>
            </div>
            <div class="stats-badges">
                <div class="stat-badge">Workspaces: <span id="wsCount">0</span></div>
            </div>
        </div>
        
        <div class="workspace-grid" id="workspaceGrid">
            <div class="empty-state">
                <h2>No Workspaces</h2>
                <p>Click "New Workspace" to create your first AI agent workspace</p>
            </div>
        </div>
    </div>
    
    <!-- New Workspace Modal -->
    <div id="newModal" class="modal">
        <div class="modal-content">
            <h3>🚀 New Workspace</h3>
            <div class="form-group">
                <label>Name *</label>
                <input id="newName" placeholder="e.g. api-dev, frontend" />
            </div>
            <div class="form-group">
                <label>AI Tool</label>
                <select id="newTool"></select>
            </div>
            <div class="form-group">
                <label>Model</label>
                <select id="newModel"></select>
            </div>
            <div class="form-group">
                <label>Working Directory</label>
                <input id="newDir" placeholder="Leave empty for current directory" />
            </div>
            <div class="form-group">
                <label>Description</label>
                <input id="newDesc" placeholder="Optional description" />
            </div>
            <div class="modal-actions">
                <button class="btn" onclick="createWorkspace()">Create</button>
                <button class="btn btn-secondary" onclick="hideModal('newModal')">Cancel</button>
            </div>
        </div>
    </div>
    
    <!-- Send Command Modal -->
    <div id="sendModal" class="modal">
        <div class="modal-content">
            <h3>📤 Send Command</h3>
            <p style="color: rgba(255,255,255,0.6); margin-bottom: 15px;">
                Sending to: <strong id="sendTarget"></strong>
            </p>
            <div class="form-group">
                <label>Command</label>
                <input id="sendText" placeholder="Enter command to send..." />
            </div>
            <div class="modal-actions">
                <button class="btn" onclick="sendCommand()">Send</button>
                <button class="btn btn-secondary" onclick="hideModal('sendModal')">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        let tools = {};
        let defaultTool = 'gemini';
        let ws;
        let currentSendTarget = '';
        
        function updateTime() {
            const now = new Date();
            document.getElementById('liveTime').textContent = now.toLocaleString('zh-CN');
        }
        
        async function init() {
            updateTime();
            setInterval(updateTime, 1000);
            
            // Load tools
            const res = await fetch('/api/tools');
            const data = await res.json();
            tools = data.tools;
            defaultTool = data.default;
            
            const toolSelect = document.getElementById('newTool');
            toolSelect.innerHTML = Object.keys(tools).map(t => 
                `<option value="${t}" ${t === defaultTool ? 'selected' : ''}>${t}</option>`
            ).join('');
            toolSelect.onchange = updateModels;
            updateModels();
            
            connectWS();
        }
        
        function updateModels() {
            const tool = document.getElementById('newTool').value;
            const models = tools[tool]?.models || [];
            const defaultModel = tools[tool]?.default_model || '';
            document.getElementById('newModel').innerHTML = models.map(m => 
                `<option value="${m}" ${m === defaultModel ? 'selected' : ''}>${m}</option>`
            ).join('');
        }
        
        function connectWS() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${location.host}/ws`);
            ws.onmessage = (e) => render(JSON.parse(e.data));
            ws.onclose = () => setTimeout(connectWS, 3000);
        }
        
        function render(data) {
            document.getElementById('wsCount').textContent = data.count;
            
            const grid = document.getElementById('workspaceGrid');
            
            if (data.workspaces.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <h2>No Workspaces</h2>
                        <p>Click "New Workspace" to create your first AI agent workspace</p>
                    </div>
                `;
                return;
            }
            
            grid.innerHTML = data.workspaces.map((ws, i) => `
                <div class="workspace-card" style="animation-delay: ${i * 0.1}s">
                    <div class="card-header">
                        <div class="card-title">
                            <div class="status-dot"></div>
                            <h3>${escapeHtml(ws.name)}</h3>
                        </div>
                        <div class="card-meta">
                            <span class="meta-badge">${ws.tool}</span>
                            <span class="meta-badge model">${ws.model}</span>
                        </div>
                    </div>
                    <div class="card-info">
                        📁 <code>${escapeHtml(ws.dir || 'N/A')}</code>
                        ${ws.desc ? `<br>📝 ${escapeHtml(ws.desc)}` : ''}
                    </div>
                    <div class="card-log">${escapeHtml(ws.log || 'No output yet...')}</div>
                    <div class="card-actions">
                        <button class="action-btn btn-send" onclick="showSendModal('${ws.name}')">📤 Send</button>
                        <button class="action-btn btn-kill" onclick="killWorkspace('${ws.name}')">⏹ Kill</button>
                    </div>
                </div>
            `).join('');
        }
        
        function escapeHtml(s) {
            if (!s) return '';
            return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        }
        
        function showModal(id) { document.getElementById(id).classList.add('show'); }
        function hideModal(id) { document.getElementById(id).classList.remove('show'); }
        function showNewModal() { showModal('newModal'); document.getElementById('newName').focus(); }
        
        function showSendModal(name) {
            currentSendTarget = name;
            document.getElementById('sendTarget').textContent = name;
            document.getElementById('sendText').value = '';
            showModal('sendModal');
            document.getElementById('sendText').focus();
        }
        
        async function createWorkspace() {
            const name = document.getElementById('newName').value.trim();
            if (!name) { alert('Name is required'); return; }
            
            const body = {
                name,
                tool: document.getElementById('newTool').value,
                model: document.getElementById('newModel').value,
                dir: document.getElementById('newDir').value || null,
                desc: document.getElementById('newDesc').value
            };
            
            try {
                const res = await fetch('/api/workspaces', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Failed');
                hideModal('newModal');
                document.getElementById('newName').value = '';
                document.getElementById('newDir').value = '';
                document.getElementById('newDesc').value = '';
            } catch (e) {
                alert('Error: ' + e.message);
            }
        }
        
        async function sendCommand() {
            const text = document.getElementById('sendText').value.trim();
            if (!text) return;
            
            try {
                await fetch(`/api/workspaces/${currentSendTarget}/send`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text})
                });
                hideModal('sendModal');
            } catch (e) {
                alert('Error: ' + e.message);
            }
        }
        
        async function killWorkspace(name) {
            if (!confirm(`Kill workspace "${name}"?`)) return;
            try {
                await fetch(`/api/workspaces/${name}`, {method: 'DELETE'});
            } catch (e) {
                alert('Error: ' + e.message);
            }
        }
        
        function refresh() { location.reload(); }
        
        // Enter key handlers
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                if (document.getElementById('newModal').classList.contains('show')) {
                    createWorkspace();
                } else if (document.getElementById('sendModal').classList.contains('show')) {
                    sendCommand();
                }
            }
            if (e.key === 'Escape') {
                hideModal('newModal');
                hideModal('sendModal');
            }
        });
        
        init();
    </script>
</body>
</html>
'''

def run_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    print(f"🚀 AIW Server running at http://{host}:{port}")
    print(f"   Web UI: http://localhost:{port}")
    print(f"   API Docs: http://localhost:{port}/docs")
    uvicorn.run(app, host=host, port=port, log_level="warning")
