from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
#Создаём Reply клавиатуру
# reply = ReplyKeyboardMarkup(keyboard=[
#     #Каждый список соотвествует строчке клавиатуры, то есть, если в одном списке разместить
#     #Два объекта класса KeyboardButton, то на этой строчке будет две кнопки 
#     #(это же работает с inline клавиатурой)
#     [KeyboardButton(text='Получить рекомендацию')],
#     [KeyboardButton(text='Узнать свой темперамент')],
#     [KeyboardButton(text='Самые популярные произведения')],
#     [KeyboardButton(text='Мои прошлые рекомендации')],
#     [KeyboardButton(text='Полученные мной темпераменты')]
# ], resize_keyboard=True, #Уменьшаем наши кнопки
#    input_field_placeholder='Выберите пункт меню' #Изменяет значения placeholder
# )


    
reply_kb = ReplyKeyboardMarkup(keyboard=[
    #Каждый список соотвествует строчке клавиатуры, то есть, если в одном списке разместить
    #Два объекта класса KeyboardButton, то на этой строчке будет две кнопки 
    #(это же работает с inline клавиатурой)
    [KeyboardButton(text='Что посмотреть?'),KeyboardButton(text='Что послушать?')],
    [KeyboardButton(text='Что почитать?')],
], resize_keyboard=True, #Уменьшаем наши кнопки
   input_field_placeholder='Выберите пункт меню' #Изменяет значения placeholder
)

class EstimationCallbackDataFilm(CallbackData, prefix="f"):
    type: str
    film_id: int

def get_inline_like_dislike_film_kb(film_id: str):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="👍", callback_data=EstimationCallbackDataFilm(type="Like", film_id=film_id).pack()))
    kb.add(InlineKeyboardButton(text="👎", callback_data=EstimationCallbackDataFilm(type="Dislike", film_id=film_id).pack()))
    return kb.adjust(2).as_markup()
    
class EstimationCallbackDataSong(CallbackData, prefix="s"):
    type: str
    song_id: int

def get_inline_like_dislike_song_kb(song_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="👍", callback_data=EstimationCallbackDataSong(type="Like", song_id=song_id).pack()))
    kb.add(InlineKeyboardButton(text="👎", callback_data=EstimationCallbackDataSong(type="Dislike", song_id=song_id).pack()))
    return kb.adjust(2).as_markup()

class EstimationCallbackDataBook(CallbackData, prefix="b"):
    type: str
    book_id: int

def get_inline_like_dislike_book_kb(book_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="👍", callback_data=EstimationCallbackDataBook(type="Like", book_id=book_id).pack()))
    kb.add(InlineKeyboardButton(text="👎", callback_data=EstimationCallbackDataBook(type="Dislike", book_id=book_id).pack()))
    return kb.adjust(2).as_markup()
    


#Специальная функция, которая на основе входных данных создаёт inline клавиатуру и возвращает её
# async def create_inline_keyboard(inline_buttons: list[str]):
#     #Создаём объект keyboard класса InlineKeyboardBuilder
#     keyboard = InlineKeyboardBuilder()
#     for s in inline_buttons:
#         #Добавляем каждое значения списка в нашу клавиатуру
#         #При нажатии на кнопку в очередь коллбэков будет отправляться коллбэк с data равной callback_data
#         keyboard.add(InlineKeyboardButton(text=s, callback_data=s))
#     #В функцию adjust передаём значение, сколько в одном ряду будет кнопок, а as_markup() - обязательная преписка, которая возвращает итоговый объект клавиатуры
#     return keyboard.adjust(1).as_markup()
