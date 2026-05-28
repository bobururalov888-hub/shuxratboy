from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, CommandHandler, filters
import json, os, asyncio

TOKEN = "8771424495:AAHpZgMFrwqL12PidDKyW3_kS9L0WDebCbk"
USERS_FILE = "users.json"
MODE_FILE = "modes.json"

# Faqat YO‘LOVCHI kalit so‘zlar - 3 ta shahar + tumanlar + Pochta
KEYWORDS = {
    "toshkent": [
        # Asosiy
        "taksi kerak toshkent", "toshkentga taksi kerak", "toshkentga mashina kerak",
        "toshkentga bormoqchiman", "toshkentga ketmoqchiman", "toshkentga ketish kerak",
        "toshkentga odam qidiryapman", "toshkentga yo‘lovchi qidiryapman",

        # Narx
        "nechi puldan toshkent", "toshkent narxi qancha", "toshkentga qancha",
        "toshkentga necha pul", "toshkent arzon bormi", "toshkent narx bilish",

        # Vaqt
        "bugun toshkent bormi", "ertaga toshkent bormi", "hozir toshkent bormi",
        "toshkentga vaqtida ketadimi", "toshkentga tez ketadigan",

        # Joy + holat
        "toshkentga joy bormi", "toshkentga 1 joy kerak", "toshkentga 2 joy kerak",
        "toshkentga 3 joy kerak", "toshkentga 4 joy kerak", "toshkentga oila bilan",
        "toshkentga bola bilan", "toshkentga bagaj bilan",

        # Tumanlar
        "chilonzor ket", "chilonzorga toshkent", "yunusobod ket", "yunusobodga taksi kerak",
        "mirzo ulugbek ket", "sergeli ket", "yangihayot ket", "bektemir ket", "mashinasozlar ket"
    ],

    "samarqand": [
        # Asosiy
        "taksi kerak samarga", "samarqandga taksi kerak", "samarga mashina kerak",
        "samarqandga bormoqchiman", "samarga ketmoqchiman", "samarqandga ketish kerak",
        "samarqandga odam qidiryapman", "samarga yo‘lovchi qidiryapman",

        # Narx
        "nechi puldan samarga", "samarga narxi qancha", "samarqandga qancha",
        "samarga necha pul", "samarga arzon bormi", "samarga narx bilish",

        # Vaqt
        "bugun samarga bormi", "ertaga samarga bormi", "hozir samarga bormi",
        "samarga vaqtida ketadimi", "samarga tez ketadigan",

        # Joy + holat
        "samarga joy bormi", "samarga 1 joy kerak", "samarga 2 joy kerak",
        "samarga 3 joy kerak", "samarga oila bilan", "samarga bagaj bilan",

        # Tumanlar
        "urqut ket", "kattakorgon ket", "pastdargom ket", "payariq ket", "ishtixon ket",
        "jombay ket", "nurabad ket", "oqdaryo ket", "bulungur ket"
    ],

    "surxondaryo": [
        # Umumiy
        "taksi kerak surxon", "surxondaryoga taksi kerak", "surxonga mashina kerak",
        "surxonga bormoqchiman", "surxonga ketish kerak", "surxonga odam qidiryapman",
        "nechi pul surxon", "surxon narxi qancha", "bugun surxon bormi", "surxonga joy bormi",

        # Termiz
        "taksi kerak termiz", "termizga taksi kerak", "termizga mashina kerak",
        "termizga bormoqchiman", "termizga ketish kerak", "termizga odam qidiryapman",
        "nechi pul termiz", "termiz narxi qancha", "termizga qancha", "bugun termiz bormi",
        "termizga joy bormi", "termizga 1 joy kerak", "termizga 2 joy kerak", "termizga oila bilan",

        # Denov
        "taksi kerak denov", "denovga taksi kerak", "denovga mashina kerak",
        "denovga bormoqchiman", "nechi pul denov", "denov narxi qancha", "bugun denov bormi",
        "denovga joy bormi", "denovga 1 joy kerak",

        # Sherobod
        "taksi kerak sherobod", "sherobodga taksi kerak", "sherobodga mashina kerak",
        "nechi pul sherobod", "sherobod narxi qancha", "sherobodga joy bormi",

        # Qumqo‘rg‘on
        "taksi kerak qumqo‘rg‘on", "qumqorgon ket", "qumqo‘rg‘onga taksi kerak",
        "nechi pul qumqo‘rg‘on", "qumqo‘rg‘onga joy bormi",

        # Angor, Uzun, Boysun, Sariosiyo
        "taksi kerak angor", "angorga taksi kerak", "nechi pul angor", "angorga joy bormi",
        "taksi kerak uzun", "uzunga taksi kerak", "nechi pul uzun",
        "taksi kerak boysun", "boysunga taksi kerak", "nechi pul boysun",
        "taksi kerak sariosiyo", "sariosiyoga taksi kerak", "nechi pul sariosiyo",

        # Qolgan tumanlar
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

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if file == MODE_FILE else set()

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(list(data) if isinstance(data, set) else data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    users.add(int(user_id))
    save_json(USERS_FILE, users)

    # 5 ta menyu
    keyboard = [
        [KeyboardButton("🚕 Toshkent"), KeyboardButton("🏛 Samarqand")],
        [KeyboardButton("🌴 Surxondaryo"), KeyboardButton("📦 Pochta")],
        [KeyboardButton("❌ Bekor qilish")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    text = """Salom! 👋
Taksi e'lonlarini kuzatuvchi bot.

Faqat yo'lovchi yozgan xabarlar keladi.
Taksichi "ketamiz" desa kelmaydi.

Qaysi yo'nalishni tanlaysan? 👇"""
    await update.message.reply_text(text, reply_markup=reply_markup)

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
        await update.message.reply_text(f"✅ {text} yoqildi.\nEndi faqat yo'lovchi e'lonlari keladi.")

    elif text == "❌ Bekor qilish":
        if user_id in modes:
            del modes[user_id]
            save_json(MODE_FILE, modes)
            await update.message.reply_text("❌ Rejim bekor qilindi. Qayta tanla 👇")
        else:
            await update.message.reply_text("Sen rejim tanlamagansan.")

async def scan_messages(update: Update, context):
    if not update.message or not update.message.text:
        return

    msg_text = update.message.text.lower()
    chat_name = update.effective_chat.title or "Shaxsiy"
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
                rejim_nomi = {"toshkent":"🚕 Toshkent","samarqand":"🏛 Samarqand","surxondaryo":"🌴 Surxondaryo","pochta":"📦 Pochta"}
                send_text = f"🔍 [{rejim_nomi[mode]}]\nGuruh: {chat_name}\n\n{update.message.text}"
                try:
                    await context.bot.send_message(chat_id=user_id, text=send_text)
                    await asyncio.sleep(0.05)
                except:
                    pass
                break

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(🚕 Toshkent|🏛 Samarqand|🌴 Surxondaryo|📦 Pochta|❌ Bekor qilish)$"), handle_mode))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_messages))
print("Bot ishga tushdi... Faqat yo'lovchi ushlaydi")
app.run_polling()
