from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

#Создаём Reply клавиатуру
reply = ReplyKeyboardMarkup(keyboard=[
    #Каждый список соотвествует строчке клавиатуры, то есть, если в одном списке разместить
    #Два объекта класса KeyboardButton, то на этой строчке будет две кнопки 
    #(это же работает с inline клавиатурой)
    [KeyboardButton(text='Получить рекомендацию')],
    [KeyboardButton(text='Узнать цвет своего вкуса')],
    [KeyboardButton(text='Самые популярные произведения')],
    [KeyboardButton(text='Мои прошлые рекомендации'), KeyboardButton(text='Цвета моего вкуса')]
], resize_keyboard=True, #Уменьшаем наши кнопки
   input_field_placeholder='Выберите пункт меню' #Изменяет значения placeholder
)

#Специальная функция, которая на основе входных данных создаёт inline клавиатуру и возвращает её
async def create_inline_keyboard(inline_buttons: list[str]):
    #Создаём объект keyboard класса InlineKeyboardBuilder
    keyboard = InlineKeyboardBuilder()
    for s in inline_buttons:
        #Добавляем каждое значения списка в нашу клавиатуру
        #При нажатии на кнопку в очередь коллбэков будет отправляться коллбэк с data равной callback_data
        keyboard.add(InlineKeyboardButton(text=s, callback_data=s))
    #В функцию adjust передаём значение, сколько в одном ряду будет кнопок, а as_markup() - обязательная преписка, которая возвращает итоговый объект клавиатуры
    return keyboard.adjust(1).as_markup()
