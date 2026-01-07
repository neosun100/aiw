"""Tmux 操作封装"""
import subprocess
import os
from datetime import datetime
from pathlib import Path
from .config import load_config, load_sessions, save_sessions, get_tool_cmd, get_default_tool, get_tool_env, get_tool_source_env

PREFIX = "aiw-"

def _run(cmd: str) -> tuple[int, str, str]:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def list_workspaces() -> list[dict]:
    """列出所有工作空间"""
    code, out, _ = _run("tmux ls -F '#{session_name}|#{session_activity}' 2>/dev/null")
    sessions = load_sessions()
    result = []
    if code == 0 and out:
        for line in out.split("\n"):
            if line.startswith(PREFIX):
                parts = line.split("|")
                name = parts[0][len(PREFIX):]
                activity = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                meta = sessions.get(name, {})
                result.append({
                    "name": name,
                    "tool": meta.get("tool", "unknown"),
                    "model": meta.get("model", ""),
                    "desc": meta.get("desc", ""),
                    "dir": meta.get("dir", ""),
                    "created": meta.get("created", ""),
                    "active": True,
                    "activity": activity,
                })
    return result

def get_workspace(name: str) -> dict | None:
    """获取单个工作空间信息"""
    for ws in list_workspaces():
        if ws["name"] == name:
            return ws
    return None

def workspace_exists(name: str) -> bool:
    """检查工作空间是否存在"""
    code, _, _ = _run(f"tmux has-session -t {PREFIX}{name} 2>/dev/null")
    return code == 0

def create_workspace(name: str, tool: str = None, model: str = None, 
                     dir: str = None, desc: str = "") -> dict:
    """创建新工作空间"""
    if workspace_exists(name):
        return {"success": False, "error": "Workspace already exists"}
    
    config = load_config()
    tool = tool or get_default_tool()
    tool_config = config.get("tools", {}).get(tool, {})
    model = model or tool_config.get("default_model", "")
    
    # 工作目录：未指定则用当前目录
    work_dir = dir or os.getcwd()
    work_dir = os.path.expanduser(work_dir)
    work_dir = os.path.abspath(work_dir)
    
    session = f"{PREFIX}{name}"
    
    # 创建 tmux 会话
    _run(f"tmux new-session -d -s {session}")
    
    # cd 到工作目录
    _run(f"tmux send-keys -t {session} 'cd {work_dir}' Enter")
    
    # 如果需要 source 环境文件 (如 claude)
    source_env = get_tool_source_env(tool)
    if source_env:
        source_path = os.path.expanduser(source_env)
        if os.path.exists(source_path):
            _run(f"tmux send-keys -t {session} 'source {source_path}' Enter")
    
    # 设置环境变量 (如 claude)
    env_vars = get_tool_env(tool)
    for key, value in env_vars.items():
        _run(f"tmux send-keys -t {session} 'export {key}=\"{value}\"' Enter")
    
    # 启动 AI 工具
    cmd = get_tool_cmd(tool, model)
    _run(f"tmux send-keys -t {session} '{cmd}' Enter")
    
    # 保存元数据
    sessions = load_sessions()
    sessions[name] = {
        "tool": tool,
        "model": model,
        "desc": desc,
        "dir": work_dir,
        "created": datetime.now().isoformat(),
    }
    save_sessions(sessions)
    
    return {"success": True, "name": name, "tool": tool, "model": model, "dir": work_dir}

def attach_workspace(name: str) -> bool:
    """进入工作空间（交互式）"""
    if not workspace_exists(name):
        return False
    subprocess.run(f"tmux attach -t {PREFIX}{name}", shell=True)
    return True

def rename_workspace(old_name: str, new_name: str) -> dict:
    """重命名工作空间"""
    old_session = f"{SESSION_PREFIX}{old_name}"
    new_session = f"{SESSION_PREFIX}{new_name}"
    
    if not workspace_exists(old_name):
        return {"success": False, "error": f"Workspace '{old_name}' not found"}
    if workspace_exists(new_name):
        return {"success": False, "error": f"Workspace '{new_name}' already exists"}
    
    # 重命名 tmux session
    run_tmux(["rename-session", "-t", old_session, new_session])
    
    # 更新元数据文件
    old_meta = META_DIR / f"{old_name}.json"
    new_meta = META_DIR / f"{new_name}.json"
    if old_meta.exists():
        import json
        data = json.loads(old_meta.read_text())
        data["name"] = new_name
        new_meta.write_text(json.dumps(data))
        old_meta.unlink()
    
    return {"success": True, "old_name": old_name, "new_name": new_name}

def kill_workspace(name: str) -> dict:
    """关闭工作空间"""
    if name == "all":
        workspaces = list_workspaces()
        for ws in workspaces:
            _run(f"tmux kill-session -t {PREFIX}{ws['name']}")
        sessions = load_sessions()
        for ws in workspaces:
            sessions.pop(ws['name'], None)
        save_sessions(sessions)
        return {"success": True, "killed": len(workspaces)}
    
    if not workspace_exists(name):
        return {"success": False, "error": "Workspace not found"}
    
    _run(f"tmux kill-session -t {PREFIX}{name}")
    sessions = load_sessions()
    sessions.pop(name, None)
    save_sessions(sessions)
    return {"success": True, "name": name}

def get_log(name: str, lines: int = 50) -> str:
    """获取工作空间日志"""
    if not workspace_exists(name):
        return ""
    _, out, _ = _run(f"tmux capture-pane -t {PREFIX}{name} -p -S -{lines}")
    return out

def send_keys(name: str, text: str) -> dict:
    """发送按键到工作空间"""
    if not workspace_exists(name):
        return {"success": False, "error": "Workspace not found"}
    # 转义单引号
    text_escaped = text.replace("'", "'\\''")
    _run(f"tmux send-keys -t {PREFIX}{name} '{text_escaped}' Enter")
    return {"success": True}

def send_to_all(text: str) -> dict:
    """发送到所有工作空间"""
    workspaces = list_workspaces()
    for ws in workspaces:
        send_keys(ws['name'], text)
    return {"success": True, "count": len(workspaces)}

def get_workspace_count() -> int:
    """获取工作空间数量"""
    return len(list_workspaces())
