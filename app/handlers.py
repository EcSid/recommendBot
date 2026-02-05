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
from aiogram.filters import or_f

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
  genre = State()
  filter_to_search = State()
  message_to_recommend = State()
  user_id = State()
  delete_profile = State()
  
#Состояние запроса для получения цвета
class Color(StatesGroup):
  message_to_get_color = State()
  message_with_color_response = State()
  
#Состояние с ответом нейросети
class Res(StatesGroup):
  message_with_response = State()
  
class Fav(StatesGroup):
  changeFilms = State()
  deleteFilms = State()
  addFilms = State()
  
  changeSongs = State()
  deleteSongs = State()
  addSongs = State()
  
  changeBooks = State()
  deleteBooks = State()
  addBooks = State()
  
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
  text = 'Отлично, приступим! Напиши свои любимые фильмы. Каждое название фильма должно идти отдельным сообщением. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода. Строго следуй ему'
  await message.answer(f'{text}<a href="https://i.ibb.co/KchfJ5hc/image-2025-11-30-13-48-18.png">:</a>',
    parse_mode="HTML")
  
  await state.set_state(Req.picks_favourite_films)

#-----------------------------------------------------------
#Выбор любимых произведений

#Picks favourite films
@router.message(or_f(Req.picks_favourite_films, Fav.addFilms))
async def picks_favourite_films_handler(message: Message, state: FSMContext):
  try:
    if message.text.lower() == "я закончил" or message.text.lower() == "я закончил.":
      films = (await state.get_data())["picks_favourite_films"]
      if len(films) != 0:
        is_registered = await db.check_user_is_full_registered(message.from_user.id)
        #Пользователь просто добавляет новые фильмы в уже существующий профиль
        if is_registered:
          films = (await state.get_data())["picks_favourite_films"] 
          for film_name in films:
            await db.create_user_favourite_film(message.from_user.id, film_name)
          await message.answer("Отлично, ты добавил свои новые любимые фильмы!")
          await state.clear()
        else:
          #Пользователь ещё не зарегистрировался
          await on_stop_picking_favourite_films(message=message, state=state)
      else:
        await message.answer("Ты должен ввести хотя бы один фильм!")
    else:
      await on_picks_favourite_films(message=message, state=state)
  except Exception as e:
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
  
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
    except Exception as e:
        await loading_msg.delete()
        await message.answer('Похоже, что такого фильма не существует. Попробуй снова')
        return 

    prevFilms = (await state.get_data())["picks_favourite_films"]
    prevFilms.append(s.strip())
    await state.update_data(picks_favourite_films=prevFilms)
    await loading_msg.delete()
    await message.answer('Отлично! Можешь продолжать')
  except Exception as e:
    await loading_msg.delete()
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать ещё раз')
  
async def on_stop_picking_favourite_films(message: Message, state: FSMContext):
  try:
    text = 'Хорошо! Теперь напиши свои любимые песни. Каждое название песни должно идти отдельным сообщением и вместе с её автором. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода. Строго следуй ему'
    await message.answer(f'{text}<a href="https://i.ibb.co/zhHpvHnH/image-2026-01-23-21-30-56.png">:</a>',
    parse_mode="HTML")
    
    await state.set_state(Req.picks_favourite_songs)
  except:
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    

