###
#CREDITS
#LogEntropyVectorizer: science_concierge (https://github.com/titipata/science_concierge/tree/master/science_concierge)
#SphericalKMeans: spherecluster (https://github.com/clara-labs/spherecluster)
###

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from spherical_kmeans import SphericalKMeans
from log_entropy_vectorizer import LogEntropyVectorizer

#------------CONSTANTS------------#

#No. of documents (is set in rate())
n_documents = 0

#tf-idf or log-entropy
vectorizer_name = "tf-idf"

#--------TF-IDF--------#
#Max no. of words allowed in tf-idf vectors 
n_tfidf_features = 3000

#Any word appearing to less than 2 documents is removed 
min_common_documents = 2

#Any word appearing in more than 50% documents is removed
max_common_document_ratio = 0.5

#----------SVD----------#
#Only take those SVD features with S value greater than 0.9  
min_S_threshold= 0.9

#If No. of SVD features is less than 2, increase that to 4
fallback_svd_features = 4

#----SPHERICAL-KMEANS----#
#No. of KMeans clusters
n_clusters = 3

#Find distance between 2 vectors using L2 Norm: sqrt((x2-x1)^2 + (y2-y1)^2)
def euclidean_distance(A,B):
    X = np.array(A)
    Y = np.array(B)
    return np.sqrt(np.sum(np.square(X - Y)))

#Main Rating Algorithm
def rate(result):

    links = []
    data = []
    
    #Extract links and data from scraper results
    for index in range(len(result)):
        links.append(result[index]['url'])
        data.append(result[index]['text'])

    n_documents = len(links)

    #Create Vectorizer: stop_words='english' are used to remove common english words like and, the

    if vectorizer_name == "tf-idf":
        vectorizer = TfidfVectorizer(max_df=max_common_document_ratio, max_features=n_tfidf_features,
                               min_df=1, stop_words='english')
    elif vectorizer_name == "log-entropy":
        vectorizer = LogEntropyVectorizer(max_df=max_common_document_ratio,
                               min_df=1, stop_words='english')    

    #Using the tf-idf vectors to vectorize documents
    tfidf_vectors = vectorizer.fit_transform(data)

    #Applying SVD to tf-idf vectors
    U, S, V = np.linalg.svd(tfidf_vectors.toarray(), full_matrices=True)

    #We will only consider those columns of U for which S[column] > min_S_threshold 
    n_svd_features = 0
    for index in range(len(S)):
        if(S[index] < min_S_threshold):
            no_svd_features = index
            break

    #But if number of colums considered < 2, we set it to fallback_svd_features
    if(n_svd_features <= 2):
        n_svd_features = fallback_svd_features

    #Multiply selected columns with it's respective S values
    # So that we give importance to the concepts which our algorithm is more confident about
    lsa_vectors = U[:,:no_svd_features] * S[:no_svd_features]

    #Performing Spherical K means Clustering on LSA Vectors
    kmeans_result = SphericalKMeans(n_clusters=n_clusters).fit(lsa_vectors)

    #labels: Which cluster does each document belongs to 
    #centers: Center points of those clusters
    centers = kmeans_result.cluster_centers_
    labels = kmeans_result.labels_
 
    #cluster_labels: one label for each cluster
    #cluster counts: number of documents in each cluster
    cluster_labels, cluster_counts = np.unique(labels, return_counts = True)

    #update number of clusters
    global n_clusters
    n_clusters = len(cluster_labels)

    #clusters: 3D array
    # one list for each cluster 
    # each list will contain an entry for each documents in that cluster
    # each entry will contain the document link and it's eucledian distance from it's respective cluster center
    clusters = []
    for cluster in range(n_clusters):
        clusters.append([])

    for index in range(n_documents):
        dist = euclidean_distance(centers[labels[index]], lsa_vectors[index])
        clusters[labels[index]].append([links[index], dist])
    
    #Sort each cluster based on document distance fromm it's cluster center
    for cluster in range(n_clusters):
        clusters[cluster].sort(key=lambda x: x[1])
    
    #Final results to be returned
    final_result = []
    
    #Sort clusters based on number of documents in them
    sorted_cluster_counts = cluster_counts.argsort()
    sorted_cluster_labels = cluster_labels[sorted_cluster_counts[::-1]]
    
    #Append sorted documents to final result
    for label in sorted_cluster_labels:
        for document in clusters[label]:
            final_result.append(document[0])
    
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

