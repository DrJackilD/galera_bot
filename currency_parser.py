from lxml.html import document_fromstring
import requests


def get_banks_currency():
    url = 'https://minfin.com.ua/currency/banks/dnepropetrovsk/'
    target_currencies = [
        ("ДОЛЛАР", "USD"),
        ("ЕВРО", "EUR"),
        ("РУБЛЬ", "Деревянный")
    ]

    r = requests.get(url)
    tree = document_fromstring(r.text)

    currencies = []
    for (el_name, title) in target_currencies:
        curr = ' / '.join(
            map(
                str.strip,
                tree.xpath(f'//td [@data-title="Курс к гривне"][a [text()="{el_name}"]]'
                           '/following-sibling::td [@data-title="Средний курс"]/text()')
            )
        )
        result = f'{title}: {curr}'
        currencies.append(result)
    return currencies


def get_market_currencies():
    currency_map = {
        'Dollar': 'USD',
        'Euro': 'EUR',
        'Rub': 'Деревянный',
    }
    rates = requests.get('http://vkurse.dp.ua/course.json').json()
    return [f"{currency_map[name]}: {values['buy']} грн / {values['sale']} грн" for (name, values) in rates.items()]


def get_nbu_currencies():
    url = 'https://minfin.com.ua/currency/nbu/'
    target_currencies = [
        ("ДОЛЛАР", "USD"),
        ("ЕВРО", "EUR"),
        ("РУБЛЬ", "Деревянный")
    ]
    currencies = []

    r = requests.get(url)
    tree = document_fromstring(r.text)

    for (el_name, title) in target_currencies:
        curr = ''.join(
            map(str.strip,
                tree.xpath(f'//a [text()="{el_name}"]/../../td[@data-title="Курс НБУ"]/text()[normalize-space()]'))
        )
        result = f'{title}: {curr}'
        currencies.append(result)
    return currencies
