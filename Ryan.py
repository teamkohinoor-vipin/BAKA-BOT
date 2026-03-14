# Copyright (c) 2025 Telegram:- @brahix <DevixOP>
# Location: Supaul, Bihar

import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

from threading import Thread
from flask import Flask
from telegram import Update 
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    ChatMemberHandler, MessageHandler, filters
)
from telegram.request import HTTPXRequest
import httpx

# --- INTERNAL IMPORTS ---
from baka.config import TOKEN, PORT
from baka.utils import track_group, log_to_channel, BOT_NAME

# --- IMPORT ALL PLUGINS ---
from baka.plugins import (
    start, economy, game, admin, broadcast, fun, events, 
    welcome, ping, chatbot, riddle, social, ai_media, 
    waifu, collection, shop, daily, stats
)

# --- FLASK SERVER ---
app = Flask(__name__)

@app.route('/')
def health():
    return "Alive"

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)


async def ping_self(context):
    url = os.getenv("PING_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.get(url)
    except Exception:
        pass


# --- STARTUP LOGIC ---
async def post_init(application):
    print("✅ Bot connected! Setting menu commands...")

    await application.bot.set_my_commands([
        ("start", "🌸 Main Menu"), 
        ("help", "📖 Command Diary"),
        ("bal", "👛 Check Wallet & Rank"), 
        ("kill", "🔪 Murder for Loot"),
        ("rob", "💰 Steal Coins"), 
        ("give", "💸 Transfer Coins"),
        ("daily", "📅 Daily Reward"),
        ("shop", "🛒 Item Shop"),
        ("ranking", "🏆 Global Leaderboard"), 
        ("wpropose", "💍 Waifu Propose"), 
        ("wmarry", "💒 Waifu Random"),
        ("propose", "💍 Marry User"), 
        ("couple", "💘 Match Maker"), 
        ("marry", "💞 Check Status"), 
        ("divorce", "💔 Break Up"),
        ("claim", "💎 Claim Group Bonus"),
        ("draw", "🎨 AI Art"), 
        ("speak", "🗣️ AI Voice"), 
        ("dice", "🎲 Gamble"),
        ("protect", "🛡️ Buy Immunity"), 
        ("revive", "✨ Revive"),
        ("chatbot", "🧠 AI Settings"), 
        ("ping", "📶 Status"),
        ("stats", "📊 Bot Statistics"),
        ("update", "🔄 Update Bot"),
    ])

    try:
        bot_info = await application.bot.get_me()
        print(f"✅ Logged in as {bot_info.username}")

        await log_to_channel(application.bot, "start", {
            "user": "System",
            "chat": "Cloud Server",
            "action": f"{BOT_NAME} (@{bot_info.username}) is now Online! 🚀"
        })

    except Exception as e:
        print(f"⚠️ Startup Log Failed: {e}")

    jq = getattr(application, "job_queue", None)
    if jq is not None:
        try:
            jq.run_repeating(ping_self, interval=300, first=60)
            print("🔁 Auto-ping job scheduled")
        except Exception as e:
            print(f"⚠️ Failed to schedule auto-ping: {e}")
    else:
        print("ℹ️ JobQueue not available")


# --- MAIN EXECUTION ---
if __name__ == '__main__':

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    if not TOKEN:
        print("CRITICAL: BOT_TOKEN missing")

    else:

        t_request = HTTPXRequest(
            connection_pool_size=16,
            connect_timeout=60.0,
            read_timeout=60.0
        )

        app_bot = (
            ApplicationBuilder()
            .token(TOKEN)
            .request(t_request)
            .post_init(post_init)
            .build()
        )

        # --- BASICS ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CommandHandler("stats", stats.stats))

        app_bot.add_handler(CallbackQueryHandler(ping.ping_callback, pattern="^sys_stats$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^return_start$"))

        # --- ECONOMY ---
        app_bot.add_handler(CommandHandler("register", economy.register))
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_"))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("claim", economy.claim))
        app_bot.add_handler(CommandHandler("daily", daily.daily))

        # --- SHOP ---
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))
        app_bot.add_handler(CommandHandler("buy", shop.buy))
        app_bot.add_handler(CallbackQueryHandler(shop.shop_callback, pattern="^shop_"))

        # --- RPG ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        app_bot.add_handler(CommandHandler("revive", game.revive))

        # --- SOCIAL ---
        app_bot.add_handler(CommandHandler("propose", social.propose))
        app_bot.add_handler(CommandHandler("marry", social.marry_status))
        app_bot.add_handler(CommandHandler("divorce", social.divorce))
        app_bot.add_handler(CommandHandler("couple", social.couple_game))
        app_bot.add_handler(CallbackQueryHandler(social.proposal_callback, pattern="^marry_"))

        # --- WAIFU ---
        app_bot.add_handler(CommandHandler("wpropose", waifu.wpropose))
        app_bot.add_handler(CommandHandler("wmarry", waifu.wmarry))

        for a in waifu.SFW_ACTIONS:
            app_bot.add_handler(CommandHandler(a, waifu.waifu_action))

        # --- FUN ---
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle_command))

        # --- AI ---
        app_bot.add_handler(CommandHandler("draw", ai_media.draw_command))
        app_bot.add_handler(CommandHandler("speak", ai_media.speak_command))
        app_bot.add_handler(CommandHandler("chatbot", chatbot.chatbot_menu))
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))
        app_bot.add_handler(CallbackQueryHandler(chatbot.chatbot_callback, pattern="^ai_"))

        # --- ADMIN ---
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("sudolist", admin.sudolist))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("update", admin.update_bot))
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern="^cnf\|"))

        # --- EVENTS ---
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))

        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, collection.collect_waifu), group=1)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, collection.check_drops), group=2)
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, riddle.check_riddle_answer), group=3)
        app_bot.add_handler(MessageHandler((filters.TEXT | filters.Sticker.ALL) & ~filters.COMMAND, chatbot.ai_message_handler), group=4)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=5)

        print("RyanBaka Bot Starting Polling...")

        app_bot.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
