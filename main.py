from os import getenv
from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()
app = Client("my_account", api_id=getenv("API_ID"), api_hash=getenv("API_HASH"))

with app:
    app.send_message("me", "Berhasil Login!")
    