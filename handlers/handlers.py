import logging

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from main import dp
from utils.business import get_coins
from utils.callback_data import monitor_callback
from utils.keyboards import coins_menu, cancel_choice

logger = logging.getLogger(__name__)


@dp.message_handler(commands=['start', 'help'])
async def start_and_help(message: Message):
    await message.answer('Привет, это coinhuntbot.')


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
    await message.answer('Выберите монету.', reply_markup=coins_menu)


for coin in get_coins():
    @dp.callback_query_handler(text_contains=coin.name)
    async def monitor_coin(call: CallbackQuery):
        await call.message.answer(f'Вы выбрали {call.data.replace("monitor:", "")} -- я буду следить за этой монетой!',
                                  reply_markup=cancel_choice)


@dp.callback_query_handler(text='cancel')
async def cancel_monitor(call: CallbackQuery):
    # await call.answer('Я перестал следить за - '
    #                   f'{call.message.text.replace("Вы выбрали ", "")
    #                   .replace(" -- я буду следить за этой монетой!", "")}',
    #                   show_alert=True)
    # todo:  business logic .....................
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.edit_text(
        f'Я больше не слежу за {call.message.text.replace("Вы выбрали ", "").replace(" -- я буду следить за этой монетой!", "")}')


# @dp.callback_query_handler(monitor_callback.filter(coin_name='Pizza'))
# async def monitor_coin(call: CallbackQuery, callback_data: dict):
#     await call.message.answer(f'Вы выбрали {callback_data["coin_name"]}',
#                               reply_markup=cancel_choice)
