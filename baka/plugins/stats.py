# Stats Command

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from baka.database import get_total_users, get_total_groups
import time
import platform
import psutil

START_TIME = time.time()

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users = get_total_users()
    groups = get_total_groups()

    uptime = time.time() - START_TIME
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    text = f"""
📊 **Bot Statistics**

👤 Users : {users}
👥 Groups : {groups}

⚙ System
🧠 CPU Usage : {cpu}%
💾 RAM Usage : {ram}%

⏳ Uptime : {hours}h {minutes}m {seconds}s
🐍 Python : {platform.python_version()}
"""

    await update.message.reply_text(text)

def setup(application):
    application.add_handler(CommandHandler("stats", stats))
