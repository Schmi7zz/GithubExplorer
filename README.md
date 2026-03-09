<div align="center">

<img src="logo.png" width="150" alt="GitHub Explorer Bot">

# 🐙 GitHub Explorer Bot

**A powerful Telegram bot to explore any GitHub repository — right from your chat.**

Browse files, download releases, view READMEs, check stats — all without leaving Telegram.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4.svg?logo=telegram)](https://t.me/SchmitzWS)

---

[Features](#-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [Configuration](#-configuration) • [Deployment](#-deployment) • [Telegram Channel](https://t.me/SchmitzWS)

**[🇮🇷 فارسی](README.fa.md)**

</div>

---

## ✨ Features

| Feature | Description |
|---------|------------|
| 📁 **File Browser** | Navigate through repository files and folders with pagination |
| 🏷 **Releases** | View all releases, assets, download counts — and download them directly |
| 🌿 **Branches** | List all branches of a repository |
| 📝 **README Viewer** | Read the README without leaving Telegram |
| 👥 **Contributors** | See who contributed and how much |
| 📊 **Language Stats** | Visual bar chart of languages used |
| ⬇️ **Source Download** | Download the full repository as ZIP |
| 📢 **Broadcast** | Admin command to send messages to all bot users |
| 👤 **User Tracking** | Track bot usage with `/users` admin command |
| 🚀 **Large Files** | Supports files up to **2GB** via Telegram Local Bot API |

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

[ 📁 Files ] [ 🏷 Releases ]
[ 🌿 Branches ] [ 📝 README ]
[ 👥 Contributors ] [ 📊 Languages ]
[ ⬇️ Download ZIP ]
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/github-explorer-bot.git
cd github-explorer-bot
```

### 2. Configure environment

```bash
cp .env.example .env
nano .env
```

Fill in your credentials:

```env
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=your_telegram_user_id
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef
```

### 3. Launch

```bash
docker-compose up -d --build
```

That's it! Send a GitHub link to your bot and start exploring.

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram Bot token from @BotFather |
| `ADMIN_IDS` | ✅ | Comma-separated Telegram user IDs for admin access |
| `TELEGRAM_API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `GITHUB_TOKEN` | ❌ | GitHub PAT — raises API rate limit from 60 to 5000 req/hr |

### Getting a GitHub Token (optional but recommended)

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Generate a **classic** token with `public_repo` scope
3. Add it to your `.env` file

---

## 🐳 Deployment

### Architecture

```
┌─────────────────┐     ┌──────────────────────┐
│  Telegram Cloud  │◄───►│  Local Bot API Server │
└─────────────────┘     │  (no 50MB file limit) │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │   GitHub Explorer Bot  │
                        │   (Python 3.10)        │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │   GitHub API           │
                        └──────────────────────┘
```

The bot uses **Telegram's Local Bot API Server** which removes the 50MB file upload limit, allowing downloads up to ~2GB.

### Commands

```bash
# Start
docker-compose up -d --build

# View logs
docker-compose logs -f bot

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Admin Commands

| Command | Description |
|---------|------------|
| `/start` | Welcome message (all users) |
| `/users` | List all bot users (admin only) |
| `/broadcast <message>` | Send message to all users (admin only) |

---

## 🏗 Project Structure

```
github-explorer-bot/
├── github_telegram_bot.py   # Main bot code
├── Dockerfile               # Container image
├── docker-compose.yml       # Service orchestration
├── .env.example             # Environment template
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📬 Contact

<div align="center">

[![Telegram Channel](https://img.shields.io/badge/Telegram-Channel-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/SchmitzWS)

**Made with 🖤 by [Schmitz](https://t.me/SchmitzWS)**

</div>

---

<div align="center">

If you found this useful, give it a ⭐

</div>
