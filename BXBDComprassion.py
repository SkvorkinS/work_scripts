import os
import sys
import math
import time
import requests
import traceback
import numpy as np
import pandas as pd
from loguru import logger
from progress.spinner import Spinner
from progress.bar import IncrementalBar
from credentials import HOST_DOMAIN, ALLOWED_COMPANY_NAMES, COMPANY_COLLUMS, COMPANY_COLLUMS_RENAMED, MIN_COMPANY_COLLUMS, MIN_COMPANY_COLLUMS_RENAMED, OTHER_CURRENCY_STORE, CURRENCY


def make_request(url):
    '''Функция получает ссылку и делает GET запросы пока не получит положительный результат'''
    try:
        requests.get(url, timeout=10)
    except:
        logger.error('Connection error. Rertry in 10s')
        time.sleep(10)
        make_request(url)

def get_company_name(argv):
    '''
    Функция проверяет аргументы запуска скрипта, если они отсутствуют или они не входят в
    список допустимых просит ввести вручную. Возвращает название компании.
    '''

    try:
        if not argv[1] or argv[1] not in ALLOWED_COMPANY_NAMES:                                     # Проверка аргументов на наличие в списке допустимых компаний
            print("Введите назваение компании: ", end="")                                           # Если аргументы не находятся в списке, то запрашивает данные у пользователя
            company = input()
        else:
            company =argv[1]
    except:
            print("Введите назваение компании: ", end="")                                           # Если никаких аргументов не передано, то обрабатывается исключение
            company = input()                                                                       # и запрашивает данные у пользователя
    return company

def read_bxdata_from_csv_by_company(company):
    """
    Функция получает на вход название компании и использует реквизиты для чтения дампа с BX24 в датафрейм bitrix_all_info,
    который используется для обновления сделок в БД. Возвращает датафрейм bitrix_all_info и форматированное название компании.
    """

    if company == ALLOWED_COMPANY_NAMES[0]:                                                                 # Если компания находится в списке допустимых компаний на 0 позиции
        company = ALLOWED_COMPANY_NAMES[0].upper()                                                          # то считывает файл по правилам компании 0
        bitrix_all_info = pd.read_csv(f'data/{company}/DEALS.csv',sep=';', usecols=COMPANY_COLLUMS[0])
        bitrix_all_info = bitrix_all_info.rename(columns=COMPANY_COLLUMS_RENAMED[0])


    elif company == ALLOWED_COMPANY_NAMES[1]:                                                               # Если компания находится в списке допустимых компаний на 1 позиции
        company = ALLOWED_COMPANY_NAMES[1].upper()                                                          # то считывает файл по правилам компании 1
        bitrix_all_info = pd.read_csv(f'data/{company}/DEALS.csv',sep=';', usecols=COMPANY_COLLUMS[1])
        bitrix_all_info = bitrix_all_info.rename(columns=COMPANY_COLLUMS_RENAMED[1])

    else:                                                                                                   # Если компания не находится в списке допустимых компаний
        logger.error(f'Company {company} is not in allowed list!')                                          # то программа завершает работу
        exit()

    return bitrix_all_info, company

def read_minimal_BX_data_for_comparison(company):
    """
    Функция получает на вход название компании и использует реквизиты для чтения дампа с BX24 в датафрейм BX_data_df,
    который используется для сравнения с датафреймом DB_data_df. Возвращает BX_data_df и сумму столбца "SUMM"
    """

    BX_data_df = pd.read_csv(f'data/{company}/DEALS.csv', sep=';', usecols=MIN_COMPANY_COLLUMS)     # Чтение файла в датафрейм BX_data_df
    BX_data_df = BX_data_df.rename(columns=MIN_COMPANY_COLLUMS_RENAMED)

    BX_data_df['STORE_NAME'] = BX_data_df['STORE_NAME'].fillna('')                                  # Заполняем NaN  в столбце STORE_NAME
    BX_data_df['SUMM'] = pd.to_numeric(BX_data_df['SUMM'], errors='coerce').fillna(0)               # Заполням нулями пустые и NaN значения

    mask = BX_data_df['STORE_NAME'].str.contains('OTHER_CURRENCY_STORE', case=False)                # Маска для определения города с другой валютой
    BX_data_df.loc[mask, 'SUMM'] = BX_data_df.loc[mask, 'SUMM'] * CURRENCY                          # Приводим его к нужной валюте
    BX_data_df.loc[mask, 'SUMM'] = BX_data_df.loc[mask, 'SUMM'].apply(lambda x: math.ceil(x))       # Округлям цифры вверхнюю сторону
    BX_data_df['SUMM'] = BX_data_df['SUMM'].astype(int)                                             # Приводим их к типу Int

    BX_data_df.drop('STORE_NAME', axis=1, inplace=True)                                             # Удаляем столбец STORE_NAME
    BX_data_summ = round(BX_data_df['SUMM'].sum())                                                  # Получаем сумму столбца SUMM

    return BX_data_df, BX_data_summ

