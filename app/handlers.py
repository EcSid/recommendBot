import io
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from PIL import Image
from aiogram.types import BufferedInputFile
from app.generators import generate
import app.keyboards as kb
import os
from dotenv import load_dotenv
import app.database as db

from app.helpers import sort_arr_to_most_popular, it_is_author, it_is_work_name, get_choice_in_art,  word_in_filter_choice, choice_in_author #Импортируем вспомогательные функции

#Подгружаем переменные окружения (они лежат в .env)
load_dotenv()

#Создаём объект класса Router (с помощью него мы будем обрабатывать входящие сообщения и очередь коллбэков)
router = Router()
#state
#Состояние запроса для рекомендации
class Req(StatesGroup):
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
async def on_start(message: Message):
  #Регистрируем пользователя в нашей базе данных
  await db.create_user(message.from_user.username if message.from_user.username else message.from_user.first_name, message.from_user.id)
  await message.reply('Привет! Здесь ты можешь на основе твоих предпочтений в музыке, книгах, фильмах получить рекомендацию от нейросети или уникальный увет своего вкуса!', reply_markup=kb.reply)
  
#Обработчик, выполняющиеся при сообщении с целью получения прошлых рекомендаций
@router.message((F.text == 'Мои прошлые рекомендации') | (F.text == '/get_my_recommendations'))
async def get_user_old_recommendations(message: Message, state: FSMContext):
  await state.clear() #Очищаем состояние приложения
  
  #Достаём из базы данных все рекомендации, полученные пользователей
  arr_with_user_recommendations = await db.get_user_recommendations(message.from_user.id)
  
  #Если есть ответ - пробегаемся по каждому запросу и полученной рекомендации, выводим их
  if arr_with_user_recommendations:
    arr_with_user_recommendations = list(map(lambda rec: f'<b>Твой запрос:</b>\n{rec[3]}\n\n<b>Ответ нейросети:</b>\n{rec[2]}', arr_with_user_recommendations))
    for user_recommendation in arr_with_user_recommendations:
      await message.reply(user_recommendation, parse_mode='html')
  else:
    await message.answer('Вы ещё не получали рекомендаций в нашем сервисе')
    
#Обработчик, выполняющиеся при сообщении с целью получения прошлых цветов вкуса пользователя
@router.message((F.text == 'Цвета моего вкуса') | (F.text == '/get_my_colors'))
async def get_user_colors(message: Message, state: FSMContext):
  await state.clear() #Очищаем состояние приложения
  
  #Достаём из базы данных все цвета, полученные пользователей
  arr_with_user_colors = await db.get_user_colors(message.from_user.id)
  
  #Если есть ответ - пробегаемся по каждому запросу и полученному цвету и отправляем их
  if arr_with_user_colors:
    arr_with_user_colors = list(map(lambda rec: f'<b>Твой запрос:</b>\n{rec[2]}\n\n<b>Цвет:</b>\nrgb({rec[3]})', arr_with_user_colors))
    for user_color in arr_with_user_colors:
      await message.reply(user_color, parse_mode='html')
  else:
    await message.answer('Вы ещё не получали рекомендаций в нашем сервисе')
    
