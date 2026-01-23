import io
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from PIL import Image
from aiogram.types import BufferedInputFile
from app.generators import generate, get_movie_original_name, get_movie_in_rus
from app.generators_music import music_is_exist, get_song_title_and_author
import app.keyboards as kb
from app.generators_books import get_book
from dotenv import load_dotenv
import app.database as db
import app.helpers as hp
import json

from app.helpers import sort_arr_to_most_popular, it_is_author, it_is_work_name, get_choice_in_art,  word_in_filter_choice, choice_in_author #Импортируем вспомогательные функции

#Подгружаем переменные окружения (они лежат в .env)
load_dotenv()

#Создаём объект класса Router (с помощью него мы будем обрабатывать входящие сообщения и очередь коллбэков)
router = Router()
#state
#Состояние запроса для рекомендации
class Req(StatesGroup):
  ready_to_start = State()
  picks_favourite_films = State()
  picks_favourite_songs = State()
  picks_favourite_books = State()
  art = State()
  filter_to_search = State()
  message_to_recommend = State()
  
#Состояние запроса для получения цвета
class Color(StatesGroup):
  message_to_get_color = State()
  message_with_color_response = State()
  
#Состояние с ответом нейросети
class Res(StatesGroup):
  message_with_response = State()
  
#message_handlers

#Обработчик, выполняющиеся при команде start
@router.message(Command('start'))
async def on_start(message: Message, state: FSMContext):
  try:
    #Регистрируем пользователя в нашей базе данных
    is_registered = await db.check_user_is_full_registered(message.from_user.id)
    if is_registered:
      await message.answer('Ты уже зарегистрирован в системе :)')
      return
    await db.create_user(message.from_user.username if message.from_user.username else message.from_user.first_name, message.from_user.id)
    await message.answer('Привет! Здесь ты сможешь получить рекомендации по фильмам, музыке, книгам, и по желанию найти людей со схожим вкусом. Для начала работы тебе нужно будет написать свои любимые фильмы, песни, книги. Так я буду лучше знать, что тебе рекомендовать. Как будешь готов для этого, напиши что-то в чат :)')
    await state.set_state(Req.ready_to_start)
    await state.update_data(picks_favourite_films=[])
    await state.update_data(picks_favourite_songs=[])
    await state.update_data(picks_favourite_books=[])
  except:
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
  
  
@router.message(Req.ready_to_start)
async def on_ready_to_start(message: Message, state: FSMContext):
  text = 'Отлично, приступим! Напиши свои любимые фильмы. Каждое название фильма должно идти отдельным сообщением. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода'
  await message.answer(f'{text}<a href="https://i.ibb.co/KchfJ5hc/image-2025-11-30-13-48-18.png">:</a>',
    parse_mode="HTML")
  
  await state.set_state(Req.picks_favourite_films)


#Picks favourite films
@router.message(Req.picks_favourite_films)
async def picks_favourite_films_handler(message: Message, state: FSMContext):
  if message.text.lower() == "я закончил" or message.text.lower() == "я закончил.":
    films = (await state.get_data())["picks_favourite_films"]
    if len(films) != 0:
      await on_stop_picking_favourite_films(message=message, state=state)
    else:
      await message.answer("Ты должен ввести хотя бы один фильм!")
  else:
    await on_picks_favourite_films(message=message, state=state)
  
async def on_picks_favourite_films(message: Message, state: FSMContext):
  try:
    loading_msg = await message.answer('Одну минуту...')
    if len(message.text) > 350:
        await loading_msg.delete()
        await message.answer('Прости, но это слишком длинное сообщение')
        return
    
    s = message.text
    try:
        answer = await get_movie_original_name(s.strip())
        s = answer
        if (answer == None):
          raise Exception
    except:
        await loading_msg.delete()
        await message.answer('Похоже, что такого фильма не существует. Попробуй снова')
        return 

    prevFilms = (await state.get_data())["picks_favourite_films"]
    prevFilms.append(s.strip())
    await state.update_data(picks_favourite_films=prevFilms)
    await loading_msg.delete()
    await message.answer('Отлично! Можешь продолжать')
  except: 
    await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать ещё раз')
  
