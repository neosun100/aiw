[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# AIW - AI ワークスペースマネージャー

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/aiw.svg)](https://github.com/neosun100/aiw/stargazers)

🤖 **tmux で複数の AI エージェントワークスペースを管理する統合ツール。**

永続的な tmux セッションで実行される複数の AI エージェント（Gemini、Kiro、Claude など）を管理します。各ワークスペースはプロジェクトディレクトリにバインドされ、ターミナルを閉じても AI エージェントがコンテキストを失うことはありません。

## ✨ 機能

- 🖥️ **CLI** - インタラクティブメニューとダッシュボード付きのコマンドライン管理
- 🌐 **Web UI** - リアルタイム監視付きのエンタープライズグレードコントロールパネル
- 🔌 **REST API** - 完全な REST API + リアルタイムログ用 WebSocket
- 🤖 **MCP サポート** - AI 間コラボレーション用の Model Context Protocol
- 📁 **プロジェクトバインディング** - 各ワークスペースはプロジェクトディレクトリにバインド
- 💾 **永続セッション** - ターミナル切断後もワークスペースは存続

## 🚀 クイックスタート

```bash
# pipx でインストール（推奨）
pipx install aiw

# または pip でインストール
pip install aiw

# ワークスペースを作成（デフォルトは Gemini）
aiw new my-project --dir ~/projects/my-project

# すべてのワークスペースを一覧表示
aiw ls

# ワークスペースに入る
aiw my-project

# Web UI を起動
aiw server
```

## 📦 インストール

### 前提条件

- Python 3.10+
- tmux
- 少なくとも1つの AI CLI ツール（gemini、kiro-cli、claude）

### 方法1：pipx（推奨）

```bash
pipx install aiw
```

### 方法2：pip

```bash
pip install aiw
```

### 方法3：ソースから

```bash
git clone https://github.com/neosun100/aiw.git
cd aiw
pip install -e .
```

### 方法4：Docker

```bash
# イメージをプル
docker pull ghcr.io/neosun100/aiw:latest

# docker で実行
docker run -it --rm \
  -v ~/.config/aiw:/root/.config/aiw \
  -p 8000:8000 \
  ghcr.io/neosun100/aiw:latest

# または docker-compose を使用
curl -O https://raw.githubusercontent.com/neosun100/aiw/main/docker-compose.yml
docker-compose up -d
```

## 📖 使用方法

### CLI コマンド

| コマンド | 説明 |
|----------|------|
| `aiw` | インタラクティブメニュー |
| `aiw ls` | すべてのワークスペースを一覧表示 |
| `aiw new <name> [-t tool] [-m model] [-d dir]` | ワークスペースを作成 |
| `aiw <name>` | ワークスペースに入る |
| `aiw watch` | CLI ダッシュボード（すべてを監視） |
| `aiw log <name> [-f]` | ワークスペースログを表示 |
| `aiw send <name\|all> "msg"` | コマンドを送信 |
| `aiw kill <name\|all>` | ワークスペースを閉じる |
| `aiw server [-p port]` | Web UI を起動 |
| `aiw tool list` | AI ツールを一覧表示 |
| `aiw tool default <name>` | デフォルトツールを設定 |

### 使用例

```bash
# 異なる AI ツールで作成
aiw new api-dev -t gemini --dir ~/projects/api
aiw new backend -t kiro -m opus --dir ~/projects/backend
aiw new frontend -t claude --dir ~/projects/frontend

# すべてのワークスペースを監視
aiw watch

# すべてのワークスペースにコマンドを送信
aiw send all "一時停止してください"

# カスタムポートで Web UI を起動
aiw server -p 9000
```

## ⚙️ 設定

設定ファイル：`~/.config/aiw/config.toml`

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
# source_env = "~/.env"  # オプション：環境ファイルを読み込む
```

## 🌐 API リファレンス

サーバーを起動：`aiw server`

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/api/workspaces` | GET | すべてのワークスペースを一覧表示 |
| `/api/workspaces` | POST | ワークスペースを作成 |
| `/api/workspaces/{name}` | GET | ワークスペースの詳細を取得 |
| `/api/workspaces/{name}` | DELETE | ワークスペースを閉じる |
| `/api/workspaces/{name}/log` | GET | ログを取得 |
| `/api/workspaces/{name}/send` | POST | コマンドを送信 |
| `/api/tools` | GET | AI ツールを一覧表示 |
| `/api/status` | GET | 全体のステータスを取得 |
| `/ws` | WebSocket | リアルタイムログストリーム |

API ドキュメント：`http://localhost:8000/docs`

## 🔌 MCP（Model Context Protocol）

AIW は AI 間コラボレーション用の MCP ツールを提供します。

### セットアップ

AI ツールの MCP 設定に追加：

```json
{
  "mcpServers": {
    "aiw": {
      "command": "aiw-mcp"
    }
  }
}
```

### 利用可能なツール

| ツール | 説明 |
|--------|------|
| `aiw_list` | すべてのワークスペースを一覧表示 |
| `aiw_create` | ワークスペースを作成 |
| `aiw_log` | ワークスペースログを取得 |
| `aiw_send` | コマンドを送信 |
| `aiw_kill` | ワークスペースを閉じる |
| `aiw_status` | ステータス概要を取得 |
| `aiw_tools` | AI ツール設定を一覧表示 |

## 📁 プロジェクト構造

```
aiw/
├── pyproject.toml
├── README.md
├── LICENSE
├── config.example.toml
└── src/aiw/
    ├── __init__.py
    ├── cli.py          # CLI コマンド
    ├── tmux.py         # Tmux 操作
    ├── config.py       # 設定管理
    ├── api.py          # REST API + Web UI
    └── mcp_server.py   # MCP サーバー
```

## 🛠️ 技術スタック

- **CLI**: Click, Rich
- **API**: FastAPI, Uvicorn
- **リアルタイム**: WebSocket
- **セッション**: tmux
- **MCP**: mcp-python

## 🤝 コントリビューション

コントリビューションを歓迎します！お気軽に Pull Request を提出してください。

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を開く

## 📝 変更履歴

### v0.1.0 (2026-01-07)
- 初回リリース
- インタラクティブメニューとダッシュボード付き CLI
- リアルタイム監視付き Web UI
- REST API + WebSocket
- MCP サポート
- マルチツールサポート（Gemini、Kiro、Claude）

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/aiw&type=Date)](https://star-history.com/#neosun100/aiw)

## 📱 フォローする

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
