from lxml.html import document_fromstring
import requests


def get_gas_prices():
    url = 'https://avtomaniya.com/site/fuel-dnepr'

    target_headers = ['АЗС', 'А95', 'А92', 'Газ']
    target_stations = ['Авиас', 'Укрнафта', 'ОККО', 'WOG', 'Glusco']
    headers_map = {}

    r = requests.get(url)
    tree = document_fromstring(r.text)

    gas_prices = []

    _headers = tree.xpath('//div [@class="prices-for-kiev for-kiev"]/table'
                          '/tr [@class="legend-table header-table"]//text() [normalize-space()]')
    for i, header in enumerate(_headers):
        if header in target_headers:
            headers_map[header] = i

    headers = [header for header in _headers if header in target_headers]
    gas_prices.append(' / '.join(headers))

    for gas_price in tree.xpath('//div [@class="prices-for-kiev for-kiev"]/table/tr')[1:-1]:
        _values = gas_price.xpath('./td//text() [normalize-space()]')
        prices = []
        if _values[0] not in target_stations:
            continue
        for h in target_headers:
            try:
                prices.append(_values[headers_map[h]])
            except IndexError:
                prices.append('-')
        gas_prices.append(' / '.join(prices))

    return gas_prices