def read_minimal_DB_data_for_comparison(company):
    """
    Функция получает на вход название компании и использует реквизиты для чтения дампа с БД в датафрейм DB_data_df,
    который используется для сравнения с датафреймом BX_data_df. Возвращает DB_data_df и сумму столбца "SUMM"
    """

    DB_data_df = pd.read_csv(f'data/{company}/company_pulse.csv', usecols=['DEALID', 'SUMM'])       # Чтение файла в датафрейм DB_data_df

    DB_data_df['SUMM'] = pd.to_numeric(DB_data_df['SUMM'], errors='coerce').fillna(0)               # Заполням нулями пустые и NaN значения

    DB_data_df['SUMM'] = DB_data_df['SUMM'].astype(int)                                             # Приводим их к типу Int

    DB_data_summ = DB_data_df['SUMM'].sum()                                                         # Получаем сумму столбца SUMM

    return DB_data_df, DB_data_summ

def get_dealid_list_from_data_comparison(BX_data_df, DB_data_df, company):
    """
    Функция получает на вход два датафрейма: "BX_data_df" и "DB_data_df". Объединяет их в датафрейм "merged_df",
    по столбцу "DEALID", и выносит строки в которых столбцы "SUMM_bitrix" и "SUMM_pbi" различаются в датафрейм "diff_df".
    И далее выносит все значения столбца в список "dealid_list".
    """

    merged_df = pd.merge(BX_data_df, DB_data_df, on='DEALID', how='outer', suffixes=('_bitrix', '_pbi'))
    merged_df.to_csv(f'data/{company}/merged_df.csv')

    diff_df = merged_df.loc[merged_df['SUMM_bitrix'] != merged_df['SUMM_pbi'], ['DEALID', 'SUMM_bitrix', 'SUMM_pbi']]
    diff_df = diff_df.loc[diff_df['SUMM_bitrix'] != 0]
    diff_df.to_csv(f'data/{company}/diff.csv')

    dealid_list = diff_df['DEALID'].tolist()
    return dealid_list

def get_deals_for_update(bitrix_all_info, dealid_list, company):
    """
    Функция получает на вход датафрейм "bitrix_all_info", список "dealid_list" и строку "company".
    Убирает все строки датафрейма "bitrix_all_info" в которых в столбце "DEALID"
    нет значений из списка "dealid_list". Возвращает изменный датафрейм "bitrix_all_info" и "amount_of_updating_deals"
    """

    bitrix_all_info['SUMM'] = bitrix_all_info['SUMM'].fillna(0).replace([np.inf, -np.inf], np.nan).astype(int)  # Заполням нулями пустые и NaN значения и приводим к типу Int

    mask = bitrix_all_info['DEALID'].isin(dealid_list)                                                          # Маска для определения всех сделок датафрейма bitrix_all_info,
    bitrix_all_info = bitrix_all_info[mask]                                                                     # которые есть в списке dealid_list

    bitrix_all_info.loc['SUMM'] = bitrix_all_info['SUMM'].astype(float).round(2)                                # Приводим значения к типу float

    bitrix_all_info = bitrix_all_info.loc[bitrix_all_info['SUMM'] != 0.0]                                       # Оставляем только строки в которых значения в столбце SUMM не равны 0
    bitrix_all_info.to_csv(f'data/{company}/diff_df.csv')

    #bitrix_all_info = bitrix_all_info.drop(bitrix_all_info.index[:420])
    amount_of_updating_deals = bitrix_all_info.shape[0]                                                         # Получаем количество сделок

    return bitrix_all_info, amount_of_updating_deals

def show_info(company, bitrix_all_info, DB_data_summ, BX_data_summ, amount_of_updating_deals):
    """
    Функция выводит в консоль информацию о сравниваемых датафреймах и запрашивает разрешение
    на запуск обновления сделок.
    """

    updating_deals_summ = bitrix_all_info['SUMM'].sum()                                             # Получаем сумму обновляемых сделок
    print('Сумма сделок в Bitrix24: ',BX_data_summ )
    print('Сумма сделок в PowerBI: ',DB_data_summ )
    print('Количество обновляемых сделок: ',amount_of_updating_deals )
    print('Обновляемая разница: ',updating_deals_summ )
    print('Фактическая разница: ',BX_data_summ - DB_data_summ )
    print('Запустить обновление? [y/N] ')                                                           # Запрашиваем разрешение на обновление сделок
    ansewer = input()
    return ansewer

