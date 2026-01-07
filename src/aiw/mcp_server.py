"""MCP Server - 让 AI 工具可以调用 AIW 功能"""
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import tmux
from .config import get_all_tools, get_default_tool

server = Server("aiw")

@server.list_tools()
async def list_tools():
    """列出所有可用的 MCP 工具"""
    return [
        Tool(
            name="aiw_list",
            description="列出所有 AI 工作空间",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="aiw_create",
            description="创建新的 AI 工作空间",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "工作空间名称"},
                    "tool": {"type": "string", "description": "AI 工具 (gemini/kiro/claude)"},
                    "model": {"type": "string", "description": "模型名称"},
                    "dir": {"type": "string", "description": "工作目录"},
                    "desc": {"type": "string", "description": "描述"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="aiw_log",
            description="获取工作空间的日志输出",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "工作空间名称"},
                    "lines": {"type": "integer", "description": "行数", "default": 30}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="aiw_send",
            description="发送命令到工作空间",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "工作空间名称，或 'all' 发送到所有"},
                    "text": {"type": "string", "description": "要发送的命令"}
                },
                "required": ["name", "text"]
            }
        ),
        Tool(
            name="aiw_kill",
            description="关闭工作空间",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "工作空间名称，或 'all' 关闭所有"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="aiw_status",
            description="获取所有工作空间的状态概览",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="aiw_tools",
            description="列出可用的 AI 工具配置",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """执行 MCP 工具调用"""
    
    if name == "aiw_list":
        workspaces = tmux.list_workspaces()
        if not workspaces:
            return [TextContent(type="text", text="没有运行中的工作空间")]
        
        lines = ["# AI 工作空间列表\n"]
        for ws in workspaces:
            lines.append(f"- **{ws['name']}** [{ws['tool']}/{ws['model']}]")
            lines.append(f"  - 目录: `{ws['dir']}`")
            if ws['desc']:
                lines.append(f"  - 描述: {ws['desc']}")
        return [TextContent(type="text", text="\n".join(lines))]
    
    elif name == "aiw_create":
        result = tmux.create_workspace(
            name=arguments["name"],
            tool=arguments.get("tool"),
            model=arguments.get("model"),
            dir=arguments.get("dir"),
            desc=arguments.get("desc", "")
        )
        if result["success"]:
            return [TextContent(type="text", text=f"✓ 已创建工作空间 **{result['name']}**\n- 工具: {result['tool']}/{result['model']}\n- 目录: `{result['dir']}`")]
        else:
            return [TextContent(type="text", text=f"✗ 创建失败: {result['error']}")]
    
    elif name == "aiw_log":
        ws_name = arguments["name"]
        lines = arguments.get("lines", 30)
        
        if not tmux.workspace_exists(ws_name):
            return [TextContent(type="text", text=f"✗ 工作空间 {ws_name} 不存在")]
        
        log = tmux.get_log(ws_name, lines)
        return [TextContent(type="text", text=f"## {ws_name} 日志\n\n```\n{log or '无输出'}\n```")]
    
    elif name == "aiw_send":
        ws_name = arguments["name"]
        text = arguments["text"]
        
        if ws_name == "all":
            result = tmux.send_to_all(text)
            return [TextContent(type="text", text=f"✓ 已发送到 {result['count']} 个工作空间")]
        else:
            result = tmux.send_keys(ws_name, text)
            if result["success"]:
                return [TextContent(type="text", text=f"✓ 已发送到 {ws_name}")]
            else:
                return [TextContent(type="text", text=f"✗ 发送失败: {result['error']}")]
    
    elif name == "aiw_kill":
        ws_name = arguments["name"]
        result = tmux.kill_workspace(ws_name)
        if result["success"]:
            if ws_name == "all":
                return [TextContent(type="text", text=f"✓ 已关闭 {result['killed']} 个工作空间")]
            else:
                return [TextContent(type="text", text=f"✓ 已关闭 {ws_name}")]
        else:
            return [TextContent(type="text", text=f"✗ 关闭失败: {result['error']}")]
    
    elif name == "aiw_status":
        workspaces = tmux.list_workspaces()
        if not workspaces:
            return [TextContent(type="text", text="没有运行中的工作空间")]
        
        lines = [f"# AI 工作空间状态 ({len(workspaces)} 个运行中)\n"]
        for ws in workspaces:
            log_preview = tmux.get_log(ws['name'], 3)
            log_preview = log_preview.replace('\n', ' ')[:100] + '...' if log_preview else '无输出'
            lines.append(f"### {ws['name']} [{ws['tool']}/{ws['model']}]")
            lines.append(f"- 目录: `{ws['dir']}`")
            lines.append(f"- 最近输出: {log_preview}\n")
        return [TextContent(type="text", text="\n".join(lines))]
    
    elif name == "aiw_tools":
        tools = get_all_tools()
        default = get_default_tool()
        lines = ["# 可用 AI 工具\n"]
        for name, cfg in tools.items():
            mark = " (默认)" if name == default else ""
            lines.append(f"### {name}{mark}")
            lines.append(f"- 命令: `{cfg.get('cmd', name)}`")
            lines.append(f"- 默认模型: {cfg.get('default_model', 'N/A')}")
            lines.append(f"- 可用模型: {', '.join(cfg.get('models', []))}\n")
        return [TextContent(type="text", text="\n".join(lines))]
    
    return [TextContent(type="text", text=f"未知工具: {name}")]

async def run_mcp_server():
    """运行 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

def main():
    """MCP 服务器入口"""
    asyncio.run(run_mcp_server())

if __name__ == "__main__":
    main()
