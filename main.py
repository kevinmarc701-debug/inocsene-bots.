import telebot
from telebot import types

TOKEN = "8987005201:AAG8VtB9D4484yU5_iCEnmWasdfb_PFiFM"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🛡️ VPN Anti-Blacklist Premium", callback_data="vpn")
    btn2 = types.InlineKeyboardButton("⚙️ Panel Anti-Ban", callback_data="panel")
    btn3 = types.InlineKeyboardButton("💬 Contacter l'administrateur", url="https://t.me/+50956466804")
    markup.add(btn1, btn2, btn3)
    
    welcome_text = (
        "⚡ INOCSENE ZERO - SERVICE OFFICIEL ⚡\n\n"
        "Salut cher client ! 👋 Bienvenue sur la plateforme officielle.\n\n"
        "🚀 Profite d'une connexion ultra-rapide, stable et sécurisée pour tes jeux !\n\n"
        "Fais ton choix ci-dessous pour commencer 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "vpn":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💰 Prix : 450 HTG via Natcash.\n📞 Admin : +50956466804\n\nEnvoie une capture de ton paiement à l'administrateur pour recevoir ta clé !")
    elif call.data == "panel":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "⚠️ Respecte bien la règle du 'no-click' sur les liens internes pour éviter le blacklistage !")

bot.infinity_polling()