@router.message((F.text == 'Самые популярные произведения') | (F.text == '/get_popular'))
async def get_top_works(message: Message, state: FSMContext):
  await state.clear() #Очищаем состояние приложения
  
  #Достаём из базы данных все рекомендации
  recommendations = await db.get_all_recommendations()
  songs = []
  books = []
  films = []
  
  #В зависимости от рекомендации добавляем её в 'песни', 'фильмы' или 'музыку'
  for recommendation in recommendations:
    if recommendation[4] == 'Музыка' and recommendation[5] == 'Песня':
      songs.append(recommendation[3])
    if recommendation[4] == 'Фильмы' and recommendation[5] == 'Фильм':
      films.append(recommendation[3])
    if recommendation[4] == 'Книги' and recommendation[5] == 'Книга':
      books.append(recommendation[3])
      
  #Сортируем песни, фильмы, музыку по популярности
  songs_str = '\n'.join(sort_arr_to_most_popular(songs))
  books_str = '\n'.join(sort_arr_to_most_popular(books))
  films_str = '\n'.join(sort_arr_to_most_popular(films))
      
  #Если есть рекомендации, отправляем их
  if recommendations:
    #Выделяем некоторые слова html тегами, чтобы они стали 'жирными'
    #Не забываем вписать parse_mode = html, чтобы текст парсился по стандратнам html
    await message.reply(f'<b>Песни:</b>\n{songs_str.title() if len(songs_str) >= 1 else "Пока нет"}', parse_mode='html')
    await message.reply(f'<b>Книги:</b>\n{books_str.title() if len(books_str) >= 1 else "Пока нет"}', parse_mode='html')
    await message.reply(f'<b>Фильмы:</b>\n{films_str.title() if len(films_str) >= 1 else "Пока нет"}', parse_mode='html')
  else:
    await message.answer('Самых популярных произведений ещё нет')

#Обработчик, выполняющиеся при сообщении с целью получения рекомендации
@router.message((F.text == 'Получить рекомендацию') | (F.text == '/get_recommendation'))
async def get_recommendation(message: Message, state: FSMContext):
  #Очищаем старое состояние (если оно есть)
  await state.clear()
  #Состояние приложения - выбор пользователем искусства (музыка, книги, фильмы)
  await state.set_state(Req.art)
  #Прикрепляем inlnine клавиатуру, сделанную с помощью функции с билдером
  await message.reply('По чему ты хочешь получить рекомендацию?', reply_markup=await kb.create_inline_keyboard(os.getenv('inline_with_all_arts').split(',')))
    
#Обработчик, выполняющиеся при сообщении с целью получения цвета
@router.message((F.text == 'Узнать цвет своего вкуса') | (F.text == '/get_unique_color'))
async def want_to_get_color(message: Message, state: FSMContext):
  #Очищаем старое состояние (если оно есть)
  await state.clear()
  #Состояние приложения: 'пользователь печает сообщение, благодаря которому получит свой цвет вкуса' (он печатает свои любмыие произведения)
  await state.set_state(Color.message_to_get_color)
  await message.answer('Напиши свои любые фильмы/музыку/книги через запятую')
  
