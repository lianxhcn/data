"""核验输出文件、行数、有限值和网络图规格。"""

from pathlib import Path
import json
import math
from PIL import Image
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def main() -> None:
    expected = [
        OUT / "tables" / "node_metrics.csv",
        OUT / "tables" / "node_metrics.dta",
        OUT / "tables" / "network_summary.csv",
        OUT / "figures" / "network.png",
        OUT / "reports" / "data_validation.md",
        OUT / "reports" / "analysis_results_zh.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in expected if not p.exists()]
    metrics = pd.read_csv(expected[0], encoding="utf-8-sig")
    summary = pd.read_csv(expected[2], encoding="utf-8-sig").iloc[0].to_dict()
    numeric = metrics.select_dtypes(include="number")
    finite = numeric.map(lambda x: math.isfinite(float(x))).all().all()
    image = Image.open(expected[3])
    checks = {
        "预期文件齐全": not missing,
        "指标表行数等于节点数": len(metrics) == int(summary["n_nodes"]),
        "孤立节点保留": int(summary["n_isolates"]) == 2
        and set(metrics.loc[(metrics.indegree == 0) & (metrics.outdegree == 0),
                            "student_id"]) == {"S29", "S30"},
        "数值字段均为有限值": bool(finite),
        "PNG 宽度合格": 1000 <= image.width <= 1200,
        "PNG 小于 1 MB": expected[3].stat().st_size < 1_000_000,
        "固定基准节点数": int(summary["n_nodes"]) == 30,
        "固定基准边数": int(summary["n_edges"]) == 88,
        "固定基准密度": abs(float(summary["density"]) - 0.10114942528735632) < 1e-12,
        "固定基准互惠性": abs(float(summary["reciprocity"]) - 0.29545454545454547) < 1e-12,
        "固定基准弱连通分量": int(summary["n_weak_components"]) == 3,
        "加权入度最高节点": metrics.sort_values(
            ["weighted_indegree", "student_id"], ascending=[False, True]
        ).iloc[0]["student_id"] == "S05",
        "加权出度最高节点": metrics.sort_values(
            ["weighted_outdegree", "student_id"], ascending=[False, True]
        ).iloc[0]["student_id"] == "S14",
        "距离中介中心性最高节点": metrics.sort_values(
            ["betweenness_distance", "student_id"], ascending=[False, True]
        ).iloc[0]["student_id"] == "S14",
        "非孤立节点约束值最低": metrics.loc[metrics["is_isolate"] == 0].sort_values(
            ["constraint", "student_id"], ascending=[True, True]
        ).iloc[0]["student_id"] == "S05",
    }
    passed = all(checks.values())
    lines = ["# 输出验证报告", "", f"- 状态：{'通过' if passed else '失败'}",
             f"- 图形尺寸：{image.width} × {image.height}",
             f"- 图形大小：{expected[3].stat().st_size} bytes", "", "## 检查项", ""]
    lines.extend([f"- {'通过' if value else '失败'}：{label}"
                  for label, value in checks.items()])
    if missing:
        lines.extend(["", "## 缺失文件", "", *[f"- `{p}`" for p in missing]])
    report = OUT / "reports" / "output_validation.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not passed:
        raise ValueError(json.dumps(checks, ensure_ascii=False))
    print("output validation passed")


if __name__ == "__main__":
    main()
