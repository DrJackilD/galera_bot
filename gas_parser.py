from lxml.html import document_fromstring
import requests


def get_gas_prices():
    url = 'https://index.minfin.com.ua/markets/fuel/reg/Днепропетровская'

    target_stations = ['Авиас', 'Укрнафта', 'ОККО', 'WOG', 'Glusco', 'SKY', 'БРСМ-Нафта']
    excluded_gas_prices = ['А\xa092']

    r = requests.get(url)
    tree = document_fromstring(r.text)

    tree.xpath('//table [./caption [contains(text(), "цены операторов")]]')

    gas_prices = []

    headers_map = {
        header.replace('\xa0', ' '): i for i, header
        in enumerate(tree.xpath('//table [./caption [contains(text(), "цены операторов")]]//th//text()'))
        if header not in excluded_gas_prices
    }

    gas_prices.append(' / '.join(headers_map))

    for gas_price in tree.xpath('//table [./caption [contains(text(), "цены операторов")]]/tr')[1:]:
        _values = gas_price.xpath('./td//text() [normalize-space()]')
        prices = []
        if _values[0] not in target_stations:
            continue
        for h in headers_map:
            try:
                prices.append(_values[headers_map[h]])
            except IndexError:
                prices.append('-')
        gas_prices.append(' / '.join(prices))

    return gas_prices
