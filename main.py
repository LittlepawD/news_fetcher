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

    def get_sources(self):
        """Returns dictionary with sources or error code."""
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

    def pick_new(self, news):
        """returns list of new articles"""
        new_articles = []
        for article in news["articles"]:
            if article["url"] not in self.news_set:
                new_articles.append(article)
                self.news_set.add(article["url"])
                # Problém - set bude růst s každým novým článkem. Přidat skript který bude jednou za týden set čistit?
                # nebo při načítání nahradit prázdným pokud délka přesáhla něco... Ani jedno ovšem není ideální a nezabrání duplicitám za všech okolností 
        self.save_news_set()
        return new_articles            

    # Poznamky ke zdrojum - independent má news digest, s minutovymi zpravami, nahovno
    # reuters vydava zpravy 2x, pro .com a indii
    # reuters někdy publikuje i stejne članky v jine domene - uk.reuters a www.reuters, zbytek linku je stejný.
    # dalo by se vyřešit tím, že by se ukládal porovnával pouze konec linku, který je stejný.
    # od independent a washington post přišla zpráva (jiná ale se stejným linkem) 2x.

    def get_news(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1, hours=1)
        data = {
            "apiKey": self._KEY,
            "sources": self.SOURCES,
            "q": "((czech republic) OR czechia OR prague OR brno) AND (-football -digest)",
            "excludeDomains": "",
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
        text = f"<b>{article['title']}</b>\n\n{article['description']}\n{article['url']}"
        self.send_message(self.news_channel, text, parse_mode="html")
        # self.send_message(channel, f"<b>{article['title']}</b>\n\n{article['url']}", parse_mode="html", disable_web_page_preview=False)

    def send_crypto_report(self):
        crypto_cli = crypto_movers.Client()
        crypto_cli.load_crypto()
        # print("crypto loaded")
        btc_diff = crypto_cli.get_currency_diff_24("BTC")
        try:
            if btc_diff > 0:
                btc_diff = "+" + str(btc_diff)
        except TypeError:
            # in case diff is NaN
            pass

        text = "<b>Crypto report</b>\n\n" + \
            f"BTC: {crypto_cli.get_btc_price('EUR')} EUR  {btc_diff}%\n\n" + \
            crypto_cli.construct_message(24)
        self.send_message(self.news_channel, text, parse_mode="html")

    def send_articles(self, new_articles: list):
        counter = 0
        for article in new_articles:
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