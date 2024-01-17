#! /usr/bin/env python3


class Graph:
    def __init__(self, nodes):
        self.nodes = nodes
        self.neighbours = {u: set() for u in nodes}
    def connect(self, u, v):
        self.neighbours[u].add(v)
        self.neighbours[v].add(u)
    def connected_components(self):
        remaining_nodes = set(self.nodes)
        result = []
        def dfs(node):
            result[-1].append(node)
            remaining_nodes.remove(node)
            for neighbour in self.neighbours[node]:
                if neighbour in remaining_nodes:
                    dfs(neighbour)
        while remaining_nodes:
            node = next(iter(remaining_nodes))
            result.append([])
            dfs(node)
            result[-1].sort()
        return sorted(result)


def transitive_closure(pairs):
    # Warshall's algorithm.
    result = set(pairs)
    nodes = {u for (u, v) in pairs} | {v for (u, v) in pairs}
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if (i, j) not in result and (i, k) in result and (k, j) in result:
                    result.add((i, j))
    return sorted(result)


if __name__ == "__main__":
    g = Graph([1, 2, 3, 4, 5, 6])
    g.connect(1, 2)
    g.connect(1, 3)
    g.connect(4, 5)
    print(g.connected_components())
