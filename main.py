import os
import random
import time
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

app = Client("my_account", api_id=api_id, api_hash=api_hash)

OWNER_ID = 5854836745


@app.on_message(filters.text)
def handle_message(client, message):
    text = message.text.lower()

    if message.from_user.id == OWNER_ID:
        if "start" in text:
            client.send_message(message.chat.id, "Halo, saya bot!")

        elif "leaveall" in text:
            dialogs = client.get_dialogs()
            dialogs_list = list(dialogs)
            print("Dialogs found:", len(dialogs_list))
            for dialog in dialogs_list:
                print(f"Checking chat: {dialog.chat.title}")
                if dialog.chat.type in ["supergroup", "channel"]:
                    try:
                        client.leave_chat(dialog.chat.id)
                        client.send_message(message.chat.id, f"Bot berhasil keluar dari {dialog.chat.title}")
                    except Exception as e:
                        print(f"Error saat keluar dari {dialog.chat.title}: {e}")
            client.send_message(message.chat.id, "Bot telah mencoba keluar dari semua grup dan channel!")

        elif "update" in text:
            try:
                client.send_message(message.chat.id, "Melakukan update... silakan tunggu.")
                subprocess.run(["git", "pull"], check=True)
                client.send_message(message.chat.id, "Update selesai, bot akan restart.")
                time.sleep(2)
                os.execl(sys.executable, sys.executable, "-m", "main")
            except subprocess.CalledProcessError as e:
                client.send_message(message.chat.id, f"Gagal melakukan update: {e}")
            except Exception as e:
                client.send_message(message.chat.id, f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    print("Running...")
    app.run()
                                    
