import datetime
from collections import namedtuple

from lxml.html import document_fromstring
import requests

CachedResult = namedtuple("CachedResult", ["request_time", "data"])


class Cache:
    def __init__(self, timeout=datetime.timedelta(minutes=5)):
        self.CACHED_RESPONSES = {
            "get_banks_currency": None,
            "get_market_currencies": None,
            "get_monobank_currencies": None,
            "get_nbu_currencies": None
        }
        self._timeout = timeout

    def get(self, key):
        current_time = datetime.datetime.now()
        cached_data = self.CACHED_RESPONSES.get(key)
        if cached_data and current_time - cached_data.request_time < self._timeout:
            return cached_data.data
        return None

    def set(self, key, data):
        current_time = datetime.datetime.now()
        self.CACHED_RESPONSES[key] = CachedResult(current_time, data)


CACHE = Cache()


def get_banks_currency():
    url = 'https://minfin.com.ua/currency/banks/dnepropetrovsk/'
    target_currencies = [
        ("ДОЛЛАР", "USD"),
        ("ЕВРО", "EUR"),
        ("РУБЛЬ", "Деревянный")
    ]
    rates = CACHE.get('get_banks_currency')
    if not rates:
        r = requests.get(url)
        tree = document_fromstring(r.text)

        rates = []
        for (el_name, title) in target_currencies:
            curr = ' / '.join(
                map(
                    str.strip,
                    tree.xpath(f'//td [@data-title="Курс к гривне"][a [text()="{el_name}"]]'
                               '/following-sibling::td [@data-title="Средний курс"]/text()')
                )
            )
            result = f'{title}: {curr}'
            rates.append(result)
            CACHE.set('get_banks_currency', rates)
    return rates


def get_market_currencies():
    currency_map = {
        'Dollar': 'USD',
        'Euro': 'EUR',
        'Rub': 'Деревянный',
    }
    rates = CACHE.get('get_market_currencies')
    if not rates:
        rates = requests.get('http://vkurse.dp.ua/course.json').json()
        rates = [f"{currency_map[name]}: {values['buy']} грн / {values['sale']} грн" for (name, values) in rates.items()]
        CACHE.set('get_market_currencies', rates)
    return rates


def get_monobank_currencies():
    UAH_CODE = 980
    currency_map = {
        840: 'USD',
        978: 'EUR',
        643: 'Деревянный',
    }
    rates = CACHE.get('get_monobank_currencies')
    if not rates:
        rates = requests.get('https://api.monobank.ua/bank/currency').json()
        rates = filter(lambda x: x['currencyCodeA'] in currency_map.keys() and x['currencyCodeB'] == UAH_CODE, rates)
        rates = [f"{currency_map[exchange_rate['currencyCodeA']]}: {exchange_rate['rateBuy']} грн / {exchange_rate['rateSell']} грн"
                for exchange_rate in rates]
        CACHE.set('get_monobank_currencies', rates)

    return rates


def get_nbu_currencies():
    url = 'https://minfin.com.ua/currency/nbu/'
    target_currencies = [
        ("ДОЛЛАР", "USD"),
        ("ЕВРО", "EUR"),
        ("РУБЛЬ", "Деревянный")
    ]
    rates = CACHE.get('get_nbu_currencies')
    if not rates:
        rates = []
        r = requests.get(url)
        tree = document_fromstring(r.text)

        for (el_name, title) in target_currencies:
            curr = ''.join(
                map(str.strip,
                    tree.xpath(f'//a [text()="{el_name}"]/../../td[@data-title="Курс НБУ"]/text()[normalize-space()]'))
            )
            result = f'{title}: {curr}'
            rates.append(result)

        CACHE.set('get_nbu_currencies', rates)
    return rates
