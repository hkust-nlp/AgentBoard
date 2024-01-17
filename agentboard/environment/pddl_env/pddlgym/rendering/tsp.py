from .utils import fig2data
import matplotlib.pyplot as plt
try:
    import networkx as nx
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False


def render(obs, mode='human', close=False):
    if not IMPORT_SUCCESS:
        raise Exception("Must install networkx to render in TSP.")

    nodes = set()
    edges = set()
    node_at = None
    visited = set()
    for lit in obs:
        if lit.predicate.name == "connected":
            node1, node2 = lit.variables
            nodes.add(node1)
            nodes.add(node2)
            edges.add((node1, node2))
        elif lit.predicate.name == "in":
            node_at = lit.variables[0]
        elif lit.predicate.name == "visited":
            visited.add(lit.variables[0])

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    color_map = []
    for node in G:
        if node == node_at:
            color_map.append('red')
        elif node in visited: 
            color_map.append('green') 
        else:
            color_map.append('yellow')

    fig = plt.figure()
    pos = nx.spring_layout(G, iterations=100, seed=0)
    nx.draw(G, pos, node_color=color_map)
    return fig2data(fig)
