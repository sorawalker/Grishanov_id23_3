from typing import Dict, List, Set

from app.schemas.graph import Graph, PathResult


def solve_tsp(graph: Graph) -> PathResult:
    if not graph.nodes:
        return PathResult(path=[], total_distance=0.0)

    adj_list: Dict[int, List[int]] = {node: [] for node in graph.nodes}
    for edge in graph.edges:
        if len(edge) >= 2:
            u, v = edge[0], edge[1]
            adj_list[u].append(v)
            adj_list[v].append(u)

    visited: Set[int] = set()
    path: List[int] = []

    def dfs(node: int):
        visited.add(node)
        path.append(node)
        for neighbor in adj_list[node]:
            if neighbor not in visited:
                dfs(neighbor)

    start_node = graph.nodes[0]
    dfs(start_node)

    if len(path) == len(graph.nodes):
        path.append(start_node)
        return PathResult(path=path, total_distance=float(len(path) - 1))
    else:
        return PathResult(path=[], total_distance=0.0)
