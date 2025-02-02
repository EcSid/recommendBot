import requests
import os
from dotenv import load_dotenv
from uuid import uuid4
import json

load_dotenv()



async def generate(text):
    #Получения токена доступа
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload={
    'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': str(uuid4()), #Генерируем id
    'Authorization': f'Basic {os.getenv("AI_TOKEN")}' #Ключ для авторизации
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False) #Запрос для получение токена доступа
    access_token = json.loads(response.text)['access_token'] #Токен доступа
    
    #Получение ответа от GigaChat на сообщение
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload = json.dumps({
    "model": "GigaChat",
    "messages": [
        {
        "role": "user",
        "content": text #Текст сообщения
        }
    ],
    "stream": False,
    "repetition_penalty": 1
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False) #запрос для получения ответа от GigaChat на сообщение
    return json.loads(response.text)['choices'][0]['message']['content']