async def on_stop_picking_favourite_films(message: Message, state: FSMContext):
  try:
    text = 'Хорошо! Теперь напиши свои любимые песни. Каждое название песни должно идти отдельным сообщением и вместе с её автором. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода'
    await message.answer(f'{text}<a href="https://i.ibb.co/j9GTY3sg/image-2025-11-30-13-46-07.png">:</a>',
    parse_mode="HTML")
    
    await state.set_state(Req.picks_favourite_songs)
  except:
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    

#Picks favourite songs   
@router.message(Req.picks_favourite_songs)
async def picks_favourite_songs_handler(message: Message, state: FSMContext):
  if message.text.lower() == "я закончил" or message.text.lower() == "я закончил.":
    songs = (await state.get_data())["picks_favourite_songs"]
    if len(songs) != 0:
      await on_stop_picking_favourite_songs(message=message, state=state)
    else:
      await message.answer("Ты должен ввести хотя бы одну песню!")
  else:
    await on_picks_favourite_songs(message=message, state=state)
  
async def on_picks_favourite_songs(message: Message, state: FSMContext):
  try:
    loading_msg = await message.answer('Одну минуту...')
    if len(message.text) > 350:
        await loading_msg.delete()
        await message.answer('Прости, но это слишком длинное сообщение')
        return
    
    s = message.text
    try:
      author, song_name = [x.strip() for x in s.split("-")]
      author, song_name = await get_song_title_and_author(song_name, author)
      s = [author, song_name]
      if song_name == None or author == None:
        raise Exception
    except:
      await loading_msg.delete()
      await message.answer('Похоже, что такой песни не существует. Попробуй снова')
      return 
    
    prevSongs = (await state.get_data())["picks_favourite_songs"]
    prevSongs.append(s)
    await state.update_data(picks_favourite_songs=prevSongs)
    await loading_msg.delete()
    await message.answer('Отлично! Можешь продолжать')
  except: 
    await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать ещё раз')
    
async def on_stop_picking_favourite_songs(message: Message, state: FSMContext):
  try:
    text = 'Хорошо! Теперь напиши свои любимые книги. Каждое название книги должно идти отдельным сообщением. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода'
    await message.answer(f'{text}<a href="https://i.ibb.co/3yqJf4Rn/image-2025-11-30-13-47-15.png">:</a>',
    parse_mode="HTML")
    
    await state.set_state(Req.picks_favourite_books)
  except:
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
#Picks favourite books
@router.message(Req.picks_favourite_books)
async def picks_favourite_books_handler(message: Message, state: FSMContext):
  if message.text.lower() == "я закончил" or message.text.lower() == "я закончил.":
    books = (await state.get_data())["picks_favourite_books"]
    if len(books) != 0:
      await on_stop_picking_favourite_books(message=message, state=state)
    else:
      await message.answer("Ты должен ввести хотя бы одну книгу!")
  else:
    await on_picks_favourite_books(message=message, state=state)
  
async def on_picks_favourite_books(message: Message, state: FSMContext):
  try:
    loading_msg = await message.answer('Одну минуту...')
    if len(message.text) > 350:
        await loading_msg.delete()
        await message.answer('Прости, но это слишком длинное сообщение')
        return
    
    s = message.text
    try:
        answer = await get_book(s.strip())
        if (answer == None):
          raise Exception
        else:
          s = answer.get("title")
    except:
        await loading_msg.delete()
        await message.answer('Похоже, что такой книги не существует. Попробуй снова')
        return 

    prevbooks = (await state.get_data())["picks_favourite_books"]
    prevbooks.append(s.strip())
    await state.update_data(picks_favourite_books=prevbooks)
    await loading_msg.delete()
    await message.answer('Отлично! Можешь продолжать')
  except: 
    await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать ещё раз')
  
async def on_stop_picking_favourite_books(message: Message, state: FSMContext):
  loading_msg = await message.answer('Одну минуту...')
  try:
    #EndRegister
    await write_favourite_in_db(message=message, state=state)
    await register_user(message.from_user.id)
    
    await loading_msg.delete()
    await message.answer('Замечательно! Теперь ты можешь приступить к использованию функций бота!', reply_markup=kb.reply_kb)
    await state.clear()
  except:
    await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
#Register
async def register_user(user_id):
  await db.register_user(user_id)
  
