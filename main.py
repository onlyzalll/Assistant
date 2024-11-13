import os
import random
from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

app = Client("my_account", api_id=api_id, api_hash=api_hash)

OWNER_ID = 5854836745

@app.on_message(filters.command("start"))
def _(client, message):
    client.send_message(message.chat.id, "Halo, saya bot!")

@app.on_message(filters.command("leaveall"))
def exit_groups(client, message):
    if message.from_user.id == OWNER_ID:
        for chat in client.get_chats():
            if chat.type in ["supergroup", "channel"]:
                client.leave_chat(chat.id)
        client.send_message(message.chat.id, "Bot telah keluar dari semua grup dan channel!")
        
app.run()
        
