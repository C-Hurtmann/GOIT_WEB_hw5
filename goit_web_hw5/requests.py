from abc import ABC, abstractmethod
import aiohttp
import asyncio
from time import time
from pprint import pprint

class Request(ABC):
    headers = ''
    
    async def _get_json(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.url) as response:
                data = await response.json()
                return data

    @abstractmethod
    def get_value(self):
        pass


class ExchangeRequest(Request):
    url = "https://api.privatbank.ua/p24api/exchange_rates?json&date=28.04.2023"

    async def get_value(self, n=1, *currency):
        result_list = []
        for _ in range(n):
            result_list.append(self._get_json())
        json_list = await asyncio.gather(*result_list)
        for json in json_list:
            json = json['exchangeRate']
            currencies = ['USD', 'EUR'] + [currency]
            json = list(filter(lambda x: x['currency'] in currencies, json))
            pprint(json)
        return json_list
    
class JokeRequest(Request):
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": 'application/json'}

    async def get_value(self):
        json = await self._get_json()
        return f"{json['joke']}"


def main():
    start = time()
    #print(asyncio.run(JokeRequest().get_value()))
    pprint(asyncio.run(ExchangeRequest().get_value(2)))
    print(time() - start)

main()