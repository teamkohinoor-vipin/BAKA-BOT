# Copyright (c) 2025 Telegram:- @brahix <DevixOP>
# Location: Supaul, Bihar 
#
# All rights reserved.
#
# This code is the intellectual property of @brahix.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: king25258069@gmail.com

import os
# --- CRITICAL FIX: MUST BE AT THE VERY TOP ---
# This prevents Heroku crashing due to Git/Path issues
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
# ---------------------------------------------

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
    waifu, collection, shop, daily, anonymous_secrets
)

# --- FLASK SERVER (Health Check) ---
app = Flask(__name__)

@app.route('/')
def health(): 
    return "Alive"

def run_flask(): 
    # Run on 0.0.0.0 to bind to Heroku's external port
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

async def ping_self(context):
    """Periodic self-ping to keep web dyno awake."""
    # Prefer explicit PING_URL, else Render's external URL, else skip
    url = os.getenv("PING_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.get(url)
    except Exception:
        # Silently ignore ping failures
        pass


# --- STARTUP LOGIC ---
async def post_init(application):
    """Runs immediately after bot connects to Telegram."""
    print("✅ Bot connected! Setting menu commands...")
    
    # Set the blue "Menu" button in Telegram
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
        ("update", "🔄 Update Bot"),
    ])
    
    try:
        bot_info = await application.bot.get_me()
        print(f"✅ Logged in as {bot_info.username}")

        # Send "Online" Log to Channel
        await log_to_channel(application.bot, "start", {
            "user": "System",
            "chat": "Cloud Server",
            "action": f"{BOT_NAME} (@{bot_info.username}) is now Online! 🚀"
        })
    except Exception as e:
        print(f"⚠️ Startup Log Failed: {e}")

    # Schedule periodic self-ping every 5 minutes to keep web alive (if JobQueue available)
    jq = getattr(application, "job_queue", None)
    if jq is not None:
        try:
            jq.run_repeating(ping_self, interval=300, first=60)
            print("🔁 Auto-ping job scheduled (every 5 minutes).")
        except Exception as e:
            print(f"⚠️ Failed to schedule auto-ping: {e}")
    else:
        print("ℹ️ JobQueue not available – auto-ping disabled. Install PTB with job-queue extra to enable it.")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # 1. Start Web Server (Background Thread)
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # 2. Check Token
    if not TOKEN:
        print("CRITICAL: BOT_TOKEN is missing. Check baka/config.py or Env Vars.")
    else:
        # 3. Configure Network (High Timeouts for Stability)
        t_request = HTTPXRequest(connection_pool_size=16, connect_timeout=60.0, read_timeout=60.0)
        
        # 4. Build Application
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # ================= REGISTER HANDLERS =================
        
        # --- Basics ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CallbackQueryHandler(ping.ping_callback, pattern="^sys_stats$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^return_start$"))
        
        # --- Economy ---
        app_bot.add_handler(CommandHandler("register", economy.register))
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_"))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("claim", economy.claim))
        app_bot.add_handler(CommandHandler("daily", daily.daily))
        
        # --- Shop ---
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))
        app_bot.add_handler(CommandHandler("buy", shop.buy))
        app_bot.add_handler(CallbackQueryHandler(shop.shop_callback, pattern="^shop_"))
        
        # --- RPG / Game ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        
        # --- Social ---
        app_bot.add_handler(CommandHandler("propose", social.propose))
        app_bot.add_handler(CommandHandler("marry", social.marry_status))
        app_bot.add_handler(CommandHandler("divorce", social.divorce))
        app_bot.add_handler(CommandHandler("couple", social.couple_game))
        app_bot.add_handler(CallbackQueryHandler(social.proposal_callback, pattern="^marry_"))
        
        # --- Waifu System ---
        app_bot.add_handler(CommandHandler("wpropose", waifu.wpropose))
        app_bot.add_handler(CommandHandler("wmarry", waifu.wmarry))
        for a in waifu.SFW_ACTIONS: 
            app_bot.add_handler(CommandHandler(a, waifu.waifu_action))

        # --- Fun / AI / Media ---
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle_command))
        app_bot.add_handler(CommandHandler("draw", ai_media.draw_command))
        app_bot.add_handler(CommandHandler("speak", ai_media.speak_command))
        app_bot.add_handler(CommandHandler("chatbot", chatbot.chatbot_menu)) 
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))           
        app_bot.add_handler(CallbackQueryHandler(chatbot.chatbot_callback, pattern="^ai_"))
        
        # --- Anonymous Secrets ---
        app_bot.add_handler(CommandHandler("secret", anonymous_secrets.secret_command))
        app_bot.add_handler(CommandHandler("roast", anonymous_secrets.roast_command))
        app_bot.add_handler(CommandHandler("confess", anonymous_secrets.confess_command))
        app_bot.add_handler(CommandHandler("crush", anonymous_secrets.crush_command))
        app_bot.add_handler(CommandHandler("spoll", anonymous_secrets.spoll_command))
        app_bot.add_handler(CommandHandler("truthordare", anonymous_secrets.truth_dare_command))
        app_bot.add_handler(CommandHandler("wyr", anonymous_secrets.wyr_command))
        app_bot.add_handler(CommandHandler("compliment", anonymous_secrets.compliment_command))
        app_bot.add_handler(CommandHandler("story", anonymous_secrets.story_command))
        app_bot.add_handler(CommandHandler("continue", anonymous_secrets.continue_story_command))
        app_bot.add_handler(CommandHandler("rate", anonymous_secrets.rate_command))
        app_bot.add_handler(CommandHandler("hotornot", anonymous_secrets.hotornot_command))
        app_bot.add_handler(CommandHandler("neverhaveiever", anonymous_secrets.neverhaveiever_command))
        app_bot.add_handler(CallbackQueryHandler(anonymous_secrets.vote_handler, pattern="^vote_"))
        app_bot.add_handler(CallbackQueryHandler(anonymous_secrets.react_handler, pattern="^react_"))
        app_bot.add_handler(CallbackQueryHandler(anonymous_secrets.truth_dare_complete_handler, pattern="^td_complete_"))
        app_bot.add_handler(CallbackQueryHandler(anonymous_secrets.wyr_vote_handler, pattern="^wyr_"))
        app_bot.add_handler(CallbackQueryHandler(anonymous_secrets.rate_handler, pattern="^rate_"))
        app_bot.add_handler(CallbackQueryHandler(anonymous_secrets.hotornot_vote_handler, pattern="^hot_"))
        app_bot.add_handler(CallbackQueryHandler(anonymous_secrets.neverhaveiever_vote_handler, pattern="^nhe_")) 
        
        # --- Admin & System ---
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
        
        # --- EVENTS & MESSAGE LISTENERS (ORDER IS CRITICAL) ---
        
        # 1. Chat Member Updates (Join/Left Logs)
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        
        # 2. Welcome New Users
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))
        
        # 3. Collection (Waifu Guessing) - Group 1
        # Catches correct answers before AI sees them
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, collection.collect_waifu), group=1)
        
        # 4. Drop Check (Message Counting) - Group 2
        # Runs on every message to count for drops
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, collection.check_drops), group=2)
        
        # 5. Riddle Answer - Group 3
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, riddle.check_riddle_answer), group=3)
        
        # 5.5. Anonymous Secrets Handlers - Group 3.5 (before AI chat)
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, anonymous_secrets.unlock_handler), group=3)
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, anonymous_secrets.confess_support_handler), group=3)
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, anonymous_secrets.message_tracker), group=3)
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, anonymous_secrets.tea_spill_reply_handler), group=3)
        
        # 6. AI Chat (General Talk & Stickers) - Group 4
        # Must be later so it doesn't reply to game inputs
        app_bot.add_handler(MessageHandler((filters.TEXT | filters.Sticker.ALL) & ~filters.COMMAND, chatbot.ai_message_handler), group=4)
        
        # 7. Track Group (Silent db update) - Group 5
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=5)

        print("RyanBaka Bot Starting Polling...")
        
        # 8. Start Polling
        app_bot.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

