import time
import logging

from bs4 import BeautifulSoup
from selenium import webdriver

logger = logging.getLogger(__name__)


def _get_coin(coin_name, coin_id, coin_votes) -> dict:
    """Returns coin in json format"""
    return {'name': coin_name.text.strip(),
            'id': coin_id['href'].replace('/coin/', '').strip(),
            'votes': coin_votes.text.strip()
            }


def _todays_best(parser: BeautifulSoup) -> dict:
    """Parser that parse today's best catalog on https://coinhunt.cc"""
    coins_table = parser.find('div', class_='Landing_table__2kfJT')
    coins = coins_table.find_all('div', class_='sc-gKAaRy dkOltH') + \
            coins_table.find_all('div', class_='sc-hKFxyN jtSqOG') + \
            coins_table.find_all('div', class_='sc-jSFjdj bcukKH') + \
            coins_table.find_all('div', class_='sc-dlnjwi keogPe')

    if not coins:
        logger.critical(f'coins is the {coins}')

    for coin in coins:
        coin_name = coin.find('div',
                              class_='px-0 align-self-center Landing_ColFontSize__1Ma9T Landing_FullName__3ORsT col') \
                    or coin.find('div',
                                 class_='px-0 align-self-center Landing_ColFontSize__1Ma9T Landing_FullName__3ORsT Landing_fourthPlaceName__3ukzi col') \
                    or coin.find('div',
                                 class_='px-0 align-self-center Landing_ColFontSize__1Ma9T col-2')

        coin_id = coin.find('a', class_='Landing_RowLink__1d-wr', href=True)
        coin_votes = coin.find('div', class_='Landing_VoteText__wuky1')

        yield _get_coin(coin_name, coin_id, coin_votes)


def get_coins_in_json() -> list[dict]:
    """Initializes a parser and returns today's best catalog"""
    options = webdriver.FirefoxOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path='/Users/arsen/Desktop/geckodriver', options=options)

    driver.get('https://coinhunt.cc')
    element = driver.find_element_by_css_selector('p.Landing_ShowAll__1jQ77')
    driver.execute_script('arguments[0].click();', element)
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return list(_todays_best(soup))