#Picks favourite songs   
@router.message(or_f(Req.picks_favourite_songs, Fav.addSongs))
async def picks_favourite_songs_handler(message: Message, state: FSMContext):
  if message.text.lower() == "я закончил" or message.text.lower() == "я закончил.":
    songs = (await state.get_data())["picks_favourite_songs"]
    if len(songs) != 0:
        is_registered = await db.check_user_is_full_registered(message.from_user.id)
        #Пользователь просто добавляет новые песни в уже существующий профиль
        if is_registered:
          songs = (await state.get_data())["picks_favourite_songs"] 
          for song in songs:
            await db.create_user_favourite_song(user_id=message.from_user.id, author=song[0],song_name=song[1])
          await message.answer("Отлично, ты добавил свои новые любимые песни!")
          await state.clear()
        else:
          #Пользователь ещё не зарегистрировался
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
      author, song_name = [x.strip() for x in s.split(":")]
      author, song_name = await get_song_title_and_author(song_name, author)
      s = [author, song_name]
      if song_name == None or author == None:
        raise Exception
    except:
      await loading_msg.delete()
      await message.answer('Похоже, что такой песни не существует, или ты вводил её не следуя вышеуказанным инструкциям. Попробуй снова')
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
    text = 'Хорошо! Теперь напиши свои любимые книги. Каждое название книги должно идти отдельным сообщением. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода. Строго следуй ему'
    await message.answer(f'{text}<a href="https://i.ibb.co/3yqJf4Rn/image-2025-11-30-13-47-15.png">:</a>',
    parse_mode="HTML")
    
    await state.set_state(Req.picks_favourite_books)
  except:
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
#Picks favourite books
@router.message(or_f(Req.picks_favourite_books, Fav.addBooks))
async def picks_favourite_books_handler(message: Message, state: FSMContext):
  if message.text.lower() == "я закончил" or message.text.lower() == "я закончил.":
    books = (await state.get_data())["picks_favourite_books"]
    if len(books) != 0:
        is_registered = await db.check_user_is_full_registered(message.from_user.id)
        #Пользователь просто добавляет новые книги в уже существующий профиль
        if is_registered:
          books = (await state.get_data())["picks_favourite_books"] 
          for book_name in books:
            await db.create_user_favourite_book(message.from_user.id, book_name)
          await message.answer("Отлично, ты добавил свои новые любимые книги!")
          await state.clear()
        else:
          #Пользователь ещё не зарегистрировался
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
  

#-----------------------------------------------------------
#Рекомендации
@router.message((F.text == 'Что посмотреть?') | (F.text == '/get_film_recommendation'))
async def get_film_recommendation(message: Message, state: FSMContext):
  try: 
    is_full_registered = await db.check_user_is_full_registered(message.from_user.id)
    if not(is_full_registered): #Если не зарегистрирован
      await message.answer('Ты должен сначала ввести все свои любимые фильмы, песни и книги!')
      return 
    
    await state.update_data(user_id=message.from_user.id)
    
    #Состояние приложения - выбор пользователем искусства (музыка, книги, фильмы)
    await state.set_state(Req.genre)
    #Прикрепляем inlnine клавиатуру, сделанную с помощью функции с билдером
    await message.reply('Фильмы какого жанра ты хочешь посмотреть?', reply_markup=kb.create_inline_keyboard_for_genres(["Это неважно", "Драма", "Комедия", "Триллер", "Хоррор", "Научная фантастика", "Фэнтези", "Детектив", "Романтика", "Приключение", "Боевик", "Военное кино", "Историческое кино", "Криминал", "Вестерн", "Семейное кино"], "f"))
  except Exception as e: 
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
  

