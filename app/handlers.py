#--------------------------------------------------------libraries--------------------------------------------------------#
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram import F, Router, types, Bot
from aiogram.types import Message
from yoomoney import Quickpay, Client
from datetime import datetime, timedelta

from app.vpn_key.vpn_key_handler import *
from app.sql import DataBase
from app.telegram_config import p2p_token, telegram_token

import string
import random
import asyncio

#-----------------------------------------------------------CONST---------------------------------------------------------#
router = Router()
bot = Bot(token=telegram_token)
db = DataBase(r'Database.db')
#-----------------------------------------------------------logic----------------------------------------------------------#
@router.message(F.photo)
async def photot_handler(message: Message):
    photo_data = message.photo[-1]
    await message.answer(f'{photo_data}')

@router.message(CommandStart())
async def cmd_start(message: Message):
    print("bot started")
    try:
        user_ID = message.chat.id
        username = message.chat.username
        print(f'user_id: {user_ID}')
        print(f'username: {username}')
        await db.add_user(user_ID, username)
    except Exception:
        pass
    finally:
        await message.answer('Это бот для покупки подписки для впн🌍', reply_markup=bot_keyboard)
        data = await db.get_info()
        print(f'Пользователи: {data}')

@router.callback_query(F.data == 'buy')
async def health(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите нужный для вас тариф:",
        reply_markup=take_tarif_keyboard)

@router.callback_query(F.data == '1_month')
async def pay_1_mnth(call: types.CallbackQuery):

    letters_and_digits = string.ascii_lowercase + string.digits
    rand_str = ''.join(random.sample(letters_and_digits, 10))

    await bot.answer_callback_query(call.id)
    quickpay_1_mnth= Quickpay(
        receiver=4100118858023438,
        quickpay_form="shop",
        targets="Оплата подписки на месяц",
        paymentType="SB",
        sum=120,
        label=rand_str
    )
    payment_url_one = quickpay_1_mnth.redirected_url
    await db.update_label(rand_str, call.message.chat.id)

    # Меняем сообщение на оплату
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Подписка на VPN.\nСрок: <b>1 месяц</b>\nСтоимость: <b>120 руб</b>',
        parse_mode='HTML',
        reply_markup=payment_keyboard_1(payment_url_one)  # Новая клавиатура для оплаты
    )

@router.callback_query(F.data == '3_month')
async def pay_3_mnth(call: types.CallbackQuery):
    letters_and_digits = string.ascii_lowercase + string.digits
    rand_str = ''.join(random.sample(letters_and_digits, 10))

    await bot.answer_callback_query(call.id)
    quickpay_3_mnth= Quickpay(
        receiver=4100118858023438,
        quickpay_form="shop",
        targets="Оплата подписки на три месяца",
        paymentType="SB",
        sum=300,
        label=rand_str
    )
    payment_url_three = quickpay_3_mnth.redirected_url
    await db.update_label(rand_str, call.message.chat.id)

    # Меняем сообщение на оплату
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Подписка на VPN.\nСрок: <b>3 месяца</b>\nСтоимость: <b>300 руб</b>',
        parse_mode='HTML',
        reply_markup=payment_keyboard_3(payment_url_three)  # Новая клавиатура для оплаты
    )


@router.callback_query(F.data == 'buy_again')
async def buy_again(call: types.CallbackQuery):
    letters_and_digits = string.ascii_lowercase + string.digits
    rand_str = ''.join(random.sample(letters_and_digits, 10))

    await bot.answer_callback_query(call.id)
    quickpay_one_more= Quickpay(
        receiver=4100118858023438,
        quickpay_form="shop",
        targets="Оплата подписки на месяц",
        paymentType="SB",
        sum=120,
        label=rand_str
    )
    payment_url_one_more = quickpay_one_more.redirected_url
    await db.update_label(rand_str, call.message.chat.id)
    # Меняем сообщение на оплату
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Подписка на VPN.\nСрок: <b>1 месяц</b>\nСтоимость: <b>120 руб</b>',
        parse_mode='HTML',
        reply_markup=payment_keyboard_again(payment_url_one_more)  # Новая клавиатура для оплаты
    )


