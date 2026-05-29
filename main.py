from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import json
import os
import asyncio

TOKEN = os.getenv("TOKEN")

USERS_FILE = "users.json"
MODE_FILE = "modes.json"

# Duplicate oldini olish
sent_cache = set()

KEYWORDS = {
    "toshkent": [
        # Asosiy
        "toshkent ket", "toshkentga ket", "toshkentga bor", "toshkentga joy", "toshkentga yo‘lovchi",
        "toshkent taksi kerak", "toshkentga mashina kerak", "toshkentga bormoqchiman",

        # Narx
        "nechi pul toshkent", "toshkent narxi qancha", "toshkentga qancha", "toshkent necha pul",
        "toshkent arzon bormi", "toshkent narx bilish", "toshkentga pul qancha",

        # Vaqt
        "bugun toshkent bormi", "ertaga toshkent bormi", "hozir toshkent bormi",
        "toshkentga tez ketadigan", "toshkentga vaqtida ketadimi", "toshkentga erta ketish",

        # Joy + holat
        "toshkentga 1 joy kerak", "toshkentga 2 joy kerak", "toshkentga 3 joy kerak",
        "toshkentga 4 joy kerak", "toshkentga oila bilan", "toshkentga bola bilan",
        "toshkentga bagaj bilan", "toshkentga odam qidiryapman", "toshkentga yo‘lovchi bor",

        # Tumanlar/rayonlar
        "chilonzor ket", "chilonzorga toshkent", "yunusobod ket", "yunusobodga taksi kerak",
        "mirzo ulugbek ket", "sergeli ket", "yangihayot ket", "bektemir ket", "mashinasozlar ket"
    ],

    "samarqand": [
        # Asosiy
        "samarga ket", "samarqand ket", "samarga bor", "samarga joy", "samarga yo‘lovchi",
        "samarga taksi kerak", "samarqandga mashina kerak", "samarqandga bormoqchiman",

        # Narx
        "nechi pul samarga", "samarga narxi qancha", "samarqandga qancha", "samarga necha pul",
        "samarga arzon bormi", "samarga narx bilish", "samarga pul qancha",

        # Vaqt
        "bugun samarga bormi", "ertaga samarga bormi", "hozir samarga bormi",
        "samarga tez ketadigan", "samarga vaqtida ketadimi", "samarga erta ketish",

        # Joy + holat
        "samarga 1 joy kerak", "samarga 2 joy kerak", "samarga 3 joy kerak", "samarga 4 joy kerak",
        "samarga oila bilan", "samarga bola bilan", "samarga bagaj bilan",
        "samarga odam qidiryapman", "samarga yo‘lovchi bor",

        # Tumanlar
        "urqut ket", "kattakorgon ket", "pastdargom ket", "payariq ket", "ishtixon ket",
        "jombay ket", "nurabad ket", "oqdaryo ket", "bulungur ket"
    ],

    "surxondaryo": [
        # Asosiy umumiy
        "surxon ket", "surxondaryo ket", "surxonga bor", "surxonga joy", "surxonga yo‘lovchi",
        "surxondaryoga taksi kerak", "surxonga mashina kerak",

        # Termiz
        "termiz ket", "termizga bor", "termizga joy", "termizga taksi kerak", "termizga mashina kerak",
        "nechi pul termiz", "termiz narxi qancha", "termizga qancha", "bugun termiz bormi",
        "termizga 1 joy kerak", "termizga 2 joy kerak", "termizga oila bilan",

        # Denov
        "denov ket", "denovga bor", "denovga joy", "denovga taksi kerak", "denovga mashina kerak",
        "nechi pul denov", "denov narxi qancha", "bugun denov bormi", "denovga 1 joy kerak",

        # Sherobod
        "sherobod ket", "sherobodga bor", "sherobodga joy", "sherobodga taksi kerak",
        "nechi pul sherobod", "sherobod narxi qancha", "sherobodga 2 joy kerak",

        # Qumqo‘rg‘on
        "qumqo‘rg‘on ket", "qumqorgon ket", "qumqo‘rg‘onga bor", "qumqo‘rg‘onga taksi kerak",
        "nechi pul qumqo‘rg‘on", "qumqo‘rg‘onga joy bor",

        # Angor
        "angor ket", "angorga bor", "angorga taksi kerak", "nechi pul angor", "angorga joy bor",

        # Uzun
        "uzun ket", "uzunga bor", "uzunga taksi kerak", "nechi pul uzun", "uzunga joy bor",

        # Boysun
        "boysun ket", "boysunga bor", "boysunga taksi kerak", "nechi pul boysun", "boysunga joy bor",

        # Sariosiyo
        "sariosiyo ket", "sariosiyoga bor", "sariosiyoga taksi kerak", "nechi pul sariosiyo",

        # Qolgani
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


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f, ensure_ascii=False, indent=2)


def load_modes():
    if os.path.exists(MODE_FILE):
        with open(MODE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_modes(modes):
    with open(MODE_FILE, "w", encoding="utf-8") as f:
        json.dump(modes, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    users = load_users()
    users.add(user_id)
    save_users(users)

    keyboard = [
        [KeyboardButton("🚕 Toshkent"), KeyboardButton("🏛 Samarqand")],
        [KeyboardButton("🌴 Surxondaryo"), KeyboardButton("📦 Pochta")],
        [KeyboardButton("❌ Bekor qilish")]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    text = """
🚖 Taxi Kuzatuvchi Bot

Yo‘nalishni tanlang 👇
"""

    await update.message.reply_text(
        text,
        reply_markup=markup
    )


async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    text = update.message.text

    modes = load_modes()

    mode_map = {
        "🚕 Toshkent": "toshkent",
        "🏛 Samarqand": "samarqand",
        "🌴 Surxondaryo": "surxondaryo",
        "📦 Pochta": "pochta"
    }

    if text in mode_map:

        modes[user_id] = mode_map[text]

        save_modes(modes)

        await update.message.reply_text(
            f"✅ {text} yoqildi"
        )

    elif text == "❌ Bekor qilish":

        if user_id in modes:
            del modes[user_id]
            save_modes(modes)

        await update.message.reply_text(
            "❌ Rejim bekor qilindi"
        )


async def scan_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    if not update.message.text:
        return

    msg_text = update.message.text.lower()

    unique_id = f"{update.effective_chat.id}_{update.message.message_id}"

    if unique_id in sent_cache:
        return

    sent_cache.add(unique_id)

    users = load_users()
    modes = load_modes()

    for user_id in users:

        user_id_str = str(user_id)

        if user_id_str not in modes:
            continue

        mode = modes[user_id_str]

        keywords = KEYWORDS[mode]

        for word in keywords:

            if word.lower() in msg_text:

                try:

                    await context.bot.forward_message(
                        chat_id=user_id,
                        from_chat_id=update.effective_chat.id,
                        message_id=update.message.message_id
                    )

                    await asyncio.sleep(0.05)

                except Exception as e:
                    print(e)

                break


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(
                "^(🚕 Toshkent|🏛 Samarqand|🌴 Surxondaryo|📦 Pochta|❌ Bekor qilish)$"
            ),
            choose_mode
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            scan_messages
        )
    )

    print("Bot ishga tushdi...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
