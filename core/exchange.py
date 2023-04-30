import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
from time import time
from pprint import pprint

class NegativeDaysError(Exception):
    pass

class Request:

    async def get_json(self, session):
        print('get_json started')
        start = time()
        async with session.get(self.url) as response:
            print(f'get_json connection: {time() - start}')
            result = await response.json()
            print(f'get_json final: {time() - start}')
            return result

    def __repr__(self):
        return self.url

class ExchangeRequest(Request):

    url = "https://api.privatbank.ua/p24api/exchange_rates?json"

    def __init__(self, days):
        self.update_url(days)

    def update_url(self, days):
        now = datetime.now()
        if 0 <= days <= 10:
            date = (now - timedelta(days=days))
        elif days > 10:
            date = (now - timedelta(days=10)) # when days more then 10
        else:
            raise NegativeDaysError
        formated_date  = date.strftime('%d.%m.%Y')
        self.url = self.url + '&date=' + formated_date


class JokeRequest(Request): # Only for testing. Don't pay attention on this.
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": 'application/json'}

    async def get_value(self):
        json = await self._get_json()
        return f"{json['joke']}"


class RequestHandler:

    async def get_exchange_rate(self, days):
        async with aiohttp.ClientSession() as session:
            start = time()
            print('get_exchange_rate started')
            requests = [ExchangeRequest(i).get_json(session) for i in range(days)]
            result = await asyncio.gather(*requests)
            print(f'get_exchange_rate: {time() - start}')
            return result



def main(days=1, add_currency=None):
    selected_currencies = ['USD', 'EUR'] + [add_currency]
    start = time()
    jsons = asyncio.run(RequestHandler().get_exchange_rate(days))
    formated_jsons = []
    for json in jsons:
        date = json['date']
        values_preset = list(filter(lambda x: x['currency'] in selected_currencies, json['exchangeRate']))
        formated_values  ={}
        for i in values_preset:
            d = {i['currency']: {'purchase': i['purchaseRate'], 'sale': i['saleRate']}}
            formated_values.update(d)
        formated_jsons.append({date: formated_values})
    pprint(formated_jsons)
    print(time() - start)

if __name__ =='__main__':
    main(2)