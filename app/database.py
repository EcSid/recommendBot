import aiosqlite as sq

db = None
cur = None

#Функция для создания всех таблиц в базе данных
async def db_start():
  global db, cur
  
  db = await sq.connect('tg.db') #Подключение к файлу с базой данных (Если его не существует - будет автоматически создан файл с базой данных, и произойдёт подключение к нему)
  cur = await db.cursor() #Создаём объект курсор, с помоью него мы будем делать sql запросы
  #Таблица с пользователями
  await cur.execute('CREATE TABLE IF NOT EXISTS users('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'username VARCHAR(64) NOT NULL, '
              'tg_id INTEGER NOT NULL, '
              'registered INTEGER NOT NULL, '
              'agreed INTEGER NOT NULL'
              ')')
  # #Таблица с рекомендациями
  # await cur.execute('CREATE TABLE IF NOT EXISTS recommendations('
  #             'id INTEGER PRIMARY KEY AUTOINCREMENT, '
  #             'user_id INTEGER, '
  #             'recommendation_text VARCHAR(4096) NOT NULL, '
  #             'request_text VARCHAR(2048) NOT NULL, '
  #             'art VARCHAR(64) NOT NULL, '
  #             'filter VARCHAR(64) NOT NULL, '
  #             'FOREIGN KEY (user_id) REFERENCES users(id)'
  #             ')')
  # #Таблица с цветами вкуса пользователей
  # await cur.execute('CREATE TABLE IF NOT EXISTS users_colors('
  #             'id INTEGER PRIMARY KEY AUTOINCREMENT, '
  #             'user_id INTEGER, '
  #             'request_text VARCHAR(4096) NOT NULL, '
  #             'text_with_color VARCHAR(128) NOT NULL, '
  #             'FOREIGN KEY (user_id) REFERENCES users(id)'
  #             ')')
  #Таблица с любимыми произведениями пользователя
  await cur.execute('CREATE TABLE IF NOT EXISTS users_favourite_films('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_favourite_songs('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'author VARCHAR(128) NOT NULL, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_favourite_books('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  
  await cur.execute('CREATE TABLE IF NOT EXISTS users_recommended_films('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_recommended_songs('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'author VARCHAR(128) NOT NULL, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_recommended_books('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_film_likes('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_film_dislikes('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_song_likes('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'author VARCHAR(128) NOT NULL, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_song_dislikes('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'author VARCHAR(128) NOT NULL, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_book_likes('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  await cur.execute('CREATE TABLE IF NOT EXISTS users_book_dislikes('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'work_name VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(tg_id)'
              ')')
  #Не забываем сохранить имзенения в базу данных
  await db.commit()
  
#Добавление пользователя в таблицу users
async def create_user(username, tg_id):
  await cur.execute('SELECT * FROM users WHERE tg_id = ?', [tg_id])
  #Говорим, чтобы будем выбирать только один элемент
  user = await cur.fetchone()
  if not user:
    await cur.execute('INSERT INTO users(username, tg_id, registered, agreed) VALUES (?, ?, ?, ?)', [username, tg_id, 0, 0])
    await db.commit() #Сохраняем изменения в таблицу
  
#Получение пользователя из таблицы users
async def get_user(tg_id):
  await cur.execute('SELECT * FROM users WHERE tg_id = ?', [tg_id])
  user = await cur.fetchone()
  return user

#Добавление рекомендации в таблицу recommendations
# async def create_user_recommendation(user_id, request_text, recommendation_text, art, filter):
#   await cur.execute('INSERT INTO recommendations (user_id, request_text, recommendation_text, art, filter) VALUES (?, ?, ?, ?, ?)', [user_id, request_text, recommendation_text, art, filter])
#   await db.commit() #Сохраняем изменения в таблицу

#CreateFavourite
async def create_user_favourite_film(user_id, work_name):
  await cur.execute('INSERT INTO users_favourite_films(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit() #Сохраняем изменения в таблицу
  
async def create_user_favourite_song(user_id, author, song_name):
  await cur.execute('INSERT INTO users_favourite_songs(user_id, author, work_name) VALUES (?, ?, ?)', [user_id, author, song_name])
  await db.commit() #Сохраняем изменения в таблицу
  
async def create_user_favourite_book(user_id, work_name):
  await cur.execute('INSERT INTO users_favourite_books(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit() #Сохраняем изменения в таблицу
  
#GetAllFavourite
async def get_all_favourite_films(user_id):
  await cur.execute('SELECT * FROM users_favourite_films WHERE user_id = ?', [user_id])
  favourite_films = await cur.fetchall()
  return map(lambda el: el[2],favourite_films)

async def get_all_favourite_songs(user_id):
  await cur.execute('SELECT * FROM users_favourite_songs WHERE user_id = ?', [user_id])
  favourite_songs = await cur.fetchall()
  return map(lambda el: [el[2], el[3]],favourite_songs)

async def get_all_favourite_books(user_id):
  await cur.execute('SELECT * FROM users_favourite_books WHERE user_id = ?', [user_id])
  favourite_books = await cur.fetchall()
  return map(lambda el: el[2],favourite_books)


#CreateRecommended
async def create_user_recommended_film(user_id, work_name):
  await cur.execute('INSERT INTO users_recommended_films(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit() #Сохраняем изменения в таблицу
  
async def create_user_recommended_song(user_id, song_name, author):
  await cur.execute('INSERT INTO users_recommended_songs(user_id, work_name, author) VALUES (?, ?, ?)', [user_id, song_name, author])
  await db.commit() #Сохраняем изменения в таблицу
  
async def create_user_recommended_book(user_id, work_name):
  await cur.execute('INSERT INTO users_recommended_books(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit() #Сохраняем изменения в таблицу
  
#GetAllRecommended
async def get_all_recommended_films(user_id):
  await cur.execute('SELECT * FROM users_recommended_films WHERE user_id = ?', [user_id])
  recommended_films = await cur.fetchall()
  return map(lambda el: el[2],recommended_films)

async def get_all_recommended_songs(user_id):
  await cur.execute('SELECT * FROM users_recommended_songs WHERE user_id = ?', [user_id])
  recommended_songs = await cur.fetchall()
  return map(lambda el: [el[2], el[3]],recommended_songs)

async def get_all_recommended_books(user_id):
  await cur.execute('SELECT * FROM users_recommended_books WHERE user_id = ?', [user_id])
  recommended_books = await cur.fetchall()
  return map(lambda el: el[2],recommended_books)

#GetRecommendedFilmId
async def get_recommended_film_id(film_name):
  await cur.execute('SELECT * FROM users_recommended_films WHERE work_name = ?', [film_name])
  recommended_film = await cur.fetchone()
  return recommended_film[0]

#GetRecommendedFilmFromId
async def get_recommended_film_name_from_film_id(film_id):
  await cur.execute('SELECT * FROM users_recommended_films WHERE id = ?', [film_id])
  recommended_film = await cur.fetchone()
  return recommended_film[2]

#GetRecommendedSongId
async def get_recommended_song_id(song_name, author):
  await cur.execute('SELECT * FROM users_recommended_songs WHERE work_name = ? AND author = ?', [song_name, author])
  recommended_song = await cur.fetchone()
  return recommended_song[0]

#GetRecommendedSongFromId
async def get_recommended_song_author_and_name_from_song_id(song_id):
  await cur.execute('SELECT * FROM users_recommended_songs WHERE id = ?', [song_id])
  recommended_song = await cur.fetchone()
  return recommended_song[2], recommended_song[3]

#GetRecommendedBookId
async def get_recommended_book_id(book_name):
  await cur.execute('SELECT * FROM users_recommended_books WHERE work_name = ?', [book_name])
  recommended_book = await cur.fetchone()
  return recommended_book[0]

#GetRecommendedBookFromId
async def get_recommended_book_name_from_book_id(book_id):
  await cur.execute('SELECT * FROM users_recommended_books WHERE id = ?', [book_id])
  recommended_book = await cur.fetchone()
  return recommended_book[2]

#Films
async def create_user_film_like(user_id, work_name: str):
  await cur.execute('INSERT INTO users_film_likes(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit()
  
async def create_user_film_dislike(user_id, work_name: str):
  await cur.execute('INSERT INTO users_film_dislikes(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit()
  
async def get_all_user_film_likes(user_id):
  await cur.execute('SELECT * FROM users_film_likes WHERE user_id = ?', [user_id])
  liked_films = await cur.fetchall()
  return map(lambda el: el[2], liked_films)
  
async def get_all_user_film_dislikes(user_id):
  await cur.execute('SELECT * FROM users_film_dislikes WHERE user_id = ?', [user_id])
  disliked_films = await cur.fetchall()
  return map(lambda el: el[2], disliked_films)

#Songs
async def create_user_song_like(user_id, author: str, work_name: str):
  await cur.execute('INSERT INTO users_song_likes(user_id, author, work_name) VALUES (?, ?, ?)', [user_id, author, work_name])
  await db.commit()
  
async def create_user_song_dislike(user_id, author: str, work_name: str):
  await cur.execute('INSERT INTO users_song_dislikes(user_id, author, work_name) VALUES (?, ?, ?)', [user_id, author, work_name])
  await db.commit()
  
async def get_all_user_song_likes(user_id):
  await cur.execute('SELECT * FROM users_song_likes WHERE user_id = ?', [user_id])
  liked_songs = await cur.fetchall()
  return map(lambda el: [el[2], el[3]], liked_songs)
  
async def get_all_user_song_dislikes(user_id):
  await cur.execute('SELECT * FROM users_song_dislikes WHERE user_id = ?', [user_id])
  disliked_songs = await cur.fetchall()
  return map(lambda el: [el[2], el[3]], disliked_songs)

#Books
async def create_user_book_like(user_id, work_name: str):
  await cur.execute('INSERT INTO users_book_likes(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit()
  
async def create_user_book_dislike(user_id, work_name: str):
  await cur.execute('INSERT INTO users_book_dislikes(user_id, work_name) VALUES (?, ?)', [user_id, work_name])
  await db.commit()
  
async def get_all_user_book_likes(user_id):
  await cur.execute('SELECT * FROM users_book_likes WHERE user_id = ?', [user_id])
  liked_books = await cur.fetchall()
  return map(lambda el: el[2], liked_books)
  
async def get_all_user_book_dislikes(user_id):
  await cur.execute('SELECT * FROM users_book_dislikes WHERE user_id = ?', [user_id])
  disliked_books = await cur.fetchall()
  return map(lambda el: el[2], disliked_books)

#Other
async def register_user(user_id):
  await cur.execute('UPDATE users '
                'SET registered = 1 '
                'WHERE tg_id = ?', [user_id])
  await db.commit()
  
async def check_user_is_full_registered(user_id):
  await cur.execute('SELECT * FROM users WHERE tg_id = ?', [user_id])
  #Говорим, чтобы будем выбирать только один элемент
  user = await cur.fetchone()
  if user: 
    if user[3] == 1:
      return True 
    else:
      return False
  else:
    return False

# #Добавление цвета в таблицу users_colors
# async def create_user_color(user_id, request_text, text_with_color):
#   await cur.execute('INSERT INTO users_colors(user_id, request_text, text_with_color) VALUES (?, ?, ?)', [user_id, request_text, text_with_color])
#   await db.commit() #Сохраняем изменения в таблицу
  
# #Получение всех рекомендаций пользователя из таблицы users
# async def get_user_recommendations(user_id):
#   await cur.execute('SELECT * FROM recommendations WHERE user_id = ?', [user_id])
#   #Говорим, чтобы будем выбирать все элементы, удовлетворяющие условию
#   recommendations = await cur.fetchall()
#   return recommendations

# #Получение всех цветов пользователя из таблицы users_colors
# async def get_user_colors(user_id):
#   await cur.execute('SELECT * FROM users_colors WHERE user_id = ?', [user_id])
#   colors = await cur.fetchall() 
#   return colors

# #Получение абсолютно всех рекомендаций из таблицы recommendations
# async def get_all_recommendations():
#   await cur.execute('SELECT * FROM recommendations')
#   recommendations = await cur.fetchall()
#   return recommendations

