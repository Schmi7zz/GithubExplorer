#!/usr/bin/env bash
# ============================================================
#   GithubExplorer Bot -- Automated Install Script
#   https://github.com/Schmi7zz/GithubExplorer
# ============================================================

set -e

# ── Colors ───────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Helpers ───────────────────────────────────────────────────
info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }

header() {
  clear
  echo ""
  echo -e "${BOLD}${CYAN}=====================================================${RESET}"
  echo -e "${BOLD}${CYAN}   GithubExplorer Bot -- Auto Installer              ${RESET}"
  echo -e "${BOLD}${CYAN}   github.com/Schmi7zz/GithubExplorer                ${RESET}"
  echo -e "${BOLD}${CYAN}=====================================================${RESET}"
  echo ""
}

# ── Install Docker (Ubuntu/Debian) ───────────────────────────
install_docker() {
  warn "Docker not found. Installing automatically (Ubuntu/Debian)..."
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
  success "Docker installed. You may need to logout/login for group changes to apply."
}

# ── Check Docker ─────────────────────────────────────────────
check_docker() {
  if ! command -v docker &>/dev/null; then
    if command -v apt-get &>/dev/null; then
      install_docker
    else
      error "Docker not found. Please install it manually: https://docs.docker.com/get-docker/"
    fi
  else
    success "Docker found: $(docker --version)"
  fi

  if ! docker info &>/dev/null 2>&1; then
    warn "Docker daemon is not running. Starting it..."
    sudo systemctl start docker || error "Failed to start Docker."
  fi
}

# ── Check Docker Compose ─────────────────────────────────────
check_compose() {
  if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    success "Docker Compose (plugin) found"
  elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
    success "docker-compose found: $(docker-compose --version)"
  else
    error "Docker Compose not found. Install it: https://docs.docker.com/compose/install/"
  fi
}

# ── Required input ───────────────────────────────────────────
prompt_required() {
  local var_name="$1"
  local prompt_msg="$2"
  local value=""
  while [[ -z "$value" ]]; do
    read -rp "  -> $prompt_msg: " value
    if [[ -z "$value" ]]; then
      echo -e "  ${RED}This field is required.${RESET}"
    fi
  done
  eval "$var_name=\"$value\""
}

# ── Optional input ───────────────────────────────────────────
prompt_optional() {
  local var_name="$1"
  local prompt_msg="$2"
  local default="$3"
  read -rp "  -> $prompt_msg [default: ${default:-empty}]: " value
  eval "$var_name=\"${value:-$default}\""
}

# ════════════════════════════════════════════════════════════
#   Main
# ════════════════════════════════════════════════════════════
header

# ── Step 1: Dependencies ─────────────────────────────────────
echo -e "${BOLD}[ Step 1 / 5 ]  Checking dependencies${RESET}"
echo "-----------------------------------------------------"

if ! command -v git &>/dev/null; then
  warn "git not found. Installing..."
  sudo apt-get update -y && sudo apt-get install -y git
fi
success "git found"

check_docker
check_compose
echo ""

# ── Step 2: Source code ──────────────────────────────────────
echo -e "${BOLD}[ Step 2 / 5 ]  Preparing source code${RESET}"
echo "-----------------------------------------------------"

INSTALL_DIR="${INSTALL_DIR:-$HOME/GithubExplorer}"

if [[ -f "$INSTALL_DIR/github_telegram_bot.py" ]]; then
  warn "Directory $INSTALL_DIR already exists."
  read -rp "  Update it with git pull? (y/N): " do_pull
  if [[ "$do_pull" =~ ^[Yy]$ ]]; then
    cd "$INSTALL_DIR"
    git pull origin main && success "Code updated." \
      || warn "git pull failed. Using existing code."
  fi
else
  info "Cloning repository into $INSTALL_DIR ..."
  git clone https://github.com/Schmi7zz/GithubExplorer.git "$INSTALL_DIR" \
    || error "Clone failed. Check your internet connection."
  success "Source code downloaded."
fi

cd "$INSTALL_DIR"
echo ""

# ── Step 3: Environment configuration ───────────────────────
echo -e "${BOLD}[ Step 3 / 5 ]  Configuring .env${RESET}"
echo "-----------------------------------------------------"

skip_env=false
if [[ -f ".env" ]]; then
  warn ".env file already exists."
  read -rp "  Overwrite it? (y/N): " overwrite_env
  if [[ ! "$overwrite_env" =~ ^[Yy]$ ]]; then
    info "Using existing .env file."
    skip_env=true
  fi
fi

