import re
from leakcheck import LeakCheckAPI
from config_data.config import api_token
from external_service.json_to_string import convert

def check(s:str):
    api = LeakCheckAPI()
    api.set_key(api_token)
    s1 = ''
    if re.search(r'[0-9a-fA-F]{24}', s)!=None:
        s1 = re.search(r'[0-9a-fA-F]{24}', s).group()
        t = 'hash'
    elif len(re.findall(r'[0-9]', s))>=11:
        for i in re.findall(r'[0-9]', s):
            s1 += i
        t = 'phone'
    elif re.search(r'\S+@\S+\.\S+', s)!=None:
        s1 = re.search(r'\S+@\S+\.\S+', s).group()
        t = 'email'
    elif re.search(r'\S+', s)!=None:
        s1 = re.search(r'\S+', s).group()
        t = 'login'
    return api.lookup(s1, t)




