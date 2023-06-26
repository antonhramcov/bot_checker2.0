from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize, BotCommand, LabeledPrice, PreCheckoutQuery )
from aiogram.types.message import ContentType
from config import bot_token, payments_token
import texts
from example_requests import check_mail
import logging
import json

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot: Bot = Bot(bot_token)
dp: Dispatcher = Dispatcher(storage=storage)


class FSMFillForm(StatesGroup):
    #fill_input_username = State()                 # Состояние ожидания ввода пользователем никнейма
    fill_input_email = State()                    # Состояние ожидания ввода почты
    #fill_input_phone = State()                    # Состояние ожидания ввода телефона


# Создаем асинхронную функцию
async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/check_email',
                   description='Проверить email'),
        BotCommand(command='/buy',
                   description='Купить доступ к базе'),
        ]
    await bot.set_my_commands(main_menu_commands)

def check_email_filter(message: Message) -> bool:
    return message.text == '/check_email'

def buy_filter(message: Message) -> bool:
    return message.text == '/buy'

# Этот хэндлер будет срабатывать на команду /start
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=texts.text1)
    logging.info(f'Start bot at user {message.from_user.username}')


# Этот хэндлер будет срабатывать на команду /check_email
@dp.message(check_email_filter, StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=texts.text3)
    await state.set_state(FSMFillForm.fill_input_email)

# Этот хэндлер будет ожидать от пользователя ввода почты и выводить результат поиска
@dp.message(StateFilter(FSMFillForm.fill_input_email))
async def process_start_command(message: Message, state: FSMContext):
    #await message.answer(text=check_mail(message.text))
    s = json.loads(check_mail(message.text))
    out_mess = ''
    if s['success']:
        out_mess += f'Кол-во найденных записей: {s["found"]}\n'
        for i in range(int(s["found"])):
            out_mess += f'{i+1}. Ресурс: {s["sources"][i]["name"]}'
            if s["sources"][i]["date"]:
                out_mess += f', дата: {s["sources"][i]["date"]}'
            out_mess +='.\n'
        await message.answer(text=out_mess)
        print(check_mail(message.text))
    else:
        await message.answer(text=f'Почта {message.text} в нашей базе данных отсутствует')
    await state.set_state(default_state)
    logging.info(f'Check email at user {message.from_user.username}')


# Этот хэндлер будет срабатывать на команду /buy
@dp.message(buy_filter, StateFilter(default_state))
async def process_start_command(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Купить доступ к базе",
        description="10 поисковых запросов к базе данных",
        provider_token=payments_token,
        currency="rub",
        photo_url="https://github.com/antonhramcov/images_for_bots/blob/master/10.jpg?raw=true",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='10 запросов', amount=200*100)],
        max_tip_amount=50000,
        suggested_tip_amounts=[10000],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    logging.info(f'billed for payment at user {message.from_user.username}')

# Проверка возможности оплаты
@dp.message(StateFilter(default_state))
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Проведение оплаты
@dp.message(StateFilter(default_state))
async def successful_payment(message: Message):
    msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}'
    await message.answer(msg)
    logging.info(f'Get payment at user {message.from_user.username} - {message.successful_payment.total_amount // 100}')

# Запускаем поллинг
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename="bot.log",
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info(f'Bot started')
    dp.startup.register(set_main_menu)
    dp.run_polling(bot, skip_updates=False)
