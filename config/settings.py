import logging

from aiogram import Dispatcher, Bot
import dotenv

# logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] -- %(levelname)s -- %(message)s')

# extract values from .env file
values = dotenv.dotenv_values('.env')

TELEGRAM_API_TOKEN = values.get('TELEGRAM_API_TOKEN')
ADMIN_ID = values.get('ADMIN_ID')

PG_PASSWORD = values.get('PG_PASS')
PG_USER = values.get('PG_USER')
PG_HOST = values.get('PG_HOST')
PG_PORT = values.get('PG_PORT')

# database connection settings
PG_DATA = dict(database='coinhunt',
               user=PG_USER,
               password=PG_PASSWORD,
               host=PG_HOST,
               port=PG_PORT,
               )

# telegram bot settings
bot = Bot(TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
