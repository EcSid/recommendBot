#Helpers(вспомагательные функции)
#Отсортировать массив по популярности
def sort_arr_to_most_popular(arr):
  #Сама сортировка
  def sort_arr(data):
    return sorted(data, key=lambda x: (-int(x.split('(')[-1].split(')')[0]), x.split(' (')[0]))
  
  #Оставляем только уникальные значения и добавляем к каждому количество в списке
  arr1 = list(map(lambda x: x.lower(), arr))
  l = list(set(arr1))
  arr2 = list(map(lambda el: f'{el} ({arr1.count(el)})', l)) 
  
  #Пробегаемся по отсортированному массиву и добавляем к каждому номер в списке
  final = []
  ind = 0
  for el in sort_arr(arr2):
    final.append(f'{ind + 1}. {el}')
    ind += 1
  return final

#Орфография
def get_choice_in_art(s): 
  return 'музыку' if s == 'Музыка' else 'фильмы' if s == 'Фильмы' else 'книги'

word_in_filter_choice = {
        'Жанр': 'название жанра',
        'Исполнитель': 'имя музыкального исполнителя',
        'Альбом': 'название альбома',
        'Песня': 'название песни',
        'Книга': 'название книги',
        'Писатель': 'имя писателя',
        'Фильм': 'название фильма',
        'Режиссёр': 'имя режиссёра',
        '⬅️Назад': '⬅️Назад'
    }

choice_in_author = {
  'Режиссёр': 'режиссёров',
  'Исполнитель': 'музыкантов',
  'Писатель': 'писателей',
}

#Проверка 

def it_is_work_name(s: str):
  if s == 'Альбом' or s == 'Книга' or s == 'Песня':
    return True
  return False

def it_is_author(s: str):
  if s == 'Исполнитель' or s == 'Писатель' or s == 'Режиссёр':
    return True
  return False




