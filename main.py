import os
import time
import subprocess
import sys
import signal
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, RPCError
from asyncio import sleep
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

app = Client("my_account", api_id=api_id, api_hash=api_hash)

OWNER_ID = 5854836745
start_time = time.time()

def format_uptime(seconds):
    days = seconds // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days}D {hours}H {minutes}M {seconds}S"

def signal_handler(sig, frame):
    print("Shutdown initiated...")
    app.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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

            async for dialog in client.get_dialogs():
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

            await message.reply(
                f"<b>Berhasil keluar dari <code>{done}</code> grup/channel, gagal keluar dari <code>{er}</code> grup/channel</b>"
            )

        elif "clearall" in text:
            await message.reply("<b>Memulai proses hapus semua history chat pribadi...</b>")
            er = 0
            done = 0

            async for dialog in client.get_dialogs():
                if dialog.chat.type == enums.ChatType.PRIVATE:
                    try:
                        await client.delete_history(dialog.chat.id)
                        done += 1
                        await sleep(1)
                    except FloodWait as e:
                        print(f"FloodWait: Menunggu {e.value} detik")
                        await sleep(e.value)
                    except Exception as e:
                        print(f"Error saat menghapus chat dengan {dialog.chat.id}: {e}")
                        er += 1

            await message.reply(
                f"<b>Berhasil menghapus history dari <code>{done}</code> chat pribadi, gagal menghapus dari <code>{er}</code> chat</b>"
            )

        elif "update" in text:
            try:
                await client.send_message(message.chat.id, "Melakukan update... silakan tunggu.")
                subprocess.run(["git", "pull"], check=True)
                await client.send_message(message.chat.id, "Update selesai, bot akan restart.")
                time.sleep(2)
                os.execl(sys.executable, sys.executable, "-m", "main")
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

if __name__ == "__main__":
    while True:
        try:
            print("Running...")
            app.run()
        except (OSError, ConnectionResetError):
            print("Koneksi terputus, mencoba untuk reconnect dalam 5 detik...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            break
                        
