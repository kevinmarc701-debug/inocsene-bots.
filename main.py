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

# Ton ID Telegram pour recevoir les notifications (optionnel)
ADMIN_TELEGRAM_ID = os.environ.get("ADMIN_TELEGRAM_ID")

ADMIN_TEL = "+50956466804"
ADMIN_URL_TG = "https://t.me/+50956466804"
# Lien WhatsApp direct avec message pré-rempli (correctement encodé)
ADMIN_URL_WA = (
    "https://wa.me/50956466804?text="
    "Salut%20Inocsene%20Zero%2C%20je%20souhaite%20effectuer%20une%20commande%20VPN%20%21"
)

LINE = "━━━━━━━━━━━━━━━━━━━━"

# ───────────── LIENS DES TUTORIELS & DEMOS ─────────────
LINK_ACTIVER_NUIT = "https://t.me/InocseneZeroTuto/4"
LINK_KEY_NUIT = "https://t.me/InocseneZeroTuto/3"
LINK_KEY_DAYOU = "https://t.me/InocseneZeroTuto/5"
LINK_DEMO_VPN_BOUTONS = "https://t.me/InocseneZeroTuto/6"
LINK_DEMO_VPN_FREEZE = "https://t.me/InocseneZeroTuto/7"
LINK_CHANNEL_PROOF = "https://t.me/InocseneZeroTuto"

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
WELCOME = (
    "<b>⚡ INOCSENE ZERO - SERVICE OFFICIEL ⚡</b>\n"
    f"{LINE}\n\n"
    "Salut <b>{name}</b> ! 👋 Bienvenue sur notre plateforme officielle.\n\n"
    "🚀 <b>Profite d'une connexion ultra-rapide, stable et 100% Anti-Blacklist pour tes jeux !</b>\n\n"
    "Fais ton choix ci-dessous pour découvrir nos services 👇"
)

VPN_BOUTONS_TEXT = (
    "<b>🛡️ VPN ANTI-BLACKLIST (AVEC BOUTONS) 🛡️</b>\n"
    f"{LINE}\n\n"
    "✅ Protection Anti-Blacklist maximale\n"
    "✅ Gameplay fluide et ultra-stable\n"
    "✅ Application avec boutons intégrés\n\n"
    f"🎬 <b>Regarde la démonstration en jeu :</b>\n👉 {LINK_DEMO_VPN_BOUTONS}\n\n"
    "💰 <b>Prix :</b> 450 HTG\n"
    "💳 <b>Paiement :</b> Natcash"
)

VPN_FREEZE_TEXT = (
    "<b>❄️ VPN ANTI-BLACKLIST (FREEZE AUTOMATIQUE) ❄️</b>\n"
    f"{LINE}\n\n"
    "✅ Protection Anti-Blacklist maximale\n"
    "✅ Système Freeze automatique haute performance\n"
    "✅ Idéal pour les longues sessions de jeu\n\n"
    f"🎬 <b>Regarde la démonstration en jeu :</b>\n👉 {LINK_DEMO_VPN_FREEZE}\n\n"
    "💰 <b>Prix :</b> 500 HTG\n"
    "💳 <b>Paiement :</b> Natcash"
)

PANEL_TEXT = (
    "<b>⏳ PANEL ANTI-BAN ⏳</b>\n"
    f"{LINE}\n\n"
    "Désolé, les panels sont indisponibles pour le moment. "
    "Seuls nos VPN Anti-Blacklist Premium sont actuellement en stock !"
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
    "✅ Connexion ultra-rapide et stable\n"
    "✅ Anti-blacklist garanti pour le jeu\n"
    f"{LINE}\n\n"
    "💰 <b>Prix :</b> {price} HTG\n"
    "💳 <b>Mode de paiement :</b> Natcash\n"
    "📌 <b>Statut :</b> ⏳ En attente de paiement\n\n"
    f"{LINE}\n"
    "📌 <b>CONSIGNES :</b>\n"
    "1️⃣ Effectue le dépôt Natcash de <b>{price} HTG</b>.\n"
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

# ───────────── OUTILS & CLAVIERS ─────────────
def get_name(user):
    first = user.first_name if user else None
    return html.escape(first) if first else "cher client"

def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🛡️ VPN Anti-Blacklist (Boutons) - 450 HTG", callback_data="vpn_boutons"),
        types.InlineKeyboardButton("❄️ VPN Anti-Blacklist (Freeze) - 500 HTG", callback_data="vpn_freeze"),
        types.InlineKeyboardButton("⚙️ Panel Anti-Ban", callback_data="panel"),
        types.InlineKeyboardButton("💬 Contacter sur WhatsApp 🟢", url=ADMIN_URL_WA),
        types.InlineKeyboardButton("💬 Contacter sur Telegram 🔵", url=ADMIN_URL_TG),
    )
    return m

def buy_menu(product_code):
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("▶️ Continuer l'achat", callback_data=f"buy_{product_code}"),
        types.InlineKeyboardButton("🔙 Retour au menu", callback_data="menu_home"),
    )
    return m

def contact_buttons():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🟢 Contacter l'administrateur sur WhatsApp", url=ADMIN_URL_WA),
        types.InlineKeyboardButton("🔵 Contacter l'administrateur sur Telegram", url=ADMIN_URL_TG),
        types.InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_home"),
    )
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

def notify_admin(user, action):
    """Envoie une notification à l'admin quand un client utilise le bot."""
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
        WELCOME.format(name=get_name(message.from_user)),
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
    data = call.data

    if data == "menu_home":
        bot.send_message(chat, WELCOME.format(name=get_name(call.from_user)), reply_markup=main_menu())

    elif data == "vpn_boutons":
        notify_admin(call.from_user, "Consultation VPN Boutons (450 HTG)")
        bot.send_message(chat, VPN_BOUTONS_TEXT, reply_markup=buy_menu("boutons"))

    elif data == "vpn_freeze":
        notify_admin(call.from_user, "Consultation VPN Freeze (500 HTG)")
        bot.send_message(chat, VPN_FREEZE_TEXT, reply_markup=buy_menu("freeze"))

    elif data.startswith("buy_"):
        prod_type = data.split("_")[1]
        if prod_type == "boutons":
            p_name, p_price = "VPN Anti-Blacklist (Boutons)", "450"
        else:
            p_name, p_price = "VPN Anti-Blacklist (Freeze Auto)", "500"

        ticket = TICKET_TEMPLATE.format(
            order=make_order_number(call.from_user.id),
            name=get_name(call.from_user),
            date=now_local().strftime("%d/%m/%Y à %H:%M (heure d'Haïti)"),
            product=p_name,
            price=p_price,
        )
        notify_admin(call.from_user, f"Génération billet de commande ({p_name})")
        bot.send_message(chat, ticket, reply_markup=contact_buttons())

    elif data == "panel":
        bot.send_message(chat, PANEL_TEXT)

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
