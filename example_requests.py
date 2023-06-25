import requests
from config import api_token

def check_mail(s:str):
    if len(s)>3:
        url = f'https://leakcheck.io/api/public?key={api_token}&check={s}'
        r = requests.get(url)
        return r.text
    else:
        return 'Кол-во символов должно быть не меньше 3'

