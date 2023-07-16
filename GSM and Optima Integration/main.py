import os
import requests
import traceback
import pytz
from loguru import logger
from ftplib import FTP
from FTPpaths import DP_INFO
from sender import TelegramMessageSender
import datetime
from credentials import API_REQUEST_TOKEN, BOT_TOKEN, CHAT_ID, FTP_HOST, FTP_USER, FTP_PASS, FTP_LOCAL_FOLDER

sender = TelegramMessageSender(BOT_TOKEN, CHAT_ID, f'{FTP_LOCAL_FOLDER}/state.json')
_now = datetime.datetime.now(pytz.timezone('Asia/Almaty'))

def send_by_ftp(server_folder, local_file_path, file_name):         # Отправляте данные на сервер оптимы
    logger.info(f"Sending file:{local_file_path}/{file_name} to server")
    try:
        with FTP(FTP_HOST) as ftp:
            ftp.login(user=FTP_USER, passwd=FTP_PASS)
            with open(local_file_path, 'rb') as f:
                ftp.cwd(server_folder)
                ftp.storbinary(f'STOR {file_name}', f)
                ftp.quit()
        logger.info(f"File succeful sent")
    except:
        error_str = traceback.format_exc()
        logger.error(f"FILE NOT SENT !")
        logger.error(error_str)


def get_ftp_path_by_folder(folder_name):
    logger.info(f"Reading server path for file: {folder_name}")
    for path in DP_INFO:
        if folder_name == path['FOLDER']:
            logger.info(f"Server path recieved succefly: \n{path['FTP_PATH']}")
            return path['FTP_PATH']
    logger.error(f"FAILED TO GET SERVER PATH !!!")


def get_data(request_url):                                              # Получение данных по API с портала GSM counters
    logger.info("Counter data request")
    response = requests.get(request_url)                                # Возвращает JSON
    json_data = response.json()
    return json_data


def convert_string(dictionary):                                         # Функция получает на вход словарь полученный с GSM counters

    dtime_str = dictionary['DTime']                                     # и форматирует в строку нужную для ITIGRIS optima
    dtime_obj = datetime.datetime.strptime(dtime_str, '%Y-%m-%dT%H:%M:%S')
    today = datetime.date.today()
    if dtime_obj.date() != today:
        return
    income = dictionary['Income']
    outcome = dictionary['Outcome']

    result_str = '{} {} {}'.format(
        dtime_obj.strftime('%H:%M'),
        str(income).zfill(4),
        str(outcome).zfill(4)
    )

    return result_str

def wrap_data(data):                                                    # Функция разворачивает JSON и раскидывает по папкам и файлам
    logger.info("Starting unwrap JSON")
    data_dict = {}                                                      # в соответсвии с датой и департаментом

    tg_result_str = ''

    for departament in data:                                            # Проходимся по департаментам из JSON
        datetime_list = []                                              # создаем список для хранения данных одного департамента
        data_dict[departament['ObjectCode']] = datetime_list            # Вклладываем в него список
        folder_name = departament['ObjectCode'].rstrip()                # Убираем возможный пробел и получаем название папки

        date_time_string = _now.strftime("%Y-%m-%d")



        if not os.path.exists(f'{FTP_LOCAL_FOLDER}/{folder_name}/'):                   # Проверяем наличие папки, если не существует - создаем
            logger.info(f'Creating folder: {FTP_LOCAL_FOLDER}/{folder_name}/')
            os.makedirs(f'{FTP_LOCAL_FOLDER}/{folder_name}/')
        else:
            logger.info(f'Folder exist: {FTP_LOCAL_FOLDER}/{folder_name}')
        with open(f'{FTP_LOCAL_FOLDER}/{folder_name}/0101_{date_time_string}', 'w') as f:   # Создаем файл департамента, и построчно записываем инфу в файл, форматируя каждую строку

            for b in departament['Items']:
                result = convert_string(b)
                if result is not None:
                    f.write(f'{result}\n')

        file_name = f"0101_{date_time_string}"
        file_to_send = f'{FTP_LOCAL_FOLDER}/{folder_name}/0101_{date_time_string}'
        FTP_path = get_ftp_path_by_folder(folder_name)

        income_sum = 0
        outcome_sum = 0

        for i in departament['Items']:
            dtime_str = i['DTime']                                     # и форматирует в строку нужную для ITIGRIS optima
            dtime_obj = datetime.datetime.strptime(dtime_str, '%Y-%m-%dT%H:%M:%S')
            today = datetime.date.today()
            if dtime_obj.date() == today:
                income_sum = income_sum + i['Income']
                outcome_sum = outcome_sum + i['Outcome']

        if income_sum > 0 and outcome_sum > 0:
            is_work = '✅' # Смайлик галочка
            average = (income_sum + outcome_sum)//2
        else:
            is_work = '❌' # Смайлик крестик
            average = 0

        tg_result_str = tg_result_str + f'Департамент: {departament["ObjectCode"]} {is_work}\nКоличество посетителей: {average}\n---\n'
        print(average)
        if FTP_path is not None and FTP_path != '':
            send_by_ftp(FTP_path, file_to_send, file_name)
    return data_dict, tg_result_str


def main():
    date_time_string = _now.strftime("%Y-%m-%d %H:%M")
    logger.info("Starting")
    raw_data = get_data(API_REQUEST_TOKEN)                                  # Получаем JSON
    data, tg_result = wrap_data(raw_data)                                              # Распаковываем инфу
    result = f'{data}'
    tg_result = f'**SOME INFO**\n Дата: {date_time_string}\n\n{tg_result}'

    sender.send_message(tg_result)
    telegram_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=\n{tg_result}'

    #request = requests.get(telegram_api_url)                                          # Отправляем результат в телеграм


    logger.info("Job finished. Exiting")
if __name__ == '__main__':
    try:

        main()
    except:
        error_str = traceback.format_exc()
        logger.error(f"ERROR !!! {error_str}")
        telegram_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={error_str}'
        #requests.get(telegram_api_url)                              # При возникновении ошибки отправить её в телеграм
