import cbpro
from datetime import datetime, timedelta


def calc_avg_price(price_entry):
    return round(sum(price_entry[1:5])/4, 2)

def calc_price_diff(prices, interval: int) -> float:
    """ Interval: Number of hours from now, range: 0-24
        Returns: percentage difference
    """
    try:
        price_now = calc_avg_price(prices[0])
        price_then = calc_avg_price(prices[interval])
    except IndexError:
        return "NaN"
    diff = price_now - price_then
    return round(diff/price_then*100, 4)

class Client: 
    def __init__(self) -> None:
        self._client = cbpro.PublicClient()

    def load_crypto(self) -> list:
        products = self._client.get_products()
        curencies = []
        cur_set = set()
        for product in products:
            if product["base_currency"] not in cur_set:
                cur_set.add(product["base_currency"])
                curencies.append(self.construct_currency_entry(product))
        return curencies

    def construct_currency_entry(self, product: dict) -> dict:
        currency_pair = product["base_currency"] + "-USD"
        prices = self.get_prices(currency_pair)
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

    def get_prices(self, currency_pair: str) -> list:
        # Now this polls one hour stats, which are calculated into average value. For more detailed values granularity 900 could be used.
        # This would need to be addressed in calc price diff func as the number of items in a list will increase 4x.
        t_now = datetime.utcnow()
        t_yesterday = t_now - timedelta(hours=25)
        return self._client.get_product_historic_rates(currency_pair, start=t_yesterday.isoformat(), end=t_now.isoformat(), granularity=3600)


def pick_top_movers(currencies: list, interval: int) -> tuple :
    currencies = [currency  for currency in currencies if "NaN" not in currency.values()]
    currencies.sort(key=lambda n: n["diff_" + str(interval)], reverse=True)
    # Return top 3 and bottom 3 differences:
    return currencies[:3], currencies[-1:-4:-1]

def construct_message(high: list, low: list, interval: int) -> str:
    high_str = [f"{h['currency']}: +{h['diff_' + str(interval)]}%" for h in high]
    low_str = [f"{h['currency']}: {h['diff_' + str(interval)]}%" for h in low]
    message = f"""
Top movers in past {interval} hours:
    {'   '.join(high_str)}
    {'   '.join(low_str)}"""
    return message

if __name__ == "__main__":
    cli = Client()
    currencies = cli.load_crypto()
    # pp.pprint(currencies)
    high, low = pick_top_movers(currencies, 12)
    print(construct_message(high, low, 12))

    high, low = pick_top_movers(currencies, 24)
    print(construct_message(high, low, 24))