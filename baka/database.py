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

# -----------------------------
# DATABASE CONNECTION
# -----------------------------

RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# -----------------------------
# COLLECTIONS
# -----------------------------

users_collection = db["users"]           
groups_collection = db["groups"]         
sudoers_collection = db["sudoers"]       
chatbot_collection = db["chatbot"]       
riddles_collection = db["riddles"]       
nsfw_media_collection = db["nsfw_media"]

# Anonymous Secrets
secrets_collection = db["secrets"]
confessions_collection = db["confessions"]
crushes_collection = db["crushes"]
polls_collection = db["secret_polls"]
tea_spills_collection = db["tea_spills"]
truth_dare_collection = db["truth_dare"]
story_chain_collection = db["story_chain"]
compliment_collection = db["compliments"]
guess_who_collection = db["guess_who"]

# AI Configuration
ai_config_collection = db["ai_config"]

# -----------------------------
# AI DATABASE FUNCTIONS
# -----------------------------

def get_all_keys():
    """Return all Gemini API keys."""
    doc = ai_config_collection.find_one({"type": "gemini_keys"})
    if doc and "keys" in doc:
        return doc["keys"]
    return []

def get_sticker_packs():
    """Return sticker packs."""
    doc = ai_config_collection.find_one({"type": "sticker_packs"})
    if doc and "packs" in doc:
        return doc["packs"]
    return ["BabyVideoSticker", "Billa20"]

def get_active_chat_model():
    """Return active AI model."""
    doc = ai_config_collection.find_one({"type": "active_model"})
    if doc and "model" in doc:
        return doc["model"]
    return "gemini"

def get_groq_api_key():
    """Return Groq API key."""
    doc = ai_config_collection.find_one({"type": "groq_key"})
    if doc and "key" in doc:
        return doc["key"]
    return None

def get_cerebras_api_key():
    """Return Cerebras API key."""
    doc = ai_config_collection.find_one({"type": "cerebras_key"})
    if doc and "key" in doc:
        return doc["key"]
    return None


# -----------------------------
# USER FUNCTIONS
# -----------------------------

def add_user(user_id: int):
    """Add new user if not exists."""
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({
            "user_id": user_id,
            "balance": 0,
            "inventory": [],
            "waifus": [],
            "stats": {}
        })

def get_user(user_id: int):
    """Get user data."""
    return users_collection.find_one({"user_id": user_id})

def update_balance(user_id: int, amount: int):
    """Update user balance."""
    users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )

# -----------------------------
# GROUP FUNCTIONS
# -----------------------------

def add_group(chat_id: int):
    """Add group if not exists."""
    if not groups_collection.find_one({"chat_id": chat_id}):
        groups_collection.insert_one({
            "chat_id": chat_id,
            "welcome": True,
            "claim_status": False
        })

def get_group(chat_id: int):
    """Return group settings."""
    return groups_collection.find_one({"chat_id": chat_id})

# -----------------------------
# SUDO FUNCTIONS
# -----------------------------

def add_sudo(user_id: int):
    """Add sudo user."""
    sudoers_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

def is_sudo(user_id: int):
    """Check sudo."""
    return sudoers_collection.find_one({"user_id": user_id}) is not None

# -----------------------------
# STATS FUNCTIONS
# -----------------------------

def get_total_users():
    """Return total users."""
    return users_collection.count_documents({})

def get_total_groups():
    """Return total groups."""
    return groups_collection.count_documents({})
