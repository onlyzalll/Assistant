import os
import time
import subprocess
import sys
import signal
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.raw.functions.messages import DeleteHistory
from asyncio import sleep
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("my_account", api_id=api_id, api_hash=api_hash)

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
            await client.send_message(message.chat.id, "Hello, I am your bot!")

        elif "leaveall" in text:
            await message.reply("<b>Starting the process of leaving all groups and channels...</b>")
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
                        print(f"FloodWait: Waiting for {e.value} seconds")
                        await sleep(e.value)
                    except Exception as e:
                        print(f"Error leaving {dialog.chat.title}: {e}")
                        er += 1

            await message.reply(
                f"<b>Successfully left <code>{done}</code> groups/channels, failed to leave <code>{er}</code> groups/channels</b>"
            )

        elif "clearall" in text:
            await message.reply("<b>Starting the process of clearing all private chat histories...</b>")
            er = 0
            done = 0

            async for dialog in client.get_dialogs():
                if dialog.chat.type == enums.ChatType.PRIVATE:
                    try:
                        bot_info = await client.resolve_peer(dialog.chat.id)
                        await client.invoke(DeleteHistory(peer=bot_info, max_id=0, revoke=True))
                        done += 1
                        await sleep(1)
                    except FloodWait as e:
                        print(f"FloodWait: Waiting for {e.value} seconds")
                        await sleep(e.value)
                    except Exception as e:
                        print(f"Error deleting chat with {dialog.chat.id}: {e}")
                        er += 1

            await message.reply(
                f"<b>Successfully deleted <code>{done}</code> messages from private chats, failed to delete from <code>{er}</code> chats</b>"
            )

        elif "update" in text:
            try:
                await client.send_message(message.chat.id, "Performing update... please wait.")
                subprocess.run(["git", "pull"], check=True)
                await client.send_message(message.chat.id, "Update completed, bot is up and running.")
                time.sleep(2)
                os.execl(sys.executable, sys.executable, "-m", "main")
            except subprocess.CalledProcessError as e:
                await client.send_message(message.chat.id, f"Update failed: {e}")
            except Exception as e:
                await client.send_message(message.chat.id, f"An error occurred: {e}")

        elif "ping" in text:
            start = datetime.now()
            await sleep(1)
            end = datetime.now()
            delta_ping = round((end - start).total_seconds() * 1000, 3)
            await client.send_message(message.chat.id, f"Ping: {delta_ping} ms")

        elif "eval" in text:
            code = text.replace("eval", "").strip()
            try:
                result = eval(code)
                await message.reply(f"Result:\n{result}")
            except Exception as e:
                await message.reply(f"Error: {e}")

        elif "sh" in text:
            command = text.replace("sh", "").strip()
            try:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                await message.reply(f"Result:\n{result.decode()}")
            except subprocess.CalledProcessError as e:
                await message.reply(f"Error: {e.output.decode()}")

if __name__ == "__main__":
    while True:
        try:
            print("Running...")
            app.run()
        except (OSError, ConnectionResetError):
            print("Connection lost, trying to reconnect in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            break
                                               
