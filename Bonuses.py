import os
import time
import traceback
import requests
import pandas as pd
from tqdm import tqdm
from loguru import logger
from credentials import ITIGRIS_API_KEY_1, ITIGRIS_API_KEY_2, ITIGRIS_COMPANY_ID





def clear_number(number):
    number = number.replace(" ", "")                                                                # удаляем пробелы
    number = number.replace("(", "")                                                                # удаляем левую скобку
    number = number.replace(")", "")                                                                # удаляем правую скобку
    number = number.replace("+", "")                                                                # удаляем знак плюса
    number = number.replace("-", "")                                                                # удаляем знак дефиса


    return number

def get_bonuses(number):                                                                            # Функция получает на вход номер телефона, номер телефона и возвращает
    logger.info(f'Truing to get info by number:{number}')                                           # количество доступных бонусов клиента
    try:
        get_client_url = f'https://optima.itigris.ru/{ITIGRIS_COMPANY_ID}/remoteClientCard/getClient?key={ITIGRIS_API_KEY_1}&tel={number}'
        client_id = requests.get(get_client_url, timeout=10).text                                              # Получаем ID клиента
        logger.info(f'Gоt client_id:{client_id}')

        get_client_card_url = f'https://optima.itigris.ru/{ITIGRIS_COMPANY_ID}/remoteClientCard/getClientCard?key={ITIGRIS_API_KEY_1}&clientId={client_id}'
        client_card_id = requests.get(get_client_card_url ,timeout=10).text                                             # Получаем ID карты клиента
        logger.info(f'Gоt client_card_id:{client_card_id}')

        get_bonus_info_url = f'https://optima.itigris.ru/{ITIGRIS_COMPANY_ID}/apiBonusInfo?key={ITIGRIS_API_KEY_2}&clientCardId={client_card_id}&withExpired=true'
        bonus_info = requests.get(get_bonus_info_url, timeout=10)                                                       # Получаем инфу по бонусам
        logger.info(f'Gоt bonus_info:{bonus_info}')


    except:                                                                                         # При нестабильном подключении ловим ошибку и пытаемся сделать запрос ещё раз
        error_str = traceback.format_exc()
        logger.error(f'Failed! error: {error_str} Retry in 10s')
        time.sleep(10)
        get_bonuses(number)

    try:                                                                                            # Пытаемся из ответа получить JSON, но при нулевом балансе, получаем строку. В этом случае ловим исключение
        logger.info('Trying to get bonus_info_json')                                                # и присваем значения для бонуса в 0
        bonus_info_json = bonus_info.json()
        bonus_info_text = bonus_info_json["activePoints"]
        logger.info(f'Sucess! bonus_info_text: {bonus_info_text}')

    except:
        logger.error(f'Failed! Client doesnt have bonus points')
        bonus_info_text = 0
    os.system('cls||clear')


    return bonus_info_text

def main():
    tqdm.pandas(desc="Processing rows")
    logger.info('Reading from csv')
    rawdata_df = pd.read_csv('data/data_bro.csv')                                                   # Читаем CSV файл
    logger.info('Formating phone numbers')
    rawdata_df['NUMBERS'] = rawdata_df['NUMBERS'].apply(clear_number)                               # Приводим номера телефонов к нормальному виду
    bonus_info = rawdata_df.copy()
    logger.info('Begining to get user info')
    bonus_info['BONUS'] = rawdata_df['NUMBERS'].progress_apply(get_bonuses)                         # Получаем бонусы по номеру телефона клиента
    bonus_info = bonus_info.drop(index=bonus_info[bonus_info['BONUS'] == 0].index)                  # Убираем строки с нулеввым бонусом
    logger.info('Finished')
    bonus_info.to_csv('data/bonus_info.csv')                                                        # Записываем результат в файл

if __name__ == '__main__':
    try:
        logger.info('Started')
        logger.add("logs/Bonuses.log", format="{time} {level} {message}", level="DEBUG")
        main()
    except:
        error_str = traceback.format_exc()
        logger.error(f'Failed! error: {error_str}')
        exit()
