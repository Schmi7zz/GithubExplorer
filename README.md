<div align="center">

<img src="logo.png" width="140" alt="GitHub Explorer Bot">

# 🐙 GitHub Explorer Bot

**A powerful Telegram bot to explore any GitHub repository — right from your chat.**

Browse files · Download releases · View READMEs · Check stats — all without leaving Telegram.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](docker-compose.yml)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram)](https://t.me/SchmitzWS)

[Features](#-features) · [Demo](#-demo) · [Quick Start](#-quick-start) · [Configuration](#%EF%B8%8F-configuration) · [Architecture](#-architecture)

**[🇮🇷 فارسی](README.fa.md)**

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **File Browser** | Navigate through repository files and folders with pagination |
| 🏷 **Releases** | View all releases, assets, download counts — and download them directly |
| 🌿 **Branches** | List all branches of a repository |
| 📝 **README Viewer** | Read the README without leaving Telegram |
| 👥 **Contributors** | See who contributed and how much |
| 📊 **Language Stats** | Visual bar chart of languages used |
| ⬇️ **Source Download** | Download the full repository as a ZIP archive |
| 📢 **Broadcast** | Admin command to send messages to all bot users |
| 👤 **User Tracking** | Track bot usage with the `/users` admin command |
| 🚀 **Large Files** | Supports files up to **2 GB** via Telegram Local Bot API |

---

## 🎬 Demo

Just send any GitHub repo link to the bot:

```
https://github.com/torvalds/linux
```

The bot instantly shows repository info with interactive buttons:

```
🐙 torvalds/linux

The Linux kernel source tree

⭐️ Stars: 195,000    🍴 Forks: 55,000
👁 Watchers: 8,000    🐛 Issues: 350
💾 Size: 4.8 GB       🌿 Branch: master
🛠 Language: C         📜 License: GPL-2.0

[ 📁 Files ]        [ 🏷 Releases ]
[ 🌿 Branches ]     [ 📝 README ]
[ 👥 Contributors ] [ 📊 Languages ]
[ ⬇️ Download ZIP ]
```

---

## 🚀 Quick Start

### Method 1 — Auto Installer (Recommended)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Schmi7zz/GithubExplorer/main/install.sh)
```

The script handles everything automatically: installs Docker if needed, clones the repo, sets up your `.env`, and launches the bot.

---

### Method 2 — Manual Setup

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

#### 1. Clone the repository

```bash
git clone https://github.com/Schmi7zz/GithubExplorer.git
cd GithubExplorer
```

#### 2. Configure environment

```bash
cp env.example .env
nano .env
```

Fill in your credentials:

```env
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=123456789
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef
GITHUB_TOKEN=                         # optional
```

#### 3. Launch

```bash
docker compose up -d --build
```

That's it! Send a GitHub link to your bot and start exploring.

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram Bot token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | ✅ | Comma-separated Telegram user IDs for admin access |
| `TELEGRAM_API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org/apps) |
| `TELEGRAM_API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org/apps) |
| `GITHUB_TOKEN` | ❌ | GitHub PAT — raises API rate limit from 60 to 5,000 req/hr |

> **Getting a GitHub Token (optional but recommended)**
> 1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
> 2. Generate a **Classic** token with the `public_repo` scope
> 3. Add it to your `.env` file

---

## 🏗 Architecture

The bot uses **Telegram's Local Bot API Server**, which removes the 50 MB file upload limit and allows downloads up to ~2 GB.

```
┌─────────────────────┐        ┌────────────────────────────┐
│   Telegram Cloud    │ ◄────► │   Local Bot API Server     │
└─────────────────────┘        │   (no 50 MB file limit)    │
                                └──────────────┬─────────────┘
                                               │
                                ┌──────────────▼─────────────┐
                                │    GitHub Explorer Bot     │
                                │       Python 3.10          │
                                └──────────────┬─────────────┘
                                               │
                                ┌──────────────▼─────────────┐
                                │        GitHub API          │
                                └────────────────────────────┘
```

### Docker Commands

```bash
# Start and build
docker compose up -d --build

# Follow bot logs
docker compose logs -f bot

# Follow Local API logs
docker compose logs -f telegram-bot-api

# Check container status
docker compose ps

# Restart the bot
docker compose restart bot

# Stop everything
docker compose down
```

---

## 🤖 Bot Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/start` | Everyone | Welcome message |
| `/users` | Admin | List all bot users |
| `/broadcast <message>` | Admin | Send a message to all users |
| GitHub URL | Everyone | Show repo info and interactive menu |

---

## 📁 Project Structure

```
GithubExplorer/
├── github_telegram_bot.py   # Main bot code
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Service orchestration
├── env.example              # Environment variables template
├── install.sh               # Automated install script
├── README.md                # English documentation
├── README.fa.md             # Persian documentation
└── LICENSE                  # MIT License
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push the branch: `git push origin feature/my-feature`
5. Open a **Pull Request**

---

## 📬 Contact

<div align="center">

[![Telegram](https://img.shields.io/badge/Telegram-Channel-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/SchmitzWS)

Made with 🖤 by **[Schmitz](https://t.me/SchmitzWS)**

If you found this useful, give it a ⭐

</div>
