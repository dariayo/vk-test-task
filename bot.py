import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from flask import Flask, request
import json
import os

TOKEN = 'your_vk_token'  # Замените на ваш токен
GROUP_ID = 'your_group_id'  # Замените на ID вашей группы

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

longpoll = VkLongPoll(vk_session, group_id=GROUP_ID)

# Создание Flask приложения для обработки Webhook 
app = Flask(__name__)

# Обработка сообщений
def send_message(user_id, message, attachment=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        attachment=attachment,
        random_id=0
    )

def handle_message(event):
    user_id = event.user_id

    if event.type == VkEventType.MESSAGE_NEW and event.from_user:
        if event.text:  
            return

        if event.attachments:
            for attachment in event.attachments:
                if attachment['type'] == 'photo':
                    photo_url = attachment['photo']['sizes'][-1]['url']
                    send_message(user_id, '', attachment=photo_url)

def listen_for_messages():
    for event in longpoll.listen():
        handle_message(event)

def send_welcome_message(user_id):
    message = "Привет! Я бот. Отправь мне изображение, и я отправлю его обратно"
    send_message(user_id, message)

# Запуск Flask 
@app.route('/', methods=['POST'])
def webhook():
    data = json.loads(request.data)
    if 'object' in data:
        object = data['object']
        if object['type'] == 'message_new':
            user_id = object['object']['message']['from_id']
            send_welcome_message(user_id) 
    return '', 200

if __name__ == '__main__':
    listen_for_messages()  
