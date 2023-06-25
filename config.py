from environs import Env

env = Env()
env.read_env()

bot_token = env('BOT_TOKEN')
payments_token = env('PAYMENTS_TOKEN')
db_name = env('DBNAME')
user = env('USER')
password = env('PASSWORD')
host = env('HOST')
port = env('PORT')