@router.callback_query(F.data == "about")
async def about(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.reply('Я бот для покупки ВПН подписки.\n'
                         'Сервер на котором находится ВПН - Стокгольм\n'
                         'Клиент на котором работает ВПН - outline')

@router.callback_query(F.data == 'check')
async def check(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    print(call.message.chat.id)
    data = await db.get_payment_status(call.message.chat.id)
    client_tg = Client(p2p_token)
    print(f'Состояние: {data}')
    bought = data[0][0]
    label = data[0][1]
    print(f'статус покупки: {bought}\n')
    print(f'индефикатор: {label}\n\n')
    if bought == 0:
        print(f'статус покупки: {bought}')
        print(f'индефикатор: {label}')
        try:
            history = client_tg.operation_history(label=label)
            for operation in history.operations:
                print(f'номер операции: {operation.operation_id}')
                print(f'дата покупки: {operation.datetime}')
                print(f'статус: {operation.status}\n\n')
            operation = history.operations[-1]
            print(f'статус: {operation.status}')
            if operation.status == 'success':
                print(f'Время покупки: {operation.datetime}')
                await db.update_payment_status(call.message.chat.id, True)
                vpn = create_new_key(name=str(call.message.chat.id), data_limit_gb=500)
                vpn_key = vpn.access_url
                print(f'vpn_key: {vpn_key}\n\n')
                print(type(vpn_key))
                await db.add_vpn_key(vpn_key, call.message.chat.id)
                if operation.amount <= 120:
                    await db.get_user_id_data()
                    db.add_sub_1month(call.message.chat.id)
                elif operation.amount <= 300 and operation.amount >= 130:
                    db.add_sub_3month(call.message.chat.id)
                await call.message.answer(f'Успешно!\nВаш ключ для подключения к впн:\n<code>{vpn_key}</code>\nПриятного пользования!\n'
                                            'Выберите нужную для вас платформу:\n',
                                            reply_markup=platform_links_keyboard, 
                                            parse_mode='HTML')
                
                await bot.send_message(chat_id=863618184, text=f'Пользователь {call.message.chat.username} купил подписку')
        except Exception:
            await call.message.answer("Оплата еще не совершена, или она в пути...")
    else:
        check_vpn = await db.check_vpn_key(call.message.chat.id)
        db_vpn_key = check_vpn[0][0]
        print(db_vpn_key)
        if db_vpn_key == None:
            vpn = create_new_key(name=str(call.message.chat.id), data_limit_gb=500)
            vpn_key = vpn.access_url
            print(f'vpn_key: {vpn_key}\n\n')
            print(type(vpn_key))
            await db.add_vpn_key(vpn_key ,call.message.chat.id)
            await call.message.answer(f'Успешно!\nВаш ключ для подключения к впн:\n<code>{vpn_key}</code>\nПриятного пользования!\n'
                                            'Выберите нужную для вас платформу:\n',
                                            reply_markup=platform_links_keyboard, 
                                            parse_mode='HTML')
        else:
            data_vpn = await db.take_vpn_key(call.message.chat.id)
            vpn_key_take = data_vpn[0][0]
            await call.message.answer(f'Ваш ключ:\n<code>{vpn_key_take}</code>\n'
                                        'Выберите нужную для вас платформу:\n',
                                        reply_markup=platform_links_keyboard, 
                                        parse_mode='HTML')

@router.callback_query(F.data == 'check_data')
async def connect_andoid(call: types.CallbackQuery):
    await call.message.answer('У вас осталось: дней')

@router.callback_query(F.data == 'connect_andr')
async def connect_andoid(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.answer("Инстуркция установке впн на андроид:\n"
                              '1. Установка клиента "outline" (Нажать на кнопку: Cкачать 🤖)\n'
                              '2. Копируем ключ выданый ботом и вставляем его в клиент\n'
                              'После того как вы скопируете ключ, программа сама предложить активировать впн'
                              '3. Готово, впн готов к использованию')
    
@router.callback_query(F.data == 'connect_apl')
async def connect_andoid(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.answer("Инстуркция установке впн на айфон:\n"
                              '1. Установка клиента "outline" (Нажать на кнопку: Cкачать 🍎)\n'
                              '2. Копируем ключ выданый ботом и вставляем его в клиент\n'
                              'После того как вы скопируете ключ, программа сама предложить активировать впн'
                              '3. Готово, впн готов к использованию')

@router.callback_query(F.data == 'connect_pc')
async def connect_andoid(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.answer("Инстуркция установке впн на компьютер:\n"
                              '1. Установка клиента "outline" (Нажать на кнопку: Cкачать 💻)\n'
                              '2. Копируем ключ выданый ботом и вставляем его в клиент\n'
                              'После того как вы скопируете ключ, программа сама предложить активировать впн'
                              '3. Готово, впн готов к использованию')
    

@router.callback_query(F.data == 'android')
async def con_andr(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    data_vpn = await db.take_vpn_key(call.message.chat.id)
    vpn_key_take = data_vpn[0][0]
    await bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Ваш ключ:\n<code>{vpn_key_take}</code>\n"
                                     f"Вы выбрали платформу: Android 🤖", 
                                reply_markup=android_links_keyboard,
                                parse_mode='HTML')

@router.callback_query(F.data == 'apple')
async def con_apple(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    data_vpn = await db.take_vpn_key(call.message.chat.id)
    vpn_key_take = data_vpn[0][0]
    await bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Ваш ключ:\n<code>{vpn_key_take}</code>\n"
                                     f"Вы выбрали платформу: Iphone 🍎", 
                                reply_markup=iphone_links_keyboard,
                                parse_mode='HTML')

@router.callback_query(F.data == 'pc')
async def con_pc(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    data_vpn = await db.take_vpn_key(call.message.chat.id)
    vpn_key_take = data_vpn[0][0]
    await bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Ваш ключ:\n<code>{vpn_key_take}</code>\n"
                                     f"Вы выбрали платформу: PC 💻", 
                                reply_markup=pc_links_keyboard,
                                parse_mode='HTML')

@router.callback_query(F.data == 'back_tarif')
async def main_menu(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='Это бот для покупки подписки для впн 🌍',
        reply_markup=bot_keyboard)

@router.callback_query(F.data == 'back_month')
async def tarif(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите нужный для вас тариф:",
        reply_markup=take_tarif_keyboard)

@router.callback_query(F.data == 'back_again')
async def tarif(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите нужный для вас тариф:",
        reply_markup=take_tarif_keyboard)

@router.callback_query(F.data == 'back_3_month')
async def tarif(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите нужный для вас тариф:",
        reply_markup=take_tarif_keyboard)

@router.callback_query(F.data == 'back_platform')
async def bak_to_menu(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    data_vpn = await db.take_vpn_key(call.message.chat.id)
    vpn_key_take = data_vpn[0][0]
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Ваш ключ:\n<code>{vpn_key_take}</code>\n'
                'Выберите нужную для вас платформу:\n',
                reply_markup=platform_links_keyboard, 
                parse_mode='HTML')

@router.callback_query(F.data == 'back_to_menu')
async def bak_to_menu(call: types.CallbackQuery):
    try:
        user_ID = call.message.chat.id
        username = call.message.chat.username
        print(f'user_id: {user_ID}')
        print(f'username: {username}')
        await db.add_user(user_ID, username)
    except Exception:
        pass
    finally:
        await call.message.answer('Это бот для покупки подписки для впн 🌍', reply_markup=bot_keyboard)
        data = await db.get_info()
        print(f'Пользователи: {data}')

#--------------------------------------------------------------Keyboards-------------------------------------------------------------------------#
bot_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
                     [InlineKeyboardButton(text="Купить подписку", callback_data="buy")],
                     [InlineKeyboardButton(text="Продлить подписку", callback_data="buy_again")],
                     [InlineKeyboardButton(text="Сколько осталось", callback_data="check_data")],
                     [InlineKeyboardButton(text="О нас", callback_data="about")],
                    ])

delete_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
                     [InlineKeyboardButton(text="Да", callback_data="yes")],
                     [InlineKeyboardButton(text="Нет", callback_data="no")]])

take_tarif_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='1 месяц', callback_data='1_month')],
        [InlineKeyboardButton(text='3 месяца', callback_data='3_month')],
        [InlineKeyboardButton(text='Назад', callback_data='back_tarif')]])

