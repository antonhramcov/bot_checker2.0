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
from test_dates import database
import texts
from example_requests import check_mail

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot: Bot = Bot(bot_token)
dp: Dispatcher = Dispatcher(storage=storage)


class FSMFillForm(StatesGroup):
    fill_input_username = State()                 # Состояние ожидания ввода пользователем никнейма
    fill_input_email = State()                    # Состояние ожидания ввода почты
    fill_input_phone = State()                    # Состояние ожидания ввода телефона


# Создаем асинхронную функцию
async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/check_email',
                   description='Проверить email'),
        BotCommand(command='/check_phone',
                   description='Проверить номер телефона'),
        BotCommand(command='/check_username',
                   description='Проверить никнейм'),
        BotCommand(command='/buy',
                   description='Купить доступ к базе'),
        ]

    await bot.set_my_commands(main_menu_commands)

def check_email_filter(message: Message) -> bool:
    return message.text == '/check_email'

def check_phone_filter(message: Message) -> bool:
    return message.text == '/check_phone'

def check_username_filter(message: Message) -> bool:
    return message.text == '/check_username'

def buy_filter(message: Message) -> bool:
    return message.text == '/buy'

# Этот хэндлер будет срабатывать на команду /start
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=texts.text1)

# Этот хэндлер будет срабатывать на команду /check_username
@dp.message(check_username_filter, StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=texts.text2)
    await state.set_state(FSMFillForm.fill_input_username)

# Этот хэндлер будет ожидать от пользователя ввода никнейма
@dp.message(StateFilter(FSMFillForm.fill_input_username))
async def process_start_command(message: Message, state: FSMContext):
    status = False
    for i in range(len(database)):
        if database[i]['username'] == str(message.text):
            await message.answer(text=str(database[i]))
            status = True
    if status == False:
        await message.answer(text='username {} в своей базе не нашел'.format(str(message.text)))
    await state.set_state(default_state)

# Этот хэндлер будет срабатывать на команду /check_email
@dp.message(check_email_filter, StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=texts.text3)
    await state.set_state(FSMFillForm.fill_input_email)

# Этот хэндлер будет ожидать от пользователя ввода почты
@dp.message(StateFilter(FSMFillForm.fill_input_email))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=check_mail(message.text))
    await state.set_state(default_state)


# Этот хэндлер будет срабатывать на команду /check_phone
@dp.message(check_phone_filter, StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=texts.text4)
    await state.set_state(FSMFillForm.fill_input_phone)


# Этот хэндлер будет ожидать от пользователя ввода почты
@dp.message(StateFilter(FSMFillForm.fill_input_phone))
async def process_start_command(message: Message, state: FSMContext):
    status = False
    for i in range(len(database)):
        if database[i]['phone'] == str(message.text):
            await message.answer(text=str(database[i]))
            status = True
    if status == False:
        await message.answer(text='номер {} в своей базе не нашел'.format(str(message.text)))
    await state.set_state(default_state)


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

# Проверка возможности оплаты
@dp.message(StateFilter(default_state))
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Проведение оплаты
@dp.message(StateFilter(default_state))
async def successful_payment(message: Message):
    msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}'
    await message.answer(msg)

# Запускаем поллинг
if __name__ == '__main__':
    dp.startup.register(set_main_menu)
    dp.run_polling(bot, skip_updates=False)