@router.message((F.text == 'Что послушать?') | (F.text == '/get_song_recommendation'))
async def get_song_recommendation(message: Message, state: FSMContext):
  try: 
    is_full_registered = await db.check_user_is_full_registered(message.from_user.id)
    if not(is_full_registered): #Если не зарегистрирован
      await message.answer('Ты должен сначала ввести все свои любимые фильмы, песни и книги!')
      return 
    
    await state.update_data(user_id=message.from_user.id)
    
    #Состояние приложения - выбор пользователем искусства (музыка, книги, фильмы)
    await state.set_state(Req.genre)
    #Прикрепляем inlnine клавиатуру, сделанную с помощью функции с билдером
    await message.reply('Песни какого жанра ты хочешь слушать?', reply_markup=kb.create_inline_keyboard_for_genres(["Это неважно", "Поп", "Рэп", "Рок", "Металл", "Джаз", "Кантри", "Регги", "Электроника", "Классическая музыка"], "s"))
  except: 
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
  
    
@router.message((F.text == 'Что почитать?') | (F.text == '/get_book_recommendation'))
async def get_book_recommendation(message: Message, state: FSMContext):
  try: 
    is_full_registered = await db.check_user_is_full_registered(message.from_user.id)
    if not(is_full_registered): #Если не зарегистрирован
      await message.answer('Ты должен сначала ввести все свои любимые фильмы, песни и книги!')
      return 
    
    await state.update_data(user_id=message.from_user.id)
    
    #Состояние приложения - выбор пользователем искусства (музыка, книги, фильмы)
    await state.set_state(Req.genre)
    #Прикрепляем inlnine клавиатуру, сделанную с помощью функции с билдером
    await message.reply('Книги какого жанра ты хочешь прочитать?', reply_markup=kb.create_inline_keyboard_for_genres(["Это неважно", "Научная фантастика", "Фэнтези", "Любовный роман", "Детектив", "История", "Приключение", "Ужасы"], "b"))
  except: 
    await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')

#-----------------------------------------------------------
#Удаление профиля

@router.message(F.text == 'Удалить профиль')
async def delete_profile(message: Message, state: FSMContext):
    try:
      is_registered = await db.check_user_is_full_registered(message.from_user.id)
      if not(is_registered):
        await message.answer('Ты не зарегистрирован в системе!')
        return
      await state.set_state(Req.delete_profile)
      await state.update_data(user_id=message.from_user.id)
      await message.reply("Ты точно хочешь удалить свой профиль?", reply_markup=kb.create_inline_keyboard_for_delete_profile())
    except Exception as e:
      await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')

#-----------------------------------------------------------
#Изменение списка любимых произведений

@router.message(F.text == 'Изменить свои любимые фильмы')
async def delete_profile(message: Message, state: FSMContext):
    try:
      is_registered = await db.check_user_is_full_registered(message.from_user.id)
      if not(is_registered):
        await message.answer('Ты не зарегистрирован в системе!')
        return
      await state.set_state(Fav.changeFilms)
      await state.update_data(user_id=message.from_user.id)
      await message.reply("Что именно ты хочешь сделать со списком своих любимых фильмов?", reply_markup=kb.create_inline_keyboard_for_change_favourites())
    except Exception as e:
      await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
      
@router.message(F.text == 'Изменить свои любимые песни')
async def delete_profile(message: Message, state: FSMContext):
    try:
      is_registered = await db.check_user_is_full_registered(message.from_user.id)
      if not(is_registered):
        await message.answer('Ты не зарегистрирован в системе!')
        return
      await state.set_state(Fav.changeSongs)
      await state.update_data(user_id=message.from_user.id)
      await message.reply("Что именно ты хочешь сделать со списком своих любимых песен?", reply_markup=kb.create_inline_keyboard_for_change_favourites())
    except Exception as e:
      await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
      
@router.message(F.text == 'Изменить свои любимые книги')
async def delete_profile(message: Message, state: FSMContext):
    try:
      is_registered = await db.check_user_is_full_registered(message.from_user.id)
      if not(is_registered):
        await message.answer('Ты не зарегистрирован в системе!')
        return
      await state.set_state(Fav.changeBooks)
      await state.update_data(user_id=message.from_user.id)
      await message.reply("Что именно ты хочешь сделать со списком своих любимых книг?", reply_markup=kb.create_inline_keyboard_for_change_favourites())
    except Exception as e:
      await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
      
#-----------------------------------------------------------
#Удаление из списка любимых произведений
@router.message(Fav.deleteFilms)
async def delete_fav_film(message: Message, state: FSMContext):
    try:
      st = await state.get_data()
      user_id = st['user_id']
      deleting_proccess_success = await db.delete_favourite_film(user_id=user_id, work_name=message.text)
      if (deleting_proccess_success):
        await message.answer('Произведение успешно было удалено')
      else:
        await message.answer('Произведение не было удалено из списка! Видимо, произошла какая-то ошибка, или ты неправильно указал название. Попробуй позже')
      await state.clear()
    except Exception as e:
      await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
      
