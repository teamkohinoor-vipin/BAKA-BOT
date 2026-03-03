

import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.database import groups_collection
from baka.utils import get_mention, ensure_user_exists
from baka.config import WELCOME_IMG_URL, BOT_NAME, START_IMG_URL, SUPPORT_GROUP

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    for member in update.message.new_chat_members:
        # --- 🤖 BOT ADDED TO GROUP ---
        if member.id == context.bot.id:
            adder = update.message.from_user
            ensure_user_exists(adder)
            
            groups_collection.update_one({"chat_id": chat.id}, {"$set": {"title": chat.title}}, upsert=True)
            
            txt = (
                f"🌸 <b>𝐀𝐫𝐢𝐠𝐚𝐭𝐨 {get_mention(adder)}!</b>\n\n"
                f"Thanks for adding <b>{chat.title}</b>! ✨\n\n"
                f"🎁 <b>First Time Bonus:</b>\n"
                f"Type <code>/claim</code> fast to get 2,000 Coins!\n"
                f"(Only the first person gets it!)"
            )
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_GROUP)]])
            
            # Use Welcome Image (gyi5iu.jpg) for this interaction
            try: await update.message.reply_photo(WELCOME_IMG_URL, caption=txt, parse_mode=ParseMode.HTML, reply_markup=kb)
            except: await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=kb)

        # --- 👤 USER JOINED GROUP ---
        else:
            ensure_user_exists(member)
            greetings = ["Hello", "Hiii", "Welcome", "Kon'nichiwa"]
            greet = random.choice(greetings)
            first_name = member.first_name or "User"
            user_link = f"<a href='tg://user?id={member.id}'>{first_name}</a>"
            txt = f"👋 <b>{greet} {user_link}!</b>\n\nWelcome to <b>{chat.title}</b> 🌸\nDon't forget to /register!"
            try: await update.message.reply_photo(WELCOME_IMG_URL, caption=txt, parse_mode=ParseMode.HTML)
            except: await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
