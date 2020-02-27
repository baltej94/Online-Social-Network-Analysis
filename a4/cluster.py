"""
Cluster data.
"""
import pickle
from collections import defaultdict, deque
import copy
import networkx as nx
import re
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import random

def readData():
	tweets = pickle.load(open('tweets.pkl', 'rb'))
	return tweets

def get_components(graph):
    """
    A helper function you may use below.
    Returns the list of all connected components in the given graph.
    """
    return [c for c in nx.connected_component_subgraphs(graph)]

def bfs(graph, root, max_depth):
    """
    Perform breadth-first search to compute the shortest paths from a root node to all
    other nodes in the graph. To reduce running time, the max_depth parameter ends
    the search after the specified depth.
    Params:
      graph.......A networkx Graph
      root........The root node in the search graph (a string). We are computing
                  shortest paths from this node to all others.
      max_depth...An integer representing the maximum depth to search.

    Returns:
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node to this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree
    """
    q = deque()
    q.append(root)
    
    seen = set()
    seen.add(root)
    
    node2distances = defaultdict(int)
    node2num_paths = defaultdict(int)
    node2parents = defaultdict(list)
    
    node2num_paths[root] = 1
    
    while len(q) > 0:
        n = q.popleft()
        
        if node2distances[n] == max_depth:
            continue
        
        for nn in graph.neighbors(n):
            if nn not in seen:
                q.append(nn)
                node2distances[nn] = node2distances[n] + 1
                node2num_paths[nn] = node2num_paths[n]
                node2parents[nn].append(n)
                seen.add(nn)
            
            elif node2distances[nn] == node2distances[n] + 1:
                node2parents[nn].append(n)
                node2num_paths[nn] += node2num_paths[n]
    
    return node2distances, node2num_paths, node2parents
    pass

def bottom_up(root, node2distances, node2num_paths, node2parents):
    """
    Compute the final step of the Girvan-Newman algorithm.
        The third and final step is to calculate for each edge e the sum
        over all nodes Y of the fraction of shortest paths from the root
        X to Y that go through e. This calculation involves computing this
        sum for both nodes and edges, from the bottom. Each node other
        than the root is given a credit of 1, representing the shortest
        path to that node. This credit may be divided among nodes and
        edges above, since there could be several different shortest paths
        to the node. The rules for the calculation are as follows: ...

    Params:
      root.............The root node in the search graph (a string). We are computing
                       shortest paths from this node to all others.
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node that pass through this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree
    Returns:
      A dict mapping edges to credit value. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).

      Any edges excluded from the results in bfs should also be exluded here.

    """
    node_credit = defaultdict(int)
    edge_credit = defaultdict(int)
    
    sorted_nodes = sorted(node2distances.items(), key = lambda x: (-x[1]))
     
    #Each node gets 1 credit (with exception of root node)    
    node_credit[root] = 0
    for node,distance in sorted_nodes:
        if node != root:
            node_credit[node] = 1

    #bottom up
    for node,distance in sorted_nodes:
        path2node = 0
        #Summing the number of paths to the node
        for path in node2parents[node]:
            path2node += node2num_paths[path]
        
        for path in node2parents[node]:
            edge = tuple(sorted((node, path)))
            #Edge credit is (credit of the node) times (number of shortest path from root to node) divided by (sum of all the paths of parents of node)
            edge_credit[edge] = node_credit[node] * node2num_paths[path] / path2node
            node_credit[path] += edge_credit[edge]
            
    return edge_credit
    pass


def approximate_betweenness(graph, max_depth):
    """
    Compute the approximate betweenness of each edge, using max_depth to reduce
    computation time in breadth-first search.

    You should call the bfs and bottom_up functions defined above for each node
    in the graph, and sum together the results. Be sure to divide by 2 at the
    end to get the final betweenness.

    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.

    Returns:
      A dict mapping edges to betweenness. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).

    """
    edge_betweenness = defaultdict(int)
    
    for node in graph.nodes():
        node2distances, node2num_paths, node2parents = bfs(graph, node, max_depth)
        edge_credit = bottom_up(node, node2distances, node2num_paths, node2parents)
        
        for edge in edge_credit:
            edge_betweenness[edge] += edge_credit[edge]
        
    for edge in edge_betweenness:
        edge_betweenness[edge] = edge_betweenness[edge] / 2
    
    return edge_betweenness   
    pass

