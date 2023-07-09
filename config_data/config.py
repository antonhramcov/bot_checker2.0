from environs import Env

env = Env()
env.read_env()

bot_token = env('BOT_TOKEN')
payments_token = env('PAYMENTS_TOKEN')
api_token = env('LEAKCHECK_TOKEN')
admin1 = env('ADMIN1')
admin2 = env('ADMIN2')