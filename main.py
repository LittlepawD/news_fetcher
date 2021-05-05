import requests as rq
import pprint as pp
import pickle, telebot, datetime

import crypto_movers

# Load News Api key, Mail keys from pickled tuple:
with open("keys.bin", "rb") as f:
    N_KEY, T_KEY, O_KEY = pickle.load(f)

class News_fetcher:
    def __init__(self, api_key):
        self.news_set = self.load_news_set()
        self._KEY = api_key
        self.URL = "https://newsapi.org/v2/"
        self.SOURCES = """abc-news,
                al-jazeera-english,
                associated-press,
                bbc-news,
                cbc-news,
                cnn,
                independent,
                reddit-r-all,
                reuters,
                the-washington-post,
                time,
                news-com-au,
                nbc-news"""

    def _get_sources(self) -> dict:
        """Returns dictionary with sources based on specified criteria or error code. Used only for initial manual setup"""
        data = {"apiKey": self._KEY,
            "language": "en",
            "category": "general"}
        resp = rq.get(self.URL + "sources", data)
        if resp.ok: 
            return resp.json()
        else: 
            return resp.status_code

    def load_news_set(self):
        try:
            with open("news_set.bin", "rb") as f:
                news_set = pickle.load(f)
        except IOError:
        # If news_set.bin doesnt exist:
            with open("news_set.bin", "wb") as f:
                pickle.dump(set(), f)
            print("Created new news_set.bin file.")
            news_set = set()

        if len(news_set) <= 100:
            return news_set
        else:
            return set()

    def save_news_set(self):
        with open("news_set.bin", "wb") as f:
            pickle.dump(self.news_set, f)

    def pick_new(self, news: dict) -> list:
        """From news from API response returns list of new articles"""
        new_articles = []
        for article in news["articles"]:
            if article["url"] not in self.news_set:
                new_articles.append(article)
                # Add article URL to set to prevent for sending it twice
                self.news_set.add(article["url"])
        self.save_news_set()
        return new_articles            

    def get_news(self) -> dict:
        """Sends request to news API and returns the response."""
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1, hours=1)
        data = {
            "apiKey": self._KEY,
            "sources": self.SOURCES,
            # This is what news are searched for:
            "q": "((czech republic) OR czechia OR prague OR brno) AND (-football -digest)",
            "excludeDomains": "",
            # What is the news time interval
            "from":  yesterday.isoformat(timespec="minutes")
        }
        resp = rq.get(self.URL + "everything", data)
        if resp.ok:
            return resp.json()
        else:
            return resp.status_code


class NewsTeleBot(telebot.TeleBot):
    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)
        self.news_channel = "@SnepsCzechNews"

    def _send_article(self, article: dict):
        """Constructs article message and sends it to telegram channel"""
        text = f"<b>{article['title']}</b>\n\n{article['description']}\n{article['url']}"
        self.send_message(self.news_channel, text, parse_mode="html")
        # Alternative formating:
        # self.send_message(channel, f"<b>{article['title']}</b>\n\n{article['url']}", parse_mode="html", disable_web_page_preview=False)

    #TODO make one method for sendind message to channel instead

    def _construct_crypto_prices(self, currencies: list) -> str:
        """
        Finds data for currencies specified in list and puts them in a message.
        param:
            currencies: list - list of dictionaries with currency pairs
        returns: 
            str - message with polled data.
        Example:
            IN : 
                {"crypto": "BTC", "currency": "EUR"},
                {"crypto": "ETH", "currency": "USD"},
                {"crypto": "LTC", "currency": "USD"}
            OUT: 
                'BTC: 46983.53 EUR  -3.78%
                ETH: 3428.38 USD  +8.73%
                LTC: 318.28 USD  +13.13%'
        """

        strings = []
        for pair in currencies:
            diff = crypto_movers.add_plus_sign(self.crypto_cli.get_currency_diff_24(pair['crypto']))
            string = f"{pair['crypto']}: {self.crypto_cli.get_crypto_price(pair['crypto'], pair['currency'])} {pair['currency']}  {diff}%"
            strings.append(string)
        return "\n".join(strings)

    def send_crypto_report(self):
        """Loads crypto information, constructs crypto report message and sends it to telegram channel."""
        self.crypto_cli = crypto_movers.Client()
        self.crypto_cli.load_crypto()
        # print("crypto loaded")

        # Currencies to put in report:
        currencies_list = [
            {"crypto": "BTC", "currency": "EUR"},
            {"crypto": "ETH", "currency": "USD"},
            {"crypto": "LTC", "currency": "USD"}
        ]
        # Construct message of 3 components - title, crypto_prices and movers_report:
        text = "<b>Crypto report</b>\n\n" + \
            self._construct_crypto_prices(currencies_list) + "\n\n" +\
            self.crypto_cli.construct_movers_report(24)
        
        self.send_message(self.news_channel, text, parse_mode="html")

    def send_articles(self, new_articles: list):
        counter = 0
        for article in new_articles:
            # Reuters India post duplicate articles, filter them out
            if "reuters india" not in article["title"].lower():
                pp.pprint(article["title"])
                self._send_article(article)
                counter += 1
        print(f"\nSent {counter} news.")


if __name__ == "__main__":
    # init bot, fetcher:
    bot = NewsTeleBot(T_KEY)
    fetcher = News_fetcher(N_KEY)
    # Get and parse news:
    news = fetcher.get_news()
    new_articles = fetcher.pick_new(news)
    bot.send_articles(new_articles)

    bot.send_crypto_report()