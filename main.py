from telethon import TelegramClient, events

api_id = 30503959
api_hash =' bbc171f557775690f74f8f9031201676'

# Akang telegram ID si
owner_id = 'me'

# Qidiriladigan so‘zlar
keywords = [
    "1 kishi bor ",
    "srochniy taksi kerak",
    "bir kamplekt odam bor",
    "ikki ta odam bor ",
    "Taxsi kerak",
    "bitta odam bor",
    "taksi kerak",
  "2 kishi bor",
  "bugunga taksi kerak"
]

client = TelegramClient('session', api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    text = event.raw_text.lower()

    if any(word in text for word in keywords):
        await client.forward_messages(owner_id, event.message)

print("Bot ishga tushdi...")

client.start()
client.run_until_disconnected()
