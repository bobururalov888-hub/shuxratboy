from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters
)

import json
import os
import asyncio

# Render ENV
TOKEN = os.getenv("TOKEN")

USERS_FILE = "users.json"
MODE_FILE = "modes.json"

# Duplicate oldini olish
sent_cache = set()

# YO‘LOVCHI keywordlari
KEYWORDS = {

    "toshkent": [

        # Asosiy
        "taksi kerak toshkent",
        "toshkentga taksi kerak",
        "toshkentga mashina kerak",
        "toshkentga bormoqchiman",
        "toshkentga ketmoqchiman",
        "toshkentga ketish kerak",
        "toshkentga chiqish kerak",

        # Narx
        "nechi pul toshkent",
        "toshkent qancha",
        "toshkentga qancha",
        "toshkent narxi qancha",
        "toshkentga necha pul",
        "toshkent arzon bormi",

        # Vaqt
        "bugun toshkent bormi",
        "ertaga toshkent bormi",
        "hozir toshkent bormi",
        "kechqurun toshkent bormi",
        "ertalab toshkent bormi",

        # Joy
        "toshkentga 1 joy kerak",
        "toshkentga 2 joy kerak",
        "toshkentga 3 joy kerak",
        "toshkentga oila bilan",
        "toshkentga bola bilan",
        "toshkentga bagaj bilan",

        # Toshkent tumanlari
        "chilonzorga borish kerak",
        "yunusobodga borish kerak",
        "sergeliga borish kerak",
        "mirzo ulugbekka borish kerak",
        "bektemirga borish kerak",
        "yangihayotga borish kerak"
    ],

    "samarqand": [

        # Asosiy
        "taksi kerak samarga",
        "samarqandga taksi kerak",
        "samarga mashina kerak",
        "samarqandga bormoqchiman",
        "samarga ketmoqchiman",
        "samarqandga ketish kerak",

        # Narx
        "nechi pul samarga",
        "samarga qancha",
        "samarqand narxi qancha",
        "samarga necha pul",

        # Vaqt
        "bugun samarga bormi",
        "ertaga samarga bormi",
        "hozir samarga bormi",

        # Joy
        "samarga 1 joy kerak",
        "samarga 2 joy kerak",
        "samarga oila bilan",

        # Tumanlar
        "urgutga borish kerak",
        "kattakorgonga borish kerak",
        "payariqqa borish kerak",
        "ishtixonga borish kerak",
        "jomboyga borish kerak",
        "oqdaryoga borish kerak"
    ],

    "surxondaryo": [

        # Umumiy
        "taksi kerak surxon",
        "surxondaryoga taksi kerak",
        "surxonga mashina kerak",
        "surxonga bormoqchiman",
        "surxonga ketmoqchiman",
        "surxonga ketish kerak",

        # Narx
        "nechi pul surxon",
        "surxon qancha",
        "surxon narxi qancha",

        # Vaqt
        "bugun surxon bormi",
        "ertaga surxon bormi",

        # Joy
        "surxonga 1 joy kerak",
        "surxonga 2 joy kerak",

        # Termiz
        "taksi kerak termiz",
        "termizga taksi kerak",
        "termizga mashina kerak",
        "termizga bormoqchiman",
        "termizga ketmoqchiman",

        "nechi pul termiz",
        "termiz qancha",
        "termiz narxi qancha",

        "bugun termiz bormi",
        "ertaga termiz bormi",

        # Denov
        "taksi kerak denov",
        "denovga taksi kerak",
        "denovga mashina kerak",
        "denovga bormoqchiman",

        "nechi pul denov",
        "denov qancha",

        "bugun denov bormi",

        # Sherobod
        "taksi kerak sherobod",
        "sherobodga taksi kerak",
        "sherobodga mashina kerak",

        "nechi pul sherobod",

        # Qumqo‘rg‘on
        "taksi kerak qumqorgon",
        "qumqorgonga taksi kerak",
        "qumqorgonga mashina kerak",

        # Tumanlar
        "angorga borish kerak",
        "uzunga borish kerak",
        "boysunga borish kerak",
        "sariosiyoga borish kerak",
        "jarqorgonga borish kerak",
        "shorchiga borish kerak",
        "oltinsoyga borish kerak",
        "muzrabotga borish kerak"
    ],

    "pochta": [

        "pochta yuborish kerak",
        "hujjat yuborish kerak",
        "pochta jo‘natish kerak",
        "konvert yuborish kerak",
        "sumka yuborish kerak",

        "pochta qancha",
        "pochta narxi qancha",

        "shoshilinch pochta kerak",
        "srochniy pochta kerak"
    ]
}


