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
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query={name}"
    headers = {
        "X-API-KEY": API_KEY
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Проверяем, что есть результаты и это действительно фильм/сериал
                    if not data.get("docs") or len(data["docs"]) == 0:
                        return None
                    
                    movie = data["docs"][0]
                    
                    # Дополнительные проверки что это фильм, а не что-то другое
                    if (not movie.get('name') or 
                        not movie.get('type') or 
                        movie.get('type') not in ['movie', 'tv-series', 'cartoon', 'anime']):
                        return None
                    
                    original_name = (
                        movie.get('alternativeName') or  # Альтернативное название
                        movie.get('enName') or          # Английское название
                        movie.get('name')               # Основное название
                    )
                    
                    return original_name
                else:
                    return None
        except:
            return None

async def get_movie_in_rus(name):
    API_KEY = os.getenv("KP_TOKEN")
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query={name}"
    headers = {
        "X-API-KEY": API_KEY
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["docs"][0]['name'], data["docs"][0]['year'], data["docs"][0]['description']
                else:
                    return None
        except:
            return None