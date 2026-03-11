#!/usr/bin/env bash
# ============================================================
#   🐙  GithubExplorer Bot — اسکریپت نصب خودکار
#   https://github.com/Schmi7zz/GithubExplorer
# ============================================================

set -e

# ── رنگ‌ها ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── توابع کمکی ───────────────────────────────────────────────
info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[✔]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[✘ ERROR]${RESET} $*" >&2; exit 1; }

header() {
  clear
  echo ""
  echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${RESET}"
  echo -e "${BOLD}${CYAN}║   🐙  GithubExplorer Bot — نصب خودکار           ║${RESET}"
  echo -e "${BOLD}${CYAN}║   github.com/Schmi7zz/GithubExplorer             ║${RESET}"
  echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${RESET}"
  echo ""
}

# ── نصب Docker روی Ubuntu/Debian ────────────────────────────
install_docker() {
  warn "Docker یافت نشد. در حال نصب خودکار (Ubuntu/Debian)..."
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER"
  success "Docker نصب شد. ممکن است برای اعمال تغییرات گروه، نیاز به logout/login داشته باشید."
}

# ── بررسی Docker ─────────────────────────────────────────────
check_docker() {
  if ! command -v docker &>/dev/null; then
    if command -v apt-get &>/dev/null; then
      install_docker
    else
      error "Docker یافت نشد. لطفاً به‌صورت دستی نصب کنید: https://docs.docker.com/get-docker/"
    fi
  else
    success "Docker یافت شد: $(docker --version)"
  fi

  # بررسی اجرا بودن Docker daemon
  if ! docker info &>/dev/null 2>&1; then
    warn "Docker daemon در حال اجرا نیست. در حال راه‌اندازی..."
    sudo systemctl start docker || error "نمیتوان Docker را راه‌اندازی کرد."
  fi
}

# ── بررسی Docker Compose ──────────────────────────────────────
check_compose() {
  if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    success "Docker Compose (plugin) یافت شد"
  elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
    success "docker-compose یافت شد: $(docker-compose --version)"
  else
    error "Docker Compose یافت نشد. لطفاً نصب کنید: https://docs.docker.com/compose/install/"
  fi
}

# ── دریافت ورودی اجباری ──────────────────────────────────────
prompt_required() {
  local var_name="$1"
  local prompt_msg="$2"
  local value=""
  while [[ -z "$value" ]]; do
    read -rp "  → $prompt_msg: " value
    if [[ -z "$value" ]]; then
      echo -e "  ${RED}این فیلد اجباری است.${RESET}"
    fi
  done
  eval "$var_name=\"$value\""
}

# ── دریافت ورودی اختیاری ─────────────────────────────────────
prompt_optional() {
  local var_name="$1"
  local prompt_msg="$2"
  local default="$3"
  read -rp "  → $prompt_msg [پیش‌فرض: ${default:-خالی}]: " value
  eval "$var_name=\"${value:-$default}\""
}

# ════════════════════════════════════════════════════════════
#   شروع اسکریپت
# ════════════════════════════════════════════════════════════
header

# ── مرحله ۱: بررسی وابستگی‌ها ───────────────────────────────
echo -e "${BOLD}[ مرحله ۱ / ۵ ]  بررسی وابستگی‌ها${RESET}"
echo "──────────────────────────────────────"

# بررسی git
if ! command -v git &>/dev/null; then
  warn "git یافت نشد. در حال نصب..."
  sudo apt-get update -y && sudo apt-get install -y git
fi
success "git یافت شد"

check_docker
check_compose
echo ""

# ── مرحله ۲: کلون یا استفاده از پوشه موجود ─────────────────
echo -e "${BOLD}[ مرحله ۲ / ۵ ]  آماده‌سازی سورس کد${RESET}"
echo "──────────────────────────────────────"

INSTALL_DIR="${INSTALL_DIR:-$HOME/GithubExplorer}"

