<div align="center">

<img src="logo.png" width="150" alt="GitHub Explorer Bot">

# 🐙 GitHub Explorer Bot

**ربات تلگرامی قدرتمند برای کاوش ریپازیتوری‌های گیتهاب — مستقیم از چت تلگرام**

مرور فایل‌ها، دانلود ریلیزها، مشاهده README، بررسی آمار — بدون خروج از تلگرام.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4.svg?logo=telegram)](https://t.me/SchmitzWS)

---

[امکانات](#-امکانات) • [دمو](#-دمو) • [شروع سریع](#-شروع-سریع) • [تنظیمات](#-تنظیمات) • [دیپلوی](#-دیپلوی) • [کانال تلگرام](https://t.me/SchmitzWS)

**[🇬🇧 English](README.md)**

</div>

---

## ✨ امکانات

| قابلیت | توضیحات |
|--------|---------|
| 📁 **مرور فایل‌ها** | پیمایش فایل‌ها و پوشه‌های ریپو با صفحه‌بندی |
| 🏷 **ریلیزها** | مشاهده ریلیزها، فایل‌ها، تعداد دانلود — و دانلود مستقیم |
| 🌿 **برنچ‌ها** | لیست تمام برنچ‌های ریپازیتوری |
| 📝 **نمایش README** | خواندن README بدون خروج از تلگرام |
| 👥 **مشارکت‌کنندگان** | لیست افرادی که در پروژه مشارکت داشتن |
| 📊 **آمار زبان‌ها** | نمودار بصری زبان‌های استفاده شده |
| ⬇️ **دانلود سورس** | دانلود کل ریپازیتوری به صورت ZIP |
| 📢 **اطلاع‌رسانی** | ارسال پیام به همه کاربران (ادمین) |
| 👤 **مدیریت کاربران** | مشاهده لیست کاربران با `/users` (ادمین) |
| 🚀 **فایل‌های حجیم** | پشتیبانی از فایل تا **۲ گیگابایت** با Local Bot API |

---

## 🎬 دمو

کافیه لینک هر ریپوی گیتهاب رو به ربات بفرستی:

```
https://github.com/torvalds/linux
```

ربات فوراً اطلاعات ریپو رو با دکمه‌های تعاملی نشون میده:

```
🐙 torvalds/linux

The Linux kernel source tree

⭐️ Stars: 195,000    🍴 Forks: 55,000
👁 Watchers: 8,000    🐛 Issues: 350
💾 Size: 4.8 GB       🌿 Branch: master
🛠 Language: C         📜 License: GPL-2.0

[ 📁 فایل‌ها ] [ 🏷 ریلیزها ]
[ 🌿 برنچ‌ها ] [ 📝 README ]
[ 👥 مشارکت‌کنندگان ] [ 📊 زبان‌ها ]
[ ⬇️ دانلود ZIP ]
```

---

## 🚀 شروع سریع

### پیش‌نیازها

- Docker و Docker Compose
- توکن ربات تلگرام از [@BotFather](https://t.me/BotFather)
- اطلاعات API تلگرام از [my.telegram.org](https://my.telegram.org)

### ۱. کلون کردن ریپازیتوری

```bash
git clone https://github.com/Schmi7zz/github-explorer-bot.git
cd github-explorer-bot
```

### ۲. تنظیم محیط

```bash
cp .env.example .env
nano .env
```

اطلاعاتت رو وارد کن:

```env
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=آیدی_عددی_تلگرامت
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef
```

### ۳. اجرا

```bash
docker-compose up -d --build
```

تمام! یه لینک گیتهاب به ربات بفرست و شروع کن.

---

## ⚙️ تنظیمات

| متغیر | الزامی | توضیحات |
|--------|--------|---------|
| `BOT_TOKEN` | ✅ | توکن ربات از @BotFather |
| `ADMIN_IDS` | ✅ | آیدی عددی تلگرام ادمین‌ها (با کاما جدا کن) |
| `TELEGRAM_API_ID` | ✅ | از [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_API_HASH` | ✅ | از [my.telegram.org](https://my.telegram.org) |
| `GITHUB_TOKEN` | ❌ | توکن گیتهاب — محدودیت API رو از ۶۰ به ۵۰۰۰ درخواست/ساعت میبره |

### گرفتن توکن گیتهاب (اختیاری ولی پیشنهادی)

1. برو به [github.com/settings/tokens](https://github.com/settings/tokens)
2. یه توکن **classic** با دسترسی `public_repo` بساز
3. توی فایل `.env` اضافه‌ش کن

---

## 🐳 دیپلوی

### معماری

```
┌─────────────────┐     ┌──────────────────────┐
│  Telegram Cloud  │◄───►│  Local Bot API Server │
└─────────────────┘     │  (بدون محدودیت ۵۰MB)  │
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

ربات از **Telegram Local Bot API Server** استفاده می‌کنه که محدودیت ۵۰ مگابایت آپلود رو برمیداره و اجازه دانلود تا ~۲ گیگابایت رو میده.

### دستورات

```bash
# شروع
docker-compose up -d --build

# مشاهده لاگ
docker-compose logs -f bot

# توقف
docker-compose down

# بازسازی بعد از تغییر کد
docker-compose up -d --build
```

### دستورات ادمین

| دستور | توضیحات |
|-------|---------|
| `/start` | پیام خوش‌آمد (همه کاربران) |
| `/users` | لیست کاربران ربات (فقط ادمین) |
| `/broadcast <پیام>` | ارسال پیام به همه کاربران (فقط ادمین) |

---

## 🏗 ساختار پروژه

```
github-explorer-bot/
├── github_telegram_bot.py   # کد اصلی ربات
├── Dockerfile               # ایمیج کانتینر
├── docker-compose.yml       # مدیریت سرویس‌ها
├── .env.example             # قالب محیط
├── .gitignore
├── LICENSE
├── README.md                # مستندات انگلیسی
└── README.fa.md             # مستندات فارسی
```

---

## 🤝 مشارکت

مشارکت شما خوش‌آمده! کافیه:

1. ریپو رو Fork کنی
2. یه برنچ بسازی (`git checkout -b feature/amazing`)
3. تغییراتت رو کامیت کنی (`git commit -m 'Add amazing feature'`)
4. پوش کنی (`git push origin feature/amazing`)
5. Pull Request باز کنی

---

## 📬 ارتباط

<div align="center">

[![Telegram Channel](https://img.shields.io/badge/Telegram-کانال-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/SchmitzWS)

**ساخته شده با 🖤 توسط [Schmitz](https://t.me/SchmitzWS)**

</div>

---

<div align="center">

اگه به دردت خورد، یه ⭐ بزن

</div>
