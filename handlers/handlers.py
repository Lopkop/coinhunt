import asyncio
import logging

from aiogram.types import Message, CallbackQuery, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text
from asyncpg import UniqueViolationError

from config.settings import dp, bot
from utils.business import get_coins, validate_and_make_relationship, get_my_coins
from utils.callback_data import monitor_callback, top_callback, delete_my_coin_callback, votes_callback
from utils.keyboards import top_choice
from config.database import get_coin_top_votes_from_user_coins, update_user_coins, insert_into_users, \
    delete_from_user_coins, update_user_coins_votes
from utils.exceptions import UserIsNotExistError

logger = logging.getLogger(__name__)

coin_name = None
flag = False


@dp.message_handler(commands=['start', 'help'])
async def start_and_help(message: Message):
    await message.answer('Привет, это coinhuntbot.')


@dp.message_handler(commands=['check_my_coins'])
async def notify_user_every_minute(message: Message):
    global flag

    if not await get_coin_top_votes_from_user_coins(user_id=message['chat']['id']):
        await message.answer('Вы не выбрали монетy.')
        return

    if flag:
        await message.answer('Я уже слежу за вашими монетами.')
        return

    flag = True
    while True:
        coins_tops_votes = await get_coin_top_votes_from_user_coins(user_id=message['chat']['id'])
        if not coins_tops_votes:
            await message.answer('Вы удалили все монеты.')
            return
        await message.answer('Начал следить за вашими монетами')

        for number, coin in enumerate(get_coins(), 1):
            for coin_top_vote in coins_tops_votes:
                if (votes := coin_top_vote.get('votes')) != -1:
                    if int(coin.votes) == votes:
                        await message.answer(emojize(text(f'Воу! У {coin.name} {votes} Голосов🔥', sep='\n')),
                                             parse_mode=ParseMode.MARKDOWN)
                if (int(coin.id), number) in (coin_top_vote.get('coin'), coin_top_vote.get('top')):
                    await message.answer(emojize(text(f'Воу! {coin.name} Топ {number}🔥', sep='\n')),
                                         parse_mode=ParseMode.MARKDOWN)
                if (int(coin.id), number) in (coin_top_vote.get('coin'), coin_top_vote.get('top') + 1):
                    await message.answer(text(f'Эй! {coin.name} Топ {number}❗️❗', sep='\n'),
                                         parse_mode=ParseMode.MARKDOWN)
                if (int(coin.id), number) in (coin_top_vote.get('coin'), coin_top_vote.get('top') + 2):
                    await message.answer(text(f'Эх, {coin.name} Топ {number}😥️', sep='\n'),
                                         parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(120)


@dp.message_handler(commands=['my_coins'])
async def my_coins(message: Message):
    user_id = message['chat']['id']
    try:
        coins_tops_votes = await get_coin_top_votes_from_user_coins(user_id=user_id)
    except UserIsNotExistError:
        await insert_into_users(user_id=user_id)
        logger.info(f'new user => {user_id}')
        await message.answer('Тут пусто.')
        return

    if not coins_tops_votes:
        await message.answer('Тут пусто.')
        return

    delete_my_coins_menu = InlineKeyboardMarkup()
    answer = await get_my_coins(user_id, message, coins_tops_votes, delete_my_coins_menu)
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
    await call.message.edit_text(f'Подождите пожалуйста, идет загрузка в базу данных.\n10% ██▒▒▒▒▒▒▒▒')
    coin_name = answer.lstrip(f'Вы выбрали ')

    loading_art = iter(
        ('20% ███▒▒▒▒▒▒▒', '30% ████▒▒▒▒▒▒', '50% █████▒▒▒▒▒', '75% ███████▒▒▒', '90% █████████▒', '100% ██████████')
    )

    for coin in get_coins():
        try:
            await call.message.edit_text(f'Подождите пожалуйста, идет загрузка в базу данных.\n{next(loading_art)}')
        except StopIteration:
            ...
        if coin.name[0:10].strip() == coin_name[0:10].strip():
            await update_user_coins(user_id=call.message['chat']['id'], coin_id=coin.id, top=callback_data["number"])
            await call.message.edit_text(f'{answer} и Топ {callback_data["number"]}.')
            break


@dp.callback_query_handler(votes_callback.filter())
async def votes(call: CallbackQuery):
    global coin_name
    answer = call.message.text.rstrip(". Теперь выберите когда мне вас уведомить.")
    coin_name = answer.lstrip(f'Вы выбрали ')
    await call.message.delete_reply_markup()
    await call.message.answer(f'Отправьте мне положительное число: ')


@dp.message_handler()
async def number(message: Message):
    if not coin_name:
        await message.answer(f'Я вас не понимаю.')
        return
    try:
        if (votes := int(message.text)) > 0:
            await message.answer(f'Подождите пожалуйста, идет загрузка в базу данных.')
        else:
            await message.answer(f'Нужно положительное число, а не {votes}.')
            return
    except ValueError:
        await message.answer(f'Я вас не понимаю.')
        return

    flag = False
    for coin in get_coins():
        if coin.name[0:10].strip() == coin_name[0:10].strip():
            flag = True
            await update_user_coins_votes(user_id=message['chat']['id'], coin_id=coin.id, votes=votes)
            await message.answer(f'Вы выбрали {coin_name} и {votes} Голосов.')
            break
    if not flag:
        logger.critical(f'190 in handlers.handlers - {coin_name[0:10].strip()}')
        await message.answer('Техническая ошибка')
