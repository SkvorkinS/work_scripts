import os
import uuid
import json
import pytz
import requests
from loguru import logger
from bs4 import BeautifulSoup
from datetime import datetime


class GetOptimaInfo:
    data_directory = "Data"
    log_directory = "Logs"

    date_now = datetime.now()
    date_now = date_now.replace(tzinfo=pytz.UTC)

    os.makedirs(log_directory, exist_ok=True)
    os.makedirs(data_directory, exist_ok=True)
    log_file = os.path.join(log_directory, f"{__name__}_{date_now}.log")

    # Проверка доступности и правильности пути к файлу
    if not os.access(os.path.dirname(log_file), os.W_OK):
        raise PermissionError("Not enougt righst to write logs!!!")

    # Добавление обработчика для ротации файлов
    logger.add(log_file, rotation="10 MB", compression="zip")
    clients_payload = {}
    orders_payload = {}

    optima_login_url = 'https://optima-yc-prod-1.itigris.ru'
    optima_request_url = 'https://optima-2-backend-yc-prod-1.itigris.ru/api/v2/'
    optima_login = ''
    optima_company = ''
    optima_password = ''
    userId = ''
    auth_info = {}
    deals_list_json = ''

    def __init__(self, company, login, password, user_ID):
        self.optima_company = company
        self.optima_login = login
        self.optima_password = password
        self.userId = user_ID

    def _is_token_alive(self):
        auth_info = {}
        try:
            with open(f"{self.data_directory}/cookie.json", "r") as file:
                auth_info = json.load(file)
            date_now = datetime.now()
            exp_date = datetime.strptime(auth_info['tokens']['expires_token'], '%Y-%m-%dT%H:%M:%S.%fZ')
            exp_date = exp_date.replace(tzinfo=pytz.UTC)
            date_now = date_now.replace(tzinfo=pytz.UTC)
            file.close()
            if exp_date > date_now:
                logger.info(f'Token alive. Expiration datetime: {exp_date}')
                auth_info['is_alive'] = True
                return auth_info
            else:
                logger.info(f'Token is dead. Expiration datetime: {exp_date}')
                auth_info['is_alive'] = False
                return auth_info
        except:
            logger.info(f'Token is broken, or doesnt exist')
            auth_info['is_alive'] = False
            return auth_info

    def get_tokens(self, data):
        logger.info(f'Reading tokens from local file')
        tokens = {}
        soup = BeautifulSoup(data, 'html.parser')
        script_tag = soup.find("script", {"type": "text/javascript"})
        tokens['access_token'] = script_tag.string.split('"')[1]
        tokens['refresh_token'] = script_tag.string.split('"')[3]
        tokens['expires_token'] = script_tag.string.split('"')[5]

        return tokens

    def _auth(self):
        logger.info(f'Starting authorization')
        self.auth_info = self._is_token_alive()
        if self.auth_info['is_alive']:
            return
        logger.info(f'Requesting new tokens.')
        session = requests.Session()
        getLoginPage = session.get(self.optima_login_url + "/" + self.optima_company)
        soup = BeautifulSoup(getLoginPage.text, 'html.parser')
        logger.info(f"{soup}")
        uuid_value = soup.find(id='uuid')['value']
        pageUUID = soup.find(id='pageUUID')['value']
        loginData = {
            'loginAction': 'true',
            'login': self.optima_login,
            'password': self.optima_password,
            'key': '',
            'userId': '',
            'pageUUID': pageUUID,
            'uuidValue': uuid_value,
            'companyUUID': self.optima_company,
        }
        login = session.post(
            self.optima_login_url + "/" + self.optima_company + "/login/login",
            data=loginData,
            headers={
                "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            })
        session_cookies = session.cookies
        cookie_jar = session_cookies
        cookie = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookie_jar])

        userStart = session.get(
            self.optima_login_url + "/" + self.optima_company + "/login/userStart",
            params={
                'loginAction': 'true',
                'pageUUID': pageUUID,
                'userId': '',
                'uuidValue': str(uuid.uuid4()),
                'companyUUID': self.optima_company,

            },
            headers={
                'Cookie': cookie,
            }, )

        tokens = self.get_tokens(userStart.text)
        access_token = 'Bearer ' + tokens['access_token']
        self.auth_info = {'pageUUID': pageUUID, 'cookie': cookie, 'a_token': access_token, 'tokens': tokens}
        with open(f"{self.data_directory}/cookie.json", "w") as file:
            # Запись словаря в файл
            json.dump(self.auth_info, file)
        logger.info(f'Requesting complete')

    def _get_deals_list(self):
        self._auth()
        logger.info(f'Making Request')
        payload = {
            'createdOnFrom': '2023-07-16',
            'createdOnTo': '2023-07-16',
            'page': '0',
            'size': '100',
        }
        headers = {
            "authorization": self.auth_info['a_token'],
        }
        url = f'{self.optima_request_url}orders'
        logger.info(f"URL is: \n {url}")
        response = requests.get(url, headers=headers, data=payload)
        if response.status_code == 200:
            logger.info(f'Success!')
            data = response.json()
            with open(f"{self.data_directory}/deals.json", "w") as file:
                json.dump(data, file)
            # Process the response data as needed
            self.deals_list_json = data
            logger.info(f"Info writed in file: {self.data_directory}/deals.json")
        else:
            logger.error(f"Request failed with status code: {str(response.status_code)}")
        return



    ### USABLE FUNCTIONS

    def make_request(self):
        self._get_deals_list()
