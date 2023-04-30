import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
from time import time
from pprint import pprint

class Request:

    async def get_json(self, session):
        async with session.get(self.url) as response:
            result = await response.json()
            return result

    def __repr__(self):
        return self.url

class ExchangeRequest(Request):

    url = "https://api.privatbank.ua/p24api/exchange_rates?json"

    def __init__(self, days):
        self.update_url(days)

    def update_url(self, days):
        now = datetime.now()
        date = (now - timedelta(days=days))
        formated_date  = date.strftime('%d.%m.%Y')
        self.url = self.url + '&date=' + formated_date


class JokeRequest(Request): # Only for testing. Don't pay attention on this.
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": 'application/json'}

    async def get_value(self):
        json = await self._get_json()
        return f"{json['joke']}"


class RequestHandler:

    async def get_exchange_rate(self, days=1):
        requests = [ExchangeRequest(i) for i in range(days)]
        pprint(requests)
        async with aiohttp.ClientSession() as session:
            exec_requests = list(map(lambda x: x.get_json(session), requests))
            result = await asyncio.gather(*exec_requests)
            return result


def main():
    start = time()
    result = asyncio.run(RequestHandler().get_exchange_rate())
    pprint(result)
    print(time() - start)

if __name__ =='__main__':
    main()