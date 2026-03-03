import random
import urllib.parse
from typing import Optional

import httpx
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction, ChatType, ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from baka.database import chatbot_collection, get_sticker_packs

# === ZEFROn API (Cerebras / multi-model backend) ===
ZEFROn_API_URL = "https://zefronapi22.vrajiv830.workers.dev"


# === Low‑level ZEFROn call ===
async def _call_zefron_api(prompt: str) -> Optional[str]:
    """
    Call the ZEFROn proxy API with a simple prompt string.
    The worker returns JSON like: {"response": "..."}.
    """
    try:
        url = f"{ZEFROn_API_URL}/?prompt={urllib.parse.quote(prompt)}"

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.get(url, timeout=25.0)
            resp.raise_for_status()

            data = resp.json()
            if isinstance(data, dict):
                # Web result example: {"response": "Hello. How can I assist you today?"}
                key = "response" if "response" in data else "Response"
                if key in data and isinstance(data[key], str):
                    text = data[key].strip()
                    if text:
                        return text
    except Exception as e:
        print(f"[ZEFROn] API error: {e}")

    return None


# === Chat‑style wrapper over ZEFROn ===
async def call_model_api(messages, max_tokens: int = 50) -> Optional[str]:
    """
    Convert OpenAI-style chat messages into a plain prompt for ZEFROn.
    messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if not content:
            continue
        if role == "system":
            parts.append(f"System: {content}")
        elif role == "assistant":
            parts.append(f"Assistant: {content}")
        else:
            parts.append(f"User: {content}")

    # Guide the model to reply once
    prompt = "\n".join(parts) + "\nAssistant:"
    return await _call_zefron_api(prompt)


# === Generate AI response (BAKA style) ===
async def get_ai_response(chat_id: int, user_input: str, user_name: str, user_id: int) -> tuple[str, bool]:
    """
    Main AI responder.
    Returns (reply_text, is_code) where is_code tells if user was talking about code.
    """
    # Per-user history key (per chat + per user) to avoid khichdi in groups
    history_key = f"{chat_id}:{user_id}"

    history = []
    if chatbot_collection is not None:
        doc = chatbot_collection.find_one({"chat_id": history_key}) or {}
        history = doc.get("history", [])

    # Build short history (last 6 turns) and send directly to ZEFROn.
    # Persona, style, and length rules are handled fully inside the Worker.
    msgs = history[-6:]
    msgs.append({"role": "user", "content": user_input})

    reply = await call_model_api(msgs, 60)
    if not reply:
        # Simple fallback if API fails
        reply = "Thoda issue aa gaya, baad me fir try karein? 🥲"

    # Save history (keep last 10 entries)
    if chatbot_collection is not None:
        new_history = (history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": reply},
        ])[-10:]

        chatbot_collection.update_one(
            {"chat_id": history_key},
            {"$set": {"history": new_history}},
            upsert=True,
        )

    # Direct API reply; no extra processing here.
    return reply, False


# === Send random sticker (from DB) ===
async def send_ai_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        packs = get_sticker_packs()
        if not packs:
            return
        # Expect DB to store sticker set names, e.g. "RandomByDarkzenitsu"
        set_name = random.choice(packs)
        s = await context.bot.get_sticker_set(set_name)
        if s.stickers:
            await update.message.reply_sticker(random.choice(s.stickers).file_id)
    except Exception:
        # Sticker errors should never crash the bot
        pass


# === Automatic AI message handler ===
async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message or update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    chat = update.effective_chat
    text = msg.text
    lowered = text.lower().strip()

    # --- Decide when to reply ---
    should_reply = False

    if chat.type == ChatType.PRIVATE:
        # Always reply in PM
        should_reply = True
    else:
        # Group / supergroup logic
        # Respect enabled flag
        doc = chatbot_collection.find_one({"chat_id": chat.id}) or {}
        is_enabled = doc.get("enabled", True)
        if not is_enabled:
            return

        bot_username = (context.bot.username or "").lower()

        if msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id:
            # Replying to bot
            should_reply = True
        elif bot_username and f"@{bot_username}" in lowered:
            # Mentioning the bot
            should_reply = True
        elif any(lowered.startswith(k) for k in ["hey", "hello", "siya","gn","gm",]):
            # Soft trigger words
            should_reply = True

    if not should_reply:
        return

    # --- Generate and send reply ---
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    reply, is_code = await get_ai_response(chat.id, text, msg.from_user.first_name, msg.from_user.id)

    # Send reply exactly as returned by the Worker
    await msg.reply_text(reply)

    # Send random sticker 80% of the time in groups / PM
    if random.random() < 0.8:
        await send_ai_sticker(update, context)


# === /ask command handler ===
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("💬 Please type something after /ask")
        return

    user_input = " ".join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    reply, is_code = await get_ai_response(
        update.effective_chat.id,
        user_input,
        update.effective_user.first_name,
        update.effective_user.id,
    )
    await update.message.reply_text(reply)


# === MENU HANDLERS (keep backward compatibility with existing /chatbot UI) ===
async def chatbot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("Hey, I'm active in DM!", parse_mode=None)

    member = await chat.get_member(user.id)
    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("You're not an admin!", parse_mode=None)

    doc = chatbot_collection.find_one({"chat_id": chat.id}) or {}
    is_enabled = doc.get("enabled", True)
    status = "Enabled" if is_enabled else "Disabled"

    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Enable", callback_data="ai_enable"),
                InlineKeyboardButton("Disable", callback_data="ai_disable"),
            ],
            [InlineKeyboardButton("Reset", callback_data="ai_reset")],
        ]
    )
    await update.message.reply_text(
        f"AI Settings\nStatus: {status}\nI'm active by default!",
        parse_mode=None,
        reply_markup=kb,
    )


async def chatbot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    member = await query.message.chat.get_member(query.from_user.id)
    if member.status not in ["administrator", "creator"]:
        return await query.answer("Only admin.", show_alert=True)

    data = query.data
    chat_id = query.message.chat.id

    if data == "ai_enable":
        chatbot_collection.update_one({"chat_id": chat_id}, {"$set": {"enabled": True}}, upsert=True)
        await query.message.edit_text("Enabled!\nAb maza ayega!", parse_mode=None)
    elif data == "ai_disable":
        chatbot_collection.update_one({"chat_id": chat_id}, {"$set": {"enabled": False}}, upsert=True)
        await query.message.edit_text("Disabled!\nJa rahi hu...", parse_mode=None)
    elif data == "ai_reset":
        chatbot_collection.update_one({"chat_id": chat_id}, {"$set": {"history": []}}, upsert=True)
        await query.answer("Sab bhool gayi!", show_alert=True)


# === SHARED AI FUNCTION FOR OTHER PLUGINS ===
async def ask_mistral_raw(system_prompt: str, user_input: str, max_tokens: int = 150) -> Optional[str]:
    """
    Backwards-compatible helper used by other plugins.
    Uses the same ZEFROn backend with a custom system prompt.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    result = await call_model_api(messages, max_tokens)
    return result.strip() if result else None