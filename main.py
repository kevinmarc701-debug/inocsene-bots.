import os
import html
import threading
import unicodedata
from datetime import datetime, timedelta, timezone

import telebot
from telebot import types
from flask import Flask

# ───────────── CONFIGURATION ─────────────
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN manquant dans Render > Environment")

ADMIN_TELEGRAM_ID = os.environ.get("ADMIN_TELEGRAM_ID")  # optionnel : notifications

ADMIN_TEL = "+50956466804"
ADMIN_USERNAME = "@Inocsene"
ADMIN_URL_TG = "https://t.me/Inocsene"
ADMIN_URL_WA = (
    "https://wa.me/50956466804?text="
    "Salut%20Inocsene%20Zero%2C%20je%20souhaite%20effectuer%20une%20commande%20VPN%20%21"
)

LINE = "━━━━━━━━━━━━━━━━━━━━"

# ───────────── LIENS ─────────────
LINK_ACTIVER_NUIT = "https://t.me/InocseneZeroTuto/4"
LINK_KEY_NUIT = "https://t.me/InocseneZeroTuto/3"
LINK_KEY_DAYOU = "https://t.me/InocseneZeroTuto/5"
LINK_CHANNEL_PROOF = "https://t.me/InocseneZeroTuto"   # utilisé dans les tutoriels
LINK_CHANNEL_BUTTON = "https://t.me/InocseneZero"      # bouton « Canal Proofs & Tutos »

# Canal où se trouvent les vidéos de démo (le bot essaie de les envoyer en vidéo directe)
DEMO_CHANNEL = "@InocseneZeroTuto"

# ───────────── OFFRES ─────────────
PRODUCTS = {
    "bouton": {
        "emoji": "🔰",
        "name": "VPN avec Bouton",
        "ticket_name": "VPN Anti-Ban (avec Bouton)",
        "features": [
            "🛡️ Protection : <b>Anti-Ban</b>",
            "🎯 Boutons intégrés dans l'application",
            "⚡ Gameplay fluide et stable",
        ],
        "price": 250,
        "old_price": 500,
        "demo_id": 6,
        "demo_link": "https://t.me/InocseneZeroTuto/6",
    },
    "auto": {
        "emoji": "⚡",
        "name": "VPN Automatique VIP",
        "ticket_name": "VPN Automatique VIP (Anti-Ban &amp; Anti-Blacklist)",
        "features": [
            "🛡️ Protection : <b>Anti-Ban &amp; Anti-Blacklist</b>",
            "🤖 Mode automatique haute précision",
            "🎮 Idéal pour les longues sessions de jeu",
        ],
        "price": 500,
        "old_price": None,
        "demo_id": 7,
        "demo_link": "https://t.me/InocseneZeroTuto/7",
    },
}

# Fuseau horaire Haïti
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Port-au-Prince")
except Exception:
    TZ = timezone(timedelta(hours=-5))

def now_local():
    return datetime.now(TZ)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ───────────── TEXTES ─────────────
def price_text(p):
    if p["old_price"]:
        return f"<s>{p['old_price']} HTG</s> ➡️ <b>{p['price']} HTG</b> 🔥"
    return f"<b>{p['price']} HTG</b>"

def build_welcome(name):
    return (
        "<b>👑 INOCSENE ZERO • VIP STORE FREE FIRE 👑</b>\n"
        f"{LINE}\n\n"
        f"Salut <b>{name}</b> ! 👋\n"
        "Bienvenue sur la plateforme officielle.\n\n"
        "✨ Connexion <b>ultra-rapide</b> et stable\n"
        "🛡️ Protection avancée pour ton compte\n"
        "🎮 Gameplay fluide, sans compromis\n\n"
        f"{LINE}\n"
        "👇 <i>Choisis ton VPN pour découvrir l'offre.</i>"
    )

def build_offer(p):
    feats = "\n".join(p["features"])
    return (
        f"<b>{p['emoji']} {p['name'].upper()} {p['emoji']}</b>\n"
        f"{LINE}\n\n"
        f"{feats}\n\n"
        f"💰 <b>Prix :</b> {price_text(p)}\n"
        "💳 <b>Paiement :</b> Natcash\n\n"
        f"{LINE}\n"
        "🛒 <i>Appuie sur « Continuer l'achat » pour commander.</i>"
    )

