import os
import re
import json
import logging
import asyncio
import base64
import zipfile
from io import BytesIO
from datetime import datetime

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatAction

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
API_BASE = "https://api.github.com"
PER_PAGE = 7
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
USERS_FILE = "data/bot_users.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def track_user(user):
    users = load_users()
    uid = str(user.id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if uid not in users:
        users[uid] = {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "joined": now,
            "last_seen": now,
        }
    else:
        users[uid]["last_seen"] = now
        users[uid]["first_name"] = user.first_name or ""
        users[uid]["last_name"] = user.last_name or ""
        users[uid]["username"] = user.username or ""
    save_users(users)


def github_headers():
    h = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = "token " + GITHUB_TOKEN
    return h


def parse_github_url(url):
    url = url.strip().rstrip("/")
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url)
    if m:
        return m.group(1), m.group(2).replace(".git", "")
    return None, None


def short(text, maxlen=300):
    if len(text) > maxlen:
        return text[:maxlen] + "..."
    return text


def clean_html(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text


def size_fmt(num):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num) < 1024:
            return "{:.1f} {}".format(num, unit)
        num /= 1024
    return "{:.1f} TB".format(num)


async def api_get(session, endpoint, params=None):
    url = API_BASE + endpoint if endpoint.startswith("/") else endpoint
    async with session.get(url, headers=github_headers(), params=params) as r:
        if r.status == 200:
            return await r.json()
        return None


async def api_download(session, url):
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = "token " + GITHUB_TOKEN
    async with session.get(url, headers=headers) as r:
        if r.status == 200:
            return await r.read()
    return None


def store_cb(ctx, action, **kwargs):
    if "cb_store" not in ctx.user_data:
        ctx.user_data["cb_store"] = {}
        ctx.user_data["cb_counter"] = 0
    ctx.user_data["cb_counter"] += 1
    key = str(ctx.user_data["cb_counter"])
    d = {"action": action}
    d.update(kwargs)
    ctx.user_data["cb_store"][key] = d
    return "s:" + key


def get_cb(ctx, data):
    if data.startswith("s:"):
        key = data[2:]
        store = ctx.user_data.get("cb_store", {})
        return store.get(key, {})
    return {}


MAX_TG_SIZE = 1900 * 1024 * 1024


async def send_file(msg, data, filename, caption, reply_markup=None):
    if not data:
        return
    if len(data) <= MAX_TG_SIZE:
        doc = BytesIO(data)
        doc.name = filename
        await msg.reply_document(
            document=InputFile(doc, filename=filename),
            caption=caption + f"\n⚖️ Size: {size_fmt(len(data))}",
            reply_markup=reply_markup
        )
    else:
        await msg.reply_text(
            f"⚠️ File too large ({size_fmt(len(data))}).",
            reply_markup=reply_markup
        )


def mm_btn(ctx, o, r):
    return InlineKeyboardButton(
        "🏠 Main Menu",
        callback_data=store_cb(ctx, "main", owner=o, repo=r))


def bk_btn(ctx, act, lbl, **kw):
    return InlineKeyboardButton(lbl, callback_data=store_cb(ctx, act, **kw))


async def cmd_start(update, ctx):
    track_user(update.effective_user)
    t = (
        "╭───────────────────╮\n"
        "│    <b>🐙 GitHub Explorer</b>    │\n"
        "╰───────────────────╯\n\n"
        "🔍 <b>Explore any GitHub repository</b>\n\n"
        "📌 Just send a repo link:\n"
        "<code>https://github.com/owner/repo</code>\n\n"
        "⚡️ <b>Features:</b>\n"
        "├ 📁 Browse files & folders\n"
        "├ 🏷 View & download releases\n"
        "├ 🌿 List branches\n"
        "├ 📝 Show README\n"
        "├ 👥 Contributors\n"
        "├ 📊 Language stats\n"
        "╰ ⬇️ Download source code\n"
    )
    await update.message.reply_text(t, parse_mode=ParseMode.HTML)


