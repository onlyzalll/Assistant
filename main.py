import os
import time
import subprocess
import sys
import signal
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from asyncio import sleep
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
OWNER_ID = 5854836745
start_time = time.time()

app = Client("my_account", api_id=api_id, api_hash=api_hash)
approved_users = set()

def format_uptime(seconds):
    days = seconds // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days}D {hours}H {minutes}M {seconds}S"

def signal_handler(sig, frame):
    print("Shutdown initiated...")
    if app.is_connected:
        app.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@app.on_message(filters.private & ~filters.me)
async def pm_permit_handler(client, message):
    user_id = message.from_user.id
    if user_id not in approved_users:
        await message.reply_text(
            "Halo! 👋\n"
            "Anda mengirim pesan ke akun bot pribadi.\n"
            "Mohon tunggu sebentar sampai diizinkan untuk mengirim pesan."
        )
        time.sleep(2)
        approved_users.add(user_id)
    else:
        await message.reply_text("Pesan Anda sudah diterima.")

@app.on_message(filters.text)
async def handle_message(client, message):
    text = message.text.lower()

    if message.from_user.id == OWNER_ID:
        if "start" in text:
            await client.send_message(message.chat.id, "Halo, saya bot!")

        elif "leaveall" in text:
            await message.reply("<b>Memulai proses keluar dari semua grup dan channel...</b>")
            er = 0
            done = 0
            dialogs = await client.get_dialogs()
            async for dialog in dialogs:
                if dialog.chat.type in (enums.ChatType.SUPERGROUP, enums.ChatType.GROUP, enums.ChatType.CHANNEL):
                    try:
                        await client.leave_chat(dialog.chat.id)
                        done += 1
                        await sleep(1)
                    except FloodWait as e:
                        print(f"FloodWait: Menunggu {e.value} detik")
                        await sleep(e.value)
                    except Exception as e:
                        print(f"Error saat keluar dari {dialog.chat.title}: {e}")
                        er += 1
            await message.reply(f"<b>Berhasil keluar dari <code>{done}</code> grup/channel, gagal keluar dari <code>{er}</code> grup/channel</b>")

        elif "clearall" in text:
            await message.reply("<b>Memulai proses hapus semua history chat pribadi...</b>")
            er = 0
            done = 0
            dialogs = await client.get_dialogs()
            async for dialog in dialogs:
                if dialog.chat.type == enums.ChatType.PRIVATE:
                    try:
                        messages = await client.get_chat_history(dialog.chat.id, limit=100)
                        message_ids = [msg.message_id for msg in messages]
                        while message_ids:
                            await client.delete_messages(dialog.chat.id, message_ids)
                            done += len(message_ids)
                            messages = await client.get_chat_history(dialog.chat.id, limit=100)
                            message_ids = [msg.message_id for msg in messages]
                            await sleep(1)
                    except FloodWait as e:
                        print(f"FloodWait: Menunggu {e.value} detik")
                        await sleep(e.value)
                    except Exception as e:
                        print(f"Error saat menghapus chat dengan {dialog.chat.id}: {e}")
                        er += 1
            await message.reply(f"<b>Berhasil menghapus <code>{done}</code> pesan dari chat pribadi, gagal menghapus dari <code>{er}</code> chat</b>")

        elif "update" in text:
            try:
                await client.send_message(message.chat.id, "Melakukan update... silakan tunggu.")
                subprocess.run(["git", "pull"], check=True)
                await client.send_message(message.chat.id, "Update selesai, bot akan restart.")
                restart_bot()
            except subprocess.CalledProcessError as e:
                await client.send_message(message.chat.id, f"Gagal melakukan update: {e}")
            except Exception as e:
                await client.send_message(message.chat.id, f"Terjadi kesalahan: {e}")

        elif "ping" in text:
            start = datetime.now()
            await sleep(1)
            end = datetime.now()
            delta_ping = round((end - start).total_seconds() * 1000, 3)
            await client.send_message(message.chat.id, f"Ping: {delta_ping} ms")

def restart_bot():
    app.stop()
    time.sleep(2)
    os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    try:
        print("Running...")
        app.run()
    except (OSError, ConnectionResetError) as e:
        print(f"Koneksi terputus: {e}. Menco ba restart dalam 5 detik...")
        time.sleep(5)
        restart_bot()
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        