#Обработчик, выполняющиеся при состоянии приложения: 'пользователь печает сообщение, благодаря которому получит свой цвет вкуса, это нужно, чтобы получить сообщение с любимыми произведениями пользователя' 
@router.message(Color.message_to_get_color)
async def get_arts_to_get_color(message: Message, state: FSMContext):
  #Отправляем сообщение с информацией об ожидании ответа от нейросети
  loading_msg = await message.answer('Нейросеть отвечает на ваше сообщение...')
  try:
    #Состояние приложения: 'ожидание овтета нейросети'
    await state.set_state(Color.message_with_color_response)
    #Проверяем существуют ли такие произведения
    res_with_bool_answer = await generate(f'Ответь одним словом "да", если все следующие произведения существуют: {message.text}, иначе ответь одним словом "нет"')
    if res_with_bool_answer.lower().find('нет') != -1:
      await loading_msg.delete()
      await message.answer(f'Введены некорректные данные или бот не знает, что это')
      return 
    #Запрос в нейросеть с чёткими инструкциями
    res_with_color_text = await generate(f'Верни уникальный цвет вкуса пользователя в формате rgb (верни только 3 числа через запятую, больше ничего не отправляй!), учитывая его любимые фильмы, книги или музыку, которые даны в следующей строке через запятую: {message.text}. Учти, что книги или фильмы с жанром "Драма", "Мелодрама", грустная музыка делают цвет голубоватым (но не полностью голубым), а книги или фильмы с жанром "Боевик", "Триллер", "Ужасы", тяжелая музыка (металл, тяжёлый рок) делают цвет почти полностью ярко выраженным красным, а оптимистичные или весёлые книги, фильмы, музыка (семейные фильмы, комедии) делают цвет почти полностью желтым. Чем больше произведений, сопутсвующих данным условиям, чем ярче будет соответсвующий цвет. Делай цвета немного необычными, но не в коем случае не отклоняйся о  условий данных выше. ОТПРАВЬ ТОЛЬКО 3 ЧИСЛА ЧЕРЕЗ ЗАПЯТУЮ, БОЛЬШЕ НИЧЕГО НЕ ПИШИ')
    #Делаем массив с тремя числами (rgb)
    tuple_color = tuple(list(map(lambda x: int(x), res_with_color_text.split(',')))) 
    #С помощью класса Image (библиотека Pillow) генерируем изображение, где цвет каждого пикселя будет передан в формате RGB, а его ширина и длинна - 500 на 500 пикселей (3 параметр - сам цвет формате rgb )
    img = Image.new('RGB', (500, 500), tuple_color)
    #С помощью библиотеки io получаем изображение в байтах 
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    buffered.seek(0) 
    buffer_img = BufferedInputFile(buffered.getvalue(), 'color.jpeg')
    await loading_msg.delete()
    #Отсылаем сообщение
    await message.answer_photo(photo=buffer_img, caption=f'Вот твой уникальный цвет в формате rgb: ({res_with_color_text})')
    
    #Записываем запрос и ответ нейросети с цветом в базу данных
    await db.create_user_color(message.from_user.id, message.text, res_with_color_text)
    
    await state.clear()
  #При возникновении любой ошибки, отправляем сообщение пользователю
  except:
      await loading_msg.delete()
      await message.answer('На сервере возникла ошибка, повторите ваш запрос позже')
  

#Обработчик, который будет выполняться при состоянии приложения: 'сообщение для получения рекомендации' (то есть состояние, когда пользователь вводит текст для получения рекомендации)
@router.message(Req.message_to_recommend)
async def on_text_to_search_message(message: Message, state: FSMContext):
  #Отправляем сообщение с информацией об ожидании ответа от нейросети
  loading_msg = await message.answer('Нейросеть отвечает на ваше сообщение...')
  try:
      #Обновляем переменную message_to_recommend в State
      await state.update_data(message_to_recommend=message.text)
      #Получаем все переменные в состоянии, они назодятся в словаре data
      data = await state.get_data()
      art = data['art']
      filter_to_search = data['filter_to_search']
      res_with_bool_answer = ''
      #Проверяем: правильно ли пользователь ввёл данные, если он ищет рекомендацию по произведению
      if it_is_work_name(filter_to_search) and len(message.text.split(':')) < 2:
        await loading_msg.delete()
        await message.answer(f'Данные были введены некорректно')
        return 
      #Проверяем есть ли такой жанр/произведение/исполнитель
      res_with_bool_answer = await generate(f'Ответь одним словом "да", если {filter_to_search} {message.text} существует в области {art}, иначе ответь одним словом "нет"')
      
      #Если ответ включает слово "нет" - отправляем пользователю 
      #нформацию о неправильных данных, введённых им
      if res_with_bool_answer.lower().find('нет') != -1:
        await loading_msg.delete()
        await message.answer(f'Введены некорректные данные или бот не знает, что это')
        return 
      #В другом случае меняем состояние приложение на 'ожидание овтета' (от нейросети)
      await state.set_state(Res.message_with_response)
      
      #В зависимости от выбора пользователя в inline клавиатуре, генерируем разные рекомендации, используя нейросеть
      res_with_recommendation_text = ''
      if it_is_author(filter_to_search):
        res_with_recommendation_text = await generate(f'Посоветуй похожего {"музыкального исполнителя" if filter_to_search == "Исполнитель" else filter_to_search}, если мне нравится {message.text}. Не начинай сообщение-ответ с утвердильных слов, по типу "Конечно", "Хорошо" и тд')
      else:
        res_with_recommendation_text = await generate(f'Посоветуй очень похожие произведения {get_choice_in_art(art)} (не авторов, ни жанры, а только произведения) исходя из {filter_to_search}, который называется {message.text}. Не начинай сообщение-ответ с утвердильных слов, по типу "Конечно", "Хорошо" и тд')
      
      
      if not res_with_recommendation_text:
          await message.answer('Нейросеть не смогла дать ответ, повтори запрос позже')
      else:
          await loading_msg.delete()
          #Отправляем сообщение с рекомендацией
          await message.answer(res_with_recommendation_text)

          #Записываем запрос и ответ нейросети с рекомендацией в базу данных
          if it_is_work_name(filter_to_search):
            await db.create_user_recommendation(message.from_user.id, (message.text[message.text.find(':')+1:]).strip(), res_with_recommendation_text, art, data['filter_to_search'])
          else:
            await db.create_user_recommendation(message.from_user.id, message.text, res_with_recommendation_text, art, data['filter_to_search'])
          await state.update_data(message_with_ressponse=res_with_recommendation_text)
      await state.clear()
  except:
      await loading_msg.delete()
      await message.answer('На сервере возникла ошибка, повторите ваш запрос позже')
  