#Write_favourite_in_db
async def write_favourite_in_db(message: Message, state: FSMContext):
  #Films
  films = (await state.get_data())["picks_favourite_films"] 
  for film_name in films:
    await db.create_user_favourite_film(message.from_user.id, film_name)
  #Songs
  songs = (await state.get_data())["picks_favourite_songs"]
  for song in songs:
    await db.create_user_favourite_song(message.from_user.id, author=song[0], song_name=song[1])
  #Books
  books = (await state.get_data())["picks_favourite_books"] 
  for book_name in books:
      await db.create_user_favourite_book(message.from_user.id, book_name)
  
    
# 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' [0]
#               'username VARCHAR(64) NOT NULL, ' [1]
#               'tg_id INTEGER NOT NULL, ' [2]
#               'registered INTEGER NOT NULL' [3]

# ('CREATE TABLE IF NOT EXISTS users_favourite_works(' [0]
#               'id INTEGER PRIMARY KEY AUTOINCREMENT, ' [1]
#               'user_id INTEGER, ' [2]
#               'art VARCHAR(64) NOT NULL, ' [3]
#               'work_name VARCHAR(128) NOT NULL, ' [4]
#               'FOREIGN KEY (user_id) REFERENCES users(id)' [5]
#               ')')
@router.message((F.text == 'Что посмотреть?') | (F.text == '/get_film_recommendation'))
async def get_film_recommendation(message: Message, state: FSMContext):
  loading_msg = await message.answer("Одну минуту...")
  rec_intro = False
  try: 
    is_full_registered = await db.check_user_is_full_registered(message.from_user.id)
    if not(is_full_registered): #Если не зарегистрирован
      await loading_msg.delete()
      await message.answer('Ты должен сначала ввести все свои любимые фильмы, песни и книги!')
      return 
    liked_films = list(await db.get_all_user_film_likes(message.from_user.id))
    disliked_films = list(await db.get_all_user_film_dislikes(message.from_user.id))
    favourite_films = list(await db.get_all_favourite_films(message.from_user.id))
    recommended_films = list(await db.get_all_recommended_films(message.from_user.id))
    
    mes = hp.get_film_recommend_ai_prompt(favourite_films=favourite_films, recommended_films=recommended_films, liked_films=liked_films,disliked_films=disliked_films)

    answer = await generate(mes)
    
    answer = json.loads(answer)
    reccomendation_intro = answer[0]
    films_name = answer[1]
    
    films_rus_with_year = []  
    for film_name in films_name:
      answer = await get_movie_in_rus(film_name) 
      if answer[0] == "" or answer[1] == "" or answer[2] == "":
        raise Exception
      films_rus_with_year.append(answer)
    
    for film_name in films_name:
      if film_name in favourite_films or film_name in recommended_films:
        raise Exception
      await db.create_user_recommended_film(message.from_user.id, film_name)  

    await loading_msg.delete()
    rec_intro = await message.answer(reccomendation_intro)
    
    for film_id in range(len(films_name)):
      film_id_in_db = await db.get_recommended_film_id(film_name=films_name[film_id])
      await message.answer(text=f'''
        <b>{films_rus_with_year[film_id][0]} ({films_rus_with_year[film_id][1]})</b>\n\n{films_rus_with_year[film_id][2]}''', 
      reply_markup=kb.get_inline_like_dislike_film_kb(int(film_id_in_db)), parse_mode="HTML")
  except: 
    if (rec_intro): await rec_intro.delete()
    if (loading_msg): await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')

