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


class BaseCurrencySource:
    def __init__(self, cache=None):
        self._cache = cache

    @property
    def cache_key(self):
        raise NotImplementedError

    def request_data(self):
        raise NotImplementedError

    @property
    def cache(self):
        if self._cache:
            return self._cache
        self._cache = Cache()
        return self.cache

    def get_rates(self):
        rates = self.cache.get(self.cache_key)
        if not rates:
            rates = self.request_data()
            self.cache.set(self.cache_key, rates)
        return rates

    def __str__(self):
        return f"Курсы {self.cache_key}:\n{self.get_rates()}"


class UkrainianBanksSource(BaseCurrencySource):
    def request_data(self):
        url = 'https://minfin.com.ua/currency/banks/dnepropetrovsk/'
        target_currencies = [
            ("ДОЛЛАР", "USD"),
            ("ЕВРО", "EUR"),
            ("ПОЛЬСКИЙ ЗЛОТЫЙ", "PLN")
        ]
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
        return rates

    @property
    def cache_key(self):
        return "get_banks_currency"

    def __str__(self):
        formatted = "\n".join(self.get_rates())
        return f"Курсы в банках города:\n{formatted}\n"


class MarketSource(BaseCurrencySource):
    @property
    def cache_key(self):
        return "get_market_currencies"

    def request_data(self):
        currency_map = {
            'Dollar': 'USD',
            'Euro': 'EUR',
            'Pln': "PLN",
        }
        rates = requests.get('http://vkurse.dp.ua/course.json').json()
        rates = [f"{currency_map[name]}: {values['buy']} грн / {values['sale']} грн" for (name, values) in
                 rates.items()]
        return rates

    def __str__(self):
        formatted = "\n".join(self.get_rates())
        return f"Курсы у независимых продавцов:\n{formatted}\n"


class MonoBankSource(BaseCurrencySource):

    @property
    def cache_key(self):
        return "get_monobank_currencies"

    def request_data(self):
        UAH_CODE = 980
        currency_map = {
            840: 'USD',
            978: 'EUR',
            985: 'PLN',
        }
        rates = requests.get('https://api.monobank.ua/bank/currency')
        try:
            rates = rates.json()
            rates = filter(lambda x: x['currencyCodeA'] in currency_map.keys() and x['currencyCodeB'] == UAH_CODE,
                           rates)
            rates = [
                f"{currency_map[exchange_rate['currencyCodeA']]}: {exchange_rate['rateBuy']} грн / {exchange_rate['rateSell']} грн"
                for exchange_rate in rates]
            return rates
        except KeyError:
            return ["Слишком много запросов"]

    def __str__(self):
        formatted = "\n".join(self.get_rates())
        return f"Курсы у Моно банк:\n{formatted}\n"


class NBUSource(BaseCurrencySource):

    @property
    def cache_key(self):
        return "get_nbu_currencies"

    def request_data(self):
        url = 'https://minfin.com.ua/currency/nbu/'
        target_currencies = [
            ("Доллар США", "USD"),
            ("Евро", "EUR"),
            ("Польский злотый", "PLN")
    ]
        rates = []
        r = requests.get(url)
        tree = document_fromstring(r.text)

        for (el_name, title) in target_currencies:
            curr = ''.join(
                map(str.strip,
                    tree.xpath(f'//h1[text()="Курс валют НБУ"]/../../following-sibling::div/table//td[preceding-sibling::td[text()="{el_name}"]]//text()'))
            )
            result = f'{title}: {curr}'
            rates.append(result)
        return rates

    def __str__(self):
        formatted = "\n".join(self.get_rates())
        return f"Курсы НБУ:\n{formatted}\n"


class SourceManager:
    def __init__(self):
        cache = Cache()
        self.sources = [cls(cache) for cls in BaseCurrencySource.__subclasses__()]

    def get_output(self):
        output = [str(source) for source in self.sources]
        return "\n".join(output)


manager = SourceManager()
