import logging

from aiogram import Dispatcher, executor
from aiogram import types

from config.settings import ADMIN_ID, bot

from handlers.handlers import dp

logger = logging.getLogger(__name__)


async def set_default_commands(dp: Dispatcher):
    """Returns default commands (menu)"""
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "start bot."),
            types.BotCommand("help", "help menu."),
            types.BotCommand("monitor", "Добавить монету за которой я буду следить."),
            types.BotCommand("my_coins", "Посмотреть на монеты за которыми я слежу."),
            types.BotCommand("check_my_coins", "Я буду следить за вашими монетами раз в минуту."),
            types.BotCommand("top", "Посмотреть today's best coins."),
        ]
    )


async def notify_admin_on_startup():
    """Returns a message to admin"""
    await bot.send_message(chat_id=ADMIN_ID, text='Bot started')


async def on_startup(dp: Dispatcher):
    """Sets default commands and notifies admin on startup"""
    await set_default_commands(dp)
    await notify_admin_on_startup()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