if [[ -f "$INSTALL_DIR/github_telegram_bot.py" ]]; then
  warn "پوشه $INSTALL_DIR از قبل وجود دارد."
  read -rp "  آیا می‌خواهید آن را آپدیت (git pull) کنید؟ (y/N): " do_pull
  if [[ "$do_pull" =~ ^[Yy]$ ]]; then
    cd "$INSTALL_DIR"
    git pull origin main && success "کد به‌روز شد" \
      || warn "آپدیت با مشکل مواجه شد، از نسخه موجود استفاده می‌شود."
  fi
else
  info "در حال کلون کردن مخزن در $INSTALL_DIR ..."
  git clone https://github.com/Schmi7zz/GithubExplorer.git "$INSTALL_DIR" \
    || error "کلون کردن با خطا مواجه شد. اتصال اینترنت را بررسی کنید."
  success "سورس کد دانلود شد"
fi

cd "$INSTALL_DIR"
echo ""

# ── مرحله ۳: پیکربندی متغیرهای محیطی ───────────────────────
echo -e "${BOLD}[ مرحله ۳ / ۵ ]  پیکربندی .env${RESET}"
echo "──────────────────────────────────────"

skip_env=false
if [[ -f ".env" ]]; then
  warn "فایل .env از قبل وجود دارد."
  read -rp "  آیا می‌خواهید آن را بازنویسی کنید؟ (y/N): " overwrite_env
  if [[ ! "$overwrite_env" =~ ^[Yy]$ ]]; then
    info "از .env موجود استفاده می‌شود."
    skip_env=true
  fi
fi

if [[ "$skip_env" == "false" ]]; then
  echo ""
  echo -e "  ${CYAN}اطلاعات زیر را وارد کنید:${RESET}"
  echo ""

  # --- BOT_TOKEN ---
  echo -e "  ${BOLD}🤖 توکن ربات تلگرام${RESET}"
  echo -e "  ${YELLOW}از @BotFather دریافت کنید${RESET}"
  prompt_required BOT_TOKEN "BOT_TOKEN"
  echo ""

  # --- ADMIN_IDS ---
  echo -e "  ${BOLD}👤 آیدی عددی تلگرام ادمین(ها)${RESET}"
  echo -e "  ${YELLOW}برای چند نفر با کاما جدا کنید: 12345,67890${RESET}"
  echo -e "  ${YELLOW}آیدی خود را از @userinfobot دریافت کنید${RESET}"
  prompt_required ADMIN_IDS "ADMIN_IDS"
  echo ""

  # --- TELEGRAM_API_ID ---
  echo -e "  ${BOLD}🔑 Telegram API ID${RESET}"
  echo -e "  ${YELLOW}از my.telegram.org/apps دریافت کنید${RESET}"
  prompt_required TELEGRAM_API_ID "TELEGRAM_API_ID"
  echo ""

  # --- TELEGRAM_API_HASH ---
  echo -e "  ${BOLD}🔑 Telegram API HASH${RESET}"
  echo -e "  ${YELLOW}از my.telegram.org/apps دریافت کنید${RESET}"
  prompt_required TELEGRAM_API_HASH "TELEGRAM_API_HASH"
  echo ""

  # --- GITHUB_TOKEN (اختیاری) ---
  echo -e "  ${BOLD}🐙 GitHub Personal Access Token${RESET} ${YELLOW}(اختیاری)${RESET}"
  echo -e "  ${YELLOW}rate limit را از ۶۰ به ۵۰۰۰ در ساعت افزایش می‌دهد${RESET}"
  echo -e "  ${YELLOW}ساخت از: github.com/settings/tokens  →  scope: public_repo${RESET}"
  prompt_optional GITHUB_TOKEN "GITHUB_TOKEN" ""
  echo ""

  # ── نوشتن .env ──────────────────────────────────────────────
  cat > .env <<EOF
# ── تنظیمات ربات تلگرام ──────────────────────────────────────
# توکن ربات از @BotFather
BOT_TOKEN=${BOT_TOKEN}

# آیدی عددی ادمین‌ها (با کاما جدا کنید)
ADMIN_IDS=${ADMIN_IDS}