TICKET_TEMPLATE = (
    "<b>🧾 BILLET DE COMMANDE OFFICIEL 🧾</b>\n"
    f"{LINE}\n"
    "<b>⚡ INOCSENE ZERO ⚡</b>\n"
    f"{LINE}\n\n"
    "📋 <b>N° de commande :</b> <code>{order}</code>\n"
    "👤 <b>Client :</b> {name}\n"
    "📅 <b>Date :</b> {date}\n\n"
    f"{LINE}\n"
    "🛡️ <b>Produit :</b> {product}\n"
    "💰 <b>Prix :</b> {price} HTG\n"
    "💳 <b>Paiement :</b> Natcash\n"
    "📌 <b>Statut :</b> ⏳ En attente de paiement\n"
    f"{LINE}\n\n"
    "<b>✅ POUR VALIDER LA COMMANDE, CONTACTE L'ADMINISTRATEUR "
    "VIA WHATSAPP OU TELEGRAM 👇</b>\n\n"
    "1️⃣ Effectue le dépôt Natcash de <b>{price} HTG</b>\n"
    f"2️⃣ Envoie ton reçu et ton n° de commande à {ADMIN_USERNAME} (<b>{ADMIN_TEL}</b>)\n"
    "3️⃣ Reçois ton fichier VPN, puis tape <b>0</b> (Nuit Cheat All) "
    "ou <b>1</b> (Dayou) pour débloquer tes tutoriels 🎓\n\n"
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

# ───────────── CLAVIERS ─────────────
def main_menu():
    m = types.InlineKeyboardMarkup()
    for code, p in PRODUCTS.items():
        m.row(types.InlineKeyboardButton(f"{p['emoji']} {p['name']}", callback_data=f"offer_{code}"))
    m.row(
        types.InlineKeyboardButton("🟢 WhatsApp", url=ADMIN_URL_WA),
        types.InlineKeyboardButton("🔵 Telegram", url=ADMIN_URL_TG),
    )
    m.row(types.InlineKeyboardButton("📢 Canal Proofs & Tutos", url=LINK_CHANNEL_BUTTON))
    return m

def offer_menu(code):
    m = types.InlineKeyboardMarkup()
    m.row(types.InlineKeyboardButton("🛒 Continuer l'achat", callback_data=f"buy_{code}"))
    m.row(types.InlineKeyboardButton("🔙 Retour au menu", callback_data="menu_home"))
    return m

def contact_buttons():
    m = types.InlineKeyboardMarkup()
    m.row(
        types.InlineKeyboardButton("🟢 WhatsApp", url=ADMIN_URL_WA),
        types.InlineKeyboardButton("🔵 Telegram", url=ADMIN_URL_TG),
    )
    m.row(types.InlineKeyboardButton("🏠 Menu principal", callback_data="menu_home"))
    return m

# ───────────── OUTILS ─────────────
def get_name(user):
    first = user.first_name if user else None
    return html.escape(first) if first else "cher client"

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

def send_demo(chat_id, p):
    """Envoie la vidéo de démo en premier : vidéo directe, sinon lien avec aperçu."""
    try:
        bot.copy_message(chat_id, DEMO_CHANNEL, p["demo_id"])
    except Exception:
        try:
            bot.send_message(chat_id, f"🎬 <b>Démonstration en vidéo</b>\n👉 {p['demo_link']}")
        except Exception:
            pass

def notify_admin(user, action):
    if not ADMIN_TELEGRAM_ID:
        return
    try:
        username = f"@{user.username}" if user.username else "Pas de pseudo"
        msg = (
            "🚨 <b>NOTIFICATION INOCSENE ZERO</b> 🚨\n"
            f"👤 <b>Client :</b> {get_name(user)} ({html.escape(username)})\n"
            f"🆔 <b>ID :</b> <code>{user.id}</code>\n"
            f"📌 <b>Action :</b> {html.escape(action)}\n"
            f"⏰ <b>Heure :</b> {now_local().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        bot.send_message(ADMIN_TELEGRAM_ID, msg)
    except Exception:
        pass

# ───────────── HANDLERS ─────────────
@bot.message_handler(commands=["start"])
def start(message):
    notify_admin(message.from_user, "Démarrage du bot (/start)")
    bot.send_message(
        message.chat.id,
        build_welcome(get_name(message.from_user)),
        reply_markup=main_menu(),
    )

@bot.message_handler(func=is_zero)
def send_guide_nuit(message):
    notify_admin(message.from_user, "Demande tutoriel Nuit Cheat All (0)")
    bot.send_message(message.chat.id, GUIDE_NUIT_CHEAT)

@bot.message_handler(func=is_one)
def send_guide_dayou(message):
    notify_admin(message.from_user, "Demande tutoriel Dayou (1)")
    bot.send_message(message.chat.id, GUIDE_DAYOU)

@bot.callback_query_handler(func=lambda call: True)
def on_click(call):
    bot.answer_callback_query(call.id)
    chat = call.message.chat.id
    data = call.data or ""

    if data == "menu_home":
        bot.send_message(chat, build_welcome(get_name(call.from_user)), reply_markup=main_menu())

    elif data.startswith("offer_"):
        code = data.split("_", 1)[1]
        if code in PRODUCTS:
            p = PRODUCTS[code]
            notify_admin(call.from_user, f"Consultation {p['name']}")
            send_demo(chat, p)                                   # 1) vidéo
            bot.send_message(chat, build_offer(p), reply_markup=offer_menu(code))  # 2) description + boutons

    elif data.startswith("buy_"):
        code = data.split("_", 1)[1]
        if code in PRODUCTS:
            p = PRODUCTS[code]
            ticket = TICKET_TEMPLATE.format(
                order=make_order_number(call.from_user.id),
                name=get_name(call.from_user),
                date=now_local().strftime("%d/%m/%Y à %H:%M (heure d'Haïti)"),
                product=p["ticket_name"],
                price=p["price"],
            )
            notify_admin(call.from_user, f"Billet de commande : {p['name']}")
            bot.send_message(chat, ticket, reply_markup=contact_buttons())

# Les autres messages ne reçoivent aucune réponse.

# ───────────── SERVEUR FLASK (Render) ─────────────
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Inocsene Zero en ligne ✅"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(skip_pending=True)
