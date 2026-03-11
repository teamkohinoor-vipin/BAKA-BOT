from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType

from baka.config import BOT_NAME, START_IMG_URL, HELP_IMG_URL, SUPPORT_GROUP, SUPPORT_CHANNEL, OWNER_LINK
from baka.utils import ensure_user_exists, get_mention, track_group, log_to_channel, SUDO_USERS


# --- IMAGES ---
SUDO_IMG = "https://files.catbox.moe/gyi5iu.jpg"


# --- KEYBOARDS ---

def get_start_keyboard(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐔𝐩𝐝𝐚𝐭𝐞𝐬", url=SUPPORT_CHANNEL),
         InlineKeyboardButton("💬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_GROUP)],

        [InlineKeyboardButton("➕ 𝐀𝐝𝐝 𝐌𝐞 𝐁𝐚𝐛𝐲 ➕",
         url=f"https://t.me/{bot_username}?startgroup=true")],

        [InlineKeyboardButton("📖 𝐇𝐞𝐥𝐩 𝐌𝐞𝐧𝐮", callback_data="help_main"),
         InlineKeyboardButton("♛ 𝐎𝐰𝐧𝐞𝐫", url=OWNER_LINK)]
    ])


def get_help_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💍 𝐒𝐨𝐜𝐢𝐚𝐥", callback_data="help_social"),
         InlineKeyboardButton("💰 𝐄𝐜𝐨𝐧𝐨𝐦𝐲", callback_data="help_economy")],

        [InlineKeyboardButton("⚔️ 𝐑𝐏𝐆", callback_data="help_rpg"),
         InlineKeyboardButton("🧠 𝐀𝐈 & 𝐅𝐮𝐧", callback_data="help_fun")],

        [InlineKeyboardButton("🔒 𝐀𝐧𝐨𝐧𝐲𝐦𝐨𝐮𝐬", callback_data="help_anonymous"),
         InlineKeyboardButton("⚙️ 𝐆𝐫𝐨𝐮𝐩", callback_data="help_group")],

        [InlineKeyboardButton("🔐 𝐒𝐮𝐝𝐨", callback_data="help_sudo"),
         InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="return_start")]
    ])


def get_back_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="help_main")]]
    )


