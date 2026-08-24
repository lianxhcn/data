"""极简网络中心性示例的复现脚本。

运行方式 (在附件根目录执行)：
    python code/centrality_demo.py

脚本只使用本目录中的两个边表，不下载外部数据。它会：
1. 计算无向网络的度、中介、接近和特征向量中心性；
2. 增加 E-G 这条绕行边，检查 B 的中介中心性如何变化；
3. 计算有向网络的入度与 PageRank；
4. 将核验结果写入 results 目录。
"""

from pathlib import Path

import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def build_graph(file_name: str, directed: bool = False) -> nx.Graph:
    """从边表构造网络，并固定节点顺序为 A-K 或 A-H。"""
    edges = pd.read_csv(DATA / file_name)
    graph_type = nx.DiGraph() if directed else nx.Graph()
    graph_type.add_edges_from(edges[["source", "target"]].itertuples(index=False, name=None))
    return graph_type


def undirected_results(graph: nx.Graph) -> pd.DataFrame:
    """计算四种无向网络中心性，并补充手算所需的中间量。"""
    n = graph.number_of_nodes()
    degree = nx.degree_centrality(graph)
    between = nx.betweenness_centrality(graph, normalized=True)
    between_raw = nx.betweenness_centrality(graph, normalized=False)
    closeness = nx.closeness_centrality(graph)
    eigen = nx.eigenvector_centrality(graph, max_iter=5000, tol=1e-12)

    rows = []
    for node in sorted(graph.nodes()):
        distances = nx.single_source_shortest_path_length(graph, node)
        rows.append(
            {
                "node": node,
                "degree_count": graph.degree(node),
                "degree_centrality": degree[node],
                "distance_sum": sum(distances.values()),
                "closeness_centrality": closeness[node],
                "betweenness_raw": between_raw[node],
                "betweenness_centrality": between[node],
                "eigenvector_centrality": eigen[node],
            }
        )
    return pd.DataFrame(rows)


def pagerank_iterations(graph: nx.DiGraph, alpha: float = 0.85, steps: int = 2) -> pd.DataFrame:
    """从均匀初值出发，手工执行若干轮 PageRank 递推并与收敛值比较。"""
    nodes = sorted(graph.nodes())
    n = len(nodes)
    history = [{node: 1 / n for node in nodes}]

    for _ in range(steps):
        previous = history[-1]
        current = {}
        for node in nodes:
            incoming = sum(
                previous[source] / graph.out_degree(source)
                for source in graph.predecessors(node)
            )
            current[node] = (1 - alpha) / n + alpha * incoming
        history.append(current)

    converged = nx.pagerank(graph, alpha=alpha, tol=1e-14, max_iter=5000)
    rows = []
    for node in nodes:
        rows.append(
            {
                "node": node,
                "in_degree": graph.in_degree(node),
                "out_degree": graph.out_degree(node),
                "initial": history[0][node],
                "t1": history[1][node],
                "t2": history[2][node],
                "converged": converged[node],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    undirected = build_graph("undirected_edges.csv")
    base = undirected_results(undirected)
    base.to_csv(RESULTS / "undirected_centrality_results.csv", index=False)

    # 只增加一条绕行边。B 的度不变，但许多最短路径不再必须经过 B。
    bypass = undirected.copy()
    bypass.add_edge("E", "G")
    changed = undirected_results(bypass)
    sensitivity = pd.concat(
        [
            base.loc[base["node"] == "B"].assign(network="original"),
            changed.loc[changed["node"] == "B"].assign(network="add_edge_E_G"),
        ],
        ignore_index=True,
    )
    sensitivity.to_csv(RESULTS / "betweenness_sensitivity.csv", index=False)

    directed = build_graph("directed_edges.csv", directed=True)
    pagerank = pagerank_iterations(directed)
    pagerank.to_csv(RESULTS / "pagerank_iterations.csv", index=False)

    print("无向网络四项指标的第一名：")
    for column in [
        "degree_centrality",
        "betweenness_centrality",
        "closeness_centrality",
        "eigenvector_centrality",
    ]:
        winner = base.loc[base[column].idxmax(), ["node", column]]
        print(f"{column:28s} {winner['node']}  {winner[column]:.4f}")

    print("\nPageRank 与入度的第一名：")
    print("入度：", pagerank.loc[pagerank["in_degree"].idxmax(), "node"])
    print("PageRank：", pagerank.loc[pagerank["converged"].idxmax(), "node"])


if __name__ == "__main__":
    main()
