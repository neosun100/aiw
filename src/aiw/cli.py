"""CLI 入口"""
import click
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Group
from rich import box
import time

from . import tmux
from .config import load_config, save_config, ensure_config, get_all_tools, get_default_tool

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """AIW - AI Workspace Manager"""
    ensure_config()
    if ctx.invoked_subcommand is None:
        interactive_menu()

@main.command("ls")
def list_cmd():
    """列出所有工作空间"""
    workspaces = tmux.list_workspaces()
    if not workspaces:
        console.print("[dim]没有运行中的工作空间[/dim]")
        console.print("[dim]使用 aiw new <name> 创建[/dim]")
        return
    
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("NAME", style="cyan")
    table.add_column("TOOL", style="green")
    table.add_column("MODEL", style="yellow")
    table.add_column("DIR", style="dim")
    table.add_column("STATUS")
    table.add_column("DESC", style="dim")
    
    for i, ws in enumerate(workspaces, 1):
        status = "[green]● active[/green]"
        dir_short = ws["dir"].replace(os.path.expanduser("~"), "~") if ws["dir"] else ""
        table.add_row(str(i), ws["name"], ws["tool"], ws["model"], dir_short, status, ws["desc"][:20])
    
    console.print(table)

@main.command("new")
@click.argument("name")
@click.option("-t", "--tool", help="AI 工具 (gemini/kiro/claude)")
@click.option("-m", "--model", help="模型")
@click.option("-d", "--dir", "work_dir", help="工作目录 (默认当前目录)")
@click.option("--desc", default="", help="描述")
def new_cmd(name, tool, model, work_dir, desc):
    """创建新工作空间"""
    result = tmux.create_workspace(name, tool, model, work_dir, desc)
    if result["success"]:
        console.print(f"[green]✓[/green] 创建工作空间 [cyan]{name}[/cyan]")
        console.print(f"  工具: [green]{result['tool']}[/green] / [yellow]{result['model']}[/yellow]")
        console.print(f"  目录: [dim]{result['dir']}[/dim]")
        console.print(f"  输入 [yellow]aiw {name}[/yellow] 进入")
    else:
        console.print(f"[red]✗[/red] {result['error']}")

@main.command("log")
@click.argument("name")
@click.option("-n", "--lines", default=30, help="显示行数")
@click.option("-f", "--follow", is_flag=True, help="持续跟踪")
def log_cmd(name, lines, follow):
    """查看工作空间日志"""
    if not tmux.workspace_exists(name):
        console.print(f"[red]✗[/red] 工作空间 [cyan]{name}[/cyan] 不存在")
        return
    
    if follow:
        try:
            with Live(console=console, refresh_per_second=2) as live:
                while True:
                    log = tmux.get_log(name, lines)
                    live.update(Panel(log or "[dim]无输出[/dim]", title=f"[cyan]{name}[/cyan]", box=box.ROUNDED))
                    time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    else:
        log = tmux.get_log(name, lines)
        console.print(Panel(log or "[dim]无输出[/dim]", title=f"[cyan]{name}[/cyan]", box=box.ROUNDED))

@main.command("send")
@click.argument("name")
@click.argument("text")
def send_cmd(name, text):
    """发送命令到工作空间"""
    if name == "all":
        result = tmux.send_to_all(text)
        console.print(f"[green]✓[/green] 已发送到 {result['count']} 个工作空间")
    else:
        result = tmux.send_keys(name, text)
        if result["success"]:
            console.print(f"[green]✓[/green] 已发送到 [cyan]{name}[/cyan]")
        else:
            console.print(f"[red]✗[/red] {result['error']}")

@main.command("kill")
@click.argument("name")
def kill_cmd(name):
    """关闭工作空间"""
    result = tmux.kill_workspace(name)
    if result["success"]:
        if name == "all":
            console.print(f"[green]✓[/green] 已关闭 {result['killed']} 个工作空间")
        else:
            console.print(f"[green]✓[/green] 已关闭 [cyan]{name}[/cyan]")
    else:
        console.print(f"[red]✗[/red] {result['error']}")

@main.command("watch")
def watch_cmd():
    """总控面板 - 实时监控所有工作空间"""
    watch_panel()

@main.command("server")
@click.option("-p", "--port", default=8000, help="端口")
@click.option("-h", "--host", default="0.0.0.0", help="主机")
def server_cmd(port, host):
    """启动 API + Web UI 服务"""
    from .api import run_server
    run_server(host, port)

@main.group("tool")
def tool_group():
    """管理 AI 工具配置"""
    pass

@tool_group.command("list")
def tool_list():
    """列出所有 AI 工具"""
    config = load_config()
    table = Table(box=box.ROUNDED)
    table.add_column("TOOL", style="cyan")
    table.add_column("CMD", style="green")
    table.add_column("DEFAULT", style="yellow")
    table.add_column("MODELS")
    
    default = config.get("default_tool", "")
    for name, cfg in config.get("tools", {}).items():
        mark = " [green]✓[/green]" if name == default else ""
        table.add_row(f"{name}{mark}", cfg.get("cmd", ""), cfg.get("default_model", ""), ", ".join(cfg.get("models", [])))
    console.print(table)

@tool_group.command("default")
@click.argument("name")
def tool_default(name):
    """设置默认工具"""
    config = load_config()
    if name not in config.get("tools", {}):
        console.print(f"[red]✗[/red] 工具 [cyan]{name}[/cyan] 不存在")
        return
    config["default_tool"] = name
    save_config(config)
    console.print(f"[green]✓[/green] 默认工具设为 [cyan]{name}[/cyan]")

