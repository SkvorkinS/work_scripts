import os
import requests
import traceback
from datetime import datetime
from credentials import API_REQUEST_TOKEN, BOT_TOKEN, CHAT_ID

def get_data(request_url):                                              # Получение данных по API с портала GSM counters
    response = requests.get(request_url)                                # Возвращает JSON
    json_data = response.json()
    return json_data

def convert_string(dictionary):                                         # Функция получает на вход словарь полученный с GSM counters
    dtime_str = dictionary['DTime']                                     # и форматирует в строку нужную для ITIGRIS optima
    dtime_obj = datetime.strptime(dtime_str, '%Y-%m-%dT%H:%M:%S')

    income = dictionary['Income']
    outcome = dictionary['Outcome']

    result_str = '{} {} {}'.format(
        dtime_obj.strftime('%H:%M'),
        str(income).zfill(4),
        str(outcome).zfill(4)
    )

    return result_str

def wrap_data(data):                                                    # Функция разворачивает JSON и раскидывает по папкам и файлам
    data_dict = {}                                                      # в соответсвии с датой и департаментом
    for a in data:                                                      # Проходимся по департаментам из JSON
        datetime_list = []                                              # создаем список для хранения данных одного департамента
        data_dict[a['ObjectCode']] = datetime_list                      # Вклладываем в него список
        folder_name = a['ObjectCode'].rstrip()                          # Убираем возможный пробел и получаем название папки
        now = datetime.now()
        date_time_string = now.strftime("%Y-%m-%d")
        if not os.path.exists(f'FTP/{folder_name}/'):                   # Проверяем наличие папки, если не существует - создаем
            os.makedirs(f'FTP/{folder_name}/')
        with open(f'FTP/{folder_name}/{date_time_string}', 'w') as f:   # Создаем файл департамента, и построчно записываем инфу в файл, форматируя каждую строку

            for b in a['Items']:
                result = convert_string(b)
                f.write(f'{result}\n')

    return data_dict


def main():
    data = get_data(API_REQUEST_TOKEN)                                  # Получаем JSON
    a = wrap_data(data)                                                 # Распаковываем инфу
    result = f'{a}'
    telegram_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={error_str}'
    requests.get(telegram_api_url) # Отправляем результат в телеграм
    print(error_str)

if __name__ == '__main__':
    try:
        main()
    except:
        error_str = traceback.format_exc()
        telegram_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={error_str}'
        requests.get(telegram_api_url)                                  # При возникновении ошибки отправить её в телеграм
