import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
mongodb_api_key = os.getenv("MONGODB_API_KEY")

MODEL_NAME=os.getenv("MODEL_NAME")

SYSTEM_PROMPT_UZ = os.getenv("SYSTEM_PROMPT_UZ")
SYSTEM_PROMPT_RU = os.getenv("SYSTEM_PROMPT_RU")

contextualize_q_system_prompt_uz = os.getenv("contextualize_q_system_prompt_uz")
contextualize_q_system_prompt_ru = os.getenv("contextualize_q_system_prompt_ru")

vector_store_id_uz = os.getenv("vector_store_id_uz")
vector_store_id_ru = os.getenv("vector_store_id_ru")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)