@tool_group.command("add")
@click.argument("name")
@click.argument("cmd")
@click.option("-m", "--models", default="", help="支持的模型，逗号分隔")
@click.option("--default-model", default="", help="默认模型")
def tool_add(name, cmd, models, default_model):
    """添加新工具"""
    config = load_config()
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    config["tools"][name] = {
        "cmd": cmd,
        "default_model": default_model or (model_list[0] if model_list else ""),
        "models": model_list,
    }
    save_config(config)
    console.print(f"[green]✓[/green] 已添加工具 [cyan]{name}[/cyan]")

def interactive_menu():
    """交互式菜单"""
    while True:
        console.clear()
        console.print("[bold]🤖 AI Workspaces[/bold]\n")
        
        workspaces = tmux.list_workspaces()
        if workspaces:
            table = Table(box=box.ROUNDED, show_header=True)
            table.add_column("#", style="dim", width=3)
            table.add_column("NAME", style="cyan")
            table.add_column("TOOL", style="green")
            table.add_column("MODEL", style="yellow")
            table.add_column("DIR", style="dim", max_width=30)
            table.add_column("STATUS")
            
            for i, ws in enumerate(workspaces, 1):
                dir_short = ws["dir"].replace(os.path.expanduser("~"), "~") if ws["dir"] else ""
                table.add_row(str(i), ws["name"], ws["tool"], ws["model"], dir_short, "[green]●[/green]")
            console.print(table)
        else:
            console.print("[dim]没有运行中的工作空间[/dim]")
        
        console.print("\n[dim][n]ew  [w]atch  [l]og  [k]ill  [s]erver  [q]uit  [1-9]进入[/dim]")
        
        try:
            choice = console.input("\n> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break
        
        if choice == "q":
            break
        elif choice == "n":
            name = console.input("名称: ").strip()
            if not name:
                continue
            tools = list(get_all_tools().keys())
            console.print(f"工具 [{'/'.join(tools)}] (回车用默认): ", end="")
            tool = console.input("").strip() or None
            model = console.input("模型 (回车用默认): ").strip() or None
            work_dir = console.input(f"工作目录 (回车用 {os.getcwd()}): ").strip() or None
            desc = console.input("描述 (可选): ").strip()
            result = tmux.create_workspace(name, tool, model, work_dir, desc)
            if result["success"]:
                console.print(f"\n[green]✓[/green] 已创建 [cyan]{name}[/cyan]")
            else:
                console.print(f"\n[red]✗[/red] {result['error']}")
            console.input("\n按 Enter 继续...")
        elif choice == "w":
            watch_panel()
        elif choice == "l":
            if workspaces:
                name = console.input("查看哪个日志: ").strip()
                if name:
                    log = tmux.get_log(name, 30)
                    console.print(Panel(log or "[dim]无输出[/dim]", title=f"[cyan]{name}[/cyan]"))
                    console.input("\n按 Enter 继续...")
        elif choice == "k":
            name = console.input("关闭哪个 (名称/all): ").strip()
            if name:
                tmux.kill_workspace(name)
                console.print(f"[green]✓[/green] 已关闭")
                console.input("\n按 Enter 继续...")
        elif choice == "s":
            from .api import run_server
            run_server("0.0.0.0", 8000)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(workspaces):
                tmux.attach_workspace(workspaces[idx]["name"])

def watch_panel():
    """总控面板"""
    def make_layout():
        workspaces = tmux.list_workspaces()
        if not workspaces:
            return Panel("[dim]没有运行中的工作空间[/dim]", title="🎛️ 总控面板", box=box.DOUBLE)
        
        term_width = console.width
        count = len(workspaces)
        cols = 1 if count <= 2 or term_width < 100 else (2 if count <= 4 or term_width < 160 else 3)
        
        panels = []
        for ws in workspaces:
            log = tmux.get_log(ws["name"], 8)
            dir_short = ws["dir"].replace(os.path.expanduser("~"), "~") if ws["dir"] else ""
            title = f"{ws['name']} [{ws['tool']}/{ws['model']}] [green]●[/green]"
            subtitle = f"[dim]{dir_short}[/dim]"
            content = f"{subtitle}\n{'─'*20}\n{log or '[dim]无输出[/dim]'}"
            panels.append(Panel(content, title=title, box=box.ROUNDED, height=12))
        
        rows = []
        for i in range(0, len(panels), cols):
            rows.append(Columns(panels[i:i+cols], equal=True, expand=True))
        
        return Panel(Group(*rows), title="🎛️ AI Agent 总控面板 [Ctrl+C 退出]", box=box.DOUBLE)
    
    console.clear()
    with Live(make_layout(), refresh_per_second=0.5, console=console) as live:
        try:
            while True:
                live.update(make_layout())
                time.sleep(2)
        except KeyboardInterrupt:
            pass

def cli():
    """CLI 入口，支持 aiw <name> 直接进入"""
    if len(sys.argv) == 2 and not sys.argv[1].startswith("-"):
        name = sys.argv[1]
        commands = ["ls", "new", "watch", "log", "send", "kill", "server", "tool"]
        if name not in commands:
            if tmux.workspace_exists(name):
                tmux.attach_workspace(name)
                return
    main()

if __name__ == "__main__":
    cli()