# --- START COMMAND ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    chat = update.effective_chat

    ensure_user_exists(user)
    track_group(chat, user)

    caption = (
        f"👋 <b>Kon'nichiwa</b> {get_mention(user)}! (≧▽≦)\n\n"
        f"『 <b>{BOT_NAME}</b> 』\n"
        f"<i>The Aesthetic AI-Powered RPG Bot!</i> 🌸\n\n"

        f"🎮 <b>𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬:</b>\n"
        f"‣ <b>RPG:</b> Kill, Rob (100%), Protect\n"
        f"‣ <b>Social:</b> Marry, Couple\n"
        f"‣ <b>Economy:</b> Claim, Give\n"
        f"‣ <b>AI:</b> Sassy Chatbot\n"
        f"‣ <b>Anonymous:</b> Secrets, Roasts, Confessions\n\n"

        f"💭 <b>𝐍𝐞𝐞𝐝 𝐇𝐞𝐥𝐩?</b>\n"
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

        if START_IMG_URL.startswith("http"):
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

    await update.message.reply_photo(
        photo=HELP_IMG_URL,
        caption=f"📖 <b>{BOT_NAME} 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐃𝐢𝐚𝐫𝐲</b> 🌸\n\n"
                "<i>Select a category below to explore all features!</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_help_keyboard()
    )


# --- CALLBACK HANDLER ---

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()  # important fix

    data = query.data

    if data == "return_start":
        await start(update, context)
        return

    if data == "help_main":
        await query.message.edit_media(
            InputMediaPhoto(
                media=HELP_IMG_URL,
                caption=f"📖 <b>{BOT_NAME} 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐃𝐢𝐚𝐫𝐲</b> 🌸\n\n"
                        "<i>Select a category below to explore all features!</i>",
                parse_mode=ParseMode.HTML
            ),
            reply_markup=get_help_keyboard()
        )
        return

    target_photo = HELP_IMG_URL
    kb = get_back_keyboard()
    text = ""


    # --- SOCIAL ---
    if data == "help_social":
        text = (
            "💍 <b>𝐒𝐨𝐜𝐢𝐚𝐥 & 𝐋𝐨𝐯𝐞</b>\n\n"

            "<b>/propose @user</b>\n"
            "↳ Marry someone (5% Tax Perk).\n\n"

            "<b>/marry</b>\n"
            "↳ Check relationship status.\n\n"

            "<b>/divorce</b>\n"
            "↳ Break up (Cost: 2k).\n\n"

            "<b>/couple</b>\n"
            "↳ Matchmaking Fun!"
        )


    # --- ECONOMY ---
    elif data == "help_economy":
        text = (
            "💰 <b>𝐄𝐜𝐨𝐧𝐨𝐦𝐲 & 𝐒𝐡𝐨𝐩</b>\n\n"

            "<b>/bal</b>\n"
            "↳ Check Wallet, Rank & Inventory.\n\n"

            "<b>/shop</b>\n"
            "↳ Buy Weapons & Armor.\n\n"

            "<b>/give [amt] [user]</b>\n"
            "↳ Transfer (10% Tax).\n\n"

            "<b>/claim</b>\n"
            "↳ Group Bonus (2k).\n\n"

            "<b>/daily</b>\n"
            "↳ Streak Rewards.\n\n"

            "<b>/ranking</b>\n"
            "↳ Global Leaderboards."
        )


    # --- RPG ---
    elif data == "help_rpg":
        text = (
            "⚔️ <b>𝐑𝐏𝐆 & 𝐖𝐚𝐫</b>\n\n"

            "<b>/kill [user]</b>\n"
            "↳ Murder. 50% Chance to loot Items!\n\n"

            "<b>/rob [amt] [user]</b>\n"
            "↳ Steal coins + 20% Chance to steal Items.\n\n"

            "<b>/protect 1d</b>\n"
            "↳ Buy Shield. Protects partner too!\n\n"

            "<b>/revive</b>\n"
            "↳ Revive instantly for 500 coins."
        )


    # --- FUN ---
    elif data == "help_fun":
        text = (
            "🧠 <b>𝐀𝐈 & 𝐅𝐮𝐧</b>\n\n"

            "<b>/draw [prompt]</b> ➪ AI Art\n"
            "<b>/speak [text]</b> ➪ Anime Voice\n"
            "<b>/chatbot</b> ➪ AI Settings\n"
            "<b>/riddle</b> ➪ AI Quiz\n"
            "<b>/dice</b> | <b>/slots</b> ➪ Gambling"
        )


    # --- ANONYMOUS ---
    elif data == "help_anonymous":
        text = (
            "🔒 <b>𝐀𝐧𝐨𝐧𝐲𝐦𝐨𝐮𝐬 𝐒𝐞𝐜𝐫𝐞𝐭𝐬 & 𝐆𝐚𝐦𝐞𝐬</b>\n\n"

            "<b>/secret @user message</b> ➪ Secret message\n"
            "<b>/confess message</b> ➪ Anonymous confession\n"
            "<b>/crush @user</b> ➪ Crush matching\n\n"

            "<b>/roast @user</b>\n"
            "<b>/truthordare</b>\n"
            "<b>/wyr</b>\n"
            "<b>/neverhaveiever</b>\n"
            "<b>/hotornot @user</b>\n"
            "<b>/rate @user</b>\n"
            "<b>/compliment @user</b>\n\n"

            "<b>/story</b>\n"
            "<b>/continue</b>\n\n"

            "<b>/spoll</b> ➪ Secret poll"
        )


    # --- GROUP ---
    elif data == "help_group":
        text = (
            "⚙️ <b>𝐆𝐫𝐨𝐮𝐩 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬</b>\n\n"

            "<b>/welcome on/off</b> ➪ Welcome Images\n"
            "<b>/ping</b> ➪ System Status"
        )


    # --- SUDO ---
    elif data == "help_sudo":

        if query.from_user.id not in SUDO_USERS:
            return await query.answer("❌ Baka! Owner Only!", show_alert=True)

        target_photo = SUDO_IMG

        text = (
            "🔐 <b>𝐒𝐮𝐝𝐨 𝐏𝐚𝐧𝐞𝐥</b>\n\n"

            "<b>/addcoins</b>\n"
            "<b>/rmcoins</b>\n"
            "<b>/freerevive</b>\n"
            "<b>/unprotect</b>\n"
            "<b>/broadcast</b>\n\n"

            "<b>👑 Owner Only</b>\n"
            "<b>/update</b>\n"
            "<b>/addsudo</b>\n"
            "<b>/rmsudo</b>\n"
            "<b>/cleandb</b>"
        )

    try:
        await query.message.edit_media(
            InputMediaPhoto(media=target_photo, caption=text, parse_mode=ParseMode.HTML),
            reply_markup=kb
        )
    except:
        await query.message.edit_caption(
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )
