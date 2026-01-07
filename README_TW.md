[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# AIW - AI 工作空間管理器

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/aiw.svg)](https://github.com/neosun100/aiw/stargazers)

🤖 **在 tmux 中管理多個 AI Agent 工作空間的統一工具。**

管理多個運行在持久化 tmux 會話中的 AI 代理（Gemini、Kiro、Claude 等）。每個工作空間綁定到一個專案目錄，確保即使關閉終端，AI 代理也不會丟失上下文。

## ✨ 功能特性

- 🖥️ **CLI** - 命令列管理，支援互動式選單和總控面板
- 🌐 **Web UI** - 企業級控制面板，即時監控
- 🔌 **REST API** - 完整的 REST API + WebSocket 即時日誌
- 🤖 **MCP 支援** - Model Context Protocol，支援 AI 之間協作
- 📁 **專案綁定** - 每個工作空間綁定一個專案目錄
- 💾 **持久化會話** - 工作空間在終端斷開後依然存在

## 🚀 快速開始

```bash
# 使用 pipx 安裝（推薦）
pipx install aiw

# 或使用 pip 安裝
pip install aiw

# 建立工作空間（預設使用 Gemini）
aiw new my-project --dir ~/projects/my-project

# 列出所有工作空間
aiw ls

# 進入工作空間
aiw my-project

# 啟動 Web UI
aiw server
```

## 📦 安裝

### 前置條件

- Python 3.10+
- tmux
- 至少一個 AI CLI 工具（gemini、kiro-cli、claude）

### 方式一：pipx（推薦）

```bash
pipx install aiw
```

### 方式二：pip

```bash
pip install aiw
```

### 方式三：從原始碼安裝

```bash
git clone https://github.com/neosun100/aiw.git
cd aiw
pip install -e .
```

### 方式四：Docker

```bash
# 拉取映像
docker pull ghcr.io/neosun100/aiw:latest

# 使用 docker 運行
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

| 命令 | 說明 |
|------|------|
| `aiw` | 互動式選單 |
| `aiw ls` | 列出所有工作空間 |
| `aiw new <name> [-t tool] [-m model] [-d dir]` | 建立工作空間 |
| `aiw <name>` | 進入工作空間 |
| `aiw watch` | CLI 總控面板（監控所有） |
| `aiw log <name> [-f]` | 查看工作空間日誌 |
| `aiw send <name\|all> "msg"` | 發送命令 |
| `aiw kill <name\|all>` | 關閉工作空間 |
| `aiw server [-p port]` | 啟動 Web UI |
| `aiw tool list` | 列出 AI 工具 |
| `aiw tool default <name>` | 設定預設工具 |

### 使用範例

```bash
# 使用不同的 AI 工具建立
aiw new api-dev -t gemini --dir ~/projects/api
aiw new backend -t kiro -m opus --dir ~/projects/backend
aiw new frontend -t claude --dir ~/projects/frontend

# 監控所有工作空間
aiw watch

# 向所有工作空間發送命令
aiw send all "請暫停"

# 在自訂埠啟動 Web UI
aiw server -p 9000
```

## ⚙️ 配置

配置檔案：`~/.config/aiw/config.toml`

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
# source_env = "~/.env"  # 可選：載入環境檔案
```

## 🌐 API 參考

啟動服務：`aiw server`

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/workspaces` | GET | 列出所有工作空間 |
| `/api/workspaces` | POST | 建立工作空間 |
| `/api/workspaces/{name}` | GET | 取得工作空間詳情 |
| `/api/workspaces/{name}` | DELETE | 關閉工作空間 |
| `/api/workspaces/{name}/log` | GET | 取得日誌 |
| `/api/workspaces/{name}/send` | POST | 發送命令 |
| `/api/tools` | GET | 列出 AI 工具 |
| `/api/status` | GET | 取得整體狀態 |
| `/ws` | WebSocket | 即時日誌流 |

API 文件：`http://localhost:8000/docs`

## 🔌 MCP（Model Context Protocol）

AIW 提供 MCP 工具，支援 AI 之間的協作。

### 配置

在 AI 工具的 MCP 配置中新增：

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

| 工具 | 說明 |
|------|------|
| `aiw_list` | 列出所有工作空間 |
| `aiw_create` | 建立工作空間 |
| `aiw_log` | 取得工作空間日誌 |
| `aiw_send` | 發送命令 |
| `aiw_kill` | 關閉工作空間 |
| `aiw_status` | 取得狀態概覽 |
| `aiw_tools` | 列出 AI 工具配置 |

## 📁 專案結構

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
    └── mcp_server.py   # MCP 伺服器
```

## 🛠️ 技術棧

- **CLI**: Click, Rich
- **API**: FastAPI, Uvicorn
- **即時通訊**: WebSocket
- **會話管理**: tmux
- **MCP**: mcp-python

## 🤝 貢獻

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📝 更新日誌

### v0.1.0 (2026-01-07)
- 首次發布
- CLI 支援互動式選單和總控面板
- Web UI 即時監控
- REST API + WebSocket
- MCP 支援
- 多工具支援（Gemini、Kiro、Claude）

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/aiw&type=Date)](https://star-history.com/#neosun100/aiw)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
