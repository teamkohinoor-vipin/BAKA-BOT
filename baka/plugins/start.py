from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType

from baka.config import START_IMG_URL, HELP_IMG_URL, SUPPORT_GROUP, SUPPORT_CHANNEL, OWNER_LINK
from baka.utils import ensure_user_exists, get_mention, track_group, log_to_channel, SUDO_USERS


# --- IMAGES ---
SUDO_IMG = "https://i.ibb.co/cKWvyMFR/IMG-20260303-120051-514.jpg"


# --- KEYBOARDS ---

def get_start_keyboard(bot_username):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 𝐔𝐩𝐝𝐚𝐭𝐞𝐬", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("💬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton(
                "➕ 𝐀𝐝𝐝 𝐌𝐞 𝐁𝐚𝐛𝐲 ➕",
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("📖 𝐇𝐞𝐥𝐩 𝐌𝐞𝐧𝐮", callback_data="help_main"),
            InlineKeyboardButton("♛ 𝐎𝐰𝐧𝐞𝐫", url=OWNER_LINK)
        ]
    ])


def get_help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💍 𝐒𝐨𝐜𝐢𝐚𝐥", callback_data="help_social"),
            InlineKeyboardButton("💰 𝐄𝐜𝐨𝐧𝐨𝐦𝐲", callback_data="help_economy")
        ],
        [
            InlineKeyboardButton("⚔️ 𝐑𝐏𝐆", callback_data="help_rpg"),
            InlineKeyboardButton("🧠 𝐀𝐈 & 𝐅𝐮𝐧", callback_data="help_fun")
        ],
        [
            InlineKeyboardButton("🔒 𝐀𝐧𝐨𝐧𝐲𝐦𝐨𝐮𝐬", callback_data="help_anonymous"),
            InlineKeyboardButton("⚙️ 𝐆𝐫𝐨𝐮𝐩", callback_data="help_group")
        ],
        [
            InlineKeyboardButton("🔐 𝐒𝐮𝐝𝐨", callback_data="help_sudo"),
            InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="return_start")
        ]
    ])


def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="help_main")]
    ])


# --- START COMMAND ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    chat = update.effective_chat

    bot_name = context.bot.first_name

    caption = (
        f"👋 <b>Hello</b> {get_mention(user)}! (≧▽≦)\n\n"
        f"『 <b>{bot_name}</b> 』\n"
        f"<i>The Aesthetic AI-Powered RPG Bot!</i> 🌸\n\n"
        f"🎮 <b>Features:</b>\n"
        f"‣ RPG\n"
        f"‣ Social\n"
        f"‣ Economy\n"
        f"‣ AI Chatbot\n"
        f"‣ Anonymous Games\n\n"
        f"💭 <b>Need Help?</b>\n"
        f"Click the buttons below!"
    )

    kb = get_start_keyboard(context.bot.username)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_media(
                InputMediaPhoto(
                    media=START_IMG_URL,
                    caption=caption,
                    parse_mode=ParseMode.HTML
                ),
                reply_markup=kb
            )
        except:
            await update.callback_query.message.edit_caption(
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=kb
            )

    else:

        if START_IMG_URL and START_IMG_URL.startswith("http"):
            try:
                await update.message.reply_photo(
                    photo=START_IMG_URL,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb
                )
            except:
                await update.message.reply_text(
                    caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb
                )
        else:
            await update.message.reply_text(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=kb
            )

    if chat.type == ChatType.PRIVATE and not update.callback_query:
        await log_to_channel(
            context.bot,
            "command",
            {
                "user": f"{get_mention(user)} (`{user.id}`)",
                "action": "Started Bot",
                "chat": "Private"
            }
        )


# --- HELP COMMAND ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    bot_name = context.bot.first_name

    await update.message.reply_photo(
        photo=HELP_IMG_URL,
        caption=f"📖 <b>{bot_name} Command Diary</b> 🌸\n\n<i>Select a category below to explore all features!</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_help_keyboard()
    )


# --- CALLBACK HANDLER ---

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()  # ⭐ FIX ADDED
    data = query.data

    bot_name = context.bot.first_name

    if data == "return_start":
        await start(update, context)
        return

    if data == "help_main":

        try:
            await query.message.edit_media(
                InputMediaPhoto(
                    media=HELP_IMG_URL,
                    caption=f"📖 <b>{bot_name} 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐃𝐢𝐚𝐫𝐲</b> 🌸\n\n<i>Select a category below to explore all features!</i>",
                    parse_mode=ParseMode.HTML
                ),
                reply_markup=get_help_keyboard()
            )

        except:

            await query.message.edit_caption(
                caption=f"📖 <b>{bot_name} 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐃𝐢𝐚𝐫𝐲</b> 🌸\n\n<i>Select a category below to explore all features!</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=get_help_keyboard()
            )

        return

    target_photo = HELP_IMG_URL
    kb = get_back_keyboard()
    text = ""

    if data == "help_social":
        text = (
            "💍 <b>𝐒𝐨𝐜𝐢𝐚𝐥 & 𝐋𝐨𝐯𝐞</b>\n\n"
            "<b>/propose @user</b>\n"
            "<b>/marry</b>\n"
            "<b>/divorce</b>\n"
            "<b>/couple</b>"
        )

    elif data == "help_economy":
        text = (
            "💰 <b>𝐄𝐜𝐨𝐧𝐨𝐦𝐲</b>\n\n"
            "<b>/bal</b>\n"
            "<b>/shop</b>\n"
            "<b>/give</b>\n"
            "<b>/claim</b>\n"
            "<b>/daily</b>\n"
            "<b>/ranking</b>"
        )

    elif data == "help_rpg":
        text = (
            "⚔️ <b>𝐑𝐏𝐆</b>\n\n"
            "<b>/kill</b>\n"
            "<b>/rob</b>\n"
            "<b>/protect</b>\n"
            "<b>/revive</b>"
        )

    elif data == "help_fun":
        text = (
            "🧠 <b>𝐀𝐈 & 𝐅𝐮𝐧</b>\n\n"
            "<b>/draw</b>\n"
            "<b>/speak</b>\n"
            "<b>/chatbot</b>\n"
            "<b>/riddle</b>\n"
            "<b>/dice</b>\n"
            "<b>/slots</b>"
        )

    elif data == "help_group":
        text = (
            "⚙️ <b>𝐆𝐫𝐨𝐮𝐩</b>\n\n"
            "<b>/welcome</b>\n"
            "<b>/ping</b>"
        )

    elif data == "help_sudo":

        if query.from_user.id not in SUDO_USERS:
            return await query.answer("❌ Owner Only!", show_alert=True)

        target_photo = SUDO_IMG

        text = (
            "🔐 <b>𝐒𝐮𝐝𝐨</b>\n\n"
            "<b>/addcoins</b>\n"
            "<b>/rmcoins</b>\n"
            "<b>/freerevive</b>\n"
            "<b>/unprotect</b>\n"
            "<b>/broadcast</b>\n"
            "<b>/update</b>\n"
            "<b>/addsudo</b>\n"
            "<b>/rmsudo</b>\n"
            "<b>/cleandb</b>"
        )

    try:
        await query.message.edit_media(
            InputMediaPhoto(
                media=target_photo,
                caption=text,
                parse_mode=ParseMode.HTML
            ),
            reply_markup=kb
        )

    except:
        await query.message.edit_caption(
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )
