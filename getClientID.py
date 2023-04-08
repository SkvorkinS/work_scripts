import os
from requests import get
from credentials import ITIGRIS_API_KEY_1, ALLOWED_COMPANY_NAMES

def clear_number(s):
    s = s.replace(" ", "")  # удаляем пробелы
    s = s.replace("(", "")  # удаляем левую скобку
    s = s.replace(")", "")  # удаляем правую скобку
    s = s.replace("+", "")  # удаляем знак плюса
    return s


def main():
    os.system('cls||clear')
    print('Введите номер клиента: ')
    tel = input()
    ctel = clear_number(tel)
    url = f'https://optima.itigris.ru/{ALLOWED_COMPANY_NAMES[0]}/remoteClientCard/getClient?key={ITIGRIS_API_KEY_1}&tel={ctel}'
    response = get(url)
    print(response.text)
    input()

if __name__ == '__main__':
    while True:
        main()
