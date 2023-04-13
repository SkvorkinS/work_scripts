import os
import requests
import traceback
from ftplib import FTP
from FTPpaths import DP_INFO
from datetime import datetime
from credentials import API_REQUEST_TOKEN, BOT_TOKEN, CHAT_ID, FTP_HOST, FTP_USER, FTP_PASS


def send_by_ftp(server_folder, local_file_path, file_name):
    with FTP(FTP_HOST) as ftp:
        ftp.login(user=FTP_USER, passwd=FTP_PASS)
        with open(local_file_path, 'rb') as f:
            ftp.cwd(server_folder)
            ftp.storbinary(f'STOR {file_name}', f)
            ftp.quit()


def get_ftp_path_by_folder(folder_name):
    for path in DP_INFO:
        if folder_name == path['FOLDER']:
            return path['FTP_PATH']


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
    for departament in data:                                            # Проходимся по департаментам из JSON
        datetime_list = []                                              # создаем список для хранения данных одного департамента
        data_dict[departament['ObjectCode']] = datetime_list            # Вклладываем в него список
        folder_name = departament['ObjectCode'].rstrip()                # Убираем возможный пробел и получаем название папки
        now = datetime.now()
        date_time_string = now.strftime("%Y-%m-%d")
        if not os.path.exists(f'FTP/{folder_name}/'):                   # Проверяем наличие папки, если не существует - создаем
            os.makedirs(f'FTP/{folder_name}/')
        with open(f'FTP/{folder_name}/0101_{date_time_string}', 'w') as f:   # Создаем файл департамента, и построчно записываем инфу в файл, форматируя каждую строку

            for b in departament['Items']:
                result = convert_string(b)
                f.write(f'{result}\n')

        file_name = f"0101_{date_time_string}"
        file_to_send = f'FTP/{folder_name}/0101_{date_time_string}'
        FTP_path = get_ftp_path_by_folder(folder_name)

        if FTP_path is not None and FTP_path != '':
            print(file_to_send,)
            print(FTP_path)
            send_by_ftp(FTP_path, file_to_send, file_name)
    return data_dict


def main():
    raw_data = get_data(API_REQUEST_TOKEN)                                  # Получаем JSON
    data = wrap_data(raw_data)                                              # Распаковываем инфу
    result = f'{data}'
    telegram_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={result}'
    requests.get(telegram_api_url)                                          # Отправляем результат в телеграм

if __name__ == '__main__':
    try:
        main()
    except:
        error_str = traceback.format_exc()
        telegram_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={error_str}'
        print(error_str)
        requests.get(telegram_api_url)                              # При возникновении ошибки отправить её в телеграм
