import os
from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

app = Client("my_account", api_id=api_id, api_hash=api_hash)

@app.on_message(filters.command("start"))
def start(client, message):
    client.send_message(message.chat.id, "Halo, saya bot!")

app.run()
print("Bot berhasil login dan aktif!")