# اطلاعات API تلگرام از my.telegram.org
TELEGRAM_API_ID=${TELEGRAM_API_ID}
TELEGRAM_API_HASH=${TELEGRAM_API_HASH}

# ── GitHub Token (اختیاری) ───────────────────────────────────
# نرخ درخواست را از ۶۰ به ۵۰۰۰ در ساعت افزایش می‌دهد
GITHUB_TOKEN=${GITHUB_TOKEN}
EOF

  success "فایل .env با موفقیت ساخته شد"
fi
echo ""

# ── مرحله ۴: بیلد و اجرا ────────────────────────────────────
echo -e "${BOLD}[ مرحله ۴ / ۵ ]  بیلد و اجرای Docker${RESET}"
echo "──────────────────────────────────────"
info "در حال بیلد image و راه‌اندازی container ها..."
echo ""

$COMPOSE_CMD up -d --build

echo ""
success "Container ها راه‌اندازی شدند"
echo ""

# ── مرحله ۵: بررسی وضعیت نهایی ─────────────────────────────
echo -e "${BOLD}[ مرحله ۵ / ۵ ]  بررسی وضعیت${RESET}"
echo "──────────────────────────────────────"
sleep 4

$COMPOSE_CMD ps
echo ""

# بررسی سلامت container ربات
if $COMPOSE_CMD ps | grep -q "github_bot.*Up"; then
  success "container ربات در حال اجراست ✅"
elif $COMPOSE_CMD ps | grep -q "github_bot"; then
  warn "container ربات راه‌اندازی شد اما وضعیت نامشخص است."
  warn "لاگ را بررسی کنید: $COMPOSE_CMD logs -f bot"
else
  warn "نمی‌توان وضعیت container را تشخیص داد. لاگ را بررسی کنید."
fi

# ── خلاصه نهایی ─────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${GREEN}║   🎉  نصب با موفقیت انجام شد!                  ║${RESET}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${BOLD}📁 محل نصب:${RESET}  $INSTALL_DIR"
echo ""
echo -e "  ${BOLD}${YELLOW}⚠️  برای اجرای دستورات، ابتدا وارد پوشه پروژه شوید:${RESET}"
echo -e "  ${CYAN}cd $INSTALL_DIR${RESET}"
echo ""
echo -e "  ${BOLD}دستورات مفید:${RESET}"
echo -e "  ${CYAN}$COMPOSE_CMD logs -f bot${RESET}               # لاگ زنده ربات"
echo -e "  ${CYAN}$COMPOSE_CMD logs -f telegram-bot-api${RESET}  # لاگ Local API Server"
echo -e "  ${CYAN}$COMPOSE_CMD ps${RESET}                        # وضعیت container ها"
echo -e "  ${CYAN}$COMPOSE_CMD restart bot${RESET}               # ری‌استارت ربات"
echo -e "  ${CYAN}$COMPOSE_CMD down${RESET}                      # توقف همه سرویس‌ها"
echo -e "  ${CYAN}$COMPOSE_CMD up -d --build${RESET}             # اعمال تغییرات کد"
echo ""
echo -e "  ${BOLD}دستورات ادمین در ربات:${RESET}"
echo -e "  ${CYAN}/start${RESET}                  # پیام خوش‌آمدگویی"
echo -e "  ${CYAN}/users${RESET}                  # لیست کاربران (فقط ادمین)"
echo -e "  ${CYAN}/broadcast <پیام>${RESET}       # ارسال همگانی (فقط ادمین)"
echo ""
echo -e "  ${YELLOW}💡 یک لینک GitHub برای ربات ارسال کنید تا شروع به کار کند!${RESET}"
echo -e "  ${YELLOW}   مثال: https://github.com/torvalds/linux${RESET}"
echo ""

# ── رفتن به پوشه پروژه در پایان ─────────────────────────────
echo -e "${BOLD}در حال انتقال به پوشه پروژه...${RESET}"
cd "$INSTALL_DIR"
exec $SHELL
