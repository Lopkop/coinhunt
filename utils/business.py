import logging
from collections import namedtuple

from aiogram.types import InlineKeyboardButton, Message, InlineKeyboardMarkup
from asyncpg.exceptions import UniqueViolationError

from parser import get_coins_in_json
from config.database import insert_into_user_coins, insert_into_users, insert_into_coin, get_from_db, \
    delete_from_user_coins

logger = logging.getLogger(__name__)

Coin = namedtuple('Coin', 'id name votes')


def json_to_namedtuple(coins: list[dict]) -> Coin:
    """Returns Coin namedtuple from json representation"""
    for coin in coins:
        coin = Coin(id=coin['id'], name=coin['name'], votes=coin['votes'])
        yield coin


def get_coins() -> list[Coin]:
    """Returns list of coins (namedtuples)"""
    top = get_coins_in_json()
    while not top:
        top = get_coins_in_json()

    return list(json_to_namedtuple(top))


async def validate_and_make_relationship(user_id: int, coin_id: int, top: int):
    try:
        if not await get_from_db(user_id=user_id):
            await insert_into_users(user_id)
        if not await get_from_db(coin_id=coin_id):
            await insert_into_coin(coin_id)
        await insert_into_user_coins(user_id=user_id, coin_id=coin_id, top=top)
    except UniqueViolationError as error:
        logger.critical(f'Error in validate_and_make_relationship => {error}')
        raise UniqueViolationError
    except Exception as error:
        logger.critical(f'Error in validate_and_make_relationship => {error}')


async def get_my_coins(user_id: int, message: Message, coins_tops_votes: list,
                       delete_my_coins_menu: InlineKeyboardMarkup):
    answer = """"""
    for coin_top_vote in coins_tops_votes:
        coin_id = coin_top_vote.get('coin')
        for coin in get_coins():
            if int(coin.id) == int(coin_id):
                if (votes := coin_top_vote.get('votes')) != -1:
                    answer += f"Монета: {coin.name}\nГолоса: {votes}\n-------------\n"
                else:
                    answer += f"Монета: {coin.name}\nТоп: {coin_top_vote.get('top')}\n-------------\n"
                delete_my_coins_menu.insert(InlineKeyboardButton(
                    text=f'Удалить {coin.name}',
                    callback_data=f'delete:{user_id}:{coin_id}:{coin.name}'))
                break
        if not answer:
            await message.answer("Монета за которой вы следите не находится в каталоге today's best, я ее удалю")
            await delete_from_user_coins(user_id=user_id, coin_id=coin_id)
            return
    return answer
