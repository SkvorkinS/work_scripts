import requests
from datetime import datetime, date
import json
from loguru import logger

class TelegramMessageSender:
    def __init__(self, token, chat_id, state_file):
        self.token = token
        self.chat_id = chat_id
        self.state_file = state_file

    def send_message(self, message):
        current_date = datetime.now().date()
        previous_message_id, previous_message_date = self._load_state()

        if previous_message_date and previous_message_date == current_date:
            self._delete_previous_message(previous_message_id)

        response = self._send_new_message(message)
        if response.status_code == 200:
            data = response.json()
            message_id = data['result']['message_id']
            self._save_state(message_id, current_date)
            logger.info('New message sent')
        else:
            logger.error(f'ERROR MESSAGE WAS NOT SENT !!!, {response.text}')

    def _load_state(self):
        try:
            with open(self.state_file, 'r') as file:
                state = json.load(file)
                previous_message_id = state.get('previous_message_id')
                previous_message_date_str = state.get('previous_message_date')
                if previous_message_date_str:
                    previous_message_date = datetime.strptime(previous_message_date_str, '%Y-%m-%d').date()
                else:
                    previous_message_date = None
        except FileNotFoundError:
            previous_message_id = None
            previous_message_date = None
        return previous_message_id, previous_message_date

    def _delete_previous_message(self, message_id):
        if message_id:
            url = f'https://api.telegram.org/bot{self.token}/deleteMessage?chat_id={self.chat_id}&message_id={message_id}'
            response = requests.get(url)
            if response.status_code == 200:
                logger.info('Old message deleted')
            else:
                logger.error(f'ERROR OLD MESSAGE WAS NOT DELETED !!!, {response.text}')

    def _send_new_message(self, message):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={message}'
        response = requests.get(url)
        return response

    def _save_state(self, message_id, current_date):
        state = {
            'previous_message_id': message_id,
            'previous_message_date': current_date.strftime('%Y-%m-%d')
        }
        with open(self.state_file, 'w') as file:
            json.dump(state, file)

# Пример использования модуля

if __name__ == '__main__':
    # Установите токен вашего бота и chat_id чата, в который нужно отправлять сообщения
    TOKEN = 'your_bot_token'
    chat_id = 'your_chat_id'

    # Установите имя файла для сохранения состояния переменных
    state_file = 'state.json'

    # Создайте экземпляр класса TelegramMessageSender
    sender = TelegramMessageSender(TOKEN, chat_id, state_file)

    # Отправьте сообщение
    message_text = 'Текст нового сообщения'
    sender.send_message(message_text)
