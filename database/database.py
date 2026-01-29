from pymongo import MongoClient
import random
from datetime import datetime

from config.settings import mongodb_api_key

# connecting
mongodb_client = MongoClient(mongodb_api_key)
db = mongodb_client['chatbot_db']         # database name
collection = db['messages']       # Collection name
user_collection = db["users"]

# Savol va javobni bazaga yozish
async def save_user(lang: str, tg_id: int, phone_number: str):
    message = {
        "user_id": random.randint(10000, 99999),  # todo uuid bilan id berish kerak
        "tg_id": tg_id,
        "lang": lang,
        "phone_number": phone_number,
    }
    user_collection.insert_one(message)
    print("✅ User muvaffaqiyatli bazaga saqlandi!")

async def update_user_lang(tg_id: int, lang: str):
    result = user_collection.update_one(
        {"tg_id": tg_id},              # qidirish sharti
        {"$set": {"lang": lang}},      # yangilash
        upsert=False                   # mavjud bo'lmasa yangi yaratmasin
    )

    if result.matched_count > 0:
        print(f"✅ User (tg_id={tg_id}) muvaffaqiyatli yangilandi!")
    else:
        print(f"⚠️ User (tg_id={tg_id}) topilmadi, yangilash amalga oshmadi.")

async def get_language(tg_id: int):

    # request: tg_id mos, va timestamp > berilgan vaqt
    results = user_collection.find({
        "tg_id": tg_id,
    })

    users = []
    for user in results:
        users.append({
            "lang": user["lang"],
        })
    return users

# Savol va javobni bazaga yozish
async def save_message(question: str, answer: str, tg_id: int):
    message = {
        "message_id": random.randint(10000, 99999),  # todo uuid bilan id berish kerak
        "tg_id": tg_id,
        "content": question,
        "answer": answer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    collection.insert_one(message)
    print("✅ Xabar muvaffaqiyatli bazaga saqlandi!")


# TG ID bo‘yicha n ta oxirgi xabarni chiqarish
async def get_last_messages(tg_id: int, time_str: str, n: int):
    try:
        time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Noto‘g‘ri sana formati! To‘g‘ri format: YYYY-MM-DD HH:MM:SS")
        return {}

    # request: tg_id mos, va timestamp > berilgan vaqt
    results = collection.find({
        "tg_id": tg_id,
        "timestamp": {"$gt": time.strftime("%Y-%m-%d %H:%M:%S")}
    }).sort("timestamp", -1).limit(n)

    messages = []
    for msg in results:
        messages.append({
            "message_id": msg["message_id"],
            "content": msg["content"],
            "answer": msg["answer"],
            "timestamp": msg["timestamp"]
        })
    return messages

async def main():
    res = await get_language(994282938)
    print(res)

import asyncio

if __name__ == "__main__":
    asyncio.run(main())