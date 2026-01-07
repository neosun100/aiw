"""配置管理"""
import json
from pathlib import Path
import toml

CONFIG_DIR = Path.home() / ".config" / "aiw"
CONFIG_FILE = CONFIG_DIR / "config.toml"
SESSIONS_FILE = CONFIG_DIR / "sessions.json"

# 默认配置 - 通用示例配置
# 用户可以在 ~/.config/aiw/config.toml 中自定义
DEFAULT_CONFIG = {
    "default_tool": "gemini",
    "server": {"host": "0.0.0.0", "port": 8000},
    "tools": {
        # Gemini CLI
        "gemini": {
            "cmd": "gemini",
            "default_model": "gemini-2.0-flash",
            "models": ["gemini-2.0-flash", "gemini-2.5-pro"],
            "model_flag": "--model",
        },
        # Kiro CLI
        "kiro": {
            "cmd": "kiro-cli chat",
            "default_model": "sonnet",
            "models": ["sonnet", "opus"],
            "model_flag": "--model",
        },
        # Claude CLI
        "claude": {
            "cmd": "claude",
            "default_model": "sonnet",
            "models": ["sonnet", "opus"],
            "model_flag": "--model",
        },
    }
}

def ensure_config():
    """确保配置目录和文件存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            toml.dump(DEFAULT_CONFIG, f)
    if not SESSIONS_FILE.exists():
        SESSIONS_FILE.write_text("{}")

def load_config() -> dict:
    ensure_config()
    try:
        return toml.load(CONFIG_FILE)
    except:
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        toml.dump(config, f)

def load_sessions() -> dict:
    ensure_config()
    try:
        return json.loads(SESSIONS_FILE.read_text() or "{}")
    except:
        return {}

def save_sessions(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def get_tool_cmd(tool: str, model: str = None) -> str:
    """获取工具的完整启动命令"""
    config = load_config()
    tool_config = config.get("tools", {}).get(tool, {})
    
    cmd = tool_config.get("cmd", tool)
    model = model or tool_config.get("default_model")
    model_flag = tool_config.get("model_flag", "--model")
    
    # 添加模型参数
    if model and model_flag:
        cmd = f"{cmd} {model_flag} {model}"
    
    return cmd

def get_tool_env(tool: str) -> dict:
    """获取工具需要的环境变量"""
    config = load_config()
    tool_config = config.get("tools", {}).get(tool, {})
    return tool_config.get("env", {})

def get_tool_source_env(tool: str) -> str:
    """获取工具需要 source 的环境文件"""
    config = load_config()
    tool_config = config.get("tools", {}).get(tool, {})
    return tool_config.get("source_env", "")

def get_default_tool() -> str:
    return load_config().get("default_tool", "gemini")

def get_all_tools() -> dict:
    return load_config().get("tools", {})
