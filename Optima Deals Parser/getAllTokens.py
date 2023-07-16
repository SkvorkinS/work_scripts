from bs4 import BeautifulSoup
import re
def get_tokens():
    with open('login.html', 'r') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    script_tag = soup.find("script", {"type": "text/javascript"})
    access_token = script_tag.string.split('"')[1]
    refresh_token = script_tag.string.split('"')[3]
    expires_token = script_tag.string.split('"')[5]

    # сохраняем access token в переменной atoken

    print('a token ', access_token)
    print('r token ', refresh_token)
    print('e token ', expires_token)


