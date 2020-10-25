import requests as rq
import pprint as pp
import pickle, telebot, datetime

# Load News Api key, Mail keys from pickled tuple:
with open(r"/home/dbodnr37/news_fetcher/keys.bin", "rb") as f:
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
        self.save_news_set()
        return new_articles            

    # Poznamky ke zdrojum - independent má news digest, s minutovymi zpravami, nahovno
    # reuters vydava zpravy 2x, pro .com a indii
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
    def send_article(self, article):
        channel = "@SnepsCzechNews"
        self.send_message(channel, f"<b>{article['title']}</b>\n\n{article['description']}\n{article['url']}", parse_mode="html")
        # self.send_message(channel, f"<b>{article['title']}</b>\n\n{article['url']}", parse_mode="html", disable_web_page_preview=False)


if __name__ == "__main__":
    # init bot, fetcher:
    bot = NewsTeleBot(T_KEY)
    fetcher = News_fetcher(N_KEY)

    # Get and parse news:
    news = fetcher.get_news()
    new_articles = fetcher.pick_new(news)
    counter = 0
    for article in new_articles:
        if "reuters india" not in article["title"].lower():
            pp.pprint(article["title"])
            # bot.send_article(article)
            counter += 1
    # print(f"\nSent {counter} news.")
