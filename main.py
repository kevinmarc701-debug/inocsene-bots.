import os
import html
import threading
import unicodedata
from datetime import datetime, timedelta, timezone

import telebot
from telebot import types
from flask import Flask

# ───────────── CONFIG ─────────────
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN manquant dans Render > Environment")

ADMIN_URL = "https://t.me/+50956466804"
ADMIN_TEL = "+50956466804"
LINE = "━━━━━━━━━━━━━━━━━━━━"

# ───────────── LIENS DES TUTORIELS ─────────────
LINK_ACTIVER_NUIT = "https://t.me/InocseneZeroTuto/4"
LINK_KEY_NUIT = "https://t.me/InocseneZeroTuto/3"
LINK_KEY_DAYOU = "https://t.me/InocseneZeroTuto/5"
LINK_CHANNEL_PROOF = "https://t.me/InocseneZeroTuto"

# Heure d'Haïti
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Port-au-Prince")
except Exception:
    TZ = timezone(timedelta(hours=-5))

def now_local():
    return datetime.now(TZ)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ───────────── TEXTES ─────────────
WELCOME = (
    "<b>⚡ INOCSENE ZERO - SERVICE OFFICIEL ⚡</b>\n"
    f"{LINE}\n\n"
    "Salut <b>{name}</b> ! 👋 Bienvenue sur la plateforme officielle.\n\n"
    "🚀 <b>Profite d'une connexion ultra-rapide, stable et sécurisée pour tes jeux !</b>\n\n"
    "Fais ton choix ci-dessous pour commencer 👇"
)

PANEL_TEXT = (
    "<b>⏳ PANEL ANTI-BAN ⏳</b>\n"
    f"{LINE}\n\n"
    "Désolé, les panels sont indisponibles pour le moment. "
    "Seuls les VPN Anti-Blacklist sont actuellement en stock !"
)

TICKET = (
    "<b>🧾 BILLET DE COMMANDE OFFICIEL 🧾</b>\n"
    f"{LINE}\n"
    "<b>⚡ INOCSENE ZERO ⚡</b>\n"
    f"{LINE}\n\n"
    "📋 <b>N° de commande :</b> <code>{order}</code>\n"
    "👤 <b>Client :</b> {name}\n"
    "📅 <b>Date :</b> {date}\n\n"
    f"{LINE}\n"
    "🛡️ <b>Produit :</b> VPN Anti-Blacklist Premium\n"
    "✅ Connexion ultra-rapide et stable\n"
    "✅ Anti-blacklist garanti pour le jeu\n"
    f"{LINE}\n\n"
    "💰 <b>Prix :</b> 450 HTG\n"
    "💳 <b>Mode de paiement :</b> Natcash\n"
    "📌 <b>Statut :</b> ⏳ En attente de paiement\n\n"
    f"{LINE}\n"
    "📌 <b>CONSIGNES :</b>\n"
    "1️⃣ Effectue le dépôt Natcash de <b>450 HTG</b>.\n"
    f"2️⃣ Contacte l'administrateur (Tél : <b>{ADMIN_TEL}</b>) "
    "avec ton reçu de paiement et ton n° de commande.\n"
    "3️⃣ Reçois ton fichier VPN, puis tape ici le code <b>0</b> pour Nuit Cheat All "
    "ou le code <b>1</b> pour Dayou afin de débloquer tes tutoriels.\n"
    f"{LINE}\n"
    "🙏 <i>Merci de ta confiance !</i>"
)