async def cmd_users(update, ctx):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("access denied")
        return
    users = load_users()
    total = len(users)
    if total == 0:
        await update.message.reply_text("no users yet")
        return

    t = "<b>👥 Users</b>\n\n"
    t += "📊 Total: <b>" + str(total) + "</b>\n\n"
    su = sorted(users.values(), key=lambda x: x.get("last_seen", ""), reverse=True)

    for i, u in enumerate(su[:50], 1):
        nm = clean_html(u.get("first_name", ""))
        if u.get("last_name"):
            nm += " " + clean_html(u["last_name"])
        un = "@" + clean_html(u["username"]) if u.get("username") else "-"
        entry = "<b>" + str(i) + ".</b> " + nm + "\n"
        entry += "    🆔 <code>" + str(u.get("id", "")) + "</code> | " + un + "\n"
        entry += "    📅 " + u.get("joined", "?") + "\n"
        entry += "    👁 " + u.get("last_seen", "?") + "\n\n"

        if len(t) + len(entry) > 4000:
            await update.message.reply_text(t, parse_mode=ParseMode.HTML)
            t = ""
        t += entry

    if total > 50:
        t += "... +" + str(total - 50) + " more"
    if t.strip():
        await update.message.reply_text(t, parse_mode=ParseMode.HTML)


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access denied.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "<code>/broadcast your message here</code>",
            parse_mode='HTML'
        )
        return

    custom_msg = " ".join(context.args)

    users = load_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    count = 0
    status_msg = await update.message.reply_text(f"⏳ Sending to {len(users)} users...")

    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=custom_msg,
                parse_mode='HTML'
            )
            count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Error sending to {uid}: {e}")

    await status_msg.edit_text(f"✅ Message sent to {count} users.")