@router.message((F.text == 'Что послушать?') | (F.text == '/get_song_recommendation'))
async def get_film_recommendation(message: Message, state: FSMContext):
  loading_msg = await message.answer("Одну минуту...")
  rec_intro = False
  try:
    is_full_registered = await db.check_user_is_full_registered(message.from_user.id)
    if not(is_full_registered): #Если не зарегистрирован
      await loading_msg.delete()
      await message.answer('Ты должен сначала ввести все свои любимые фильмы, песни и книги!')
      return 
    
    liked_songs = list(await db.get_all_user_song_likes(message.from_user.id))
    disliked_songs = list(await db.get_all_user_song_dislikes(message.from_user.id))
    favourite_songs = list(await db.get_all_favourite_songs(message.from_user.id))
    recommended_songs = list(await db.get_all_recommended_songs(message.from_user.id))
    
    mes = hp.get_song_recommend_ai_prompt(favourite_songs=favourite_songs, recommended_songs=recommended_songs, liked_songs=liked_songs,disliked_songs=disliked_songs)
    answer = await generate(mes)

    answer = json.loads(answer)
    reccomendation_intro = answer[0]
    songs = answer[1]
    
    for author, song_name in songs:
      answer = await music_is_exist(song_name, author) 
      if not(answer):
        raise Exception
      
    for author, song_name in songs:
      if song_name in hp.take_only_song_names(favourite_songs) or song_name in hp.take_only_song_names(recommended_songs):
        raise Exception
      await db.create_user_recommended_song(message.from_user.id, author=author, song_name=song_name)  
    
    await loading_msg.delete()
    rec_intro = await message.answer(reccomendation_intro)
    for author, song_name in songs:
      song_id_in_db = await db.get_recommended_song_id(song_name=song_name,author=author)
      await message.answer(text=f"{author} - {song_name}", 
      reply_markup=kb.get_inline_like_dislike_song_kb(int(song_id_in_db)))
  except: 
    if (rec_intro): await rec_intro.delete()
    if (loading_msg): await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
@router.message((F.text == 'Что почитать?') | (F.text == '/get_book_recommendation'))
async def get_film_recommendation(message: Message, state: FSMContext):
  loading_msg = await message.answer("Одну минуту...")
  rec_intro = False
  try: 
    is_full_registered = await db.check_user_is_full_registered(message.from_user.id)
    if not(is_full_registered): #Если не зарегистрирован
      await loading_msg.delete()
      await message.answer('Ты должен сначала ввести все свои любимые фильмы, песни и книги!')
      return 
    
    liked_books = list(await db.get_all_user_book_likes(message.from_user.id))
    disliked_books = list(await db.get_all_user_book_dislikes(message.from_user.id))
    favourite_books = list(await db.get_all_favourite_books(message.from_user.id))
    recommended_books = list(await db.get_all_recommended_books(message.from_user.id))
    
    mes = hp.get_book_recommend_ai_prompt(favourite_books=favourite_books, recommended_books=recommended_books, liked_books=liked_books,disliked_books=disliked_books)
    
    answer = await generate(mes)
    
    answer = json.loads(answer)
    reccomendation_intro = answer[0]
    books_name = answer[1]
    
    # books = []  
    # for book_name in books_name:
    #   book = await get_book(book_name) 
    #   if book == None:
    #     raise Exception
    #   books.append([book.get("title"), book.get("description")])
    
    for book_name in books_name:
      if book_name in favourite_books or book_name in recommended_books:
        raise Exception
      await db.create_user_recommended_book(message.from_user.id, book_name)  

    await loading_msg.delete()
    rec_intro = await message.answer(reccomendation_intro)
    
    for book_name in books_name:
      book_id_in_db = await db.get_recommended_book_id(book_name=book_name)
      await message.answer(text=f'''
        <b>{book_name}</b>''', 
      parse_mode="HTML",
      reply_markup=kb.get_inline_like_dislike_book_kb(int(book_id_in_db)))
  except: 
    if (rec_intro): await rec_intro.delete()
    if (loading_msg): await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
# #Обработчик, выполняющиеся при сообщении с целью получения прошлых рекомендаций
# @router.message((F.text == 'Мои прошлые рекомендации') | (F.text == '/get_my_recommendations'))
# async def get_user_old_recommendations(message: Message, state: FSMContext):
#   await state.clear() #Очищаем состояние приложения
  
#   #Достаём из базы данных все рекомендации, полученные пользователей
#   arr_with_user_recommendations = await db.get_user_recommendations(message.from_user.id)
  
#   #Если есть ответ - пробегаемся по каждому запросу и полученной рекомендации, выводим их
#   if arr_with_user_recommendations:
#     arr_with_user_recommendations = list(map(lambda rec: f'<b>Твой запрос:</b>\n{rec[3]}\n\n<b>Ответ нейросети:</b>\n{rec[2]}', arr_with_user_recommendations))
#     for user_recommendation in arr_with_user_recommendations:
#       await message.reply(user_recommendation, parse_mode='html')
#   else:
#     await message.answer('Вы ещё не получали рекомендаций в нашем сервисе')
    