android_links_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Cкачать 🤖', url='https://play.google.com/store/apps/details?id=org.outline.android.client'), 
                      InlineKeyboardButton(text='Подключить 🤖', callback_data='connect_andr')],
                      [InlineKeyboardButton(text='Назад', callback_data='back_platform')]])

iphone_links_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Скачать 🍎', url='https://apps.apple.com/ru/app/outline-app/id1356177741?l=ru'), 
                      InlineKeyboardButton(text='подключиться 🍎', callback_data='connect_apl')],
                      [InlineKeyboardButton(text='Назад', callback_data='back_platform')]])

pc_links_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Скачать 💻', url='https://github.com/Jigsaw-Code/outline-apps/releases/download/v1.10.1/Outline-Client.exe'), 
                      InlineKeyboardButton(text='подключиться 💻', callback_data='connect_pc')],
                      [InlineKeyboardButton(text='Назад', callback_data='back_platform')]])

platform_links_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='android 🤖', callback_data='android'),
                     InlineKeyboardButton(text='iphone 🍎', callback_data='apple')],
                     [InlineKeyboardButton(text='windows/linux/mac os 💻', callback_data='pc')],
                     [InlineKeyboardButton(text='Вернуться в меню', callback_data='Back_to_menu')]])

def payment_keyboard_1(payment_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Оплатить', url=payment_url)],
        [InlineKeyboardButton(text='Проверить оплату', callback_data='check')],
        [InlineKeyboardButton(text='Назад', callback_data='back_month')]])

def payment_keyboard_again(payment_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Продлить подписку', url=payment_url)],
        [InlineKeyboardButton(text='Проверить оплату', callback_data='check')],
        [InlineKeyboardButton(text='Назад', callback_data='back_again')]])

def payment_keyboard_3(payment_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Оплатить', url=payment_url)],
        [InlineKeyboardButton(text='Проверить оплату', callback_data='check')],
        [InlineKeyboardButton(text='Назад', callback_data='back_3_month')]])
        
    
client_tg = Client(p2p_token)
history = client_tg.operation_history()
operation = history.operations[-1].status
print(operation)
