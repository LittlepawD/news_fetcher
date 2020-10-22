import requests as rq
import pprint as pp
import pickle

# Load News Api key, Mail keys from pickled tuple:
with open("keys.bin", "rb") as f:
    N_KEY, T_KEY, O_KEY = pickle.load(f)

URL = "https://newsapi.org/v2/"
SOURCES = """abc-news,
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

def get_sources():
    data = {"apiKey": N_KEY,
        "language": "en"}
    data["category"] = "general"
    resp = rq.get(URL + "sources", data)
    if resp.ok: return resp 
    else: return resp.status_code

def get_news():
    data = {
        "apiKey": N_KEY,
        #"sources": SOURCES,
        "q": "((czech republic) OR czechia OR prague OR brno) AND -football",
        "from":  "10-20-2020"
    }
    resp = rq.get(URL + "everything", data)
    if resp.ok: return resp 
    else: return resp.status_code

pp.pprint(news)

if __name__ == "__main__":
    
    news = get_news().json()