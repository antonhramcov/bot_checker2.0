from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery,
                           Message, LabeledPrice, PreCheckoutQuery, successful_payment, BotCommand)
from config_data.config import bot_token, payments_token, admin1
import texts, logging
from external_service.private_api import check
from external_service.json_to_string import convert, convert_for_bitch
import sqlite3 as sql

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

admins = [admin1]

# Создаем объекты бота и диспетчера
bot: Bot = Bot(bot_token)
dp: Dispatcher = Dispatcher(storage=storage)


class FSMFillForm(StatesGroup):
    fill_payments = State()
    check_payments = State()
    fill_answer = State()
    fill_input_sum = State()


# Создаем объекты инлайн-кнопок
big_button_1: InlineKeyboardButton = InlineKeyboardButton(
    text='1 запрос',
    callback_data='big_button_1_pressed')
big_button_2: InlineKeyboardButton = InlineKeyboardButton(
    text='5 запросов',
    callback_data='big_button_2_pressed')
big_button_3: InlineKeyboardButton = InlineKeyboardButton(
    text='25 запросов',
    callback_data='big_button_3_pressed')
big_button_4: InlineKeyboardButton = InlineKeyboardButton(
    text='100 запросов',
    callback_data='big_button_4_pressed')
url_button_1: InlineKeyboardButton = InlineKeyboardButton(
                                    text='Разработчик телеграмм ботов',
                                    url=f'tg://user?id={admin1}')

# Создаем объект инлайн-клавиатуры
keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[big_button_1, big_button_2],
                     [big_button_3, big_button_4]])
url_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[url_button_1]])

async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/about',
                   description='Расскажу о себе'),
        BotCommand(command='/wiki',
                   description='Как правильно искать'),
        BotCommand(command='/balance',
                   description='Баланс'),
        BotCommand(command='/buy',
                   description='Купить доступ')
        ]

    await bot.set_my_commands(main_menu_commands)

def query_filter(message: Message) -> bool:
    if message.text[0]!='/': return True

# Этот хэндлер будет срабатывать на команду /start
@dp.message(CommandStart())
async def command_start(message: Message, state: State):
    await state.set_state(default_state)
    cursor.execute(f"SELECT id FROM users_list WHERE id = {message.from_user.id}")
    data = cursor.fetchone()
    if data is None:
        s1 = f"INSERT INTO users_list (id, username, counts, lang) VALUES(?, ?, ?, ?);"
        cursor.execute(s1, [message.from_user.id, message.from_user.username, 0 ,'rus'])
        connect.commit()
        logging.info(f'Add values in users_list by {message.from_user.username}')
    logging.info(f'Start bot at user {message.from_user.username}')
    await message.answer(text=texts.text1_rus)
    await bot.send_message(chat_id=admins[0], text=f'<b>Пользователь @{message.from_user.username} запустил бота</b>', parse_mode='HTML')

@dp.message(Text(text='/about'))
async def command_about(message: Message, state: State):
    await state.set_state(default_state)
    await message.answer(text=texts.text12_rus, reply_markup=url_keyboard)

@dp.message(Text(text='/wiki'))
async def command_wiki(message: Message, state: State):
    await state.set_state(default_state)
    await message.answer(text=texts.text15_rus, parse_mode='HTML')

@dp.message(Text(text='/balance'))
async def command_balance(message: Message, state: State):
    await state.set_state(default_state)
    s1 = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}")
    balance = s1.fetchone()[0]
    if balance == -1:
        await message.answer(text=f"{texts.text9_rus}{balance+1}")
        await message.answer(text=texts.text3_rus)
    elif balance >= 0:
        await message.answer(text=f"{texts.text9_rus}{balance}")
    await message.answer(text=texts.text11_rus)
    logging.info(f"User {message.from_user.username} requested balance")

@dp.message(Text(text='/buy'))
async def command_buy(message: Message, state: FSMContext):
    await message.answer(text=texts.text6_rus,reply_markup=keyboard)

