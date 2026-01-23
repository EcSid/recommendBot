import aiohttp
import os
from urllib.parse import quote

async def get_book(title):
    """Асинхронно получает данные о книге по русскому названию"""
    
    # Кодируем запрос для URL
    query = quote(f"intitle:{title}")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&langRestrict=ru&maxResults=1&key={os.getenv("GOOGLE_BOKS_API_KEY")}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    book_data = process_book_data(data)
                    original_title = book_data.get("title")
                    if (title.lower() in original_title.lower()):
                        return book_data
                    return None
                else:
                    print(f"Ошибка HTTP: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None
      
def process_book_data(data):
    if not data.get('items'):
        print("Книга не найдены")
        return None
      
    item = data["items"][0]
    
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