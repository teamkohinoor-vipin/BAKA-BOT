# Copyright (c) 2025 Telegram:- @brahix <DevixOP>
# Location: Supaul, Bihar 
#
# All rights reserved.
#
# This code is the intellectual property of @brahix.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: king25258069@gmail.com

import random
import httpx
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.database import groups_collection, users_collection
from baka.utils import ensure_user_exists, get_mention

# In-Memory Drop Storage
active_drops = {}
DROP_MESSAGE_COUNT = 100

WAIFU_NAMES = [
    ("Rem", "rem"), ("Ram", "ram"), ("Emilia", "emilia"), ("Asuna", "asuna"), 
    ("Zero Two", "zero two"), ("Makima", "makima"), ("Nezuko", "nezuko"),
    ("Hinata", "hinata"), ("Sakura", "sakura"), ("Mikasa", "mikasa"), 
    ("Yor", "yor"), ("Anya", "anya"), ("Power", "power")
]

async def check_drops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Use effective_message to support more update types safely
    message = update.effective_message
    chat = update.effective_chat
    if message is None or chat is None:
        return

    if chat.type == "private": return

    group = groups_collection.find_one_and_update(
        {"chat_id": chat.id}, {"$inc": {"msg_count": 1}}, upsert=True, return_document=True
    )
    
    if group.get("msg_count", 0) % DROP_MESSAGE_COUNT == 0:
        char = random.choice(WAIFU_NAMES)
        name, slug = char
        
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://api.waifu.im/search?included_tags={slug}")
            url = r.json()['images'][0]['url'] if r.status_code == 200 else "https://telegra.ph/file/5e5480760e412bd402e88.jpg"

        active_drops[chat.id] = name.lower()

        # Some waifu.im URLs may not be direct images; wrap in try/except
        try:
            await message.reply_photo(
                photo=url,
                caption=(
                    "👧 <b>A Waifu Appeared!</b>\n\n"
                    "Guess her name to collect her!\n"
                    "<i>Reply to this image.</i>"
                ),
                parse_mode=ParseMode.HTML
            )
        except Exception:
            # Fallback to a known good image URL if Telegram rejects the original
            fallback_url = "https://telegra.ph/file/5e5480760e412bd402e88.jpg"
            try:
                await message.reply_photo(
                    photo=fallback_url,
                    caption=(
                        "👧 <b>A Waifu Appeared!</b>\n\n"
                        "Guess her name to collect her!\n"
                        "<i>Reply to this image.</i>"
                    ),
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                # If even fallback fails, just skip silently
                pass

async def collect_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message

    if chat is None or msg is None:
        return

    # Only react to text messages that are replies to the waifu drop
    if not msg.text or not msg.reply_to_message:
        return

    if chat.id not in active_drops:
        return

    guess = msg.text.lower().strip()
    correct = active_drops[chat.id]
    
    if guess == correct:
        user = ensure_user_exists(msg.from_user)
        del active_drops[chat.id]
        
        rarity = random.choice(["Common", "Rare", "Epic", "Legendary"])
        waifu = {"name": correct.title(), "rarity": rarity, "date": datetime.utcnow()}
        users_collection.update_one({"user_id": user['user_id']}, {"$push": {"waifus": waifu}})
        
        await msg.reply_text(
            f"🎉 <b>Collected!</b>\n\n👤 {get_mention(user)} caught <b>{correct.title()}</b>!\n🌟 <b>Rarity:</b> {rarity}",
            parse_mode=ParseMode.HTML
        )
