import aiohttp
import os
from urllib.parse import quote
import re

async def get_book(title):
    def normalize_string(text):
        # Приводим к нижнему регистру, заменяем ё на е, оставляем только буквы, цифры и пробелы
        text = text.lower().replace('ё', 'е')
        text = re.sub(r'[^a-zа-я0-9\s]', '', text) 
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    normalized_search_title = normalize_string(title)
    
    query = quote(f"intitle:{title}")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&langRestrict=ru&maxResults=5&key={os.getenv('GOOGLE_BOOKS_API_KEY')}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('items'):
                        for item in data['items']:
                            volume_info = item.get('volumeInfo', {})
                            original_title = volume_info.get('title', '')
                            
                            normalized_original_title = normalize_string(original_title)
                            
                            if (normalized_search_title in normalized_original_title or 
                                normalized_original_title in normalized_search_title):
                                return process_book_data_item(item)
            
                        # print(f"Не совпали названия")
                    return None
                else:
                    # print(f"Ошибка HTTP: {response.status}")
                    return None
    except Exception as e:
        # print(f"Произошла ошибка: {e}")
        return None

def process_book_data_item(item):
    """Обрабатывает данные одной книги из items"""
    volume_info = item.get('volumeInfo', {})
    book = {
        'title': volume_info.get('title', 'Нет названия'),
        'authors': volume_info.get('authors', ['Авторы не указаны']),
        'published_date': volume_info.get('publishedDate', 'Дата не указана'),
        'description': volume_info.get('description', 'Описание отсутствует'),
        'page_count': volume_info.get('pageCount'),
        'categories': volume_info.get('categories', []),
        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail'),
        'preview_link': volume_info.get('previewLink'),
        'info_link': volume_info.get('infoLink')
    }
    return book