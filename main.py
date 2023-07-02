from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                           Message, LabeledPrice, PreCheckoutQuery, successful_payment)
from config import bot_token, payments_token, admin1
import texts
from example_requests import check_mail
import logging
import json
import sqlite3 as sql

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

admins = [admin1]

# Создаем объекты бота и диспетчера
bot: Bot = Bot(bot_token)
dp: Dispatcher = Dispatcher(storage=storage)


class FSMFillForm(StatesGroup):
    fill_input_email = State()                 # Переход в проверку почты
    fill_payments_30rub = State()
    fill_payments_100rub = State()
    fill_payments_200rub = State()
    fill_payments_500rub = State()
    check_payments_30rub = State()
    check_payments_100rub = State()
    check_payments_200rub = State()
    check_payments_500rub = State()


# Создаем объекты кнопок
button_1: KeyboardButton = KeyboardButton(text='Проверить email')
button_2: KeyboardButton = KeyboardButton(text='Баланс')
button_3: KeyboardButton = KeyboardButton(text='О боте')
button_4: KeyboardButton = KeyboardButton(text='Пополнить баланс')
button_5: KeyboardButton = KeyboardButton(text='Купить 1 поисковой запрос')
button_6: KeyboardButton = KeyboardButton(text='Купить 5 поисковых запросов')
button_7: KeyboardButton = KeyboardButton(text='Купить 30 поисковых запросов')
button_8: KeyboardButton = KeyboardButton(text='Купить 100 поисковых запросов')
button_9: KeyboardButton = KeyboardButton(text='В меню')

# Создаем объект клавиатуры, добавляя в него кнопки
keyboard1: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                    keyboard=[[button_1], [button_2, button_3]],
                                    resize_keyboard=True)

keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                    keyboard=[[button_5], [button_6], [button_7], [button_8], [button_9]],
                                    resize_keyboard=True)

keyboard3: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                    keyboard=[[button_9]],
                                    resize_keyboard=True)


# Этот хэндлер будет срабатывать на команду /start
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    cursor.execute(f"SELECT id FROM users_list WHERE id = {message.from_user.id}")
    data = cursor.fetchone()
    if data is None:
        s1 = f"INSERT INTO users_list (id, username, counts, lang) VALUES(?, ?, ?, ?);"
        cursor.execute(s1, [message.from_user.id, message.from_user.username, 0 ,'rus'])
        connect.commit()
        logging.info(f'Add values in users_list by {message.from_user.username}')
    logging.info(f'Start bot at user {message.from_user.username}')
    await message.answer(text=texts.text1_rus, reply_markup=keyboard1)
    await bot.send_message(chat_id=admins[0], text=f'Пользователь {message.from_user.username} запустил бота')

# Этот хэндлер будет срабатывать на кнопку О боте
@dp.message(Text(text='О боте'))
async def process_about_command(message: Message, state: FSMContext):
    await message.answer(text=texts.text12_rus, reply_markup=keyboard1)

# Этот хэндлер будет срабатывать на кнопку В меню
@dp.message(Text(text='В меню'))
async def process_menu_command(message: Message, state: FSMContext):
    await state.set_state(default_state)
    await message.answer(text='Вы вышли в меню', reply_markup=keyboard1)

# Этот хэндлер будет срабатывать на кнопку Баланс
@dp.message(Text(text='Баланс'), StateFilter(default_state))
async def process_balance_command(message: Message):
    s1 = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}")
    await message.answer(text=f"{texts.text9_rus}{s1.fetchone()[0]}", reply_markup=ReplyKeyboardRemove())
    await message.answer(text=texts.text11_rus, reply_markup=keyboard2)
    logging.info(f"User {message.from_user.username} requested balance")

# Этот хэндлер будет срабатывать на кнопку Проверить email
@dp.message(Text(text='Проверить email'), StateFilter(default_state))
async def process_check_command(message: Message, state: FSMContext):
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
    if balance > 0:
        await message.answer(text=texts.text3_rus, reply_markup=keyboard3)
        await state.set_state(FSMFillForm.fill_input_email)
    else:
        await message.answer(text=texts.text10_rus)

# Этот хэндлер будет ожидать от пользователя ввода почты и выводить результат поиска
@dp.message(StateFilter(FSMFillForm.fill_input_email))
async def process_input_command(message: Message, state: FSMContext):
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
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
        balance -= 1
        cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
        connect.commit()
    else:
        await message.answer(text=f'Почта {message.text} в нашей базе данных отсутствует')
        await message.answer(text=texts.text14_rus)
    await state.set_state(default_state)
    logging.info(f'Check {message.text} at user {message.from_user.username}')


# Этот хэндлер будет срабатывать на кнопку Купить 1 поисковой запрос
@dp.message(Text(text='Купить 1 поисковой запрос'), StateFilter(default_state))
async def process_buy1_command(message: Message, state: FSMContext):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Купить доступ к базе",
        description="1 поисковой запрос к базе данных",
        provider_token=payments_token,
        currency="rub",
        photo_url="https://github.com/antonhramcov/images_for_bots/blob/master/1.jpg?raw=true",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='1 запрос', amount=60*100)],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await message.answer(text=texts.text13_rus, reply_markup=keyboard3)
    await state.set_state(FSMFillForm.fill_payments_30rub)

