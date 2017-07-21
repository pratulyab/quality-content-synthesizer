#normalize svd result
#use log entropy model
#explain data cleaning step
#K MEANS SIMILARITY METRIC
#n_clusters twice
#how to align different clusters
import pickle
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans, MiniBatchKMeans

#constants
min_common_documents = 1
max_common_document_ratio = 0.7
min_S_threshold= 0.9
fallback_svd_features = 4
n_clusters = 3
n_documents = 0

result = pickle.load(open("links-and-data", "rb")) # {'url': <URL>, 'text': <TextBlob>}


def print_helper(clusters):
    for i in range(len(clusters)):
        print("\n\n[%d]:\n"%i)
        for j in range(len(clusters[i])):
            print("%d :"%j)
            print(clusters[i][j][0], "\n")

def print_array(A):
    for ele in A:
        print(ele)

def rate(result):
    n_documents = len(result)
    links = []
    data = []
    
    for index in range(len(result)):
        links.append(result[index]['url'])
        data.append(result[index]['text'])

    vectorizer = TfidfVectorizer(max_df=max_common_document_ratio, max_features=500,
                                    min_df=1, stop_words='english', #min_df = 2 -> 1
                                    use_idf=True)

    tfidf_vectors = vectorizer.fit_transform(data)

    U, S, V = np.linalg.svd(tfidf_vectors.toarray(), full_matrices=True)

    n_svd_features = 0
    for index in range(len(S)):
        if(S[index] < min_S_threshold):
            no_svd_features = index
            break
    if(n_svd_features <= 2):
        n_svd_features = fallback_svd_features

    lsa_vectors = U[:,:no_svd_features] * S[:no_svd_features]

    kmeans_result = KMeans(n_clusters=n_clusters, random_state=0).fit(lsa_vectors)

    centers = kmeans_result.cluster_centers_
    labels = kmeans_result.labels_

    cluster_labels, cluster_counts = np.unique(labels, return_counts = True)

    global n_clusters
    n_clusters = len(cluster_labels)

    clusters = []
    for cluster in range(n_clusters):
        clusters.append([])
    
    for index in range(n_documents):
        dist = euclidean_distance(centers[labels[index]], lsa_vectors[index])
        clusters[labels[index]].append([links[index], dist])
    
    for cluster in range(n_clusters):
        clusters[cluster].sort(key=lambda x: x[1])
    print_helper(clusters)
    final_result = []
    
    sorted_cluster_counts = cluster_counts.argsort()
    sorted_cluster_labels = cluster_labels[sorted_cluster_counts[::-1]]
    
    for label in sorted_cluster_labels:
        for document in clusters[label]:
            final_result.append(document[0])

    print_array(final_result)

def euclidean_distance(A,B):
    X = np.array(A)
    Y = np.array(B)
    return np.sqrt(np.sum(np.square(X - Y)))
rate(result)