if [[ "$skip_env" == "false" ]]; then
  echo ""
  echo -e "  ${CYAN}Please enter your credentials:${RESET}"
  echo ""

  echo -e "  ${BOLD}[1] Telegram Bot Token${RESET}"
  echo -e "  ${YELLOW}Get it from @BotFather on Telegram${RESET}"
  prompt_required BOT_TOKEN "BOT_TOKEN"
  echo ""

  echo -e "  ${BOLD}[2] Admin Telegram User ID(s)${RESET}"
  echo -e "  ${YELLOW}Separate multiple IDs with commas: 12345,67890${RESET}"
  echo -e "  ${YELLOW}Find your ID via @userinfobot on Telegram${RESET}"
  prompt_required ADMIN_IDS "ADMIN_IDS"
  echo ""

  echo -e "  ${BOLD}[3] Telegram API ID${RESET}"
  echo -e "  ${YELLOW}Get it from https://my.telegram.org/apps${RESET}"
  prompt_required TELEGRAM_API_ID "TELEGRAM_API_ID"
  echo ""

  echo -e "  ${BOLD}[4] Telegram API HASH${RESET}"
  echo -e "  ${YELLOW}Get it from https://my.telegram.org/apps${RESET}"
  prompt_required TELEGRAM_API_HASH "TELEGRAM_API_HASH"
  echo ""

  echo -e "  ${BOLD}[5] GitHub Personal Access Token${RESET} ${YELLOW}(optional)${RESET}"
  echo -e "  ${YELLOW}Raises API rate limit from 60 to 5000 req/hr${RESET}"
  echo -e "  ${YELLOW}Create at: github.com/settings/tokens  ->  scope: public_repo${RESET}"
  prompt_optional GITHUB_TOKEN "GITHUB_TOKEN" ""
  echo ""

  cat > .env <<EOF
# Telegram Bot Token (from @BotFather)
BOT_TOKEN=${BOT_TOKEN}

# Admin Telegram user IDs (comma-separated)
ADMIN_IDS=${ADMIN_IDS}

# Telegram API credentials (from https://my.telegram.org/apps)
TELEGRAM_API_ID=${TELEGRAM_API_ID}
TELEGRAM_API_HASH=${TELEGRAM_API_HASH}

# GitHub Personal Access Token (optional — raises rate limit to 5000 req/hr)
GITHUB_TOKEN=${GITHUB_TOKEN}
EOF

  success ".env file created successfully."
fi
echo ""

# ── Step 4: Build & Launch ───────────────────────────────────
echo -e "${BOLD}[ Step 4 / 5 ]  Building and launching Docker containers${RESET}"
echo "-----------------------------------------------------"
info "Building image and starting containers..."
echo ""

$COMPOSE_CMD up -d --build

echo ""
success "Containers started."
echo ""

# ── Step 5: Status check ─────────────────────────────────────
echo -e "${BOLD}[ Step 5 / 5 ]  Status check${RESET}"
echo "-----------------------------------------------------"
sleep 4

$COMPOSE_CMD ps
echo ""

if $COMPOSE_CMD ps | grep -q "github_bot.*Up"; then
  success "Bot container is running."
else
  warn "Could not confirm bot status. Check logs: $COMPOSE_CMD logs -f bot"
fi

# ── Summary ──────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}=====================================================${RESET}"
echo -e "${BOLD}${GREEN}   Installation complete!                            ${RESET}"
echo -e "${BOLD}${GREEN}=====================================================${RESET}"
echo ""
echo -e "  ${BOLD}Install directory:${RESET}  $INSTALL_DIR"
echo ""
echo -e "  ${BOLD}${YELLOW}NOTE: Run all commands from the project directory:${RESET}"
echo -e "  ${CYAN}cd $INSTALL_DIR${RESET}"
echo ""
echo -e "  ${BOLD}Useful commands:${RESET}"
echo -e "  ${CYAN}$COMPOSE_CMD logs -f bot${RESET}               # Live bot logs"
echo -e "  ${CYAN}$COMPOSE_CMD logs -f telegram-bot-api${RESET}  # Live Local API logs"
echo -e "  ${CYAN}$COMPOSE_CMD ps${RESET}                        # Container status"
echo -e "  ${CYAN}$COMPOSE_CMD restart bot${RESET}               # Restart the bot"
echo -e "  ${CYAN}$COMPOSE_CMD down${RESET}                      # Stop all services"
echo -e "  ${CYAN}$COMPOSE_CMD up -d --build${RESET}             # Rebuild after code changes"
echo ""
echo -e "  ${BOLD}Bot admin commands:${RESET}"
echo -e "  ${CYAN}/start${RESET}                   Welcome message"
echo -e "  ${CYAN}/users${RESET}                   List all bot users (admin only)"
echo -e "  ${CYAN}/broadcast <message>${RESET}     Send message to all users (admin only)"
echo ""
echo -e "  ${YELLOW}Send any GitHub URL to the bot to start exploring!${RESET}"
echo -e "  ${YELLOW}Example: https://github.com/torvalds/linux${RESET}"
echo ""

cd "$INSTALL_DIR"
exec $SHELL
