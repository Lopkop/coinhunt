from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from .business import get_coins

# coins_menu = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text='Pizza Token'),
#             KeyboardButton(text='Nasty token'),
#         ],
#     ],
#     resize_keyboard=True
# )


coins_menu = InlineKeyboardMarkup()

for coin in get_coins():
    coins_menu.insert(InlineKeyboardButton(text=coin.name, callback_data=f'monitor:{coin.name}'))

cancel_choice = InlineKeyboardMarkup()

cancel_choice.insert(InlineKeyboardButton(text='Отмена', callback_data=f'cancel'))
