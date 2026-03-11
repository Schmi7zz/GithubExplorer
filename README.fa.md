<div align="center">

<img src="logo.png" width="140" alt="GitHub Explorer Bot">

# 🐙 GitHub Explorer Bot

**ربات تلگرامی قدرتمند برای کاوش ریپازیتوری‌های گیتهاب — مستقیم از چت**

مرور فایل‌ها · دانلود ریلیز · مشاهده README · آمار پروژه — بدون خروج از تلگرام

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](docker-compose.yml)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram)](https://t.me/SchmitzWS)

[امکانات](#-امکانات) · [دمو](#-دمو) · [نصب سریع](#-نصب-سریع) · [تنظیمات](#%EF%B8%8F-تنظیمات) · [معماری](#-معماری)

**[🇬🇧 English](README.md)**

</div>

---

## ✨ امکانات

| قابلیت | توضیح |
|--------|-------|
| 📁 **مرور فایل‌ها** | پیمایش فایل‌ها و پوشه‌های ریپو با صفحه‌بندی |
| 🏷 **ریلیزها** | مشاهده تمام ریلیزها، فایل‌ها، تعداد دانلود و دانلود مستقیم |
| 🌿 **برنچ‌ها** | لیست تمام برنچ‌های ریپازیتوری |
| 📝 **نمایش README** | خواندن فایل README بدون ترک تلگرام |
| 👥 **مشارکت‌کنندگان** | لیست contributors به همراه تعداد commit |
| 📊 **آمار زبان‌ها** | نمودار بصری زبان‌های برنامه‌نویسی استفاده‌شده |
| ⬇️ **دانلود ZIP** | دانلود کامل سورس‌کد ریپازیتوری به صورت فشرده |
| 📢 **Broadcast** | ارسال پیام همگانی به تمام کاربران ربات (ادمین) |
| 👤 **مدیریت کاربران** | مشاهده لیست کاربران ربات با دستور `/users` (ادمین) |
| 🚀 **فایل‌های بزرگ** | پشتیبانی از فایل تا **۲ گیگابایت** با Local Bot API |

---

## 🎬 دمو

یک لینک GitHub به ربات بفرست:

```
https://github.com/torvalds/linux
```

ربات بلافاصله اطلاعات کامل ریپو را با دکمه‌های تعاملی نمایش می‌دهد:

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

## 🚀 نصب سریع

### روش ۱ — اسکریپت خودکار (پیشنهادی)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Schmi7zz/GithubExplorer/main/install.sh)
```

اسکریپت تمام مراحل را خودکار انجام می‌دهد: نصب Docker در صورت نیاز، کلون پروژه، ساخت `.env` و راه‌اندازی ربات.

---

### روش ۲ — نصب دستی

#### پیش‌نیازها

- [Docker](https://docs.docker.com/get-docker/) و Docker Compose
- توکن ربات از [@BotFather](https://t.me/BotFather)
- اطلاعات API از [my.telegram.org](https://my.telegram.org)

#### ۱. کلون کردن

```bash
git clone https://github.com/Schmi7zz/GithubExplorer.git
cd GithubExplorer
```

#### ۲. ساخت فایل `.env`

```bash
cp env.example .env
nano .env
```

اطلاعات را وارد کنید:

```env
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=123456789
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef
GITHUB_TOKEN=                         # اختیاری
```

#### ۳. اجرا

```bash
docker compose up -d --build
```

تمام! ربات آماده است.

---

## ⚙️ تنظیمات

| متغیر | اجباری | توضیح |
|-------|--------|-------|
| `BOT_TOKEN` | ✅ | توکن ربات از [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | ✅ | آیدی عددی تلگرام ادمین‌ها — برای چند نفر با کاما جدا کنید |
| `TELEGRAM_API_ID` | ✅ | از [my.telegram.org](https://my.telegram.org/apps) |
| `TELEGRAM_API_HASH` | ✅ | از [my.telegram.org](https://my.telegram.org/apps) |
| `GITHUB_TOKEN` | ❌ | توکن GitHub — rate limit را از ۶۰ به ۵۰۰۰ درخواست/ساعت می‌رساند |

> **دریافت GitHub Token (اختیاری اما توصیه‌شده)**
> ۱. به [github.com/settings/tokens](https://github.com/settings/tokens) بروید
> ۲. یک توکن **Classic** با scope ‏`public_repo` بسازید
> ۳. در فایل `.env` اضافه کنید

---

## 🏗 معماری

ربات از **Telegram Local Bot API Server** استفاده می‌کند که محدودیت ۵۰ مگابایت را برمی‌دارد و امکان دانلود فایل تا ۲ گیگابایت را فراهم می‌کند.

```
┌─────────────────────┐        ┌────────────────────────────┐
│   Telegram Cloud    │ ◄────► │   Local Bot API Server     │
└─────────────────────┘        │   (بدون محدودیت ۵۰ مگ)    │
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

### دستورات Docker

```bash
# اجرا و بیلد
docker compose up -d --build

# مشاهده لاگ زنده ربات
docker compose logs -f bot

# مشاهده لاگ Local API
docker compose logs -f telegram-bot-api

# وضعیت container ها
docker compose ps

# ری‌استارت ربات
docker compose restart bot

# توقف کامل
docker compose down
```

---

## 🤖 دستورات ربات

| دستور | دسترسی | توضیح |
|-------|---------|-------|
| `/start` | همه | پیام خوش‌آمدگویی |
| `/users` | ادمین | لیست تمام کاربران ربات |
| `/broadcast <پیام>` | ادمین | ارسال پیام به همه کاربران |
| لینک GitHub | همه | نمایش اطلاعات و منوی تعاملی ریپو |

---

## 📁 ساختار پروژه

```
GithubExplorer/
├── github_telegram_bot.py   # کد اصلی ربات
├── Dockerfile               # تعریف image کانتینر
├── docker-compose.yml       # تنظیمات سرویس‌ها
├── env.example              # قالب متغیرهای محیطی
├── install.sh               # اسکریپت نصب خودکار
├── README.md                # مستندات انگلیسی
├── README.fa.md             # مستندات فارسی
└── LICENSE                  # مجوز MIT
```

---

## 🤝 مشارکت

مشارکت شما خوش‌آمد است:

1. ریپو را **Fork** کنید
2. برنچ جدید بسازید: `git checkout -b feature/my-feature`
3. تغییرات را commit کنید: `git commit -m 'feat: add my feature'`
4. push کنید: `git push origin feature/my-feature`
5. یک **Pull Request** باز کنید

---

## 📬 ارتباط

<div align="center">

[![Telegram](https://img.shields.io/badge/Telegram-کانال-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/SchmitzWS)

ساخته شده با 🖤 توسط **[Schmitz](https://t.me/SchmitzWS)**

اگر مفید بود، یک ⭐ بزنید!

</div>