@router.message(Fav.deleteSongs)
async def delete_fav_song(message: Message, state: FSMContext):
    try:
      st = await state.get_data()
      user_id = st['user_id']
      deleting_proccess_success = await db.delete_favourite_song(user_id=user_id, work_name=message.text)
      if (deleting_proccess_success):
        await message.answer('Произведение успешно было удалено')
      else:
        await message.answer('Произведение не было удалено из списка! Видимо, произошла какая-то ошибка, или ты неправильно указал название. Попробуй позже')
      await state.clear()
    except Exception as e:
      await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
      
@router.message(Fav.deleteBooks)
async def delete_fav_book(message: Message, state: FSMContext):
    try:
      st = await state.get_data()
      user_id = st['user_id']
      deleting_proccess_success = await db.delete_favourite_book(user_id=user_id, work_name=message.text)
      if (deleting_proccess_success):
        await message.answer('Произведение успешно было удалено')
      else:
        await message.answer('Произведение не было удалено из списка! Видимо, произошла какая-то ошибка, или ты неправильно указал название. Попробуй позже')
      await state.clear()
    except Exception as e:
      await message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')

#-------------------------------------------
#callback_query

#-----------------------------------------------------------
#Добавление в список любимых

@router.callback_query(Fav.changeFilms, F.data == "Add")
async def add_fav_films(callback: CallbackQuery, state: FSMContext):
  try:
    await callback.answer('')
    st = await state.get_data()
    user_id = st['user_id']
    favFilms = list(await db.get_all_favourite_films(user_id=user_id))
    await state.update_data(picks_favourite_films=favFilms)
    text = 'Отлично, напиши те фильмы, которые ты хочешь добавить. Каждое название фильма должно идти отдельным сообщением. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода. Строго следуй ему'
    await callback.message.edit_text(f'{text}<a href="https://i.ibb.co/KchfJ5hc/image-2025-11-30-13-48-18.png">:</a>',
      parse_mode="HTML")
    
    await state.set_state(Fav.addFilms)
  except Exception as e:
    await callback.message.edit_text('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    

@router.callback_query(Fav.changeSongs, F.data == "Add")
async def add_fav_Songs(callback: CallbackQuery, state: FSMContext):
  try:
    await callback.answer('')
    st = await state.get_data()
    user_id = st['user_id']
    favSongs = list(await db.get_all_favourite_songs(user_id=user_id))
    await state.update_data(picks_favourite_songs=favSongs)
    text = 'Хорошо, напиши те песни, которые ты хочешь добавить. Каждое название песни должно идти отдельным сообщением и вместе с её автором. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода. Строго следуй ему'
    await callback.message.edit_text(f'{text}<a href="https://i.ibb.co/zhHpvHnH/image-2026-01-23-21-30-56.png">:</a>',
    parse_mode="HTML")
    
    await state.set_state(Fav.addSongs)
  except Exception as e:
    await callback.message.edit_text('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
    
@router.callback_query(Fav.changeBooks, F.data == "Add")
async def add_fav_books(callback: CallbackQuery, state: FSMContext):
  try:
    await callback.answer('')
    st = await state.get_data()
    user_id = st['user_id']
    favBooks = list(await db.get_all_favourite_books(user_id=user_id))
    await state.update_data(picks_favourite_books=favBooks)
    text = 'Хорошо, теперь напиши те книги, которые ты хочешь добавить. Каждое название книги должно идти отдельным сообщением. Когда закончишь, напиши "Я закончил".\nСнизу приведён пример ввода. Строго следуй ему'
    await callback.message.edit_text(f'{text}<a href="https://i.ibb.co/3yqJf4Rn/image-2025-11-30-13-47-15.png">:</a>',
    parse_mode="HTML")
    
    await state.set_state(Fav.addBooks)
  except Exception as e:
    await callback.message.edit_text('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
#-----------------------------------------------------------
#Удаление из списка любимых произведений
    
@router.callback_query(Fav.changeFilms, F.data == "Delete")
async def delete_fav_films(callback: CallbackQuery, state: FSMContext):
  try:
    await callback.answer('')
    st = await state.get_data()
    user_id = st['user_id']
    favFilms = list(await db.get_all_favourite_films(user_id=user_id))
    
    #Строим сообщение
    text = '<b>Вот список твоих любимых фильмов:</b>\n'
    id = 1
    for film in favFilms:
      text += f'\n{id}. {film}'
      id += 1
    text += '\n\n<b>Напиши название того фильма, который ты хочешь удалить из списка</b>'
    
    await callback.message.edit_text(text, parse_mode="HTML")
    
    await state.set_state(Fav.deleteFilms)
  except Exception as e:
    await callback.message.edit_text('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
@router.callback_query(Fav.changeSongs, F.data == "Delete")
async def delete_fav_songs(callback: CallbackQuery, state: FSMContext):
  try:
    await callback.answer('')
    st = await state.get_data()
    user_id = st['user_id']
    favSongs = list(await db.get_all_favourite_songs(user_id=user_id))
    
    #Строим сообщение
    text = '<b>Вот список твоих любимых песен:</b>\n'
    id = 1
    for song in favSongs:
      text += f'\n{id}. {song[1]}'
      id += 1
    text += '\n\n<b>Напиши название той песни (без автора), которую ты хочешь удалить из списка</b>'
    
    await callback.message.edit_text(text, parse_mode="HTML")
    
    await state.set_state(Fav.deleteSongs)
  except Exception as e:
    await callback.message.edit_text('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
@router.callback_query(Fav.changeBooks, F.data == "Delete")
async def delete_fav_books(callback: CallbackQuery, state: FSMContext):
  try:
    await callback.answer('')
    st = await state.get_data()
    user_id = st['user_id']
    favBooks = list(await db.get_all_favourite_books(user_id=user_id))
    
    #Строим сообщение
    text = '<b>Вот список твоих любимых книг:</b>\n'
    id = 1
    for book in favBooks:
      text += f'\n{id}. {book}'
      id += 1
    text += '\n\n<b>Напиши название той книги, которую ты хочешь удалить из списка</b>'
    
    await callback.message.edit_text(text, parse_mode="HTML")
    
    await state.set_state(Fav.deleteBooks)
  except Exception as e:
    await callback.message.edit_text('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    
#-----------------------------------------------------------
#Удаление профиля

@router.callback_query(Req.delete_profile, F.data == "No")
async def not_deleting_account(callback: CallbackQuery, state: FSMContext):
  await callback.answer('')
  await callback.message.edit_text("Хорошо! Ваш профиль не будет удалён")
  await state.clear()
  
@router.callback_query(Req.delete_profile, F.data == "Yes")
async def deleting_account(callback: CallbackQuery, state: FSMContext):
  try:
    st = await state.get_data()
    user_id = st['user_id']
    
    await db.delete_profile(user_id)
    
    await callback.message.edit_text("Ваш профиль был успешно удалён. Для создания аккаунта напишите комманду '/start'")
    
    await state.clear()
  except:
    await callback.answer('Произошла ошибка при удалении профиля! Попробуй позже')
    await state.clear()
    
#-----------------------------------------------------------
#Лайк/Дизлайк произведению

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
    
#-----------------------------------------------------------
#Выбор жанра для рекомендации

@router.callback_query(Req.genre)
async def recommend_from_genre(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.delete()
    
    data = callback.data.split("~#~")
    
    st = await state.get_data()
    user_id = st['user_id']
      
    if data[0] == "b":
      loading_msg = await callback.message.answer("Одну минуту...")
      rec_intro = False
      try: 
        liked_books = list(await db.get_all_user_book_likes(user_id))
        disliked_books = list(await db.get_all_user_book_dislikes(user_id))
        favourite_books = list(await db.get_all_favourite_books(user_id))
        recommended_books = list(await db.get_all_recommended_books(user_id))
        
        mes = hp.get_book_recommend_ai_prompt(favourite_books=favourite_books, recommended_books=recommended_books, liked_books=liked_books,disliked_books=disliked_books,genre=data[1])
        
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
          await db.create_user_recommended_book(user_id, book_name)  

        await loading_msg.delete()
        rec_intro = await callback.message.answer(reccomendation_intro)
        
        for book_name in books_name:
          book_id_in_db = await db.get_recommended_book_id(book_name=book_name)
          await callback.message.answer(text=f'''
            <b>{book_name}</b>''', 
          parse_mode="HTML",
          reply_markup=kb.get_inline_like_dislike_book_kb(int(book_id_in_db)))
      except: 
        if (rec_intro): await rec_intro.delete()
        if (loading_msg): await loading_msg.delete()
        await callback.message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
        
    elif data[0] == "s":
      loading_msg = await callback.message.answer("Одну минуту...")
      rec_intro = False
      try:
        
        liked_songs = list(await db.get_all_user_song_likes(user_id))
        disliked_songs = list(await db.get_all_user_song_dislikes(user_id))
        favourite_songs = list(await db.get_all_favourite_songs(user_id))
        recommended_songs = list(await db.get_all_recommended_songs(user_id))
        
        mes = hp.get_song_recommend_ai_prompt(favourite_songs=favourite_songs, recommended_songs=recommended_songs, liked_songs=liked_songs,disliked_songs=disliked_songs,genre=data[1])
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
          await db.create_user_recommended_song(user_id, author=author, song_name=song_name)  
        
        await loading_msg.delete()
        rec_intro = await callback.message.answer(reccomendation_intro)
        for author, song_name in songs:
          song_id_in_db = await db.get_recommended_song_id(song_name=song_name,author=author)
          await callback.message.answer(text=f"{author} - {song_name}", 
          reply_markup=kb.get_inline_like_dislike_song_kb(int(song_id_in_db)))
      except: 
        if (rec_intro): await rec_intro.delete()
        if (loading_msg): await loading_msg.delete()
        await callback.message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
        
    elif data[0] == "f":
      loading_msg = await callback.message.answer("Одну минуту...")
      rec_intro = False
      try: 
        liked_films = list(await db.get_all_user_film_likes(user_id))
        disliked_films = list(await db.get_all_user_film_dislikes(user_id))
        favourite_films = list(await db.get_all_favourite_films(user_id))
        recommended_films = list(await db.get_all_recommended_films(user_id))
        
        mes = hp.get_film_recommend_ai_prompt(favourite_films=favourite_films, recommended_films=recommended_films, liked_films=liked_films,disliked_films=disliked_films,genre=data[1])

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
          await db.create_user_recommended_film(user_id, film_name)  

        await loading_msg.delete()
        rec_intro = await callback.message.answer(reccomendation_intro)
        
        for film_id in range(len(films_name)):
          film_id_in_db = await db.get_recommended_film_id(film_name=films_name[film_id])
          await callback.message.answer(text=f'''
            <b>{films_rus_with_year[film_id][0]} ({films_rus_with_year[film_id][1]})</b>\n\n{films_rus_with_year[film_id][2]}''', 
          reply_markup=kb.get_inline_like_dislike_film_kb(int(film_id_in_db)), parse_mode="HTML")
      except Exception as e: 
        if (rec_intro): await rec_intro.delete()
        if (loading_msg): await loading_msg.delete()
        await callback.message.answer('Ой! Произошла какая-то ошибка. Попробуй написать позже')
    await state.clear()
  
    