#callback_query

#Обработчик, который проверяет - есть ли в очереди коллбэков элемент (callback) с data = 'Музыка'
@router.callback_query(F.data == 'Музыка', Req.art)
async def picks_music(callback: CallbackQuery, state: FSMContext):
    await state.update_data(art=callback.data)
    await state.set_state(Req.filter_to_search)
    await callback.answer('')
    await callback.message.edit_text('Выбери на основе чего ты хочешь найти рекомендацию', reply_markup=await kb.create_inline_keyboard([*os.getenv('inline_with_music_fields').split(','), '⬅️Назад']))

@router.callback_query(F.data == 'Книги', Req.art)
async def picks_books(callback: CallbackQuery, state: FSMContext):
    await state.update_data(art=callback.data)
    await state.set_state(Req.filter_to_search)
    await callback.answer('')
    #Изменяем текст сообщения, к которому прикреплён коллбэк
    await callback.message.edit_text('Выбери на основе чего ты хочешь найти рекомендацию', reply_markup=await kb.create_inline_keyboard([*os.getenv('inline_with_book_fields').split(','), '⬅️Назад']))

@router.callback_query(F.data == 'Фильмы', Req.art)
async def picks_films(callback: CallbackQuery, state: FSMContext):
    await state.update_data(art=callback.data)
    await state.set_state(Req.filter_to_search)
    await callback.answer('')
    await callback.message.edit_text('Выбери на основе чего ты хочешь найти рекомендацию', reply_markup=await kb.create_inline_keyboard([*os.getenv('inline_with_film_fields').split(','), '⬅️Назад']))
    
@router.callback_query(F.data == '⬅️Назад', Req.filter_to_search)
async def picks_films(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Req.art)
    await callback.answer('')
    await callback.message.edit_text('По чему ты хочешь получить рекомендацию?', reply_markup=await kb.create_inline_keyboard(os.getenv('inline_with_all_arts').split(',')))
    


@router.callback_query(Req.filter_to_search)
async def message_to_recommend(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.update_data(filter_to_search=callback.data)
    await state.set_state(Req.message_to_recommend)
    
    #Используем вспомогательные функции
    old_choice_in_filter = callback.data
    choice_in_filter = word_in_filter_choice[old_choice_in_filter]
    its_author = it_is_author(old_choice_in_filter)
    
    if it_is_work_name(old_choice_in_filter):
      await callback.message.edit_text(f'Введи {choice_in_filter} и имя автора, чтобы найти произведения, подходящие тебе по мнению нейросети. Пример ввода: "Автор: {choice_in_filter}"')
    else:
      await callback.message.edit_text(f'Введи {choice_in_filter}, чтобы найти {choice_in_author[old_choice_in_filter] if its_author else "произведения"}, подходящ{"их" if its_author else "ие"} тебе по мнению нейросети')
    
    
