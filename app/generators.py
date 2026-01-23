from dotenv import load_dotenv
from openai import OpenAI
import aiohttp
import os
from urllib.parse import quote

load_dotenv()

max_count = 350

client = OpenAI(api_key=os.getenv("AI_TOKEN"), base_url="https://api.deepseek.com")



async def generate(content):
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": content + f". Ответ должен быть максимум {max_count} символов"},
        ],
        stream=False
    )

    return response.choices[0].message.content

async def get_movie_original_name(name):
    API_KEY = os.getenv("KP_TOKEN")
    url = f"https://api.poiskkino.dev/v1.4/movie/search"
    headers = {"X-API-KEY": API_KEY}
    params = {"page": 1, "limit": 1, "query": name}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get("docs") or len(data["docs"]) == 0:
                        return None
                    movie = data["docs"][0]
                    if not movie.get('name') or movie.get('type') not in ['movie', 'tv-series', 'cartoon', 'anime']:
                        return None
                    return movie.get('alternativeName') or movie.get('enName') or movie.get('name')
                return None
        except Exception:
            return None

async def get_movie_in_rus(name):
    API_KEY = os.getenv("KP_TOKEN")
    url = f"https://api.poiskkino.dev/v1.4/movie/search"
    headers = {"X-API-KEY": API_KEY}
    params = {"page": 1, "limit": 1, "query": name}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    movie_data = data["docs"][0]
                    return movie_data.get('name'), movie_data.get('year'), movie_data.get('description')
                return None
        except Exception:
            return None