async def send_main_menu(tgt, ctx, o, r, edit=False):
    async with aiohttp.ClientSession() as s:
        info = await api_get(s, "/repos/" + o + "/" + r)
    if not info:
        tx = "not found"
        if edit:
            try:
                await tgt.edit_message_text(tx)
            except Exception:
                await tgt.message.reply_text(tx)
        else:
            await tgt.reply_text(tx)
        return
    ctx.user_data["owner"] = o
    ctx.user_data["repo"] = r
    st = info.get("stargazers_count", 0)
    fk = info.get("forks_count", 0)
    wt = info.get("subscribers_count", 0)
    ln = info.get("language") or "-"
    lc = (info.get("license") or {}).get("spdx_id", "-")
    ds = clean_html(info.get("description") or "-")
    sz = size_fmt(info.get("size", 0) * 1024)
    br = info.get("default_branch", "main")
    iss = info.get("open_issues_count", 0)
    tp = ", ".join(info.get("topics", [])) or "-"
    tx = "<b>🐙 " + o + "/" + r + "</b>\n\n"
    tx += short(ds) + "\n\n"
    tx += "⭐️ Stars: <b>" + "{:,}".format(st) + "</b>\n"
    tx += "🍴 Forks: <b>" + "{:,}".format(fk) + "</b>\n"
    tx += "👁 Watchers: <b>" + "{:,}".format(wt) + "</b>\n"
    tx += "🐛 Issues: <b>" + "{:,}".format(iss) + "</b>\n"
    tx += "💾 Size: <b>" + sz + "</b>\n"
    tx += "🌿 Branch: <code>" + br + "</code>\n"
    tx += "🛠 Language: <b>" + ln + "</b>\n"
    tx += "📜 License: <b>" + lc + "</b>\n"
    tx += "🏷 Topics: " + tp
    kb = [
        [
            InlineKeyboardButton(
                "📁 Files",
                callback_data=store_cb(ctx, "files", owner=o, repo=r, page=0, path="")),
            InlineKeyboardButton(
                "🏷 Releases",
                callback_data=store_cb(ctx, "rels", owner=o, repo=r, page=0)),
        ],
        [
            InlineKeyboardButton(
                "🌿 Branches",
                callback_data=store_cb(ctx, "brnch", owner=o, repo=r)),
            InlineKeyboardButton(
                "📝 README",
                callback_data=store_cb(ctx, "readm", owner=o, repo=r)),
        ],
        [
            InlineKeyboardButton(
                "👥 Contributors",
                callback_data=store_cb(ctx, "contr", owner=o, repo=r, page=0)),
            InlineKeyboardButton(
                "📊 Languages",
                callback_data=store_cb(ctx, "langs", owner=o, repo=r)),
        ],
        [
            InlineKeyboardButton(
                "⬇️ Download ZIP",
                callback_data=store_cb(ctx, "dlzip", owner=o, repo=r)),
        ],
    ]
    if edit:
        try:
            await tgt.edit_message_text(tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        except Exception:
            await tgt.message.reply_text(tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await tgt.reply_text(tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def handle_link(update, ctx):
    track_user(update.effective_user)
    url = update.message.text.strip()
    o, r = parse_github_url(url)
    if not o:
        await update.message.reply_text("invalid link")
        return
    await update.message.chat.send_action(ChatAction.TYPING)
    await send_main_menu(update.message, ctx, o, r, edit=False)


async def safe_edit(q, text, parse_mode=None, reply_markup=None, disable_web_page_preview=False):
    kw = {}
    if parse_mode:
        kw["parse_mode"] = parse_mode
    if reply_markup:
        kw["reply_markup"] = reply_markup
    if disable_web_page_preview:
        kw["disable_web_page_preview"] = True
    try:
        await q.edit_message_text(text, **kw)
    except Exception:
        await q.message.reply_text(text, **kw)


async def on_callback(update, ctx):
    q = update.callback_query
    await q.answer()
    p = get_cb(ctx, q.data)
    a = p.get("action", "")
    o = p.get("owner", ctx.user_data.get("owner", ""))
    r = p.get("repo", ctx.user_data.get("repo", ""))
    if a == "main":
        is_doc = q.message and q.message.document
        if is_doc:
            await send_main_menu(q.message, ctx, o, r, edit=False)
        else:
            await send_main_menu(q, ctx, o, r, edit=True)
    elif a == "noop":
        pass
    elif a == "files":
        await show_files(q, ctx, o, r, p.get("path", ""), p.get("page", 0))
    elif a == "rels":
        await show_releases(q, ctx, o, r, p.get("page", 0))
    elif a == "brnch":
        await show_branches(q, ctx, o, r)
    elif a == "readm":
        await show_readme(q, ctx, o, r)
    elif a == "contr":
        await show_contributors(q, ctx, o, r, p.get("page", 0))
    elif a == "langs":
        await show_languages(q, ctx, o, r)
    elif a == "dlzip":
        await download_zip(q, ctx, o, r)
    elif a == "dlf":
        await download_file(q, ctx, o, r, p.get("path", ""))
    elif a == "reld":
        await release_detail(q, ctx, o, r, p.get("idx", 0))
    elif a == "dlra":
        await dl_release_asset(q, ctx, o, r, p.get("asset_idx", ""), p.get("rel_idx", 0))
    elif a == "relassets":
        await release_assets_page(q, ctx, o, r, p.get("rel_idx", 0), p.get("page", 0))


async def show_files(q, ctx, o, r, path, page):
    async with aiohttp.ClientSession() as s:
        items = await api_get(s, "/repos/" + o + "/" + r + "/contents/" + path)
    if not items or not isinstance(items, list):
        await safe_edit(q, "error", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    dirs = sorted([i for i in items if i["type"] == "dir"], key=lambda x: x["name"])
    fls = sorted([i for i in items if i["type"] != "dir"], key=lambda x: x["name"])
    al = dirs + fls
    tp = max(1, (len(al) + PER_PAGE - 1) // PER_PAGE)
    page = max(0, min(page, tp - 1))
    st = page * PER_PAGE
    ch = al[st:st + PER_PAGE]
    btns = []
    for it in ch:
        if it["type"] == "dir":
            btns.append([InlineKeyboardButton(
                "📁 " + it["name"],
                callback_data=store_cb(ctx, "files", owner=o, repo=r, path=it["path"], page=0))])
        else:
            btns.append([InlineKeyboardButton(
                "📄 " + it["name"] + " (" + size_fmt(it.get("size", 0)) + ")",
                callback_data=store_cb(ctx, "dlf", owner=o, repo=r, path=it["path"]))])
    if tp > 1:
        nv = []
        if page > 0:
            nv.append(InlineKeyboardButton(
                "◀️",
                callback_data=store_cb(ctx, "files", owner=o, repo=r, path=path, page=page - 1)))
        nv.append(InlineKeyboardButton(
            str(page + 1) + "/" + str(tp),
            callback_data=store_cb(ctx, "noop")))
        if page < tp - 1:
            nv.append(InlineKeyboardButton(
                "▶️",
                callback_data=store_cb(ctx, "files", owner=o, repo=r, path=path, page=page + 1)))
        btns.append(nv)
    nr = []
    if path:
        pr = "/".join(path.split("/")[:-1])
        nr.append(bk_btn(ctx, "files", "🔙", owner=o, repo=r, path=pr, page=0))
    nr.append(mm_btn(ctx, o, r))
    btns.append(nr)
    tx = "<b>📁 " + o + "/" + r + "</b>\n<code>/" + (path or ".") + "</code>\n" + str(len(al)) + " items"
    await safe_edit(q, tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btns))


async def download_file(q, ctx, o, r, path):
    await safe_edit(q, "downloading " + path + " ...")
    async with aiohttp.ClientSession() as s:
        info = await api_get(s, "/repos/" + o + "/" + r + "/contents/" + path)
        if not info or "download_url" not in info:
            await safe_edit(q, "error", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
            return
        data = await api_download(s, info["download_url"])
    if not data:
        await safe_edit(q, "failed", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    fn = path.split("/")[-1]
    pr = "/".join(path.split("/")[:-1])
    btns = [[bk_btn(ctx, "files", "🔙", owner=o, repo=r, path=pr, page=0), mm_btn(ctx, o, r)]]
    await send_file(q.message, data, fn, path, reply_markup=InlineKeyboardMarkup(btns))


async def show_releases(q, ctx, o, r, page):
    async with aiohttp.ClientSession() as s:
        rels = await api_get(s, "/repos/" + o + "/" + r + "/releases", params={"per_page": 100})
    if not rels:
        await safe_edit(q, "no releases", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    ctx.user_data["releases"] = rels
    tp = max(1, (len(rels) + PER_PAGE - 1) // PER_PAGE)
    page = max(0, min(page, tp - 1))
    st = page * PER_PAGE
    ch = rels[st:st + PER_PAGE]
    btns = []
    for i, rl in enumerate(ch):
        ri = st + i
        tg = rl.get("tag_name", "?")
        nm = rl.get("name") or tg
        pr = " pre" if rl.get("prerelease") else ""
        ac = len(rl.get("assets", []))
        btns.append([InlineKeyboardButton(
            "🏷 " + nm + pr + " [" + str(ac) + "]",
            callback_data=store_cb(ctx, "reld", owner=o, repo=r, idx=ri))])
    if tp > 1:
        nv = []
        if page > 0:
            nv.append(InlineKeyboardButton("◀️", callback_data=store_cb(ctx, "rels", owner=o, repo=r, page=page - 1)))
        nv.append(InlineKeyboardButton(str(page + 1) + "/" + str(tp), callback_data=store_cb(ctx, "noop")))
        if page < tp - 1:
            nv.append(InlineKeyboardButton("▶️", callback_data=store_cb(ctx, "rels", owner=o, repo=r, page=page + 1)))
        btns.append(nv)
    btns.append([mm_btn(ctx, o, r)])
    tx = "<b>🏷 Releases " + o + "/" + r + "</b>\n" + str(len(rels)) + " releases"
    await safe_edit(q, tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btns))


async def release_detail(q, ctx, o, r, idx):
    rels = ctx.user_data.get("releases", [])
    try:
        rl = rels[int(idx)]
    except (IndexError, ValueError):
        await safe_edit(q, "not found", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    tg = rl.get("tag_name", "?")
    nm = rl.get("name") or tg
    bd = clean_html(short(rl.get("body") or "-", 500))
    dt = (rl.get("published_at") or "")[:10]
    assets = rl.get("assets", [])
    tx = "<b>🏷 " + nm + "</b> (<code>" + tg + "</code>)\n"
    tx += dt + "\n\n" + bd + "\n\n" + str(len(assets)) + " file(s)"
    btns = []
    tap = max(1, (len(assets) + PER_PAGE - 1) // PER_PAGE)
    ch = assets[:PER_PAGE]
    for i, a in enumerate(ch):
        sz = size_fmt(a.get("size", 0))
        dl = str(a.get("download_count", 0))
        btns.append([InlineKeyboardButton(
            "⬇️ " + a["name"] + " (" + sz + ") [" + dl + "x]",
            callback_data=store_cb(ctx, "dlra", owner=o, repo=r, asset_idx=str(i), rel_idx=int(idx)))])
    if tap > 1:
        nv = []
        nv.append(InlineKeyboardButton("1/" + str(tap), callback_data=store_cb(ctx, "noop")))
        nv.append(InlineKeyboardButton("▶️", callback_data=store_cb(ctx, "relassets", owner=o, repo=r, rel_idx=int(idx), page=1)))
        btns.append(nv)
    sr = []
    if rl.get("zipball_url"):
        sr.append(InlineKeyboardButton("ZIP src", callback_data=store_cb(ctx, "dlra", owner=o, repo=r, asset_idx="srcz", rel_idx=int(idx))))
    if rl.get("tarball_url"):
        sr.append(InlineKeyboardButton("TAR src", callback_data=store_cb(ctx, "dlra", owner=o, repo=r, asset_idx="srct", rel_idx=int(idx))))
    if sr:
        btns.append(sr)
    btns.append([bk_btn(ctx, "rels", "🔙 releases", owner=o, repo=r, page=0), mm_btn(ctx, o, r)])
    await safe_edit(q, tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btns))


async def release_assets_page(q, ctx, o, r, rel_idx, page):
    rels = ctx.user_data.get("releases", [])
    try:
        rl = rels[int(rel_idx)]
    except (IndexError, ValueError):
        await safe_edit(q, "not found", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    assets = rl.get("assets", [])
    tp = max(1, (len(assets) + PER_PAGE - 1) // PER_PAGE)
    page = max(0, min(page, tp - 1))
    st = page * PER_PAGE
    ch = assets[st:st + PER_PAGE]
    nm = rl.get("name") or rl.get("tag_name", "?")
    btns = []
    for i, a in enumerate(ch):
        ri = st + i
        sz = size_fmt(a.get("size", 0))
        dl = str(a.get("download_count", 0))
        btns.append([InlineKeyboardButton(
            "⬇️ " + a["name"] + " (" + sz + ") [" + dl + "x]",
            callback_data=store_cb(ctx, "dlra", owner=o, repo=r, asset_idx=str(ri), rel_idx=int(rel_idx)))])
    if tp > 1:
        nv = []
        if page > 0:
            nv.append(InlineKeyboardButton("◀️", callback_data=store_cb(ctx, "relassets", owner=o, repo=r, rel_idx=int(rel_idx), page=page - 1)))
        nv.append(InlineKeyboardButton(str(page + 1) + "/" + str(tp), callback_data=store_cb(ctx, "noop")))
        if page < tp - 1:
            nv.append(InlineKeyboardButton("▶️", callback_data=store_cb(ctx, "relassets", owner=o, repo=r, rel_idx=int(rel_idx), page=page + 1)))
        btns.append(nv)
    btns.append([bk_btn(ctx, "reld", "🔙 release", owner=o, repo=r, idx=int(rel_idx)), mm_btn(ctx, o, r)])
    await safe_edit(q, "<b>" + nm + " files</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btns))


async def dl_release_asset(q, ctx, o, r, asset_idx, rel_idx):
    await safe_edit(q, "downloading ...")
    rels = ctx.user_data.get("releases", [])
    try:
        rl = rels[int(rel_idx)]
    except (IndexError, ValueError):
        await safe_edit(q, "not found", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    assets = rl.get("assets", [])
    bb = [[bk_btn(ctx, "reld", "🔙 release", owner=o, repo=r, idx=int(rel_idx)), mm_btn(ctx, o, r)]]
    async with aiohttp.ClientSession() as s:
        if asset_idx == "srcz":
            if rl.get("zipball_url"):
                data = await api_download(s, rl["zipball_url"])
                if data:
                    await send_file(q.message, data, r + "-src.zip", "source zip", reply_markup=InlineKeyboardMarkup(bb))
                    return
        elif asset_idx == "srct":
            if rl.get("tarball_url"):
                data = await api_download(s, rl["tarball_url"])
                if data:
                    await send_file(q.message, data, r + "-src.tar.gz", "source tar", reply_markup=InlineKeyboardMarkup(bb))
                    return
        else:
            try:
                asset = assets[int(asset_idx)]
            except (IndexError, ValueError):
                await safe_edit(q, "not found", reply_markup=InlineKeyboardMarkup(bb))
                return
            url = asset.get("browser_download_url") or asset.get("url")
            data = await api_download(s, url)
            if data:
                await send_file(q.message, data, asset["name"], asset["name"], reply_markup=InlineKeyboardMarkup(bb))
                return
    await safe_edit(q, "download failed", reply_markup=InlineKeyboardMarkup(bb))


async def show_branches(q, ctx, o, r):
    async with aiohttp.ClientSession() as s:
        br = await api_get(s, "/repos/" + o + "/" + r + "/branches", params={"per_page": 100})
    if not br:
        await safe_edit(q, "error", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    tx = "<b>🌿 Branches " + o + "/" + r + "</b>\n\n"
    for b in br[:50]:
        tx += "• <code>" + b["name"] + "</code>\n"
    if len(br) > 50:
        tx += "\n+" + str(len(br) - 50) + " more"
    await safe_edit(q, tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))


async def show_readme(q, ctx, o, r):
    async with aiohttp.ClientSession() as s:
        info = await api_get(s, "/repos/" + o + "/" + r + "/readme")
    if not info:
        await safe_edit(q, "no README", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    ct = base64.b64decode(info.get("content", "")).decode("utf-8", errors="replace")
    ct = re.sub(r"!\[.*?\]\(.*?\)", "", ct)
    ct = re.sub(r"<[^>]+>", "", ct)
    ct = short(ct, 3500)
    ct = ct.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    await safe_edit(q, "<b>README</b>\n\n<pre>" + ct + "</pre>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))


async def show_contributors(q, ctx, o, r, page):
    async with aiohttp.ClientSession() as s:
        ct = await api_get(s, "/repos/" + o + "/" + r + "/contributors", params={"per_page": 100})
    if not ct:
        await safe_edit(q, "error", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    tp = max(1, (len(ct) + PER_PAGE - 1) // PER_PAGE)
    page = max(0, min(page, tp - 1))
    st = page * PER_PAGE
    ch = ct[st:st + PER_PAGE]
    tx = "<b>👥 Contributors " + o + "/" + r + "</b>\n" + str(len(ct)) + " people\n\n"
    for c in ch:
        tx += "• <a href='" + c["html_url"] + "'>" + clean_html(c["login"]) + "</a> " + str(c["contributions"]) + "\n"
    btns = []
    if tp > 1:
        nv = []
        if page > 0:
            nv.append(InlineKeyboardButton("◀️", callback_data=store_cb(ctx, "contr", owner=o, repo=r, page=page - 1)))
        nv.append(InlineKeyboardButton(str(page + 1) + "/" + str(tp), callback_data=store_cb(ctx, "noop")))
        if page < tp - 1:
            nv.append(InlineKeyboardButton("▶️", callback_data=store_cb(ctx, "contr", owner=o, repo=r, page=page + 1)))
        btns.append(nv)
    btns.append([mm_btn(ctx, o, r)])
    await safe_edit(q, tx, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btns))


async def show_languages(q, ctx, o, r):
    async with aiohttp.ClientSession() as s:
        lg = await api_get(s, "/repos/" + o + "/" + r + "/languages")
    if not lg:
        await safe_edit(q, "error", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    tl = sum(lg.values())
    tx = "<b>📊 Languages " + o + "/" + r + "</b>\n\n"
    for ln, bc in sorted(lg.items(), key=lambda x: -x[1]):
        pc = (bc / tl) * 100 if tl else 0
        bl = int(pc / 5)
        bar = "█" * bl + "░" * (20 - bl)
        tx += "<code>" + bar + "</code> " + ln + " " + "{:.1f}".format(pc) + "%\n"
    await safe_edit(q, tx, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))


async def download_zip(q, ctx, o, r):
    await safe_edit(q, "downloading source ...")
    url = "https://github.com/" + o + "/" + r + "/archive/refs/heads/main.zip"
    async with aiohttp.ClientSession() as s:
        data = await api_download(s, url)
        if not data:
            url2 = "https://github.com/" + o + "/" + r + "/archive/refs/heads/master.zip"
            data = await api_download(s, url2)
    if not data:
        await safe_edit(q, "failed", reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))
        return
    await send_file(q.message, data, r + ".zip", o + "/" + r, reply_markup=InlineKeyboardMarkup([[mm_btn(ctx, o, r)]]))


def main():
    builder = Application.builder().token(BOT_TOKEN)

    local_api = os.getenv("LOCAL_API_URL", "")
    if local_api:
        builder = builder.base_url(local_api)

    application = builder.build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("users", cmd_users))
    application.add_handler(CommandHandler("broadcast", cmd_broadcast))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"https?://github\.com/"), handle_link))
    application.add_handler(CallbackQueryHandler(on_callback))

    logger.info("--- GitHub Explorer Bot Started ---")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
