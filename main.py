import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
TOKEN = " 8771424495:AAHpZgMFrwqLI2PidDKyW3_kS9L0WDebCbk"# o‘zingni tokeningni qo‘y

logging.basicConfig(level=logging.INFO)

VILOYATLAR = {
    "toshkent": "🚕 Toshkent",
    "samarqand": "🚕 Samarqand",
    "surxondaryo": "🚕 Surxondaryo",
    "pochta": "📮 Pochta"
}

user_viloyat = {}

# SEN BERGAN KEYWORDLAR
KEYWORDS = {
    "toshkent": [
        "toshkent ket", "toshkentga ket", "toshkentga bor", "toshkentga joy", "toshkentga yo‘lovchi",
        "toshkent taksi kerak", "toshkentga mashina kerak", "toshkentga bormoqchiman",
        "nechi pul toshkent", "toshkent narxi qancha", "toshkentga qancha", "toshkent necha pul",
        "toshkent arzon bormi", "toshkent narx bilish", "toshkentga pul qancha",
        "bugun toshkent bormi", "ertaga toshkent bormi", "hozir toshkent bormi",
        "toshkentga tez ketadigan", "toshkentga vaqtida ketadimi", "toshkentga erta ketish",
        "toshkentga 1 joy kerak", "toshkentga 2 joy kerak", "toshkentga 3 joy kerak",
        "toshkentga 4 joy kerak", "toshkentga oila bilan", "toshkentga bola bilan",
        "toshkentga bagaj bilan", "toshkentga odam qidiryapman", "toshkentga yo‘lovchi bor",
        "chilonzor ket", "chilonzorga toshkent", "yunusobod ket", "yunusobodga taksi kerak",
        "mirzo ulugbek ket", "sergeli ket", "yangihayot ket", "bektemir ket", "mashinasozlar ket"
    ],

    "samarqand": [
        "samarga ket", "samarqand ket", "samarga bor", "samarga joy", "samarga yo‘lovchi",
        "samarga taksi kerak", "samarqandga mashina kerak", "samarqandga bormoqchiman",
        "nechi pul samarga", "samarga narxi qancha", "samarqandga qancha", "samarga necha pul",
        "samarga arzon bormi", "samarga narx bilish", "samarga pul qancha",
        "bugun samarga bormi", "ertaga samarga bormi", "hozir samarga bormi",
        "samarga tez ketadigan", "samarga vaqtida ketadimi", "samarga erta ketish",
        "samarga 1 joy kerak", "samarga 2 joy kerak", "samarga 3 joy kerak", "samarga 4 joy kerak",
        "samarga oila bilan", "samarga bola bilan", "samarga bagaj bilan",
        "samarga odam qidiryapman", "samarga yo‘lovchi bor",
        "urqut ket", "kattakorgon ket", "pastdargom ket", "payariq ket", "ishtixon ket",
        "jombay ket", "nurabad ket", "oqdaryo ket", "bulungur ket"
    ],

    "surxondaryo": [
        "surxon ket", "surxondaryo ket", "surxonga bor", "surxonga joy", "surxonga yo‘lovchi",
        "surxondaryoga taksi kerak", "surxonga mashina kerak",
        "termiz ket", "termizga bor", "termizga joy", "termizga taksi kerak", "termizga mashina kerak",
        "nechi pul termiz", "termiz narxi qancha", "termizga qancha", "bugun termiz bormi",
        "termizga 1 joy kerak", "termizga 2 joy kerak", "termizga oila bilan",
        "denov ket", "denovga bor", "denovga joy", "denovga taksi kerak", "denovga mashina kerak",
        "nechi pul denov", "denov narxi qancha", "bugun denov bormi", "denovga 1 joy kerak",
        "sherobod ket", "sherobodga bor", "sherobodga joy", "sherobodga taksi kerak",
        "nechi pul sherobod", "sherobod narxi qancha", "sherobodga 2 joy kerak",
        "qumqo‘rg‘on ket", "qumqorgon ket", "qumqo‘rg‘onga bor", "qumqo‘rg‘onga taksi kerak",
        "nechi pul qumqo‘rg‘on", "qumqo‘rg‘onga joy bor",
        "angor ket", "angorga bor", "angorga taksi kerak", "nechi pul angor", "angorga joy bor",
        "uzun ket", "uzunga bor", "uzunga taksi kerak", "nechi pul uzun", "uzunga joy bor",
        "boysun ket", "boysunga bor", "boysunga taksi kerak", "nechi pul boysun", "boysunga joy bor",
        "sariosiyo ket", "sariosiyoga bor", "sariosiyoga taksi kerak", "nechi pul sariosiyo",
        "jarqo‘rg‘on ket", "jarqorgon ket", "sho‘rchi ket", "shorchi ket", "oltinsoy ket", "muzrabot ket",
        "nechi pul jarqorgon", "nechi pul shorchi", "muzrabotga taksi kerak"
    ],

    "pochta": [
        "pochta yuborish kerak", "hujjat yuborish kerak", "pochta jo‘natish kerak",
        "pochta tashish kerak", "konvert yuborish kerak", "sumka yuborish kerak",
        "pochta qancha", "pochta narxi qancha", "hujjat qancha", "pochta narx bilish",
        "pochta arzon bormi", "srochniy pochta kerak", "shoshilinch pochta", "bugun pochta bor"
    ]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text, callback_data=key)] for key, text in VILOYATLAR.items()]
    await update.message.reply_text("Viloyatni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_viloyat[query.from_user.id] = query.data
    await query.edit_message_text(f"{VILOYATLAR[query.data]} tanlandi. Endi keyword yozing")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_viloyat:
        return

    tanlangan = user_viloyat[uid]
    matn = update.message.text.lower()

    # Faqat tanlangan viloyat keywordini tekshiradi
    if tanlangan in KEYWORDS:
        if any(kw in matn for kw in KEYWORDS[tanlangan]):
            viloyat_nomi = VILOYATLAR[tanlangan]
            ism = update.effective_user.first_name
            xabar = f"📢 {viloyat_nomi}\n👤 {ism}: {update.message.text}"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=xabar)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    print("Bot ishga tushdi... Keyword filter yoqildi")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
