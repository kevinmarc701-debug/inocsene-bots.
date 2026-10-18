import os
import html
import time
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

ADMIN_USERNAME = "@Inocsene"   # contact Telegram
ADMIN_TEL = "+50956466804"
ADMIN_URL_WA = (
    "https://wa.me/50956466804?text="
    "Salut%20Inocsene%20Zero%2C%20je%20souhaite%20effectuer%20une%20commande%20VPN%20%21"
)

LINE = "━━━━━━━━━━━━━━━━━━━━"

# Animation à l'arrivée d'un nouvel écran
# 🔥 flammes et étincelles : "5104841245755180586"
# 🎉 confettis            : "5046509860389126442"
EFFECT_ID = "5104841245755180586"

# ───────────── LIENS ─────────────
LINK_ACTIVER_NUIT = "https://t.me/InocseneZeroTuto/4"
LINK_KEY_NUIT = "https://t.me/InocseneZeroTuto/3"
LINK_KEY_DAYOU = "https://t.me/InocseneZeroTuto/5"
LINK_CHANNEL_PROOF = "https://t.me/InocseneZeroTuto"   # canal « Tutos & Proofs »

DEMO_CHANNEL = "@InocseneZeroTuto"

# Anti-spam : dernier clic par utilisateur
USER_COOLDOWN = {}
COOLDOWN_SECONDS = 1.5

# Vidéo de démo envoyée à chaque client (pour la supprimer ensuite)
DEMO_MSG = {}

