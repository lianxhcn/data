"""准确率和混淆矩阵相同，OLS 系数仍可一正一负。

100 条观测和两种误判模式均为教学构造。
本脚本无需调用 LLM，也不复现原论文的实证估计。

安装依赖：python -m pip install numpy==2.3.5 matplotlib==3.10.8
运行示例：python llm_annotation_demo.py
可选参数：--output-dir PATH；--font 指定本地中文字体文件。

重复运行会覆盖两个同名 CSV；配图文件名含北京时间的时间戳。
脚本中的固定结果断言用于核验原例子，探索其他误判模式请使用正文精简代码。
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np


def make_data():
    """构造固定数据，无随机抽样，因此每次运行的数值结果相同。"""
    true_label = np.repeat([1, 0], [10, 90])
    success = np.repeat([1, 0, 1, 0], [8, 2, 45, 45])
    label_a, label_b = true_label.copy(), true_label.copy()
    # A 的 10 个假阳性来自失败项目，B 的 10 个假阳性来自成功项目。
    label_a[np.flatnonzero((true_label == 0) & (success == 0))[:10]] = 1
    label_b[np.flatnonzero((true_label == 0) & (success == 1))[:10]] = 1
    return true_label, success, label_a, label_b


def evaluate(name, observed_label, true_label, success):
    """计算含截距的 OLS、分类指标和两组成功率。"""
    design = np.column_stack([np.ones(len(success)), observed_label])
    beta = np.linalg.lstsq(design, success, rcond=None)[0][1]
    tp = int(np.sum((observed_label == 1) & (true_label == 1)))
    fp = int(np.sum((observed_label == 1) & (true_label == 0)))
    fn = int(np.sum((observed_label == 0) & (true_label == 1)))
    tn = int(np.sum((observed_label == 0) & (true_label == 0)))
    mean1 = float(success[observed_label == 1].mean())
    mean0 = float(success[observed_label == 0].mean())
    # 独立核验：二元解释变量的简单 OLS 系数等于两组均值之差。
    assert np.isclose(beta, mean1 - mean0)
    return {
        "label": name,
        "n": len(success),
        "accuracy": (tp + tn) / len(success),
        "precision": tp / (tp + fp),
        "recall": tp / (tp + fn),
        "f1": 2 * tp / (2 * tp + fp + fn),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "success_rate_label1": mean1,
        "success_rate_label0": mean0,
        "ols_coefficient": float(beta),
    }


def check_teaching_claims(rows):
    """核对正文的三个系数，以及 A、B 相同的混淆矩阵和分类指标。"""
    assert np.allclose([r["ols_coefficient"] for r in rows], [.30, -.1625, .4625])
    for row in rows[1:]:
        assert (row["tp"], row["fp"], row["fn"], row["tn"]) == (10, 10, 0, 80)
        assert np.isclose(row["accuracy"], .90)
        assert np.isclose(row["precision"], .50)
        assert np.isclose(row["recall"], 1.0)
        assert np.isclose(row["f1"], 2 / 3)


def write_csv(path, rows):
    # UTF-8 BOM 便于常见表格软件识别文件编码。
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_results(rows, path, font_path=None):
    """优先使用中文字体；未找到时自动改用英文标签。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    chinese = False
    if font_path is not None:
        font_manager.fontManager.addfont(str(font_path))
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=font_path).get_name()
        chinese = True
    else:
        available = {font.name for font in font_manager.fontManager.ttflist}
        for name in ("Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei", "PingFang SC"):
            if name in available:
                plt.rcParams["font.family"] = name
                chinese = True
                break
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 16})
    values = [r["ols_coefficient"] * 100 for r in rows]
    labels = (["设定标签\n准确率 100%", "标注 A\n准确率 90%", "标注 B\n准确率 90%"]
              if chinese else ["True labels\nAccuracy 100%", "Labels A\nAccuracy 90%", "Labels B\nAccuracy 90%"])
    fig, ax = plt.subplots(figsize=(6, 4.25), dpi=200)
    fig.subplots_adjust(left=.32, right=.94, top=.96, bottom=.28)
    ax.barh(range(3), values, height=.46, color=["#64748B", "#BE4F45", "#286FA3"], zorder=3)
    ax.axvline(0, color="#334155", linewidth=1.1, zorder=2)
    ax.set_yticks(range(3), labels, fontsize=16)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.set_xlim(-43, 67)
    ax.set_xticks([-25, 0, 25, 50], ["-25", "0", "25", "50"])
    ax.tick_params(axis="x", length=0, labelsize=14, pad=8)
    ax.set_ylim(2.55, -.55)
    ax.grid(axis="x", color="#E2E8F0", linewidth=.7, zorder=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for pos, value in enumerate(values):
        ax.text(value + (1.4 if value >= 0 else -1.4), pos,
                f"{value:+.2f}".rstrip("0").rstrip("."),
                ha="left" if value >= 0 else "right", va="center",
                fontsize=16, color="#172B3A")
    ax.set_xlabel("两组成功率之差 (百分点)" if chinese else "Difference in success rates (pp)",
                  fontsize=15, labelpad=12)
    fig.text(.5, .045,
             "100 个虚构项目；含截距的简单 OLS" if chinese else "100 constructed projects; OLS with an intercept",
             ha="center", fontsize=12, color="#64748B")
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--font", type=Path, help="可选：本地中文字体文件路径")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    true_label, success, label_a, label_b = make_data()
    rows = [evaluate(name, label, true_label, success)
            for name, label in [("true", true_label), ("A", label_a), ("B", label_b)]]
    check_teaching_claims(rows)
    data_rows = [{"project_id": i + 1, "true_social_benefit": int(true_label[i]),
                  "success": int(success[i]), "label_A": int(label_a[i]), "label_B": int(label_b[i])}
                 for i in range(len(success))]
    data_path = args.output_dir / "llm-annotation-toy-data.csv"
    result_path = args.output_dir / "llm-annotation-toy-results.csv"
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    figure_path = args.output_dir / f"llm-annotation-regression-comparison-{stamp}.png"
    write_csv(data_path, data_rows)
    write_csv(result_path, rows)
    plot_results(rows, figure_path, args.font)
    print("label   accuracy   precision   recall   F1        OLS coefficient")
    for row in rows:
        print(f'{row["label"]:<7} {row["accuracy"]:.2f}       {row["precision"]:.2f}        '
              f'{row["recall"]:.2f}     {row["f1"]:.6f}  {row["ols_coefficient"]:+.4f}')
    print("All checks passed: counts, confusion matrices, and group-mean/OLS identity.")
    for path in (data_path, result_path, figure_path):
        print(path)


if __name__ == "__main__":
    main()