# JSON yuklash
def load_json(file):

    if os.path.exists(file):

        with open(file, "r", encoding="utf-8") as f:

            data = json.load(f)

            # users.json -> set
            if file == USERS_FILE:
                return set(data)

            return data

    return {} if file == MODE_FILE else set()


# JSON saqlash
def save_json(file, data):

    with open(file, "w", encoding="utf-8") as f:

        json.dump(
            list(data) if isinstance(data, set) else data,
            f,
            ensure_ascii=False,
            indent=2
        )


# /start
async def start(update: Update, context):

    user_id = update.effective_user.id

    users = load_json(USERS_FILE)

    users.add(user_id)

    save_json(USERS_FILE, users)

    keyboard = [
        [KeyboardButton("🚕 Toshkent"), KeyboardButton("🏛 Samarqand")],
        [KeyboardButton("🌴 Surxondaryo"), KeyboardButton("📦 Pochta")],
        [KeyboardButton("❌ Bekor qilish")]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    text = """
🚖 Taxi Kuzatuvchi Bot

Kerakli yo‘nalishni tanlang 👇
"""

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )


# Rejim tanlash
async def handle_mode(update: Update, context):

    user_id = str(update.effective_user.id)

    text = update.message.text

    modes = load_json(MODE_FILE)

    rejim_map = {
        "🚕 Toshkent": "toshkent",
        "🏛 Samarqand": "samarqand",
        "🌴 Surxondaryo": "surxondaryo",
        "📦 Pochta": "pochta"
    }

    if text in rejim_map:

        modes[user_id] = rejim_map[text]

        save_json(MODE_FILE, modes)

        await update.message.reply_text(
            f"✅ {text} yoqildi"
        )

    elif text == "❌ Bekor qilish":

        if user_id in modes:

            del modes[user_id]

            save_json(MODE_FILE, modes)

        await update.message.reply_text(
            "❌ Rejim bekor qilindi"
        )


# Guruh xabarlarini scan qilish
async def scan_messages(update: Update, context):

    if not update.message:
        return

    if not update.message.text:
        return

    msg_text = update.message.text.lower()

    # duplicate check
    msg_unique = f"{update.effective_chat.id}_{update.message.message_id}"

    if msg_unique in sent_cache:
        return

    sent_cache.add(msg_unique)

    users = load_json(USERS_FILE)

    modes = load_json(MODE_FILE)

    for user_id in users:

        user_id_str = str(user_id)

        if user_id_str not in modes:
            continue

        mode = modes[user_id_str]

        keywords = KEYWORDS[mode]

        for word in keywords:

            if word in msg_text:

                try:

                    # ORIGINAL FORWARD
                    await context.bot.forward_message(
                        chat_id=user_id,
                        from_chat_id=update.effective_chat.id,
                        message_id=update.message.message_id
                    )

                    await asyncio.sleep(0.05)

                except Exception as e:
                    print(e)

                break


# APP
app = Application.builder().token(TOKEN).build()

# /start
app.add_handler(CommandHandler("start", start))

# Menu handler
app.add_handler(
    MessageHandler(
        filters.TEXT & filters.Regex(
            "^(🚕 Toshkent|🏛 Samarqand|🌴 Surxondaryo|📦 Pochta|❌ Bekor qilish)$"
        ),
        handle_mode
    )
)

# Message scanner
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        scan_messages
    )
)

print("Bot ishga tushdi...")

app.run_polling()
