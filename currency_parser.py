from lxml.html import document_fromstring
import requests


def get_currency():
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
