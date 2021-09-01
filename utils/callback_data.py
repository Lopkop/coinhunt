from aiogram.utils.callback_data import CallbackData

monitor_callback = CallbackData('monitor', 'coin_name', 'coin_id')
cancel_callback = CallbackData('cancel', 'c')
top_callback = CallbackData('top', 'number')
delete_my_coin_callback = CallbackData('delete', 'user_id', 'coin_id', 'coin_name')
votes_callback = CallbackData('votes', 'coin')
