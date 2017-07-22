from __future__ import print_function
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
import pickle
from time import time
import numpy as np

np.set_printoptions(threshold=np.nan)

links, data = pickle.load(open("pickled.p", "rb"))
#print(len(links), len(data))
labels = data

vectorizer = TfidfVectorizer(max_df=0.5, max_features=100,
                                 min_df=1, stop_words='english', #min_df = 2 -> 1
                                 use_idf=True)
X = vectorizer.fit_transform(data)

#print("n_samples: %d, n_features: %d" % X.shape)
#print()
#print(X)

#print("Performing dimensionality reduction using LSA")
t0 = time()
# Vectorizer results are normalized, which makes KMeans behave as
# spherical k-means for better results. Since LSA/SVD results are
# not normalized, we have to redo the normalization.
svd = TruncatedSVD(10)
normalizer = Normalizer(copy=False)
lsa = make_pipeline(svd, normalizer)
True
result = lsa.fit_transform(X)

#print("done in %fs" % (time() - t0))

explained_variance = svd.explained_variance_ratio_.sum()
#print("Explained variance of the SVD step: {}%".format(
#    int(explained_variance * 100)))

#print("Result:\n")
#print(result[:])

x2 = vectorizer.fit_transform(data)

U, s, V = np.linalg.svd(x2.toarray(), full_matrices=True)
no_rows = U.shape[0]
product = np.zeros((no_rows, 12))

# Multiply U with S ( first 12 entries only, rest ignored )
for i in range(no_rows):
    product[i] = np.multiply(U[i, :12], s[:12])

# In[66]:
#print("\n\nSVD Decomposition\n\n:")
#print(s)
#print("\n\nFirst Matrix\n", U[:,3])
#print("\n\nSecond Matrix\n", V[3,:])

# Dump results into file
pickle.dump(result, open("svd.p", "wb" ))
pickle.dump((product,s,V), open("svd-decomposed.p", "wb" ))
