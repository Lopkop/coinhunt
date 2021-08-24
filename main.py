import logging

from aiogram import Dispatcher, Bot, executor
from aiogram import types

from config.settings import ADMIN_ID, TELEGRAM_API_TOKEN, FORMAT

logging.basicConfig(level=logging.WARNING, filename='logs/warnings.log', format=FORMAT)
logger = logging.getLogger(__name__)

bot = Bot(TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)


async def set_default_commands(dp: Dispatcher):
    """Returns default commands (menu)"""
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "start bot."),
            types.BotCommand("help", "help menu."),
            types.BotCommand("monitor", "monitor coin."),
            types.BotCommand("top", "Shows today's top coins."),
        ]
    )


async def notify_admin_on_startup():
    """Returns a message to admin"""
    await bot.send_message(chat_id=ADMIN_ID, text='Bot started')


async def on_startup(dp: Dispatcher):
    """Sets default commands and notifies admin on startup"""
    await set_default_commands(dp)
    await notify_admin_on_startup()


# TODO: SELENIUM
# TODO: parser finish
# TODO: finish bot
if __name__ == '__main__':
    from handlers.handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
