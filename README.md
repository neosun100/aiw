[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# AIW - AI Workspace Manager

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/aiw.svg)](https://github.com/neosun100/aiw/stargazers)

🤖 **A unified tool for managing multiple AI Agent workspaces in tmux.**

Manage multiple AI agents (Gemini, Kiro, Claude, etc.) running in persistent tmux sessions. Each workspace is bound to a project directory, ensuring your AI agents never lose context even when you close your terminal.

## ✨ Features

- 🖥️ **CLI** - Command-line management with interactive menu and dashboard
- 🌐 **Web UI** - Enterprise-grade control panel with real-time monitoring
- 🔌 **REST API** - Full REST API + WebSocket for real-time logs
- 🤖 **MCP Support** - Model Context Protocol for AI-to-AI collaboration
- 📁 **Project Binding** - Each workspace binds to a project directory
- 💾 **Persistent Sessions** - Workspaces survive terminal disconnection

## 🚀 Quick Start

```bash
# Install with pipx (recommended)
pipx install aiw

# Or install with pip
pip install aiw

# Create a workspace (defaults to Gemini)
aiw new my-project --dir ~/projects/my-project

# List all workspaces
aiw ls

# Enter a workspace
aiw my-project

# Launch Web UI
aiw server
```

## 📦 Installation

### Prerequisites

- Python 3.10+
- tmux
- At least one AI CLI tool (gemini, kiro-cli, claude)

### Method 1: pipx (Recommended)

```bash
pipx install aiw
```

### Method 2: pip

```bash
pip install aiw
```

### Method 3: From Source

```bash
git clone https://github.com/neosun100/aiw.git
cd aiw
pip install -e .
```

### Method 4: Docker

```bash
# Pull the image
docker pull ghcr.io/neosun100/aiw:latest

# Run with docker
docker run -it --rm \
  -v ~/.config/aiw:/root/.config/aiw \
  -p 8000:8000 \
  ghcr.io/neosun100/aiw:latest

# Or use docker-compose
curl -O https://raw.githubusercontent.com/neosun100/aiw/main/docker-compose.yml
docker-compose up -d
```

## 📖 Usage

### CLI Commands

| Command | Description |
|---------|-------------|
| `aiw` | Interactive menu |
| `aiw ls` | List all workspaces |
| `aiw new <name> [-t tool] [-m model] [-d dir]` | Create workspace |
| `aiw <name>` | Enter workspace |
| `aiw watch` | CLI dashboard (monitor all) |
| `aiw log <name> [-f]` | View workspace logs |
| `aiw send <name\|all> "msg"` | Send command |
| `aiw kill <name\|all>` | Close workspace |
| `aiw server [-p port]` | Start Web UI |
| `aiw tool list` | List AI tools |
| `aiw tool default <name>` | Set default tool |

### Examples

```bash
# Create with different AI tools
aiw new api-dev -t gemini --dir ~/projects/api
aiw new backend -t kiro -m opus --dir ~/projects/backend
aiw new frontend -t claude --dir ~/projects/frontend

# Monitor all workspaces
aiw watch

# Send command to all workspaces
aiw send all "please pause"

# Start Web UI on custom port
aiw server -p 9000
```

## ⚙️ Configuration

Configuration file: `~/.config/aiw/config.toml`

```toml
default_tool = "gemini"

[server]
host = "0.0.0.0"
port = 8000

[tools.gemini]
cmd = "gemini"
default_model = "gemini-2.0-flash"
models = ["gemini-2.0-flash", "gemini-2.5-pro"]
model_flag = "--model"

[tools.kiro]
cmd = "kiro-cli chat"
default_model = "sonnet"
models = ["sonnet", "opus"]
model_flag = "--model"

[tools.claude]
cmd = "claude"
default_model = "sonnet"
models = ["sonnet", "opus"]
model_flag = "--model"
# source_env = "~/.env"  # Optional: source env file
```

## 🌐 API Reference

Start the server: `aiw server`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/workspaces` | GET | List all workspaces |
| `/api/workspaces` | POST | Create workspace |
| `/api/workspaces/{name}` | GET | Get workspace details |
| `/api/workspaces/{name}` | DELETE | Close workspace |
| `/api/workspaces/{name}/log` | GET | Get logs |
| `/api/workspaces/{name}/send` | POST | Send command |
| `/api/tools` | GET | List AI tools |
| `/api/status` | GET | Get overall status |
| `/ws` | WebSocket | Real-time log stream |

API Documentation: `http://localhost:8000/docs`

## 🔌 MCP (Model Context Protocol)

AIW provides MCP tools for AI-to-AI collaboration.

### Setup

Add to your AI tool's MCP config:

```json
{
  "mcpServers": {
    "aiw": {
      "command": "aiw-mcp"
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `aiw_list` | List all workspaces |
| `aiw_create` | Create workspace |
| `aiw_log` | Get workspace logs |
| `aiw_send` | Send command |
| `aiw_kill` | Close workspace |
| `aiw_status` | Get status overview |
| `aiw_tools` | List AI tool configs |

## 📁 Project Structure

```
aiw/
├── pyproject.toml
├── README.md
├── LICENSE
├── config.example.toml
└── src/aiw/
    ├── __init__.py
    ├── cli.py          # CLI commands
    ├── tmux.py         # Tmux operations
    ├── config.py       # Configuration
    ├── api.py          # REST API + Web UI
    └── mcp_server.py   # MCP Server
```

## 🛠️ Tech Stack

- **CLI**: Click, Rich
- **API**: FastAPI, Uvicorn
- **Real-time**: WebSocket
- **Session**: tmux
- **MCP**: mcp-python

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Changelog

### v0.1.0 (2026-01-07)
- Initial release
- CLI with interactive menu and dashboard
- Web UI with real-time monitoring
- REST API + WebSocket
- MCP support
- Multi-tool support (Gemini, Kiro, Claude)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/aiw&type=Date)](https://star-history.com/#neosun100/aiw)

## 📱 Follow Us

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
