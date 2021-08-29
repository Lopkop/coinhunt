import asyncio
import logging

from aiogram.types import Message, CallbackQuery, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text
from asyncpg import UniqueViolationError

from config.settings import dp
from utils.business import get_coins, validate_and_make_relationship
from utils.callback_data import monitor_callback, top_callback, delete_my_coin_callback
from utils.keyboards import top_choice
from config.database import get_coin_and_top_from_user_coins, update_user_coins, insert_into_users, \
    delete_from_user_coins
from utils.exceptions import UserIsNotExistError

logger = logging.getLogger(__name__)

flag = False


@dp.message_handler(commands=['start', 'help'])
async def start_and_help(message: Message):
    await message.answer('Привет, это coinhuntbot.')


@dp.message_handler(commands=['check_my_coins'])
async def notify_user_every_minute(message: Message):
    global flag

    if not await get_coin_and_top_from_user_coins(user_id=message['chat']['id']):
        await message.answer('Вы не выбрали монетy.')
        return

    if flag:
        await message.answer('Я уже слежу за вашими монетами.')
        return

    flag = True
    while True:
        coins_and_tops = await get_coin_and_top_from_user_coins(user_id=message['chat']['id'])
        if not coins_and_tops:
            await message.answer('Вы удалили все монеты.')
            return
        await message.answer('Начал следить за вашими монетами')

        for number, coin in enumerate(get_coins(), 1):
            if (int(coin.id), number) in ((coin_and_top.get('coin'), coin_and_top.get('top')) for coin_and_top in
                                          coins_and_tops):
                await message.answer(emojize(text(f'Воу! {coin.name} Топ {number}🔥', sep='\n')),
                                     parse_mode=ParseMode.MARKDOWN)
            if (int(coin.id), number) in ((coin_and_top.get('coin'), coin_and_top.get('top') + 1) for coin_and_top
                                          in coins_and_tops):
                await message.answer(text(f'Эй! {coin.name} Топ {number}❗️❗', sep='\n'),
                                     parse_mode=ParseMode.MARKDOWN)
            if (int(coin.id), number) in ((coin_and_top.get('coin'), coin_and_top.get('top') + 2) for coin_and_top
                                          in coins_and_tops):
                await message.answer(text(f'Эх, {coin.name} Топ {number}😥️', sep='\n'),
                                     parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(120)


@dp.message_handler(commands=['my_coins'])
async def my_coins(message: Message):
    user_id = message['chat']['id']
    try:
        coins_and_tops = await get_coin_and_top_from_user_coins(user_id=user_id)
    except UserIsNotExistError:
        await insert_into_users(user_id=user_id)
        logger.info(f'new user => {user_id}')
        await message.answer('Тут пусто.')
        return

    if not coins_and_tops:
        await message.answer('Тут пусто.')
        return

    delete_my_coins_menu = InlineKeyboardMarkup()

    answer = """"""
    for coin_and_top in coins_and_tops:
        coin_id = coin_and_top.get('coin')
        for coin in get_coins():
            if int(coin.id) == int(coin_id):
                answer += f"Монета: {coin.name}\nТоп: {coin_and_top.get('top')}\n-------------\n"
                delete_my_coins_menu.insert(InlineKeyboardButton(
                    text=f'Удалить {coin.name}',
                    callback_data=f'delete:{message["chat"]["id"]}:{coin_id}:{coin.name}'))
                break
        if not answer:
            await message.answer("Монета за которой вы следите не находится в каталоге today's best, я ее удалю")
            await delete_from_user_coins(user_id=user_id, coin_id=coin_id)
            return
    await message.answer(f'Вы следите за: \n{answer}', reply_markup=delete_my_coins_menu)


@dp.callback_query_handler(delete_my_coin_callback.filter())
async def delete_my_coins(call: CallbackQuery, callback_data: dict):
    user_id = callback_data.get('user_id')
    coin_id = callback_data.get('coin_id')
    coin_name = callback_data.get('coin_name')
    await delete_from_user_coins(user_id=user_id, coin_id=coin_id)
    await call.message.delete_reply_markup()
    await call.message.answer(f'Я больше не слежу за {coin_name}')


@dp.message_handler(commands=['top'])
async def top_coins(message: Message):
    """Returns a today's best coins on https://coinhunt.cc"""

    coins = get_coins()
    answer = """"""
    for coin in coins:
        answer += f'Монета: {coin.name}\nID: {coin.id}\nГолоса: {coin.votes}\n-------------\n'
    await message.answer(answer)


@dp.message_handler(commands=['monitor'])
async def get_coin_menu(message: Message):
    coins_menu = InlineKeyboardMarkup(row_width=3)
    for coin in get_coins():
        coins_menu.insert(InlineKeyboardButton(text=coin.name, callback_data=f'monitor:{coin.name[0:10]}:{coin.id}'))

    await message.answer('Выберите монету:', reply_markup=coins_menu)


@dp.callback_query_handler(text='cancel:coin')
async def cancel_monitor(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.delete()


@dp.callback_query_handler(monitor_callback.filter())
async def monitor_coin(call: CallbackQuery, callback_data: dict):
    try:
        await validate_and_make_relationship(user_id=int(call.message['chat']['id']),
                                             coin_id=int(callback_data['coin_id']),
                                             top=1)
    except UniqueViolationError:
        await call.message.edit_text('Вы уже выбирали эту монету.')
        return
    await call.message.edit_text(f'Вы выбрали {callback_data["coin_name"]}. Теперь выберите когда мне вас уведомить.',
                                 reply_markup=top_choice)


@dp.callback_query_handler(top_callback.filter())
async def top(call: CallbackQuery, callback_data: dict):
    answer = call.message.text.rstrip(". Теперь выберите когда мне вас уведомить.")
    await call.message.delete_reply_markup()
    await call.message.edit_text(f'{answer} и Топ {callback_data["number"]}.')
    coin_name = answer.lstrip(f'Вы выбрали ')

    for coin in get_coins():
        if coin.name[0:10] == coin_name[0:10]:
            await update_user_coins(user_id=call.message['chat']['id'], coin_id=coin.id, top=callback_data["number"])
            break
