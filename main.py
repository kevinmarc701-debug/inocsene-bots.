import os
import html
import threading
import unicodedata
from datetime import datetime

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
    "3️⃣ Reçois ton fichier VPN, puis tape le code <b>0</b> ici "
    "pour débloquer tes tutoriels.\n"
    f"{LINE}\n"
    "🙏 <i>Merci de ta confiance !</i>"
)

GUIDE_TEXT = (
    "<b>🎬 GUIDES ET TUTORIELS - INOCSENE ZERO 🎬</b>\n"
    f"{LINE}\n\n"
    "🔷 Étape 1 : Comment générer la clé (Key)\n"
    "👉 Regarde cette vidéo : https://t.me/InosceneZeroTuto/4\n\n"
    "🔷 Étape 2 : Comment activer le VPN\n"
    "👉 Regarde cette vidéo : https://t.me/InosceneZeroTuto/3\n\n"
    "⚠️ AVERTISSEMENT DE SÉCURITÉ TRÈS IMPORTANT :\n"
    "Ne clique jamais sur le bouton « Join Telegram » ou sur les liens externes "
    "situés à l'intérieur de l'application VPN.\n"
    "<b>Cela annulera instantanément ta protection Anti-Blacklist et risquera de "
    "compromettre la sécurité de ton compte de jeu.</b>\n\n"
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
    """Minuscules, sans accents, espaces ni ponctuation (0, ０, o, zéro, Zero...)."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return "".join(c for c in text.lower() if c.isalnum())

def is_zero(message):
    return bool(message.text) and normalize(message.text) in {"0", "o", "zero"}

def make_order_number(user_id):
    now = datetime.utcnow()
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
def send_guide(message):
    bot.send_message(message.chat.id, GUIDE_TEXT)

@bot.callback_query_handler(func=lambda call: True)
def on_click(call):
    bot.answer_callback_query(call.id)
    chat = call.message.chat.id
    if call.data == "vpn":
        ticket = TICKET.format(
            order=make_order_number(call.from_user.id),
            name=get_name(call.from_user),
            date=datetime.utcnow().strftime("%d/%m/%Y à %H:%M UTC"),
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
    
