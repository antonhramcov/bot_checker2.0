import requests
from config import api_token

def check_mail(s:str):
    if len(s)>3:
        url = f'https://leakcheck.io/api?key=81b12756d6783316a95018515d56e3b86c1eb4dd&check={s}&type=email'
        r = requests.get(url)
        return r.text
    else:
        return 'Кол-во символов должно быть не меньше 3'

print(check_mail('ahramcov2018@yandex.ru'))
