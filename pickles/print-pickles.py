import pickle

clusters = pickle.load(open("sph-macbook-pro-clusters.p", "rb"))

def print_helper(clusters):
    for i in range(len(clusters)):
        print("\n\n[%d]:\n"%i)
        for j in range(len(clusters[i])):
            print("%d :"%j)
            print(clusters[i][j][1], " ", clusters[i][j][0], "\n")

print_helper(clusters)

sorted_cluster_counts = cluster_counts.argsort()
sorted_cluster_labels = cluster_labels[sorted_cluster_counts[::-1]]


print_helper(clusters)

