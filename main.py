import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "TOKENINGNI_SHUYERGA_QOY"

logging.basicConfig(level=logging.INFO)
VILOYATLAR = {"toshkent": "🚕 Toshkent", "samarqand": "🚕 Samarqand", "surxondaryo": "🚕 Surxondaryo", "pochta": "📮 Pochta"}
user_viloyat = {}
KEYWORDS = {"toshkent": ["toshkent ket", "toshkentga bor"], "samarqand": ["samarga ket"], "surxondaryo": ["termiz ket"], "pochta": ["pochta yuborish"]}

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(v, callback_data=k)] for k,v in VILOYATLAR.items()]
    await u.message.reply_text("Viloyat tanla:", reply_markup=InlineKeyboardMarkup(kb))

async def button(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    user_viloyat[q.from_user.id] = q.data
    await q.edit_message_text(f"{VILOYATLAR[q.data]} tanlandi")

async def handle(u: Update, c: ContextTypes.DEFAULT_TYPE):
    uid = u.effective_user.id
    if uid in user_viloyat and any(kw in u.message.text.lower() for kw in KEYWORDS.get(user_viloyat[uid], [])):
        await c.bot.send_message(u.effective_chat.id, f"📢 {VILOYATLAR[user_viloyat[uid]]}\n👤 {u.effective_user.first_name}: {u.message.text}")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot ishga tushdi")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
