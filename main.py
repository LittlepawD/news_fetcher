import requests as rq
import pprint as pp
import pickle, telebot, datetime

# Load News Api key, Mail keys from pickled tuple:
with open("keys.bin", "rb") as f:
    N_KEY, T_KEY, O_KEY = pickle.load(f)

class News_fetcher:

    def __init__(self, api_key):
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
        data = {"apiKey": self._KEY,
            "language": "en",
            "category": "general"}
        resp = rq.get(self.URL + "sources", data)
        if resp.ok: return resp 
        else: return resp.status_code

    # Poznamky ke zdrojum - independent má news digest, s minutovymi zpravami, nahovno
    # reuters vydava zpravy 2x, pro .com a indii
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
        if resp.ok: return resp 
        else: return resp.status_code

class NewsTeleBot(telebot.TeleBot):
    def send_article(self, article):
        channel = "@SnepsCzechNews"
        self.send_message(channel, f"<b>{article['title']}</b>\n\n{article['description']}\n{article['url']}", parse_mode="html")
        # self.send_message(channel, f"<b>{article['title']}</b>\n\n{article['url']}", parse_mode="html", disable_web_page_preview=False)


if __name__ == "__main__":
    # init bot, fetcher:
    bot = NewsTeleBot(T_KEY)
    fetcher = News_fetcher(N_KEY)

    # Get and parse news:
    news = fetcher.get_news().json()
    print(f"Fetcher got {news['totalResults']} news.")
    counter = 0
    for new in news["articles"]:
        if "reuters india" not in new["title"].lower():
            pp.pprint(new["title"])
            bot.send_article(new)
            counter += 1

    print(f"\nSent {counter} news.")
