# Copyright (c) 2025 Telegram:- @brahix <DevixOP>
# Location: Supaul, Bihar 
#
# All rights reserved.
#
# This code is the intellectual property of @brahix.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
# Contact for permissions:
# Email: king25258069@gmail.com

from pymongo import MongoClient
import certifi
from baka.config import MONGO_URI

# Initialize Connection
RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# --- DEFINING COLLECTIONS ---
users_collection = db["users"]           # Stores balance, inventory, waifus, stats
groups_collection = db["groups"]         # Tracks group settings (welcome, claim status)
sudoers_collection = db["sudoers"]       # Stores admin IDs
chatbot_collection = db["chatbot"]       # Stores AI chat history per group/user
riddles_collection = db["riddles"]       # Stores active riddles and answers
nsfw_media_collection = db["nsfw_media"] # Caches known NSFW media by unique file id
# Anonymous Secrets Collections
secrets_collection = db["secrets"]       # Stores secret messages with unlock tasks
confessions_collection = db["confessions"] # Stores anonymous confessions
crushes_collection = db["crushes"]       # Stores crush matches
polls_collection = db["secret_polls"]    # Stores secret polls
tea_spills_collection = db["tea_spills"] # Stores daily tea spills
truth_dare_collection = db["truth_dare"] # Stores truth or dare games
story_chain_collection = db["story_chain"] # Stores story chain games
compliment_collection = db["compliments"] # Stores anonymous compliments
guess_who_collection = db["guess_who"]   # Stores guess who games

# --- AI CONFIGURATION COLLECTIONS ---
ai_config_collection = db["ai_config"]     # Stores AI model settings and API keys

# --- AI DATABASE FUNCTIONS ---

def get_all_keys():
    """Get all available Gemini API keys."""
    doc = ai_config_collection.find_one({"type": "gemini_keys"})
    if doc and "keys" in doc:
        return doc["keys"]
    return []

def get_sticker_packs():
    """Get all available sticker pack names."""
    doc = ai_config_collection.find_one({"type": "sticker_packs"})
    if doc and "packs" in doc:
        return doc["packs"]
    return ["BabyVideoSticker", "Billa20"]  # Default fallback

def get_active_chat_model():
    """Get the currently active AI model (gemini, groq, or cerebras)."""
    doc = ai_config_collection.find_one({"type": "active_model"})
    if doc and "model" in doc:
        return doc["model"]
    return "gemini"  # Default to Gemini

def get_groq_api_key():
    """Get Groq API key."""
    doc = ai_config_collection.find_one({"type": "groq_key"})
    if doc and "key" in doc:
        return doc["key"]
    return None

def get_cerebras_api_key():
    """Get Cerebras API key."""
    doc = ai_config_collection.find_one({"type": "cerebras_key"})
    if doc and "key" in doc:
        return doc["key"]
    return None