@dp.callback_query(Text(text='big_button_1_pressed'))
async def process_buttons_press(callback: CallbackQuery, state: State):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Количество запросов: {1}",
        description=f"Цена за 1 запрос: {60}",
        provider_token=payments_token,
        currency="rub",
        photo_url="",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='Доступ к базе данных', amount=60 * 100)],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await state.set_state(FSMFillForm.fill_payments)

@dp.callback_query(Text(text='big_button_2_pressed'))
async def process_buttons_press(callback: CallbackQuery, state: State):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Количество запросов: {5}",
        description=f"Цена за 1 запрос: {20}",
        provider_token=payments_token,
        currency="rub",
        photo_url="",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='Доступ к базе данных', amount=100 * 100)],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await state.set_state(FSMFillForm.fill_payments)

@dp.callback_query(Text(text='big_button_3_pressed'))
async def process_buttons_press(callback: CallbackQuery, state: State):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Количество запросов: {25}",
        description=f"Цена за 1 запрос: {8}",
        provider_token=payments_token,
        currency="rub",
        photo_url="",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='Доступ к базе данных', amount=200 * 100)],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await state.set_state(FSMFillForm.fill_payments)

@dp.callback_query(Text(text='big_button_4_pressed'))
async def process_buttons_press(callback: CallbackQuery, state: State):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Количество запросов: {100}",
        description=f"Цена за 1 запрос: {5}",
        provider_token=payments_token,
        currency="rub",
        photo_url="",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='Доступ к базе данных', amount=500 * 100)],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await state.set_state(FSMFillForm.fill_payments)

@dp.pre_checkout_query(FSMFillForm.fill_payments)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await state.set_state(FSMFillForm.check_payments)

@dp.message(StateFilter(FSMFillForm.check_payments))
async def successful_payment(message:Message, state: FSMContext):
    await message.answer(f'Спасибо за оплату!')
    sum = message.successful_payment.total_amount // 100
    count = 0
    if sum == 60: count = 1
    elif sum == 100: count = 5
    elif sum == 200: count = 25
    elif sum == 500: count = 100
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
    if balance == -1:
        count += 1
    balance += count
    cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
    connect.commit()
    logging.info(f'Get payment at user {message.from_user.username} - {message.successful_payment.total_amount // 100}')
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f"<b>Пользователь @{message.from_user.username} оплатил {message.successful_payment.total_amount // 100} руб.</b>", parse_mode='HTML')
    await state.set_state(default_state)

# Этот хэндлер будет срабатывать на любое текстовое сообщение
@dp.message(StateFilter(default_state))
async def process_check_command(message: Message):
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
    if balance > 0:
        out = check(message.text)
        if len(out) > 2:
            out = convert(out)
            for part in out:
                await message.answer(text=part, parse_mode='HTML')
            balance -= 1
            cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
            connect.commit()
        else:
            await message.answer(text='К сожалению, я ничего не нашел')
            await message.answer(text=texts.text14_rus)
        logging.info(f'Check {message.text} at user {message.from_user.username}')
    elif balance == 0:
        out = check(message.text)
        if len(out) > 2:
            out = convert_for_bitch(out)
            for part in out:
                await message.answer(text=part, parse_mode='HTML')
            balance -= 1
            cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
            connect.commit()
        else:
            await message.answer(text='К сожалению, я ничего не нашел')
        logging.info(f'Trial check {message.text} at user {message.from_user.username}')
        await message.answer(text=texts.text2_rus)
    elif balance<0:
        await message.answer(text=texts.text10_rus)

# Запускаем пуллинг
if __name__ == '__main__':
    connect = sql.connect('users.db')
    cursor = connect.cursor()
    logging.basicConfig(level=logging.INFO, filename="bot.log", filemode='a',
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info(f'Bot started')
    dp.startup.register(set_main_menu)
    dp.run_polling(bot, skip_updates=False)