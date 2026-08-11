"""计算核心网络指标并生成可复现图表。"""

from pathlib import Path
import json
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
SEED = 20260811


def build_graph(nodes: pd.DataFrame, edges: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in nodes.itertuples(index=False):
        graph.add_node(row.student_id, grade=row.grade, field=row.field)
    for row in edges.itertuples(index=False):
        graph.add_edge(row.source, row.target, weight=float(row.weight),
                       distance=1.0 / float(row.weight))
    return graph


def main() -> None:
    nodes = pd.read_csv(ROOT / "data" / "nodes.csv", encoding="utf-8-sig")
    edges = pd.read_csv(ROOT / "data" / "edges.csv", encoding="utf-8-sig")
    graph = build_graph(nodes, edges)
    undirected = nx.Graph()
    undirected.add_nodes_from(graph.nodes(data=True))
    for u, v, data in graph.edges(data=True):
        if undirected.has_edge(u, v):
            undirected[u][v]["weight"] += data["weight"]
        else:
            undirected.add_edge(u, v, weight=data["weight"])

    nonisolates = [n for n in undirected if undirected.degree(n) > 0]
    communities = list(nx.community.louvain_communities(
        undirected.subgraph(nonisolates), weight="weight", seed=SEED
    ))
    community_id = {
        node: idx + 1 for idx, community in enumerate(communities)
        for node in community
    }
    for node in nx.isolates(undirected):
        community_id[node] = 0
    indegree = dict(graph.in_degree())
    outdegree = dict(graph.out_degree())
    weighted_in = dict(graph.in_degree(weight="weight"))
    weighted_out = dict(graph.out_degree(weight="weight"))
    between_unweighted = nx.betweenness_centrality(graph, weight=None)
    between_distance = nx.betweenness_centrality(graph, weight="distance")
    constraint = nx.constraint(undirected, weight="weight")
    effective_size = nx.effective_size(undirected, weight="weight")
    # NetworkX 对孤立节点返回 NaN。导出表用 0 保存，并单独提供孤立标记；
    # 0 仅是便于 Stata 读取的编码，不能解释为真实结构洞得分。
    for node in nx.isolates(undirected):
        constraint[node] = 0.0
        effective_size[node] = 0.0

    metrics = nodes.copy()
    mappings = {
        "indegree": indegree, "outdegree": outdegree,
        "weighted_indegree": weighted_in,
        "weighted_outdegree": weighted_out,
        "betweenness_unweighted": between_unweighted,
        "betweenness_distance": between_distance,
        "constraint": constraint, "effective_size": effective_size,
        "community": community_id,
    }
    for column, mapping in mappings.items():
        metrics[column] = metrics["student_id"].map(mapping)
    metrics["is_isolate"] = metrics["student_id"].isin(nx.isolates(graph)).astype(int)

    isolates = list(nx.isolates(graph))
    reciprocity = nx.reciprocity(graph)
    summary = {
        "n_nodes": graph.number_of_nodes(),
        "n_edges": graph.number_of_edges(),
        "n_isolates": len(isolates),
        "density": nx.density(graph),
        "reciprocity": 0.0 if reciprocity is None else reciprocity,
        "n_weak_components": nx.number_weakly_connected_components(graph),
        "n_communities": len(communities),
    }
    tables = OUT / "tables"
    reports = OUT / "reports"
    figures = OUT / "figures"
    for path in (tables, reports, figures):
        path.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(tables / "node_metrics.csv", index=False, encoding="utf-8-sig")
    metrics.to_stata(tables / "node_metrics.dta", write_index=False, version=119)
    pd.DataFrame([summary]).to_csv(
        tables / "network_summary.csv", index=False, encoding="utf-8-sig"
    )
    (reports / "network_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    plot_graph(graph, community_id, weighted_in, between_distance, figures)
    top = lambda col, ascending=False, nonisolates=False: (
        metrics.loc[metrics["is_isolate"] == 0] if nonisolates else metrics
    ).sort_values([col, "student_id"], ascending=[ascending, True]).iloc[0]["student_id"]
    result_lines = [
        "# 分析结果说明", "",
        f"- 节点数：{summary['n_nodes']}", f"- 边数：{summary['n_edges']}",
        f"- 孤立节点：{summary['n_isolates']} ({', '.join(isolates)})",
        f"- 密度：{summary['density']:.4f}",
        f"- 互惠性：{summary['reciprocity']:.4f}",
        f"- 弱连通分量：{summary['n_weak_components']}",
        f"- 加权入度最高：{top('weighted_indegree')}",
        f"- 加权出度最高：{top('weighted_outdegree')}",
        f"- 距离中介中心性最高：{top('betweenness_distance')}",
        f"- 非孤立节点约束值最低：{top('constraint', ascending=True, nonisolates=True)}", "",
        "指标基于完整有向网络；结构洞指标和社群使用对称化网络。",
        "图形仅显示 `weight >= 2` 的边，不改变指标计算网络。",
    ]
    (reports / "analysis_results_zh.md").write_text(
        "\n".join(result_lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))


def plot_graph(graph, communities, weighted_in, between_distance, figures):
    display_edges = [(u, v) for u, v, d in graph.edges(data=True)
                     if d["weight"] >= 2]
    display = graph.edge_subgraph(display_edges).copy()
    display.add_nodes_from(graph.nodes(data=True))
    # 布局权重表示吸引力，应使用联系强度，而不是最短路径距离。
    pos = nx.spring_layout(graph, seed=SEED, weight="weight", k=0.8)
    top_in = max(weighted_in, key=lambda n: (weighted_in[n], n))
    top_between = max(between_distance,
                      key=lambda n: (between_distance[n], n))
    sizes = [220 + weighted_in[n] * 18 for n in display.nodes]
    colors = [communities[n] for n in display.nodes]
    widths = [0.5 + display[u][v]["weight"] * 0.45
              for u, v in display.edges]
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
    nx.draw_networkx_nodes(display, pos, node_size=sizes, node_color=colors,
                           cmap="Set2", edgecolors="#ffffff", linewidths=1, ax=ax)
    nx.draw_networkx_edges(display, pos, width=widths, alpha=0.45,
                           edge_color="#657786", arrowsize=10, ax=ax)
    nx.draw_networkx_labels(display, pos,
                            labels={top_in: top_in, top_between: top_between},
                            font_size=11, font_weight="bold", ax=ax)
    ax.set_title("博士生求助网络 (展示 weight >= 2 的边)", fontsize=16)
    ax.text(0.01, 0.01, "节点大小：加权入度；颜色：社群；边宽：求助次数\n"
            "指标基于完整网络，筛边只用于展示", transform=ax.transAxes,
            fontsize=10, va="bottom")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(figures / "network.png", dpi=100, bbox_inches="tight")
    fig.savefig(figures / "network.svg", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
