from yandex_music import ClientAsync

async def music_is_exist(fir, sec):
    # Инициализация асинхронного клиента
    client = ClientAsync()
    await client.init()

    try:
        # Выполнение асинхронного поиска
        search_result = await client.search(f"{sec} {fir}", type_="track")
        if search_result.tracks.results[0].title:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return False
    
async def get_song_title_and_author(fir, sec):
    # Инициализация асинхронного клиента
    client = ClientAsync()
    await client.init()

    try:
        # Выполнение асинхронного поиска
        search_result = await client.search(f"{sec} {fir}", type_="track")
        if search_result.tracks.results[0].title:
            return search_result.tracks.results[0].artists[0].name, search_result.tracks.results[0].title
        else:
            return None, None
            
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return None
