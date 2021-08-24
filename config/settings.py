import dotenv

values = dotenv.dotenv_values('.env')

TELEGRAM_API_TOKEN = values.get('TELEGRAM_API_TOKEN')
ADMIN_ID = values.get('ADMIN_ID')

FORMAT = '[%(asctime)s] -- %(levelname)s -- %(message)s'
