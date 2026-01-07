[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# AIW - AI 工作空间管理器

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/aiw.svg)](https://github.com/neosun100/aiw/stargazers)

🤖 **在 tmux 中管理多个 AI Agent 工作空间的统一工具。**

管理多个运行在持久化 tmux 会话中的 AI 代理（Gemini、Kiro、Claude 等）。每个工作空间绑定到一个项目目录，确保即使关闭终端，AI 代理也不会丢失上下文。

## ✨ 功能特性

- 🖥️ **CLI** - 命令行管理，支持交互式菜单和总控面板
- 🌐 **Web UI** - 企业级控制面板，实时监控
- 🔌 **REST API** - 完整的 REST API + WebSocket 实时日志
- 🤖 **MCP 支持** - Model Context Protocol，支持 AI 之间协作
- 📁 **项目绑定** - 每个工作空间绑定一个项目目录
- 💾 **持久化会话** - 工作空间在终端断开后依然存在

## 🚀 快速开始

```bash
# 使用 pipx 安装（推荐）
pipx install aiw

# 或使用 pip 安装
pip install aiw

# 创建工作空间（默认使用 Gemini）
aiw new my-project --dir ~/projects/my-project

# 列出所有工作空间
aiw ls

# 进入工作空间
aiw my-project

# 启动 Web UI
aiw server
```

## 📦 安装

### 前置条件

- Python 3.10+
- tmux
- 至少一个 AI CLI 工具（gemini、kiro-cli、claude）

### 方式一：pipx（推荐）

```bash
pipx install aiw
```

### 方式二：pip

```bash
pip install aiw
```

### 方式三：从源码安装

```bash
git clone https://github.com/neosun100/aiw.git
cd aiw
pip install -e .
```

### 方式四：Docker

```bash
# 拉取镜像
docker pull ghcr.io/neosun100/aiw:latest

# 使用 docker 运行
docker run -it --rm \
  -v ~/.config/aiw:/root/.config/aiw \
  -p 8000:8000 \
  ghcr.io/neosun100/aiw:latest

# 或使用 docker-compose
curl -O https://raw.githubusercontent.com/neosun100/aiw/main/docker-compose.yml
docker-compose up -d
```

## 📖 使用方法

### CLI 命令

| 命令 | 说明 |
|------|------|
| `aiw` | 交互式菜单 |
| `aiw ls` | 列出所有工作空间 |
| `aiw new <name> [-t tool] [-m model] [-d dir]` | 创建工作空间 |
| `aiw <name>` | 进入工作空间 |
| `aiw watch` | CLI 总控面板（监控所有） |
| `aiw log <name> [-f]` | 查看工作空间日志 |
| `aiw send <name\|all> "msg"` | 发送命令 |
| `aiw kill <name\|all>` | 关闭工作空间 |
| `aiw server [-p port]` | 启动 Web UI |
| `aiw tool list` | 列出 AI 工具 |
| `aiw tool default <name>` | 设置默认工具 |

### 使用示例

```bash
# 使用不同的 AI 工具创建
aiw new api-dev -t gemini --dir ~/projects/api
aiw new backend -t kiro -m opus --dir ~/projects/backend
aiw new frontend -t claude --dir ~/projects/frontend

# 监控所有工作空间
aiw watch

# 向所有工作空间发送命令
aiw send all "请暂停"

# 在自定义端口启动 Web UI
aiw server -p 9000
```

## ⚙️ 配置

配置文件：`~/.config/aiw/config.toml`

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
# source_env = "~/.env"  # 可选：加载环境文件
```

## 🌐 API 参考

启动服务：`aiw server`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/workspaces` | GET | 列出所有工作空间 |
| `/api/workspaces` | POST | 创建工作空间 |
| `/api/workspaces/{name}` | GET | 获取工作空间详情 |
| `/api/workspaces/{name}` | DELETE | 关闭工作空间 |
| `/api/workspaces/{name}/log` | GET | 获取日志 |
| `/api/workspaces/{name}/send` | POST | 发送命令 |
| `/api/tools` | GET | 列出 AI 工具 |
| `/api/status` | GET | 获取整体状态 |
| `/ws` | WebSocket | 实时日志流 |

API 文档：`http://localhost:8000/docs`

## 🔌 MCP（Model Context Protocol）

AIW 提供 MCP 工具，支持 AI 之间的协作。

### 配置

在 AI 工具的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "aiw": {
      "command": "aiw-mcp"
    }
  }
}
```

### 可用工具

| 工具 | 说明 |
|------|------|
| `aiw_list` | 列出所有工作空间 |
| `aiw_create` | 创建工作空间 |
| `aiw_log` | 获取工作空间日志 |
| `aiw_send` | 发送命令 |
| `aiw_kill` | 关闭工作空间 |
| `aiw_status` | 获取状态概览 |
| `aiw_tools` | 列出 AI 工具配置 |

## 📁 项目结构

```
aiw/
├── pyproject.toml
├── README.md
├── LICENSE
├── config.example.toml
└── src/aiw/
    ├── __init__.py
    ├── cli.py          # CLI 命令
    ├── tmux.py         # Tmux 操作
    ├── config.py       # 配置管理
    ├── api.py          # REST API + Web UI
    └── mcp_server.py   # MCP 服务器
```

## 🛠️ 技术栈

- **CLI**: Click, Rich
- **API**: FastAPI, Uvicorn
- **实时通信**: WebSocket
- **会话管理**: tmux
- **MCP**: mcp-python

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 📝 更新日志

### v0.1.0 (2026-01-07)
- 首次发布
- CLI 支持交互式菜单和总控面板
- Web UI 实时监控
- REST API + WebSocket
- MCP 支持
- 多工具支持（Gemini、Kiro、Claude）

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/aiw&type=Date)](https://star-history.com/#neosun100/aiw)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
