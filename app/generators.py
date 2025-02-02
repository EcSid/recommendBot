import requests
import os
from dotenv import load_dotenv
from uuid import uuid4
import json

load_dotenv()



async def generate(text):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload={
    'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': str(uuid4()),
    'Authorization': f'Basic {os.getenv("AI_TOKEN")}'
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    access_token = json.loads(response.text)['access_token']
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload = json.dumps({
    "model": "GigaChat",
    "messages": [
        {
        "role": "user",
        "content": text
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

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return json.loads(response.text)['choices'][0]['message']['content']
