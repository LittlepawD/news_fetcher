import cbpro    # 
import requests
from datetime import datetime, timedelta

from requests.exceptions import RequestException

def calc_avg_price(price_entry):
    """Calculate avg price from 'candle'"""
    return round(sum(price_entry[1:5])/4, 2)

def calc_price_diff(prices, interval: int) -> float:
    """ 
    Interval: Number of hours from now, range: 0-24
    Returns: Prices percentage difference
    """
    try:
        price_now = calc_avg_price(prices[0])
        price_then = calc_avg_price(prices[interval])
        diff = price_now - price_then
        return round(diff/price_then*100, 2)
    except IndexError:
        return "NaN"

class Client: 
    def __init__(self) -> None:
        self._client = cbpro.PublicClient()
        self.currencies = []

    def load_crypto(self):
        """
        Saves a list of crypto currencies and their price difference available on coinbase.
        currency = {currency: str,
                    id: str,
                    delta: str,
                    diff_12: float,
                    diff_24: float} 
        """
        products = self._client.get_products()
        currencies = []
        cur_set = set()
        # Remove duplicites:
        for product in products:
            if product["base_currency"] not in cur_set:
                cur_set.add(product["base_currency"])
                # this polls data from coinbase API.
                # TODO Try multiprocessing to increase speed and reliability? Or different API
                currencies.append(self._construct_currency_entry(product))
        self.currencies = currencies

    def _construct_currency_entry(self, product: dict) -> dict:
        """
        Constructs currency dictionary out of product response from coinbase API. Calculates differences in prices.
        """
        currency_pair = product["base_currency"] + "-USD"
        prices = self._get_prices(currency_pair)
        # TODO try polling again if currency pair was not found
        # In case currency pair prices are not found:
        if "message" in prices:
            currency = {
                "currency": product["base_currency"],
                "id": product["id"],
                "delta": currency_pair,
                "diff_12": "NaN",
                "diff_24": "NaN"
            }

        else:
            currency = {
                "currency": product["base_currency"],
                "id": product["id"],
                "delta": currency_pair,
                "diff_12": calc_price_diff(prices, 12),
                "diff_24": calc_price_diff(prices, 24)
            }
        return currency

    def _get_prices(self, currency_pair: str) -> list:
        """Gets 25hrs price history for currency pair from coinbase, as a list of 'candles'."""
        # Now this polls one hour stats, which are calculated into average value. For more detailed values granularity 900 could be used.
        # This would need to be addressed in calc price diff func as the number of items in a list will increase 4x.
        t_now = datetime.utcnow()
        t_yesterday = t_now - timedelta(hours=25)
        # Here is the issue: currency pair is not always found.
        return self._client.get_product_historic_rates(currency_pair, start=t_yesterday.isoformat(), end=t_now.isoformat(), granularity=3600)

    def construct_movers_report(self, interval: int) -> str:
        """
        Constructs a message with 3 highest and 3 lowest differences. Interval can currently be 12 or 24.
        Example return:
            'Top movers in past 24 hours:
            LTC: +13.13%  ETC: +11.48%  BAL: +10.01%
            FORTH: -10.27%  OGN: -8.38%  MANA: -6.85%'
        """
        high, low = pick_top_movers(self.currencies, interval)
        difference = 'diff_' + str(interval)
        high_str = [f"{val['currency']}: {add_plus_sign(val[difference])}%" for val in high]
        low_str = [f"{val['currency']}: {add_plus_sign(val[difference])}%" for val in low]
        message = f"""Top movers in past {interval} hours:
{'  '.join(high_str)}
{'  '.join(low_str)}"""
        return message
    
    def get_crypto_price(self, crypto: str,  currency: str) -> str:
        """Returns current conversion rate for crypto - currency as a string"""
        URL = f"https://api.coinbase.com/v2/prices/{crypto}-{currency}/spot"
        resp = requests.request("GET", URL)
        if resp.ok:
            return resp.json()["data"]["amount"]
        elif resp.status_code == 400:
            raise ValueError("Requested invalid currency")
        else:
            raise UnboundLocalError(str(resp))
    
    def get_currency_diff_24(self, currency: str) -> float:
        """
        Finds currency price difference in self.currencies.

        self.load_crypto() must be executed prior to calling this
        """
        cur_dict = next((cur for cur in self.currencies if cur["currency"] == currency), None)
        return cur_dict["diff_24"] 


def add_plus_sign(value) -> str:
    """If value is positive, add '+' in front of it and return it as a string."""
    try:
        if value > 0:
            return "+" + str(value)
        else:
            return str(value)
    except TypeError:
        return value

def pick_top_movers(currencies: list, interval: int) -> tuple :
    # Filter out 'NaN' values
    currencies = [currency  for currency in currencies if "NaN" not in currency.values()]
    # Sort currencies list based on difference
    currencies.sort(key=lambda n: n["diff_" + str(interval)], reverse=True)
    # Return top 3 and bottom 3 differences:
    return currencies[:3], currencies[-1:-4:-1]

if __name__ == "__main__":
    # For testing purposes
    cli = Client()
    cli.load_crypto()
    # # pp.pprint(currencies)
    print(cli.construct_movers_report(12))
    print(cli.construct_movers_report(24))
    print(cli.get_currency_diff_24("BTC"))
