import asyncio
import logging
from typing import Union

import asyncpg

from .settings import PG_DATA
from utils.exceptions import UserIsNotExistError

logger = logging.getLogger(__name__)


async def create_db():
    with open('config/createdb.sql', 'r') as f:
        sql = f.read()

    conn: asyncpg.Connection = await asyncpg.connect(
        **PG_DATA,
    )
    values = await conn.fetchrow('SELECT * FROM coin WHERE id=1')
    user_values = await conn.fetchrow('SELECT * FROM users WHERE id=1')
    if not (values and user_values):
        logger.critical('db is not created yet.')
        await conn.execute(sql)
    await conn.close()


async def create_pool():
    try:
        return await asyncpg.create_pool(
            **PG_DATA
        )
    except OSError as error:
        logger.critical(f'Error occurred while connecting to db. (db server is running?) => {error}')


async def get_from_db(*, user_id: Union[int, None] = None, coin_id: Union[int, None] = None) -> bool:
    conn = await create_pool()
    if user_id:
        value = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id=$1",
            int(user_id)
        )

    elif coin_id:
        value = await conn.fetchrow(
            "SELECT * FROM coin WHERE coin_id=$1",
            int(coin_id)
        )
    await conn.close()
    return bool(value)


async def get_coin_and_top_from_user_coins(user_id: int):
    conn: asyncpg.Connection = await create_pool()
    if not await get_from_db(user_id=user_id):
        logger.info(f'Usser is not in the DB - {user_id}')
        raise UserIsNotExistError('User is not in the DB.')
    else:
        coin = await conn.fetch(
            "SELECT coin, top FROM user_coins WHERE user_id=$1",
            int(user_id)
        )
    await conn.close()
    return coin


async def update_user_coins(*, user_id: int, coin_id: int, top: int):
    conn: asyncpg.Connection = await create_pool()
    if not await get_from_db(user_id=user_id):
        logger.info(f'Usser is not in the DB - {user_id}')
        raise UserIsNotExistError('User is not in the DB.')
    else:
        await conn.execute(
            "UPDATE user_coins SET top=$1 WHERE user_id=$2 and coin=$3;",
            int(top),
            int(user_id),
            int(coin_id),
        )
    await conn.close()


async def insert_into_coin(coin_id: int):
    conn = await create_pool()
    await conn.execute(
        "INSERT INTO coin (coin_id) VALUES ($1)",
        coin_id
    )
    await conn.close()


async def insert_into_users(user_id: int):
    conn = await create_pool()
    await conn.execute(
        "INSERT INTO users (user_id) VALUES ($1)",
        user_id
    )
    await conn.close()


async def insert_into_user_coins(user_id: int, coin_id: int, top: int):
    conn = await create_pool()
    await conn.execute(
        "INSERT INTO user_coins (user_id, coin, top) VALUES ($1, $2, $3)",
        user_id,
        coin_id,
        top,
    )
    await conn.close()


async def delete_from_user_coins(user_id: int, coin_id: int):
    conn = await create_pool()
    await conn.execute(
        "DELETE FROM user_coins as uc WHERE uc.user_id=$1 AND uc.coin=$2 RETURNING *;",
        int(user_id),
        int(coin_id),
    )
    logger.info(f'coin: {coin_id} deleted from user: {user_id}')
    await conn.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(create_db())
    except Exception as error:
        logger.error(f'in config/database.py occurred error {error}')
        raise
