import pickle
from spider.main import get_corpora

query = "review of macbook pro"
result = get_corpora(query,15)

pickle.dump(result, open("links-and-data", "wb" ))