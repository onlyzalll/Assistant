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
def leave_all(client, message):
    if message.from_user.id == OWNER_ID:
        dialogs = client.get_dialogs() 
        print("Dialogs found:", len(dialogs))
        for dialog in dialogs:
            print(f"Checking chat: {dialog.chat.title}")
            if dialog.chat.type in ["supergroup", "channel"]:
                try:
                    client.leave_chat(dialog.chat.id)
                    client.send_message(message.chat.id, f"Bot berhasil keluar dari {dialog.chat.title}")
                except Exception as e:
                    print(f"Error saat keluar dari {dialog.chat.title}: {e}")
        client.send_message(message.chat.id, "Bot telah mencoba keluar dari semua grup dan channel!")
        
if __name__ == "__main__":
    print("Running...")
    app.run() 