# Этот хэндлер будет срабатывать на кнопку Купить 5 поисковых запросов
@dp.message(Text(text='Купить 5 поисковых запросов'), StateFilter(default_state))
async def process_buy5_command(message: Message, state: FSMContext):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Купить доступ к базе",
        description="5 поисковых запросов к базе данных",
        provider_token=payments_token,
        currency="rub",
        photo_url="https://github.com/antonhramcov/images_for_bots/blob/master/5.jpg?raw=true",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='1 запрос', amount=100*100)],
        max_tip_amount=50000,
        suggested_tip_amounts=[2500],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await message.answer(text=texts.text13_rus, reply_markup=keyboard3)
    await state.set_state(FSMFillForm.fill_payments_100rub)

# Этот хэндлер будет срабатывать на кнопку Купить 30 поисковых запросов
@dp.message(Text(text='Купить 30 поисковых запросов'), StateFilter(default_state))
async def process_buy30_command(message: Message, state: FSMContext):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Купить доступ к базе",
        description="30 поисковых запросов к базе данных",
        provider_token=payments_token,
        currency="rub",
        photo_url="https://github.com/antonhramcov/images_for_bots/blob/master/30.jpg?raw=true",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='1 запрос', amount=200*100)],
        max_tip_amount=50000,
        suggested_tip_amounts=[5000],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await message.answer(text=texts.text13_rus, reply_markup=keyboard3)
    await state.set_state(FSMFillForm.fill_payments_200rub)

# Этот хэндлер будет срабатывать на команду Купить 100 поисковых запросов
@dp.message(Text(text='Купить 100 поисковых запросов'), StateFilter(default_state))
async def process_buy100_command(message: Message, state: FSMContext):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Купить доступ к базе",
        description="100 поисковых запросов к базе данных",
        provider_token=payments_token,
        currency="rub",
        photo_url="https://github.com/antonhramcov/images_for_bots/blob/master/100.jpg?raw=true",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label='100 запросов', amount=500*100)],
        max_tip_amount=50000,
        suggested_tip_amounts=[5000],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload")
    await message.answer(text=texts.text13_rus, reply_markup=keyboard3)
    await state.set_state(FSMFillForm.fill_payments_500rub)

# Проверка возможности оплаты
@dp.pre_checkout_query(StateFilter(FSMFillForm.fill_payments_30rub))
async def pre_checkout1_query(pre_checkout_query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await state.set_state(FSMFillForm.check_payments_30rub)


@dp.pre_checkout_query(StateFilter(FSMFillForm.fill_payments_100rub))
async def pre_checkout5_query(pre_checkout_query: PreCheckoutQuery, state: FSMContext, message: Message):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await state.set_state(FSMFillForm.check_payments_100rub)

@dp.pre_checkout_query(StateFilter(FSMFillForm.fill_payments_200rub))
async def pre_checkout30_query(pre_checkout_query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await state.set_state(FSMFillForm.check_payments_200rub)

@dp.pre_checkout_query(FSMFillForm.fill_payments_500rub)
async def pre_checkout100_query(pre_checkout_query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await state.set_state(FSMFillForm.check_payments_500rub)

# Проведение оплаты
@dp.message(StateFilter(FSMFillForm.check_payments_30rub))
async def successful1_payment(message: Message, state: FSMContext):
    print('ШАГ 3')
    msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}'
    await message.answer(msg)
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
    balance += 1
    cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
    connect.commit()
    logging.info(f'Get payment at user {message.from_user.username} - {message.successful_payment.total_amount // 100}')
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f"Пользователь {message.from_user.username} оплатил {message.successful_payment.total_amount // 100} руб.")
    await state.set_state(default_state)

@dp.message(StateFilter(FSMFillForm.check_payments_100rub))
async def successful5_payment(message: Message, state: FSMContext):
    print('ШАГ 3')
    msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}'
    await message.answer(msg)
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
    balance += 5
    cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
    connect.commit()
    logging.info(f'Get payment at user {message.from_user.username} - {message.successful_payment.total_amount // 100}')
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f"Пользователь {message.from_user.username} оплатил {message.successful_payment.total_amount // 100} руб.")
    await state.set_state(default_state)

@dp.message(StateFilter(FSMFillForm.check_payments_200rub))
async def successful30_payment(message: Message, state: FSMContext):
    msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}'
    await message.answer(msg)
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
    balance += 30
    cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
    connect.commit()
    logging.info(f'Get payment at user {message.from_user.username} - {message.successful_payment.total_amount // 100}')
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f"Пользователь {message.from_user.username} оплатил {message.successful_payment.total_amount // 100} руб.")
    await state.set_state(default_state)

@dp.message(StateFilter(FSMFillForm.check_payments_500rub))
async def successful100_payment(message: Message, state: FSMContext):
    msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}'
    await message.answer(msg)
    balance = cursor.execute(f"SELECT counts FROM users_list WHERE id={message.from_user.id}").fetchone()[0]
    balance += 100
    cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={message.from_user.id}")
    connect.commit()
    logging.info(f'Get payment at user {message.from_user.username} - {message.successful_payment.total_amount // 100}')
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f"Пользователь {message.from_user.username} оплатил {message.successful_payment.total_amount // 100} руб.")
    await state.set_state(default_state)

# Запускаем пуллинг
if __name__ == '__main__':
    connect = sql.connect('users.db')
    cursor = connect.cursor()
    logging.basicConfig(level=logging.INFO, filename="bot.log", filemode='w',
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info(f'Bot started')
    dp.run_polling(bot, skip_updates=False)