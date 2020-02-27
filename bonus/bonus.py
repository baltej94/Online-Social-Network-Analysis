import networkx as nx

def jaccard_wt(graph, node):
    """
    The weighted jaccard score, defined above.
    Args:
      graph....a networkx graph
      node.....a node to score potential new edges for.
    Returns:
      A list of ((node, ni), score) tuples, representing the 
                score assigned to edge (node, ni)
                (note the edge order)
    """
    neighbors = set(graph.neighbors(node))
    scores = []
    for n in graph.nodes():
    	if ((n not in neighbors) and (n !=node)):
    		neighbors2 = set(graph.neighbors(n))

    		numerator = 0
    		Sum_A_degrees = 0
    		Sum_B_degrees = 0

    		for i in neighbors & neighbors2:
    				numerator += 1 / (graph.degree(i))
    		for i in graph.neighbors(node):
    			Sum_A_degrees += (graph.degree(i))
    		for j in graph.neighbors(n):
    			Sum_B_degrees += (graph.degree(j))

    		denominator = (1/Sum_A_degrees) + (1/Sum_B_degrees)

    		score = numerator/denominator

    		scores.append(((node, n), score))
    return sorted(scores, key=lambda x:(-x[1]))
    pass


## Used for testing the jaccard_wt method 

def example_graph():
    """
    Create the example graph from class. Used for testing.
    Do not modify.
    """
    g = nx.Graph()
    g.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('D', 'E'), ('D', 'F'), ('D', 'G'), ('E', 'F'), ('G', 'F')])
    return g


def main():
	graph = example_graph()
	print(jaccard_wt(graph, 'B'))

if __name__ == '__main__':
	main()

