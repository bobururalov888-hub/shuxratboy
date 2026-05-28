import nest_asyncio
nest_asyncio.apply()

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "TOKENINGNI_SHUYERGA_QOY" # Bu yerga BotFather'dan olgan tokeningni qo'y

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

VILOYATLAR = {
    "toshkent": "🚕 Toshkent",
    "samarqand": "🚕 Samarqand",
    "surxondaryo": "🚕 Surxondaryo",
    "pochta": "📮 Pochta"
}

user_viloyat = {}

KEYWORDS = {
    "toshkent": ["toshkent ket", "toshkentga bor", "chilonzor ket", "yashnobod ket"],
    "samarqand": ["samarga ket", "urqut ket", "bulungur ket"],
    "surxondaryo": ["termiz ket", "denov ket", "sherobod ket", "jarqurgon ket"],
    "pochta": ["pochta yuborish", "hujjat yuborish", "posilka yuborish"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v, callback_data=k)] for k, v in VILOYATLAR.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Assalomu alaykum! Viloyat tanlang:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_viloyat[query.from_user.id] = query.data
    await query.edit_message_text(f"{VILOYATLAR[query.data]} tanlandi ✅\nEndi 'toshkent ket' kabi yozing")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_viloyat:
        await update.message.reply_text("Avval /start bosib viloyat tanlang")
        return

    viloyat = user_viloyat[user_id]
    matn = update.message.text.lower()

    if any(kw in matn for kw in KEYWORDS.get(viloyat, [])):
        msg = f"📢 {VILOYATLAR[viloyat]}\n👤 {update.effective_user.first_name}: {update.message.text}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        logging.info(f"Xabar yuborildi: {viloyat} - {update.effective_user.first_name}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi - Render uchun tayyor")
    app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False, stop_signals=None)

if __name__ == "__main__":
    main()