# ───────────── OFFRES ─────────────
PRODUCTS = {
    "bouton": {
        "emoji": "🔰",
        "name": "VPN avec Bouton",
        "ticket_name": "VPN Anti-Ban (avec Bouton)",
        "features": [
            "Protection Anti-Ban maximale",
            "Gameplay fluide et ultra-stable",
            "Application avec boutons intégrés",
            "Installation guidée par vidéo",
        ],
        "price": 250,
        "old_price": 500,
        "code": "1",
        "tuto": "Dayou",
        "demo_id": 6,
        "demo_link": "https://t.me/InocseneZeroTuto/6",
    },
    "auto": {
        "emoji": "❄️",
        "name": "VPN Freeze Automatique VIP",
        "ticket_name": "VPN Freeze Automatique VIP (Anti-Ban &amp; Anti-Blacklist)",
        "features": [
            "Protection Anti-Ban &amp; Anti-Blacklist (haute précision)",
            "Système Freeze automatique haute performance",
            "Gameplay fluide et ultra-stable",
            "Idéal pour les longues sessions de jeu",
        ],
        "price": 500,
        "old_price": None,
        "code": "0",
        "tuto": "Nuit Cheat All",
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

# ───────────── GRAS POUR LES BOUTONS ─────────────
def bold(text):
    out = []
    for c in text:
        if "A" <= c <= "Z":
            out.append(chr(0x1D5D4 + ord(c) - 65))
        elif "a" <= c <= "z":
            out.append(chr(0x1D5EE + ord(c) - 97))
        elif "0" <= c <= "9":
            out.append(chr(0x1D7EC + ord(c) - 48))
        else:
            out.append(c)
    return "".join(out)

# ───────────── TEXTES ─────────────
def price_text(p):
    if p["old_price"]:
        return f"<s>{p['old_price']} HTG</s> ➡️ <b>{p['price']} HTG</b> 🔥"
    return f"<b>{p['price']} HTG</b>"

def build_welcome(name):
    return (
        "<b>⚡ INOCSENE ZERO • SERVICE OFFICIEL ⚡</b>\n"
        "<b>👑 VIP STORE FREE FIRE 👑</b>\n"
        f"{LINE}\n\n"
        f"Salut <b>{name}</b> ! 👋 Bienvenue sur la plateforme officielle.\n\n"
        "<blockquote>🚀 <b>Connexion ultra-rapide et stable</b>\n"
        "🛡️ <b>Protection Anti-Ban &amp; Anti-Blacklist</b>\n"
        "🎮 <b>Gameplay fluide pour tes jeux</b></blockquote>\n\n"
        f"{LINE}\n"
        "👇 <i>Fais ton choix ci-dessous pour découvrir nos services.</i>"
    )

def build_offer(p):
    feats = "\n".join(f"✅ <b>{f}</b>" for f in p["features"])
    return (
        f"<b>{p['emoji']} {p['name'].upper()} {p['emoji']}</b>\n"
        f"{LINE}\n\n"
        f"<blockquote>{feats}</blockquote>\n\n"
        f"{LINE}\n"
        f"💰 <b>Prix :</b> {price_text(p)}\n"
        "💳 <b>Paiement :</b> Natcash\n"
        f"{LINE}\n\n"
        "🛒 <i>Appuie sur « Continuer l'achat » pour commander.</i>"
    )

PANEL_TEXT = (
    "<b>🔥 PANEL ANTI-BAN VIP PRO 🛡️</b>\n"
    f"{LINE}\n\n"
    "<blockquote>⚡ <b>ACCÈS VIP EXCLUSIF</b>\n"
    "Les panels sont actuellement en cours de mise à jour.\n"
    "Seuls nos VPN Ultra-Sécurisés sont disponibles en stock pour le moment.</blockquote>\n\n"
    f"🔔 <i>Contacte directement l'administrateur ({ADMIN_USERNAME}) pour être inscrit "
    "sur la liste de réservation prioritaire !</i>"
)

TICKET_TEMPLATE = (
    "<b>🧾 BILLET DE COMMANDE OFFICIEL 🧾</b>\n"
    f"{LINE}\n"
    "<b>⚡ INOCSENE ZERO ⚡</b>\n"
    f"{LINE}\n\n"
    "<blockquote>📋 <b>N° de commande :</b> <code>{order}</code>\n"
    "👤 <b>Client :</b> {name}\n"
    "📅 <b>Date :</b> {date}</blockquote>\n\n"
    f"{LINE}\n"
    "🛡️ <b>Produit :</b> {product}\n"
    "✅ Connexion ultra-rapide et stable\n"
    "✅ Protection avancée pour le jeu\n"
    f"{LINE}\n\n"
    "<blockquote>💰 <b>Prix :</b> {price} HTG\n"
    "💳 <b>Paiement :</b> Natcash\n"
    "📌 <b>Statut :</b> ⏳ En attente de paiement</blockquote>\n\n"
    f"{LINE}\n"
    "<b>✅ POUR VALIDER LA COMMANDE, CONTACTE L'ADMINISTRATEUR "
    "SUR TELEGRAM OU WHATSAPP 👇</b>\n\n"
    "📌 <b>CONSIGNES :</b>\n"
    f"1️⃣ Pour recevoir ton VPN, contacte l'administrateur sur Telegram : <b>{ADMIN_USERNAME}</b>\n"
    "2️⃣ Envoie-lui ce billet de commande et ton reçu Natcash de <b>{price} HTG</b>\n"
    "3️⃣ Une fois ton VPN reçu, tape <b>{code}</b> dans ce chat "
    "pour débloquer ton tutoriel <b>{tuto}</b> 🎓\n"
    f"{LINE}\n"
    f"📲 <i>Tu peux aussi écrire sur WhatsApp ({ADMIN_TEL}) avec le bouton ci-dessous.</i>\n\n"
    "🙏 <i>Merci de ta confiance !</i>"
)

SECURITY_WARNING = (
    "⚠️ AVERTISSEMENT DE SÉCURITÉ TRÈS IMPORTANT :\n"
    "Ne clique jamais sur le bouton « Join Telegram » ou sur les liens externes "
    "situés à l'intérieur de l'application VPN.\n"
    "<b>Cela annulera instantanément ta protection Anti-Blacklist et risquera de "
    "compromettre la sécurité de ton compte de jeu.</b>\n\n"
    "🚨 <b>SI UN MESSAGE « UPDATE » (MISE À JOUR) APPARAÎT SUR TON ÉCRAN :</b>\n"
    "Ne clique sur rien et <b>supprime rapidement l'APK</b> de ton téléphone.\n\n"
)

GUIDE_NUIT_CHEAT = (
    "<b>🎬 TUTORIELS NUIT CHEAT ALL - INOCSENE ZERO 🎬</b>\n"
    f"{LINE}\n\n"
    "🔷 Étape 1 : Comment activer le Nuit Cheat All\n"
    f"👉 Regarde cette vidéo : {LINK_ACTIVER_NUIT}\n\n"
    "🔷 Étape 2 : Comment générer la clé (Key)\n"
    f"👉 Regarde cette vidéo : {LINK_KEY_NUIT}\n\n"
    + SECURITY_WARNING +
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
    + SECURITY_WARNING +
    f"{LINE}\n"
    "📢 <i>Si un lien pose problème, rejoins directement notre canal officiel :</i>\n"
    f"👉 <b>Inocsene Zero • Tutos &amp; Proofs</b> ({LINK_CHANNEL_PROOF})\n\n"
    "⚡ <b>Bon jeu et profite de ton service Inocsene Zero !</b>"
)

# ───────────── CLAVIERS ─────────────
def main_menu():
    m = types.InlineKeyboardMarkup()
    for code, p in PRODUCTS.items():
        m.row(types.InlineKeyboardButton(f"{p['emoji']} {bold(p['name'])}", callback_data=f"offer_{code}"))
    m.row(types.InlineKeyboardButton(f"🔥 {bold('PANEL ANTI-BAN VIP PRO')} 🛡️", callback_data="panel"))
    m.row(types.InlineKeyboardButton(f"🟢 {bold('Contacter sur WhatsApp')}", url=ADMIN_URL_WA))
    m.row(types.InlineKeyboardButton(f"📢 {bold('Canal Proofs & Tutos')}", url=LINK_CHANNEL_PROOF))
    return m

def offer_menu(code):
    m = types.InlineKeyboardMarkup()
    m.row(types.InlineKeyboardButton(f"🛒 {bold('CONTINUER L' + chr(39) + 'ACHAT')} ✅", callback_data=f"buy_{code}"))
    m.row(types.InlineKeyboardButton(f"⬅️ {bold('Retour au menu')}", callback_data="menu_home"))
    return m

def contact_buttons():
    m = types.InlineKeyboardMarkup()
    m.row(types.InlineKeyboardButton(f"🟢 {bold('Contacter sur WhatsApp')}", url=ADMIN_URL_WA))
    m.row(types.InlineKeyboardButton(f"⬅️ {bold('Menu principal')}", callback_data="menu_home"))
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

def send_fx(chat, text, reply_markup=None):
    """Envoie un message avec une animation (effet Telegram) ; sans effet si indisponible."""
    try:
        return bot.send_message(chat, text, reply_markup=reply_markup, message_effect_id=EFFECT_ID)
    except Exception:
        return bot.send_message(chat, text, reply_markup=reply_markup)

def remove_msg(chat, msg_id):
    try:
        bot.delete_message(chat, msg_id)
    except Exception:
        pass

def send_demo(chat_id, p):
    """Vidéo de démo en premier : vidéo directe, sinon lien avec aperçu."""
    sent = None
    try:
        sent = bot.copy_message(chat_id, DEMO_CHANNEL, p["demo_id"])
    except Exception:
        try:
            sent = bot.send_message(chat_id, f"🎬 <b>Démonstration en vidéo</b>\n👉 {p['demo_link']}")
        except Exception:
            pass
    if sent is not None:
        if len(DEMO_MSG) > 1000:
            DEMO_MSG.clear()
        DEMO_MSG[chat_id] = sent.message_id

def clear_demo(chat_id):
    """Supprime la vidéo de démo pour garder un chat propre."""
    mid = DEMO_MSG.pop(chat_id, None)
    if mid:
        remove_msg(chat_id, mid)

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
    clear_demo(message.chat.id)
    send_fx(
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

# ───────────── GESTION DES CLICS (anti-spam + animation) ─────────────
@bot.callback_query_handler(func=lambda call: True)
def on_click(call):
    user_id = call.from_user.id
    now = time.time()

    # Nettoyage de la mémoire anti-spam
    if len(USER_COOLDOWN) > 1000:
        for uid in [u for u, t in USER_COOLDOWN.items() if now - t > 60]:
            USER_COOLDOWN.pop(uid, None)

    if user_id in USER_COOLDOWN and (now - USER_COOLDOWN[user_id]) < COOLDOWN_SECONDS:
        bot.answer_callback_query(call.id, "⚠️ Patiente une seconde avant de re-cliquer...", show_alert=False)
        return

    USER_COOLDOWN[user_id] = now
    bot.answer_callback_query(call.id)

    chat = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data or ""

    if data == "menu_home":
        clear_demo(chat)
        notify_admin(call.from_user, "Retour au menu principal")
        if "BILLET DE COMMANDE" not in (call.message.text or ""):
            remove_msg(chat, msg_id)          # l'ancien écran disparaît (le billet, lui, reste)
        send_fx(chat, build_welcome(get_name(call.from_user)), reply_markup=main_menu())

    elif data == "panel":
        clear_demo(chat)
        notify_admin(call.from_user, "Consultation Panel Anti-Ban VIP PRO")
        remove_msg(chat, msg_id)
        send_fx(chat, PANEL_TEXT, reply_markup=contact_buttons())

    elif data.startswith("offer_"):
        code = data.split("_", 1)[1]
        if code in PRODUCTS:
            p = PRODUCTS[code]
            notify_admin(call.from_user, f"Consultation {p['name']}")
            clear_demo(chat)
            remove_msg(chat, msg_id)                                     # le menu disparaît
            send_demo(chat, p)                                           # 1) vidéo
            send_fx(chat, build_offer(p), reply_markup=offer_menu(code)) # 2) fiche + boutons, avec animation

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
                code=p["code"],
                tuto=p["tuto"],
            )
            notify_admin(call.from_user, f"Billet de commande : {p['name']}")
            clear_demo(chat)
            remove_msg(chat, msg_id)                                     # la fiche disparaît
            send_fx(chat, ticket, reply_markup=contact_buttons())

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