def deals_update(bitrix_all_info, company, amount_of_updating_deals, ansewer):
    """
    Функция проходит по всем строкам датафрейма "bitrix_all_info", и отправляет
    информацию в БД
    """

    bar = IncrementalBar('', max = amount_of_updating_deals)                                            # Инициализируем прогрес бар и спинер
    spinner = Spinner('')


    if ansewer == 'y':                                                                                  # Запуск обновления если ответ пользователя "y"
        logger.info('Stared deals update')
        i = 0
        for index, row in bitrix_all_info.iterrows():                                                   # Проходимся по всем строкам датафрейма bitrix_all_info
            os.system('cls||clear')                                                                     # Очищаем консоль
            message = f" Сделка в работе: \nID: {row['DEALID']}; Сумма: {row['SUMM']}"

            url = f"https://{HOST_DOMAIN}/{ALLOWED_COMPANY_NAMES[0]}?DEALID={row['DEALID']}&CREATION_DATE={row['CREATION_DATE']}&NPS={row['NPS_VALUE']}&store={row['STORE_NAME']}&REVIEW={row['REVIEW']}&DEALNAME=Сделка №{row['DEALID']}&RESPONSIBLE={row['RESPONSIBLE']}&SUMM={row['SUMM']}0&PROJECT={company}&category={row['category']}&DEALSTATUS={row['DEALSTATUS']}"  # Ссылка для обновления
            strped_url = url.replace(str(np.nan), "")                                                   # Убираем возможные NaN
            logger.info(f'Got url: {strped_url}')

            logger.info('Trying to make request')
            make_request(strped_url)                                                                    # Вызываем функцию для GET запросов

            spinner.next()                                                                              # Выводим в консоль инфу и прогрессбар
            print(message,end='\n')
            bar.next()

            i += 1
            logger.info(f'Iterator: {i}')
            time.sleep(1)
    else:                                                                                               # Eсли ответ пользователя отличный от  "y" то происходит выход из программы

        print('Выход из програмы')
        logger.info(f'User ansewer: "{ansewer}". Update doesnt start')
        exit()

def main():                                                                                             # Основная фунция программы для запуска отстальных функций
    pd.options.mode.chained_assignment = None                                                           # Отключаем сообщение от Pandas
    logger.info('Started')

    company_arg = get_company_name(sys.argv)                                                            # Получаем компанию из аргументов
    logger.info(f'Got company arg{company_arg}')

    bitrix_all_info, company = read_bxdata_from_csv_by_company(company_arg)                             # Читаем из файла данные в датафрейм "bitrix_all_info"
    logger.info('Readed "bitrix_all_info" dataframe')

    BX_data_df, BX_data_summ = read_minimal_BX_data_for_comparison(company)                             # Читаем из файла данные в датафрейм "BX_data_df"
    logger.info('Readed "BX_data_df" dataframe')

    DB_data_df, DB_data_summ = read_minimal_DB_data_for_comparison(company)                             # Читаем из файла данные в датафрейм "DB_data_df"
    logger.info('Readed "DB_data_df" dataframe')

    dealid_list = get_dealid_list_from_data_comparison(BX_data_df, DB_data_df, company)                 # Сравниваем BX_data_df и  DB_data_df и получам список обновляемых сделок

    bitrix_all_info, amount_of_updating_deals = get_deals_for_update(bitrix_all_info, dealid_list, company) # Получам обновленный датафрейм "bitrix_all_info"
    logger.info('Got "dealid_list" list')

    ansewer = show_info(company, bitrix_all_info, DB_data_summ, BX_data_summ, amount_of_updating_deals) # Выводим информацию на экран и делаем запрос на обновлене сделок
    logger.info(f'Got ansewer from user: {ansewer}')

    deals_update(bitrix_all_info, company, amount_of_updating_deals, ansewer)                           # Обновляем сделки при положительном ответе

if __name__ == '__main__':
    logger.configure(handlers=[{"sink": sys.stderr, "level": "ERROR"}])
    logger.add("logs/BXBDComprassion.log", format="{time} {level} {message}", level="DEBUG")

    try:
        main()                                                                                          # Запускаем основную функцию

    except SystemExit:                                                                                  # Обрабатываем исключение при выходе из программы
        error_str = traceback.format_exc()
        logger.info('Quiting')

    except:
        error_str = traceback.format_exc()
        logger.error(f'Error occured: {error_str}')
