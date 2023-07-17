import platform
import sys
import aiohttp
import asyncio
from datetime import datetime, timedelta

template = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
# cur_list = ['USD', 'EUR', 'CHF', 'GBP', 'PLZ', 'SEK', 'XAU', 'CAD']
currency = ["EUR", "USD"]
today = datetime.now().date()

try:
    number_of_days = int(sys.argv[1])
except IndexError:
    print("No param, set current date")
    number_of_days = 1

if number_of_days > 10:
    print("Max value of days is 10, setting param to 10")
    number_of_days = 10
elif number_of_days <= 0:
    print("Min value of days is 1, setting param to 1")
    number_of_days = 1

if len(sys.argv) > 2:
    currency = []
    for i in range(2, len(sys.argv)):
        currency.append(sys.argv[i].upper())


async def days(d):
    for k in range(d):
        complete_link = template + datetime.strftime(today - timedelta(days=k), "%d.%m.%Y")
        yield complete_link
        await asyncio.sleep(0.05)


def normalize_json(json: dict, currency_list: list):
    main_dict = {}
    dict_of_dicts = {}
    for cur in currency_list:
        for j in json['exchangeRate']:
            if j['currency'] == cur:
                try:
                    dict_of_dicts.update({cur: {'sale': j['saleRate'], 'purchase': j['purchaseRate']}})
                except KeyError:
                    dict_of_dicts.update({cur: {'sale': j['saleRateNB'], 'purchase': j['purchaseRateNB']}})
    main_dict.update({json['date']: dict_of_dicts})

    return main_dict


async def main():
    res_array = []
    async with aiohttp.ClientSession() as session:
        async for link in days(number_of_days):
            try:
                async with session.get(link) as response:
                    if response.status == 200:
                        result = await response.json()
                        res_array.append(normalize_json(result, currency))
                    else:
                        print(f"Error status: {response.status} for {link}")
            except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {link}', str(err))
    return res_array


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # start = datetime.now()
    r = asyncio.run(main())
    # end = datetime.now()
    # print(end - start)
    # print(r)
    for i in r:
        print(i)
