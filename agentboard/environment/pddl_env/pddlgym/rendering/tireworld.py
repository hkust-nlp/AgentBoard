from .utils import fig2data
import matplotlib.pyplot as plt
try:
    import networkx as nx
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False


def render(obs, mode='human', close=False):
    if not IMPORT_SUCCESS:
        raise Exception("Must `pip install networkx` to render in Tireworld.")

    nodes = set()
    edges = set()
    node_at = None
    has_spare = set()
    flattire = True
    for lit in obs:
        if lit.predicate.name == "road":
            node1, node2 = lit.variables
            nodes.add(node1)
            nodes.add(node2)
            edges.add((node1, node2))
        elif lit.predicate.name == "vehicle-at":
            node_at = lit.variables[0]
        elif lit.predicate.name == "spare-in":
            has_spare.add(lit.variables[0])
        elif lit.predicate.name == "not-flattire":
            flattire = False

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    color_map = []
    for node in G:
        if node == node_at:
            color_map.append('red')
        elif node in has_spare: 
            color_map.append('green') 
        else:
            color_map.append('yellow')

    fig = plt.figure()
    title = "Flat tire!" if flattire else "Tire not flat"
    plt.title(title)
    pos = nx.spring_layout(G, iterations=100, seed=0)
    nx.draw(G, pos, node_color=color_map)
    return fig2data(fig)
