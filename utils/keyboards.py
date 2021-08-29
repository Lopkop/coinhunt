from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


top_choice = InlineKeyboardMarkup()

tops = ['Топ 1', 'Топ 2', 'Топ 3', 'Топ 4', 'Топ 5', 'Топ 6', 'Топ 7', 'Топ 8', 'Топ 9', 'Топ 10']

for number, top in enumerate(tops, 1):
    top_choice.insert(InlineKeyboardButton(text=top, callback_data=f'top:{number}'))
top_choice.insert(InlineKeyboardButton(text='Отмена', callback_data=f'cancel:coin'))


delete_my_coins = InlineKeyboardMarkup()