GUIDE_NUIT_CHEAT = (
    "<b>🎬 TUTORIELS NUIT CHEAT ALL - INOCSENE ZERO 🎬</b>\n"
    f"{LINE}\n\n"
    "🔷 Étape 1 : Comment activer le Nuit Cheat All\n"
    f"👉 Regarde cette vidéo : {LINK_ACTIVER_NUIT}\n\n"
    "🔷 Étape 2 : Comment générer la clé (Key)\n"
    f"👉 Regarde cette vidéo : {LINK_KEY_NUIT}\n\n"
    "⚠️ AVERTISSEMENT DE SÉCURITÉ TRÈS IMPORTANT :\n"
    "Ne clique jamais sur le bouton « Join Telegram » ou sur les liens externes "
    "situés à l'intérieur de l'application VPN.\n"
    "<b>Cela annulera instantanément ta protection Anti-Blacklist et risquera de "
    "compromettre la sécurité de ton compte de jeu.</b>\n\n"
    f"{LINE}\n"
    "📢 <i>Si un lien pose problème, rejoins directement notre canal officiel :</i>\n"
    f"👉 <b>Inocsene Zero • Tutos &amp; Proofs</b> ({LINK_CHANNEL_PROOF})\n\n"
    "⚡ <b>Bon jeu et profite de ton service Inocsene Zero !</b>"
)

GUIDE_DAYOU = (
    "<b>💎 TUTORIEL DAYOU - INOCSENE ZERO 💎</b>\n"
    f"{LINE}\n\n"
    "🔷 Étape unique : Comment générer la clé (Key) de Dayou\n"
    f"👉 Regarde cette vidéo : {LINK_KEY_DAYOU}\n\n"
    "⚠️ AVERTISSEMENT DE SÉCURITÉ TRÈS IMPORTANT :\n"
    "Ne clique jamais sur le bouton « Join Telegram » ou sur les liens externes "
    "situés à l'intérieur de l'application VPN.\n"
    "<b>Cela annulera instantanément ta protection Anti-Blacklist et risquera de "
    "compromettre la sécurité de ton compte de jeu.</b>\n\n"
    f"{LINE}\n"
    "📢 <i>Si un lien pose problème, rejoins directement notre canal officiel :</i>\n"
    f"👉 <b>Inocsene Zero • Tutos &amp; Proofs</b> ({LINK_CHANNEL_PROOF})\n\n"
    "⚡ <b>Bon jeu et profite de ton service Inocsene Zero !</b>"
)

# ───────────── OUTILS ─────────────
def get_name(user):
    first = user.first_name if user else None
    return html.escape(first) if first else "cher client"

def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🛡️ VPN Anti-Blacklist Premium", callback_data="vpn"),
        types.InlineKeyboardButton("⚙️ Panel Anti-Ban", callback_data="panel"),
        types.InlineKeyboardButton("💬 Contacter l'administrateur", url=ADMIN_URL),
    )
    return m

def admin_button():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("💬 Contacter l'administrateur", url=ADMIN_URL))
    return m

def normalize(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return "".join(c for c in text.lower() if c.isalnum())

def is_zero(message):
    return bool(message.text) and normalize(message.text) in {"0", "o", "zero"}

def is_one(message):
    return bool(message.text) and normalize(message.text) in {"1", "un", "one"}

def make_order_number(user_id):
    now = now_local()
    return f"IZ-{now.strftime('%y%m%d')}-{str(user_id)[-4:]}{now.strftime('%H%M')}"

# ───────────── HANDLERS ─────────────
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        WELCOME.format(name=get_name(message.from_user)),
        reply_markup=main_menu(),
    )

@bot.message_handler(func=is_zero)
def send_guide_nuit(message):
    bot.send_message(message.chat.id, GUIDE_NUIT_CHEAT)

@bot.message_handler(func=is_one)
def send_guide_dayou(message):
    bot.send_message(message.chat.id, GUIDE_DAYOU)

@bot.callback_query_handler(func=lambda call: True)
def on_click(call):
    bot.answer_callback_query(call.id)
    chat = call.message.chat.id
    if call.data == "vpn":
        ticket = TICKET.format(
            order=make_order_number(call.from_user.id),
            name=get_name(call.from_user),
            date=now_local().strftime("%d/%m/%Y à %H:%M (heure d'Haïti)"),
        )
        bot.send_message(chat, ticket, reply_markup=admin_button())
    elif call.data == "panel":
        bot.send_message(chat, PANEL_TEXT)

# Les autres messages ne reçoivent aucune réponse.

# ───────────── SERVEUR FLASK (Render) ─────────────
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot en ligne ✅"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(skip_pending=True)
