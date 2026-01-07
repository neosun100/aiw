"""API 服务 + Web UI"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import subprocess
import pty
import os
import select
import struct
import fcntl
import termios

from . import tmux
from .config import load_config, get_all_tools, get_default_tool
from .templates import HTML_TEMPLATE

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
    return {"workspaces": tmux.list_workspaces(), "count": tmux.get_workspace_count()}

@app.get("/api/workspaces/{name}")
def api_get_workspace(name: str):
    ws = tmux.get_workspace(name)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws

@app.post("/api/workspaces")
def api_create_workspace(data: CreateWorkspace):
    result = tmux.create_workspace(data.name, data.tool, data.model, data.dir, data.desc)
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result

@app.post("/api/workspaces/{name}/rename")
def api_rename_workspace(name: str, new_name: str):
    """重命名工作空间"""
    result = tmux.rename_workspace(name, new_name)
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result

@app.delete("/api/workspaces/{name}")
def api_kill_workspace(name: str):
    result = tmux.kill_workspace(name)
    if not result["success"]:
        raise HTTPException(404, result["error"])
    return result

@app.get("/api/workspaces/{name}/log")
def api_get_log(name: str, lines: int = 50):
    if not tmux.workspace_exists(name):
        raise HTTPException(404, "Workspace not found")
    return {"name": name, "log": tmux.get_log(name, lines)}

@app.post("/api/workspaces/{name}/send")
def api_send_command(name: str, data: SendCommand):
    if name == "all":
        return tmux.send_to_all(data.text)
    result = tmux.send_keys(name, data.text)
    if not result["success"]:
        raise HTTPException(404, result["error"])
    return result

@app.get("/api/tools")
def api_list_tools():
    return {"default": get_default_tool(), "tools": get_all_tools()}

@app.get("/api/status")
def api_status():
    workspaces = tmux.list_workspaces()
    return {
        "workspaces": [{**ws, "log": tmux.get_log(ws["name"], 10)} for ws in workspaces],
        "count": len(workspaces),
        "tools": get_all_tools(),
        "default_tool": get_default_tool(),
    }

# === WebSocket: Status Updates ===
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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

# === WebSocket: Interactive Terminal ===
@app.websocket("/ws/terminal/{name}")
async def terminal_websocket(websocket: WebSocket, name: str):
    """交互式终端 - 直接 attach 到 tmux session"""
    await websocket.accept()
    
    session_name = f"aiw-{name}"
    if not tmux.workspace_exists(name):
        await websocket.close(code=4004, reason="Workspace not found")
        return
    
    # 等待客户端发送初始大小
    cols, rows = 120, 30
    try:
        msg = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
        import json
        parsed = json.loads(msg)
        if parsed.get("type") == "resize":
            cols, rows = parsed.get("cols", 120), parsed.get("rows", 30)
    except:
        pass
    
    master_fd, slave_fd = pty.openpty()
    
    # 设置初始终端大小
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
    
    # 设置 TERM 环境变量
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    
    proc = subprocess.Popen(
        ["tmux", "attach-session", "-d", "-t", session_name],  # -d 强制 detach 其他客户端
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        preexec_fn=os.setsid, env=env
    )
    os.close(slave_fd)
    
    fl = fcntl.fcntl(master_fd, fcntl.F_GETFL)
    fcntl.fcntl(master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    async def read_output():
        try:
            while proc.poll() is None:
                await asyncio.sleep(0.01)
                try:
                    if select.select([master_fd], [], [], 0)[0]:
                        data = os.read(master_fd, 4096)
                        if data:
                            await websocket.send_bytes(data)
                except (OSError, IOError):
                    break
        except Exception:
            pass
    
    read_task = asyncio.create_task(read_output())
    
    try:
        while True:
            msg = await websocket.receive()
            if msg["type"] == "websocket.disconnect":
                break
            
            if "bytes" in msg:
                data = msg["bytes"]
            elif "text" in msg:
                import json
                try:
                    parsed = json.loads(msg["text"])
                    if parsed.get("type") == "resize":
                        cols, rows = parsed.get("cols", 80), parsed.get("rows", 24)
                        winsize = struct.pack("HHHH", rows, cols, 0, 0)
                        fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
                        continue
                    data = parsed.get("data", "").encode()
                except json.JSONDecodeError:
                    data = msg["text"].encode()
            else:
                continue
            
            if data:
                os.write(master_fd, data)
                
    except WebSocketDisconnect:
        pass
    finally:
        read_task.cancel()
        proc.terminate()
        os.close(master_fd)

# === Web UI ===
@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE

def run_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    print(f"🚀 AIW Server running at http://{host}:{port}")
    print(f"   Web UI: http://localhost:{port}")
    print(f"   API Docs: http://localhost:{port}/docs")
    uvicorn.run(app, host=host, port=port, log_level="warning")