def get_subgraph(graph, min_degree):
    """Return a subgraph containing nodes whose degree is
    greater than or equal to min_degree.
    We'll use this in the main method to prune the original graph.

    Params:
      graph........a networkx graph
      min_degree...degree threshold
    Returns:
      a networkx graph, filtered as defined above.
    """
    subgraph = graph.copy()
    degrees = graph.degree()
    for node, degree in dict(degrees).items():
        if degree < min_degree:
            subgraph.remove_node(node)
    return subgraph
    pass

def partition_girvan_newman(graph, max_depth, length = 2):
    """
    Use your approximate_betweenness implementation to partition a graph.
    Unlike in class, here you will not implement this recursively. Instead,
    just remove edges until more than one component is created, then return
    those components.
    That is, compute the approximate betweenness of all edges, and remove
    them until multiple components are created.
    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.

    Returns:
      A list of networkx Graph objects, one per partition.

    """
    graph_copy = graph.copy()
    betweenness = sorted(approximate_betweenness(graph_copy, max_depth).items(), key = lambda x: (-x[1],x[0][0],x[0][1]))
   
    for edge, credit in betweenness:
        graph_copy.remove_edge(*edge)
        if len(get_components(graph_copy)) > length:
            break
    partitioned_graph = sorted(list(get_components(graph_copy)), key = lambda x: -len(x))
    return partitioned_graph    
    pass


def generateGraph(tweets):
    """ Method used to generate graph from all the tweets collected
        All the nodes are twitter users and the edge is added if there is an mention of 
        the user in the tweet test

        Args:
            tweets
        Returns:
            Generated Graph
    """
    graph = nx.Graph()
    for tweet in tweets:
		#Getting mentions from all tweets
        if '@' in tweet['full_text']:
            mentions = re.findall(r"[@]\S+", tweet['full_text'])
            for mention in mentions:
            	graph.add_edge(tweet['user']['screen_name'], mention[1:])
    return graph

def plotClusteredGraph(graph, clusters):
    """
        Method used to plot the clustered graph

        Args:
            Graph
            clusters
    """
    pos=nx.spring_layout(graph, scale = 5)
    plt.figure()
    plt.axis('off')

    colors_list = list(colors._colors_full_map.values())

    for i in range(len(clusters)):
    	nx.draw_networkx_nodes(graph, pos, nodelist=clusters[i], alpha= 0.5, node_size = 22, node_color = colors_list[random.randint(0,1000)])
    nx.draw_networkx_edges(graph, pos, alpha=0.3, width = 0.5)
    plt.savefig("Figure_3_Community_Detected_Graph.jpg", dpi=500)


def plotGraph(graph):
    pos=nx.spring_layout(graph, scale = 5)
    plt.figure()
    plt.axis('off')
    nx.draw_networkx_nodes(graph, pos, with_labels = False, node_size = 22, alpha = 0.5, node_color = 'red')
    nx.draw_networkx_edges(graph, pos, alpha=0.15, width=1.0, edge_color = 'black')
    return plt


def main():
	print('\nReading Tweets.')
	tweets = readData()
	print('\nGenerating Graph.')
	graph = generateGraph(tweets)
	
	print('Raw Graph has %d nodes and %d edges' %(graph.order(), graph.number_of_edges()))
	plt = plotGraph(graph)
	plt.savefig("Figure_1_Raw_Graph.jpg", dpi=500)
	
	giant = max(nx.connected_component_subgraphs(graph), key=len)
	print('Biggest Cluster from raw graph has %d nodes and %d edges' %(giant.order(), giant.number_of_edges()))
	plt = plotGraph(giant)
	plt.savefig("Figure_2_Sampled_Graph.jpg", dpi=500)

	giant = get_subgraph(giant, 2)
	print('\nPartitioning graph using Girvan-Newman Algorithm.')
	subgraphs = partition_girvan_newman(giant, 5, 25)
	
	clusters = []
	for i in range(len(subgraphs)):
			clusters.append(subgraphs[i].nodes())

	print("Community Detection after Girvan-Newman Algorithm:")
	plotClusteredGraph(giant, subgraphs)

	print('Saving Cluster to pickle.')
	pickle.dump(clusters, open('clusters.pkl', 'wb'))
	print("\nClustering Completed. \nClusters stored in clusters.pkl") 
	pass

if __name__ == "__main__":
    main()