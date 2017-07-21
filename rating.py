#remove pickle files and imports
#explain data cleaning step
#how to align different clusters
#repeated results in search

#------Algo Changes-----#
#use log entropy model
#DONE: normalize svd result
#DONE: kmeans by cosine similarity

import numpy as np
#import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from spherical_kmeans import SphericalKMeans
from log_entropy_vectorizer import LogEntropyVectorizer

#constants
min_common_documents = 1
max_common_document_ratio = 0.7
min_S_threshold= 0.9
fallback_svd_features = 4
n_clusters = 3
n_documents = 0
vectorizer_name = "tf-idf"

def euclidean_distance(A,B):
    X = np.array(A)
    Y = np.array(B)
    return np.sqrt(np.sum(np.square(X - Y)))

def rate(result):

    links = []
    data = []
    
    for index in range(len(result)):
        if result[index]['url'] not in links:
            links.append(result[index]['url'])
            data.append(result[index]['text'])

    n_documents = len(links)
    if vectorizer_name == "tf-idf":
        vectorizer = TfidfVectorizer(max_df=max_common_document_ratio, max_features=500,
                               min_df=1, stop_words='english')
    elif vectorizer_name == "log-entropy":
        vectorizer = LogEntropyVectorizer(max_df=max_common_document_ratio,
                               min_df=1, stop_words='english')    

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

    kmeans_result = SphericalKMeans(n_clusters=n_clusters).fit(lsa_vectors)
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
    
    final_result = []
    
    sorted_cluster_counts = cluster_counts.argsort()
    sorted_cluster_labels = cluster_labels[sorted_cluster_counts[::-1]]
    
    for label in sorted_cluster_labels:
        for document in clusters[label]:
            final_result.append(document[0])
    #pickle.dump(clusters, open("./pickles/sph-macbook-pro-clusters.p", "wb" ))
    return final_result

#----------HELPER FUNCTIONS-----------#
def print_helper(clusters):
    for i in range(len(clusters)):
        print("\n\n[%d]:\n"%i)
        for j in range(len(clusters[i])):
            print("%d :"%j)
            print(clusters[i][j][0], "\n")

def print_array(A):
    for ele in A:
        print(ele)

# result = pickle.load(open("./pickles/sph-macbook-pro.p", "rb"))
# rate(result)