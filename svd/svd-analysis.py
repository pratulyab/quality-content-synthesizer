import numpy as np
import pickle
from collections import defaultdict
from sklearn.cluster import KMeans

np.set_printoptions(threshold=np.nan)

links, data = pickle.load(open("pickled.p", "rb"))
svd = pickle.load(open("svd.p", "rb"))

#Here U is the product of U*S from svd-algo.py
(U,s,V) = pickle.load(open("svd-decomposed.p", "rb"))

'''
for i in range(len(U)):
    print("\n\n[%d]:"%i)
    print(links[i])
    print("Length:%d"%len(data[i]))
    print(U[i])
'''

kmeans = KMeans(n_clusters=3, random_state=0).fit(U[:,:])

centroids = kmeans.cluster_centers_
labels = kmeans.labels_

# Get links into dictionary by label
d = defaultdict(list)
for i in range(len(labels)):
    d[labels[i]].append(links[i])

# Sorted dictionary based on number of links in a label
d_len = defaultdict(list)
for i in sorted(d.values()):
    d_len[len(i)] = i

# Print list of links
for i in sorted(d_len.keys(), reverse=True):
    print(len(d_len[i]), '\n', d_len[i])
    print('\n')

#Trying to plot links on a graph
'''
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')
c = ['r', 'g', 'b']

keys = list(d_len.keys())
for i in range(len(keys)):
    for j in range(len(d_len[keys[i]])):
        plt.scatter(i, d_len[keys[i]][j], color=c[i])
#PLOT STRING VALUES (LINKS) ON PLOT | CANNOT PLOT STRINGS SO GET VALUES FROM U CORRESPONDING TO STRING
plt.show()
'''
