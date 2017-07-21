from spider.main import get_corpora
from rating import rate

from time import time
# import pickle

t0 = time()

query = "macbook pro"
n_results = 10
results = get_corpora(query,n_results)
# pickle.dump(results, open("./pickles/sph-macbook-pro.p", "wb" ))
rated_results = rate(results)

for res in rated_results:
    print(res)

print(time() - t0)