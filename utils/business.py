from collections import namedtuple

from parser import get_coins_in_json

Coin = namedtuple('Coin', 'id name votes')


def json_to_namedtuple(coins: list[dict]) -> Coin:
    """Returns Coin namedtuple from json representation"""
    for coin in coins:
        coin = Coin(id=coin['id'], name=coin['name'], votes=coin['votes'])
        yield coin


def get_coins() -> list[Coin]:
    top = get_coins_in_json()
    while not top:
        top = get_coins_in_json()

    return list(json_to_namedtuple(top))
