import sqlite3 as sq

db = sq.connect('tg.db') #Подключение к файлу с базой данных (Если его не существует - будет автоматически создан файл с базой данных, и произойдёт подключение к нему)
cur = db.cursor() #Создаём объект курсор, с помоью него мы будем делать sql запросы

#Функция для создания всех таблиц в базе данных
async def db_start():
  #Таблица с пользователями
  cur.execute('CREATE TABLE IF NOT EXISTS users('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'username VARCHAR(64) NOT NULL, '
              'tg_id INTEGER NOT NULL'
              ')')
  #Таблица с рекомендациями
  cur.execute('CREATE TABLE IF NOT EXISTS recommendations('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'recommendation_text VARCHAR(4096) NOT NULL, '
              'request_text VARCHAR(2048) NOT NULL, '
              'art VARCHAR(64) NOT NULL, '
              'filter VARCHAR(64) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(id)'
              ')')
  #Таблица с цветами вкуса пользователей
  cur.execute('CREATE TABLE IF NOT EXISTS users_colors('
              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'user_id INTEGER, '
              'request_text VARCHAR(4096) NOT NULL, '
              'text_with_color VARCHAR(128) NOT NULL, '
              'FOREIGN KEY (user_id) REFERENCES users(id)'
              ')')
  #Не забываем сохранить имзенения в базу данных
  db.commit()
  
#Добавление пользователя в таблицу users
async def create_user(username, tg_id):
  cur.execute('SELECT * FROM users WHERE tg_id = ?', [tg_id])
  #Говорим, чтобы будем выбирать только один элемент
  user = cur.fetchone()
  if not user:
    cur.execute('INSERT INTO users(username, tg_id) VALUES (?, ?)', [username, tg_id])
    db.commit() #Сохраняем изменения в таблицу
  
#Получение пользователя из таблицы users
async def get_user(tg_id):
  user = cur.execute('SELECT * FROM users WHERE tg_id = ?', [tg_id]).fetchone()
  return user

#Добавление рекомендации в таблицу recommendations
async def create_user_recommendation(user_id, request_text, recommendation_text, art, filter):
  cur.execute('INSERT INTO recommendations (user_id, request_text, recommendation_text, art, filter) VALUES (?, ?, ?, ?, ?)', [user_id, request_text, recommendation_text, art, filter])
  db.commit() #Сохраняем изменения в таблицу
  
#Добавление цвета в таблицу users_colors
async def create_user_color(user_id, request_text, text_with_color):
  cur.execute('INSERT INTO users_colors(user_id, request_text, text_with_color) VALUES (?, ?, ?)', [user_id, request_text, text_with_color])
  db.commit() #Сохраняем изменения в таблицу
  
#Получение всех рекомендаций пользователя из таблицы users
async def get_user_recommendations(user_id):
  cur.execute('SELECT * FROM recommendations WHERE user_id = ?', [user_id])
  #Говорим, чтобы будем выбирать все элементы, удовлетворяющие условию
  recommendations = cur.fetchall()
  return recommendations

#Получение всех цветов пользователя из таблицы users_colors
async def get_user_colors(user_id):
  cur.execute('SELECT * FROM users_colors WHERE user_id = ?', [user_id])
  #Говорим, чтобы будем выбирать все элементы, удовлетворяющие условию
  colors = cur.fetchall() 
  return colors

#Получение абсолютно всех рекомендаций из таблицы recommendations
async def get_all_recommendations():
  cur.execute('SELECT * FROM recommendations')
  #Говорим, чтобы будем выбирать все элементы, удовлетворяющие условию
  recommendations = cur.fetchall()
  return recommendations