import argparse
import aiohttp
from aiopath import AsyncPath
from aiofile import AIOFile
import asyncio
from datetime import datetime, timedelta
from functools import wraps
from time import time
from pprint import pprint


class NegativeDaysError(Exception):
    pass


class Request:
    async def get_json(self, session: aiohttp.ClientSession):
        try:
            async with session.get(
                self.url
            ) as resp:  #  The main delay in connection here
                if resp.status == 200:
                    result = await resp.json()
                else:
                    print(f"Error status {resp.status} for {self.url}")
                return result
        except aiohttp.ClientConnectionError as err:
            print(f"Connection error: {self.url}", str(err))

    def __repr__(self):
        return self.url


class ExchangeRequest(Request):
    url = "https://api.privatbank.ua/p24api/exchange_rates?json"

    def __init__(self, days):
        self.update_url(days)

    def update_url(self, days):
        now = datetime.now()
        if days <= 10:
            date = now - timedelta(days=days)
        elif days > 10:
            date = now - timedelta(days=10)  # when days more then 10
        formated_date = date.strftime("%d.%m.%Y")
        self.url = self.url + "&date=" + formated_date


class JokeRequest(Request):  # Only for testing. Don't pay attention on this.
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": "application/json"}

    async def get_value(self):
        json = await self._get_json()
        return f"{json['joke']}"


class RequestHandler:
    async def get_exchange_rate(self, days):
        async with aiohttp.ClientSession() as session:
            requests = [ExchangeRequest(i).get_json(session) for i in range(days)]
            result = await asyncio.gather(*requests)
            return result

def logger(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        date_stamp = str(datetime.now())
        result = await func(*args, **kwargs)
        finish = time() - start
        loggs = f"{date_stamp} | exchange called with {kwargs['days']} days. Execution time is {finish}\n"
        async with AIOFile('logs/exchange.log', 'a') as aiof:
            await aiof.write(loggs)
        return result
    
    return wrapper

@logger
async def main(days=1, add_currency=None):
    selected_currencies = ["USD", "EUR"] + [add_currency]
    jsons = await RequestHandler().get_exchange_rate(days)
    formated_jsons = []
    for json in jsons:
        date = json["date"]
        values_preset = list(
            filter(lambda x: x["currency"] in selected_currencies, json["exchangeRate"])
        )
        formated_values = {}
        for i in values_preset:
            d = {i["currency"]: {"purchase": i["purchaseRate"], "sale": i["saleRate"]}}
            formated_values.update(d)
        formated_jsons.append({date: formated_values})
    return formated_jsons


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates report of currenices exchange rate. If not args, create by today and only for USD adn EUR"
    )
    parser.add_argument(
        "-d",
        type=int,
        default=1,
        help="Creates additional reports for chosen number of days from today counting back",
    )
    parser.add_argument(
        "-a",
        type=str,
        default=None,
        help="Extend report by chosen currency"
    )
    namespace = parser.parse_args()
    pprint(asyncio.run(main(days=namespace.d, add_currency=namespace.a)))
