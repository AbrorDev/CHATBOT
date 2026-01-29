import httpx

async def ask_ai(user_id: int, text: str):
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "http://api:8000/chat",
            json={
                "user_id": user_id,
                "text": text
            }
        )
        resp.raise_for_status()
        return resp.json()