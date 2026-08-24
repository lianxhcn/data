"""生成固定的博士生求助网络模拟数据。"""

from pathlib import Path
import random
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = 20260811


def main() -> None:
    random.seed(SEED)
    DATA.mkdir(parents=True, exist_ok=True)
    groups = ["Finance", "Econometrics", "Strategy", "Sociology"]
    nodes = []
    for i in range(1, 31):
        nodes.append(
            {
                "student_id": f"S{i:02d}",
                "grade": 1 + (i - 1) % 4,
                "field": groups[(i - 1) // 7 if i <= 28 else 3],
            }
        )

    # S29、S30 被有意保留为孤立节点。S05 是高频答疑者，S14 是跨组桥梁。
    edges: dict[tuple[str, str], int] = {}

    def add(source: str, target: str, weight: int) -> None:
        if source != target:
            edges[(source, target)] = edges.get((source, target), 0) + weight

    active = [f"S{i:02d}" for i in range(1, 29)]
    for source in active:
        i = int(source[1:])
        group_start = ((i - 1) // 7) * 7 + 1
        peers = [f"S{j:02d}" for j in range(group_start, min(group_start + 7, 29))]
        peers = [p for p in peers if p != source]
        for target in random.sample(peers, k=min(2, len(peers))):
            add(source, target, random.randint(1, 3))
        if source != "S05" and random.random() < 0.75:
            add(source, "S05", random.randint(2, 5))

    # 透明地加入跨研究方向联系，使桥梁位置与高入强度位置有所区别。
    cross_edges = [
        ("S03", "S14", 3), ("S14", "S03", 2),
        ("S10", "S14", 4), ("S14", "S18", 3),
        ("S18", "S14", 2), ("S14", "S24", 4),
        ("S24", "S14", 2), ("S07", "S15", 1),
        ("S12", "S21", 2), ("S20", "S27", 2),
        ("S26", "S04", 1), ("S22", "S11", 1),
    ]
    for edge in cross_edges:
        add(*edge)

    node_df = pd.DataFrame(nodes)
    edge_df = pd.DataFrame(
        [
            {"source": source, "target": target, "weight": weight}
            for (source, target), weight in sorted(edges.items())
        ]
    )
    node_df.to_csv(DATA / "nodes.csv", index=False, encoding="utf-8-sig")
    edge_df.to_csv(DATA / "edges.csv", index=False, encoding="utf-8-sig")
    print(f"generated {len(node_df)} nodes and {len(edge_df)} edges")


if __name__ == "__main__":
    main()
