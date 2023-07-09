# Этот хендлер будет ожидать ввод количества покупаемых запросов:
@dp.message(StateFilter(FSMFillForm.fill_input_sum))
async def process_fill_input_sum(message: Message, state: FSMContext):
    count = int(message.text)
    price = 0
    if count>0 and count<=100:
        if count == 1:
            price = 60
        elif count > 1 and count <= 5:
            price = 40
        elif count > 5 and count <= 10:
            price = 31
        elif count > 10 and count <= 30:
            price = 22
        elif count > 30 and count <= 100:
            price = 10
        await bot.send_invoice(
            chat_id=message.chat.id,
            title=f"Количество запросов: {count}",
            description=f"Цена за 1 запрос: {price}",
            provider_token=payments_token,
            currency="rub",
            photo_url="",
            photo_width=416,
            photo_height=234,
            photo_size=416,
            is_flexible=False,
            prices=[LabeledPrice(label='Доступ к базе данных', amount=price*count*100)],
            max_tip_amount=50000,
            suggested_tip_amounts=[5000],
            start_parameter="one-month-subscription",
            payload="test-invoice-payload")
        await state.set_state(FSMFillForm.fill_payments)
    else:
        await message.reply(text=texts.text5_rus)

@dp.pre_checkout_query(FSMFillForm.fill_payments)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await state.set_state(FSMFillForm.check_payments)

@dp.message(StateFilter(FSMFillForm.check_payments))
async def successful100_payment(message: Message, state: FSMContext):
    await message.answer(f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}')
    sum = message.successful_payment.total_amount // 100
    if sum == 60:
        count = 1
    elif sum%40==0 and sum>=80 and sum<=200:
        count = sum/40
    elif sum%31==0 and sum>=186 and sum<=310:
        count = sum/31
    elif sum%22==0 and sum>=242 and sum<=660:
        count = sum/22
    elif sum%10==0 and sum>310 and sum<=1000:
        count = sum/10
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