import os
import threading
import telebot
from telebot import types
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN manquant dans Render > Environment")

ADMIN_URL = "https://t.me/+50956466804"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🛡️ VPN Anti-Blacklist Premium", callback_data="vpn"),
        types.InlineKeyboardButton("⚙️ Panel Anti-Ban", callback_data="panel"),
        types.InlineKeyboardButton("💬 Contacter l'administrateur", url=ADMIN_URL),
    )
    return m

def back_menu():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("⬅️ Retour au menu", callback_data="home"))
    return m

WELCOME = (
    "⚡ <b>INOCSENE ZERO</b> — Service officiel ⚡\n\n"
    "Salut {name} ! 👋 Bienvenue sur la plateforme officielle.\n\n"
    "🚀 Connexion ultra-rapide, stable et sécurisée pour tes jeux.\n\n"
    "Fais ton choix ci-dessous 👇"
)

PAGES = {
    "vpn": (
        "🛡️ <b>VPN Anti-Blacklist Premium</b>\n\n"
        "💰 Prix : <b>450 HTG</b> via Natcash\n"
        "📞 Admin : +50956466804\n\n"
        "📸 Envoie une capture de ton paiement à l'administrateur pour recevoir ta clé."
    ),
    "panel": (
        "⚙️ <b>Panel Anti-Ban</b>\n\n"
        "⚠️ Respecte la règle du « no-click » sur les liens internes "
        "pour éviter le blacklistage."
    ),
}

@bot.message_handler(commands=["start", "menu", "help"])
def start(message):
    name = message.from_user.first_name or "cher client"
    bot.send_message(message.chat.id, WELCOME.format(name=name), reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def on_click(call):
    bot.answer_callback_query(call.id)
    chat, msg = call.message.chat.id, call.message.message_id
    if call.data == "home":
        name = call.from_user.first_name or "cher client"
        bot.edit_message_text(WELCOME.format(name=name), chat, msg, reply_markup=main_menu())
    elif call.data in PAGES:
        bot.edit_message_text(PAGES[call.data], chat, msg, reply_markup=back_menu())

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot en ligne ✅"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(skip_pending=True)

