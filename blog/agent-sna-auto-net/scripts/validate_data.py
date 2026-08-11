"""严格验证节点表和边表，异常时停止分析。"""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORT = ROOT / "outputs" / "reports" / "data_validation.md"


def main() -> None:
    nodes = pd.read_csv(DATA / "nodes.csv", encoding="utf-8-sig")
    edges = pd.read_csv(DATA / "edges.csv", encoding="utf-8-sig")
    errors = []
    required_nodes = {"student_id", "grade", "field"}
    required_edges = {"source", "target", "weight"}
    if not required_nodes.issubset(nodes.columns):
        errors.append("节点表缺少必需字段")
    if not required_edges.issubset(edges.columns):
        errors.append("边表缺少必需字段")
    if errors:
        raise ValueError("; ".join(errors))

    node_ids = set(nodes["student_id"])
    checks = {
        "节点 ID 重复数": int(nodes["student_id"].duplicated().sum()),
        "缺失值数": int(nodes.isna().sum().sum() + edges.isna().sum().sum()),
        "无法匹配的边端点数": int(
            (~edges["source"].isin(node_ids)).sum()
            + (~edges["target"].isin(node_ids)).sum()
        ),
        "自环数": int((edges["source"] == edges["target"]).sum()),
        "重复有向边数": int(edges.duplicated(["source", "target"]).sum()),
        "非正权重数": int((edges["weight"] <= 0).sum()),
    }
    for label, value in checks.items():
        if value:
            errors.append(f"{label}={value}")
    incident = set(edges["source"]) | set(edges["target"])
    isolates = sorted(node_ids - incident)
    lines = [
        "# 数据验证报告", "", "- 状态：" + ("通过" if not errors else "失败"),
        "- 网络方向：有向，`source` 为求助者，`target` 为被求助者。",
        "- 权重语义：`weight` 为一个月内求助次数，表示联系强度。",
        "- 重复边策略：报告错误并停止，不静默合并。",
        f"- 节点数：{len(nodes)}", f"- 边数：{len(edges)}",
        f"- 边表外孤立节点：{len(isolates)} ({', '.join(isolates)})", "",
        "## 检查项", "",
    ]
    lines.extend([f"- {label}：{value}" for label, value in checks.items()])
    if errors:
        lines.extend(["", "## 错误", "", *[f"- {e}" for e in errors]])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        raise ValueError("data validation failed: " + "; ".join(errors))
    print("data validation passed")


if __name__ == "__main__":
    main()
