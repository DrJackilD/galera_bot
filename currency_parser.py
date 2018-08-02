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
    target_currencies = [
        ('USD', 'https://minfin.com.ua/currency/auction/usd/buy/dnepropetrovsk/?presort=&sort=time&order=desc'),
        ('EUR', 'https://minfin.com.ua/currency/auction/eur/buy/dnepropetrovsk/?presort=&sort=time&order=desc'),
        ('Деревянный', 'https://minfin.com.ua/currency/auction/rub/buy/dnepropetrovsk/?presort=&sort=time&order=desc')
    ]
    currencies = []

    for (title, url) in target_currencies:
        r = requests.get(url)
        tree = document_fromstring(r.text)
        curr = ' / '.join(
            map(str.strip,
                tree.xpath('//div [@class="au-mid-buysell"][small]/text()[normalize-space()]'))
        )
        result = f'{title}: {curr}'
        currencies.append(result)
    return currencies


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