# #Обработчик, выполняющиеся при сообщении с целью получения прошлых цветов вкуса пользователя
# @router.message((F.text == 'Полученные мной темпераменты') | (F.text == '/get_received_temperaments'))
# async def get_user_colors(message: Message, state: FSMContext):
#   await state.clear() #Очищаем состояние приложения
  
#   #Достаём из базы данных все цвета, полученные пользователей
#   arr_with_user_colors = await db.get_user_colors(message.from_user.id)
  
#   #Если есть ответ - пробегаемся по каждому запросу и полученному цвету и отправляем их
#   if arr_with_user_colors:
#     arr_with_user_colors = list(map(lambda rec: f'<b>Твой запрос:</b>\n{rec[2]}\n\n<b>Темперамент:</b>\n{rec[3]}', arr_with_user_colors))
#     for user_color in arr_with_user_colors:
#       await message.reply(user_color, parse_mode='html')
#   else:
#     await message.answer('Вы ещё не получали темперамент в нашем сервисе')
    
# @router.message((F.text == 'Самые популярные произведения') | (F.text == '/get_popular'))
# async def get_top_works(message: Message, state: FSMContext):
#   await state.clear() #Очищаем состояние приложения
  
#   #Достаём из базы данных все рекомендации
#   recommendations = await db.get_all_recommendations()
#   songs = []
#   books = []
#   films = []
  
#   #В зависимости от рекомендации добавляем её в 'песни', 'фильмы' или 'музыку'
#   for recommendation in recommendations:
#     if recommendation[4] == 'Музыка' and recommendation[5] == 'Песня':
#       songs.append(recommendation[3])
#     if recommendation[4] == 'Фильмы' and recommendation[5] == 'Фильм':
#       films.append(recommendation[3])
#     if recommendation[4] == 'Книги' and recommendation[5] == 'Книга':
#       books.append(recommendation[3])
      
#   #Сортируем песни, фильмы, музыку по популярности
#   songs_str = '\n'.join(sort_arr_to_most_popular(songs))
#   books_str = '\n'.join(sort_arr_to_most_popular(books))
#   films_str = '\n'.join(sort_arr_to_most_popular(films))
      
#   #Если есть рекомендации, отправляем их
#   if recommendations:
#     #Выделяем некоторые слова html тегами, чтобы они стали 'жирными'
#     #Не забываем вписать parse_mode = html, чтобы текст парсился по стандратнам html
#     await message.reply(f'<b>Песни:</b>\n{songs_str.title() if len(songs_str) >= 1 else "Пока нет"}', parse_mode='html')
#     await message.reply(f'<b>Книги:</b>\n{books_str.title() if len(books_str) >= 1 else "Пока нет"}', parse_mode='html')
#     await message.reply(f'<b>Фильмы:</b>\n{films_str.title() if len(films_str) >= 1 else "Пока нет"}', parse_mode='html')
#   else:
#     await message.answer('Самых популярных произведений ещё нет')


# #callback_query

@router.callback_query(kb.EstimationCallbackDataFilm.filter())
async def handle_film_action(
    query: CallbackQuery, 
    callback_data: kb.EstimationCallbackDataFilm
):
  await query.message.edit_reply_markup()
  film_name = await db.get_recommended_film_name_from_film_id(callback_data.film_id)
  if callback_data.type == "Like":
    await db.create_user_film_like(query.from_user.id, film_name)
  else:
    await db.create_user_film_dislike(query.from_user.id, film_name)
    
@router.callback_query(kb.EstimationCallbackDataSong.filter())
async def handle_song_action(
    query: CallbackQuery, 
    callback_data: kb.EstimationCallbackDataSong
):
  await query.message.edit_reply_markup()
  author, song_name = await db.get_recommended_song_author_and_name_from_song_id(callback_data.song_id)
  if callback_data.type == "Like":
    await db.create_user_song_like(query.from_user.id, author, song_name)
  else:
    await db.create_user_song_dislike(query.from_user.id, author, song_name)
    
@router.callback_query(kb.EstimationCallbackDataBook.filter())
async def handle_book_action(
    query: CallbackQuery, 
    callback_data: kb.EstimationCallbackDataBook
):
  await query.message.edit_reply_markup()
  book_name = await db.get_recommended_book_name_from_book_id(callback_data.book_id)
  if callback_data.type == "Like":
    await db.create_user_book_like(query.from_user.id, book_name)
  else:
    await db.create_user_book_dislike(query.from_user.id, book_name)
    