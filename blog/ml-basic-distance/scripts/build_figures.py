"""为机器学习距离入门推文生成精确配图及可复核数值。

从项目根运行：python -X utf8 scripts/build_figures.py
图形使用固定教学数据；KNN、K-Means、SVM 与约束最优点均实际计算。
"""
from __future__ import annotations

import json
import hashlib
import logging
from pathlib import Path
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle, Polygon, Rectangle
from matplotlib.text import Text
import numpy as np
import scipy
from scipy.optimize import LinearConstraint, minimize
import sklearn
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figs" / "raw"
RESULTS = ROOT / "results"
LOGS = ROOT / "logs"
STAMP = "20261109-004303"
DPI = 150
PRIMARY_PT = 25.0
SECONDARY_PT = 23.5
TITLE_PT = 26.0
BLUE = "#2364AA"
OCHRE = "#BD661E"
GREEN = "#22755E"
DARK = "#202C39"
MUTED = "#5B6674"
GRID = "#DDE3E8"
PALE_BLUE = "#E9F0F8"
PALE_OCHRE = "#FAEEE4"
CHECKS: dict = {
    "description": "固定教学数据的数学与图片检查；不是实证结果",
    "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                 "matplotlib": matplotlib.__version__, "scipy": scipy.__version__,
                 "scikit-learn": sklearn.__version__},
    "figures": [], "checks": {},
}


def setup() -> None:
    """显式加载中文字体；只修改本进程，不修改系统配置。"""
    for folder in (OUT, RESULTS, LOGS):
        folder.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOGS / "figures.log", filemode="w", encoding="utf-8",
                        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    if not font_path.exists():
        raise FileNotFoundError(f"找不到中文字体：{font_path}")
    font_manager.fontManager.addfont(str(font_path))
    family = font_manager.FontProperties(fname=str(font_path)).get_name()
    plt.rcParams.update({
        "font.family": family, "font.size": PRIMARY_PT,
        "axes.labelsize": SECONDARY_PT,
        "xtick.labelsize": SECONDARY_PT, "ytick.labelsize": SECONDARY_PT,
        "axes.unicode_minus": False, "mathtext.fontset": "stix",
        "axes.edgecolor": MUTED, "axes.labelcolor": DARK,
        "text.color": DARK, "xtick.color": MUTED, "ytick.color": MUTED,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "svg.fonttype": "none",
        "lines.solid_capstyle": "round", "axes.linewidth": 1.1,
    })
    CHECKS["font"] = {"path": str(font_path), "family": family}
    CHECKS["font_policy"] = {
        "primary_pt": PRIMARY_PT, "secondary_pt": SECONDARY_PT,
        "title_pt": TITLE_PT, "export_dpi": DPI,
        "source_px_formula": "font_pt * export_dpi / 72",
        "display_px_formula": "source_px * display_width_px / source_width_px",
        "planned_display_widths_px": {"desktop": 425, "mobile": 336},
        "body_px": {"desktop": 17, "mobile": 16},
    }


def axes_style(ax, *, grid=False) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=4, width=1, pad=7)
    if grid:
        ax.grid(color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def coordinate_labels(ax) -> None:
    """把坐标符号置于轴端，避免与图下注释、居中的刻度混在一起。"""
    ax.xaxis.set_label_coords(1.025, -.025)
    ax.yaxis.set_label_coords(-.055, .985)


def font_layout(fig) -> list[dict]:
    """为实际绘制的文字设置语义层级，隐藏坐标轴上的伪可见文字不计入。"""
    fig.canvas.draw()
    ticks, axis_labels, excluded = set(), set(), set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            related = {axis.label, axis.get_offset_text()}
            labels = {text for tick in axis.get_major_ticks() + axis.get_minor_ticks()
                      for text in (tick.label1, tick.label2)}
            if ax.axison:
                ticks.update(labels)
                axis_labels.update(related)
            else:
                excluded.update(labels | related)
    labels = []
    for text in fig.findobj(Text):
        value = text.get_text().strip()
        if text in excluded or not text.get_visible() or not value:
            continue
        if value in {"Lasso", "Ridge"}:
            category, points = "panel_title", TITLE_PT
        elif (text in ticks or text in axis_labels or value.startswith(("A (", "B ("))
              or "\\Delta" in value or value == "45°"
              or value in {r"$x$", r"$2x$", r"$y$", r"$q$", r"$\hat{\beta}$",
                           r"$\beta_{1}$", r"$\beta_{2}$"}):
            category, points = "secondary_label", SECONDARY_PT
        else:
            category, points = "primary_label", PRIMARY_PT
        text.set_fontsize(points)
        text.set_gid(f"font-{category}-{len(labels) + 1:02d}")
        labels.append({"artist": text, "text": value, "category": category,
                       "font_pt": points, "source_px": points * DPI / 72})
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    scale = DPI / fig.dpi
    result = []
    for item in labels:
        text = item.pop("artist")
        bbox = text.get_window_extent(renderer)
        item["bbox_source_px"] = [float(v * scale) for v in
                                  (bbox.x0, bbox.y0, bbox.x1, bbox.y1)]
        item["display_px"] = {"desktop_425": item["source_px"] * 425 / 1200,
                              "mobile_336": item["source_px"] * 336 / 1200}
        result.append(item)
    return result


def save(fig, number: int, content: str, core: str) -> None:
    """保留同源 PNG/SVG，并检查画布尺寸、大小和文字越界。"""
    label_metrics = font_layout(fig)
    renderer = fig.canvas.get_renderer()
    outside = []
    for item in label_metrics:
        x0, y0, x1, y1 = item["bbox_source_px"]
        if (x0 < -1 or y0 < -1 or
                x1 > fig.get_figwidth() * DPI + 1 or
                y1 > fig.get_figheight() * DPI + 1):
            outside.append(item["text"])
    if outside:
        raise AssertionError(f"图 {number} 存在画布外文字：{outside}")
    name = f"ml-distance-fig{number:02d}-{content}-{STAMP}"
    png = OUT / f"{name}.png"
    svg = OUT / f"{name}.svg"
    fig.savefig(png, dpi=DPI)
    fig.savefig(svg)
    with Image.open(png) as im:
        width, height = im.size
    assert width == 1200, (number, width)
    assert height <= 1800, (number, height)
    assert png.stat().st_size < 1_000_000
    CHECKS["figures"].append({
        "number": number, "content": content, "core": core,
        "png": png.relative_to(ROOT).as_posix(),
        "svg": svg.relative_to(ROOT).as_posix(),
        "width": width, "height": height, "bytes": png.stat().st_size,
        "outside_canvas_text": outside,
        "font_points": sorted({item["font_pt"] for item in label_metrics}),
        "label_metrics": label_metrics,
        "typography": {
            "canvas_width_points": fig.get_figwidth() * 72,
            "texts": [{"text": item["text"], "font_pt": item["font_pt"],
                       "source_font_px": item["source_px"], "role": item["category"]}
                      for item in label_metrics],
        },
    })
    logging.info("生成图 %02d %s (%s × %s)", number, content, width, height)
    plt.close(fig)


def three_distances() -> None:
    a, b = np.array([1.0, 1.0]), np.array([5.0, 4.0])
    delta = b - a
    values = [float(np.linalg.norm(delta, ord=p)) for p in (1, 2, np.inf)]
    assert np.allclose(values, [7, 5, 4])
    CHECKS["checks"]["three_distances"] = {
        "A": a.tolist(), "B": b.tolist(), "delta": delta.tolist(),
        "l1": values[0], "l2": values[1], "linf": values[2],
        "chebyshev_rendering": "标注最大位移分量，不把任意曲线当作路径长度",
    }
    fig = plt.figure(figsize=(8, 7.8))
    ax = fig.add_axes([0.095, 0.23, 0.85, 0.72])
    axes_style(ax, grid=True)
    ax.set_aspect("equal")
    ax.set_xlim(0, 6.0); ax.set_ylim(0, 5.0)
    ax.set_xticks([0, 1, 3, 5]); ax.set_yticks([0, 1, 4])
    ax.set_xlabel(r"$x_{1}$", labelpad=5)
    ax.set_ylabel(r"$x_{2}$", rotation=0, labelpad=13)
    coordinate_labels(ax)
    # 欧氏路径为直线；曼哈顿路径仅由横向和纵向线段构成。
    ax.plot([a[0], b[0]], [a[1], b[1]], color=BLUE, lw=3.4, zorder=3)
    ax.plot([1, 5, 5], [1, 1, 4], color=OCHRE, lw=3.4, zorder=2)
    ax.scatter([1, 5], [1, 4], s=115, color=DARK, zorder=5)
    ax.text(0.57, 0.43, "A (1, 1)", fontsize=PRIMARY_PT)
    ax.text(4.60, 4.43, "B (5, 4)", fontsize=PRIMARY_PT)
    ax.text(2.1, 2.68, "欧氏 5", color=BLUE, fontsize=PRIMARY_PT,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 2})
    ax.text(2.40, 0.48, r"$\Delta x_{1}=4$", color=OCHRE, fontsize=PRIMARY_PT)
    ax.text(5.15, 2.30, r"$\Delta x_{2}=3$", color=OCHRE, fontsize=PRIMARY_PT,
            rotation=90, va="center")
    fig.text(0.5, 0.135, "曼哈顿：4 + 3 = 7", ha="center", color=OCHRE, fontsize=PRIMARY_PT)
    fig.text(0.5, 0.065, "切比雪夫：max(4, 3) = 4", ha="center", color=GREEN, fontsize=PRIMARY_PT)
    save(fig, 1, "three-distances", "同一差向量在三种度量下分别为 7、5、4。")


def unit_balls() -> None:
    fig = plt.figure(figsize=(8, 4.6))
    specs = [(1, BLUE, "菱形"), (2, OCHRE, "圆形"), (np.inf, GREEN, "正方形")]
    for idx, (p, color, shape) in enumerate(specs):
        ax = fig.add_axes([0.025 + idx * 0.33, 0.20, 0.29, 0.59])
        ax.set_aspect("equal"); ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35)
        ax.axis("off")
        ax.axhline(0, color=GRID, lw=1.2); ax.axvline(0, color=GRID, lw=1.2)
        if p == 1:
            ax.add_patch(Polygon([(1, 0), (0, 1), (-1, 0), (0, -1)],
                                 facecolor=color, alpha=0.12, edgecolor="none"))
            ax.plot([1, 0, -1, 0, 1], [0, 1, 0, -1, 0], color=color, lw=3)
        elif p == 2:
            ax.add_patch(Circle((0, 0), 1, facecolor=color, alpha=0.12, edgecolor="none"))
            t = np.linspace(0, 2 * np.pi, 361)
            ax.plot(np.cos(t), np.sin(t), color=color, lw=3)
        else:
            # L∞ 单位球直接画正方形，不以极大 p 的幂和近似。
            ax.add_patch(Rectangle((-1, -1), 2, 2, facecolor=color, alpha=0.12, edgecolor="none"))
            ax.plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], color=color, lw=3)
        label = r"$\|x\|_{\infty}=1$" if np.isinf(p) else rf"$\|x\|_{{{p}}}=1$"
        fig.text(0.17 + idx * 0.33, 0.89, label, color=color, fontsize=PRIMARY_PT, ha="center")
        fig.text(0.17 + idx * 0.33, 0.105, shape, color=color, fontsize=PRIMARY_PT, ha="center")
    CHECKS["checks"]["unit_balls"] = {
        "l1_vertices": [[1, 0], [0, 1], [-1, 0], [0, -1]],
        "linf_vertices": [[-1, -1], [1, -1], [1, 1], [-1, 1]],
        "interpretation": "彩色边界满足范数等于 1；浅色区域满足范数小于等于 1。",
    }
    save(fig, 2, "unit-balls", "不同范数的单位球边界是菱形、圆和正方形。")


def cosine() -> None:
    x = np.array([3.0, 0.0]); y = np.array([2.0, 2.0])
    cxy = float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))
    cx2x = float(x @ (2 * x) / (np.linalg.norm(x) * np.linalg.norm(2 * x)))
    assert np.isclose(cxy, 1 / np.sqrt(2)) and np.isclose(cx2x, 1)
    CHECKS["checks"]["cosine"] = {"x": x.tolist(), "y": y.tolist(),
        "cos_x_y": cxy, "cos_x_2x": cx2x, "theta_degrees": 45,
        "zero_vector": "余弦相似度对零向量未定义"}
    fig = plt.figure(figsize=(8, 5.5))
    ax = fig.add_axes([0.07, 0.29, 0.89, 0.67])
    ax.set_aspect("equal"); ax.set_xlim(-0.3, 6.8); ax.set_ylim(-0.55, 2.7)
    ax.axis("off")
    ax.plot([-.2, 6.5], [0, 0], color=GRID, lw=1)
    ax.plot([0, 0], [-.25, 2.5], color=GRID, lw=1)
    # 先画较长的 2x，再画较短的 x，二者从同一原点出发。
    arrow = {"arrowstyle": "-|>", "mutation_scale": 23, "lw": 2.8}
    ax.annotate("", xy=2 * x, xytext=(0, 0), arrowprops={**arrow, "color": BLUE, "alpha": .55})
    ax.annotate("", xy=x, xytext=(0, 0), arrowprops={**arrow, "color": BLUE, "lw": 4.0})
    ax.annotate("", xy=y, xytext=(0, 0), arrowprops={**arrow, "color": OCHRE})
    ax.scatter([0], [0], s=55, color=DARK, zorder=5)
    ax.text(2.90, -0.45, r"$x$", color=BLUE, fontsize=PRIMARY_PT)
    ax.text(5.90, -0.45, r"$2x$", color=BLUE, fontsize=PRIMARY_PT)
    ax.text(2.12, 2.06, r"$y$", color=OCHRE, fontsize=PRIMARY_PT)
    ax.add_patch(Arc((0, 0), 1.65, 1.65, theta1=0, theta2=45, color=MUTED, lw=1.5))
    ax.text(0.95, .25, "45°", fontsize=PRIMARY_PT)
    fig.text(.5, .18, r"$\cos(x,2x)=1$", color=BLUE, fontsize=PRIMARY_PT, ha="center")
    fig.text(.5, .075, r"$\cos(x,y)=1/\sqrt{2}\approx0.707$", color=OCHRE, fontsize=PRIMARY_PT, ha="center")
    save(fig, 3, "cosine", "正比例缩放保持方向，余弦相似度由夹角决定。")


def knn() -> None:
    points = np.array([[2.3, 2.2], [3.4, 3.2], [1.3, 3.8], [1., 1.],
                       [3.6, 2.4], [4.8, 3.6], [4.7, 1.], [3., .8]])
    labels = np.array(["A", "A", "A", "A", "B", "B", "B", "B"])
    query = np.array([3., 2.5])
    model = KNeighborsClassifier(n_neighbors=3, metric="euclidean").fit(points, labels)
    distances, indices = model.kneighbors(query[None, :])
    predicted = str(model.predict(query[None, :])[0])
    neighbors = labels[indices[0]].tolist()
    assert neighbors.count("A") == 2 and predicted == "A"
    CHECKS["checks"]["knn"] = {"points": points.tolist(), "labels": labels.tolist(),
        "query": query.tolist(), "k": 3, "neighbor_indices": indices[0].tolist(),
        "neighbor_distances": distances[0].tolist(), "neighbor_labels": neighbors,
        "prediction": predicted, "weights": "uniform"}
    fig = plt.figure(figsize=(8, 7.0))
    ax = fig.add_axes([.10, .17, .84, .72])
    axes_style(ax, grid=True)
    ax.set_aspect("equal"); ax.set_xlim(.4, 5.5); ax.set_ylim(.3, 4.5)
    ax.set_xticks([1, 3, 5]); ax.set_yticks([1, 3])
    ax.set_xlabel(r"$x_{1}$", labelpad=5); ax.set_ylabel(r"$x_{2}$", rotation=0, labelpad=10)
    coordinate_labels(ax)
    for group, color, marker in [("A", BLUE, "o"), ("B", OCHRE, "^")]:
        mask = labels == group
        ax.scatter(points[mask, 0], points[mask, 1], s=180, color=color, marker=marker,
                   edgecolor="white", linewidth=1.3, zorder=4, label=f"类别 {group}")
    for point in points[indices[0]]:
        ax.plot([query[0], point[0]], [query[1], point[1]], color=MUTED, lw=1.4,
                ls=(0, (3, 3)), zorder=2)
    ax.scatter(points[indices[0], 0], points[indices[0], 1], s=500,
               facecolor="none", edgecolor=DARK, linewidth=1.4, zorder=5)
    ax.scatter(*query, s=340, color=DARK, marker="*", zorder=6)
    ax.annotate(r"$q$", xy=query, xytext=(2.65, 2.78), fontsize=PRIMARY_PT)
    fig.legend(*ax.get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.5, .99),
               ncol=2, frameon=False, fontsize=PRIMARY_PT, handletextpad=.35, columnspacing=1.5)
    fig.text(.5, .055, "k = 3：A、A、B → 预测为 A", ha="center", fontsize=PRIMARY_PT)
    save(fig, 4, "knn", "实际找出最近的三个样本，并以多数票进行分类。")


def kmeans() -> None:
    points = np.array([[.8, 1.2], [1.2, .8], [1.5, 1.6], [1.8, 1.0],
                       [3.8, 3.8], [4.3, 3.3], [4.6, 4.2], [5.0, 3.7]])
    model = KMeans(n_clusters=2, n_init=20, random_state=2026).fit(points)
    # 仅为配色与命名排序，聚类结果仍来自拟合。
    order = np.argsort(model.cluster_centers_[:, 0])
    centers = model.cluster_centers_[order]
    labels = np.array([int(np.flatnonzero(order == v)[0]) for v in model.labels_])
    direct_inertia = float(np.sum((points - centers[labels]) ** 2))
    for c in (0, 1):
        assert np.allclose(centers[c], points[labels == c].mean(axis=0))
    assert np.isclose(direct_inertia, model.inertia_)
    CHECKS["checks"]["kmeans"] = {"points": points.tolist(), "k": 2,
        "labels": labels.tolist(), "centers": centers.tolist(), "inertia": direct_inertia,
        "centers_equal_cluster_means": True, "objective": "sum of squared Euclidean distances"}
    fig = plt.figure(figsize=(8, 6.8))
    ax = fig.add_axes([.10, .16, .84, .74])
    axes_style(ax, grid=True)
    ax.set_aspect("equal"); ax.set_xlim(0, 5.7); ax.set_ylim(.1, 4.9)
    ax.set_xticks([0, 2, 4]); ax.set_yticks([1, 3])
    ax.set_xlabel(r"$x_{1}$", labelpad=5); ax.set_ylabel(r"$x_{2}$", rotation=0, labelpad=10)
    coordinate_labels(ax)
    for c, color in [(0, BLUE), (1, OCHRE)]:
        for point in points[labels == c]:
            ax.plot([point[0], centers[c, 0]], [point[1], centers[c, 1]],
                    color=color, lw=1.5, alpha=.55, zorder=2)
        ax.scatter(points[labels == c, 0], points[labels == c, 1], color=color, s=160,
                   edgecolor="white", lw=1, zorder=3, label=f"簇 {c + 1}")
        ax.scatter(*centers[c], marker="*", s=520, color=color, edgecolor=DARK, lw=1, zorder=5)
    ax.annotate(r"$\mu_{1}$", xy=centers[0], xytext=(2.00, 1.8), fontsize=PRIMARY_PT, color=BLUE,
                arrowprops={"arrowstyle": "-", "color": BLUE, "lw": 1.1})
    ax.annotate(r"$\mu_{2}$", xy=centers[1], xytext=(3.2, 4.4), fontsize=PRIMARY_PT, color=OCHRE,
                arrowprops={"arrowstyle": "-", "color": OCHRE, "lw": 1.1})
    fig.legend(*ax.get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.5, .99),
               ncol=2, frameon=False, fontsize=PRIMARY_PT, handletextpad=.35)
    fig.text(.5, .045, "星号为质心：各簇样本的均值", ha="center", fontsize=PRIMARY_PT)
    save(fig, 5, "kmeans", "K-Means 使用到簇质心的欧氏距离平方和。")


def svm_margin() -> None:
    points = np.array([[0, 2], [1, 1], [2, 0], [-.5, .3],
                       [1, 3], [2, 2], [3, 1], [3.3, 3.2]], dtype=float)
    labels = np.array([-1, -1, -1, -1, 1, 1, 1, 1])
    model = SVC(kernel="linear", C=1e6, tol=1e-10).fit(points, labels)
    w = model.coef_[0]; intercept = float(model.intercept_[0])
    norm_w = float(np.linalg.norm(w))
    # 采用确在间隔线上的样本，按点到直线公式计算垂足。
    selected = np.array([2., 2.])
    foot = selected - ((w @ selected + intercept) / (w @ w)) * w
    tangent = np.array([w[1], -w[0]]) / norm_w
    normal = w / norm_w
    orthogonality = float((selected - foot) @ tangent)
    canonical_margins = labels * (points @ w + intercept)
    assert np.min(canonical_margins) >= 1 - 1e-7
    assert np.isclose(w @ foot + intercept, 0, atol=1e-9)
    assert abs(orthogonality) < 1e-9
    assert np.isclose(np.linalg.norm(selected - foot), 1 / norm_w, atol=1e-7)
    CHECKS["checks"]["svm"] = {"points": points.tolist(), "labels": labels.tolist(),
        "w": w.tolist(), "intercept": intercept, "support_indices": model.support_.tolist(),
        "canonical_margins": canonical_margins.tolist(), "selected_point": selected.tolist(),
        "foot": foot.tolist(), "foot_boundary_residual": float(w @ foot + intercept),
        "normal_tangent_dot": orthogonality, "one_sided_margin": 1 / norm_w,
        "full_margin": 2 / norm_w, "training_accuracy": float(model.score(points, labels)),
        "model": "linear SVC with C=1e6 on separable teaching data"}
    fig = plt.figure(figsize=(8, 7.8))
    ax = fig.add_axes([.105, .17, .83, .72])
    axes_style(ax)
    ax.set_aspect("equal"); ax.set_xlim(-.9, 4.25); ax.set_ylim(-.75, 4.4)
    ax.set_xticks([0, 2, 4]); ax.set_yticks([0, 2, 4])
    ax.set_xlabel(r"$x_{1}$", labelpad=5); ax.set_ylabel(r"$x_{2}$", rotation=0, labelpad=9)
    coordinate_labels(ax)
    xx = np.linspace(-1, 4.5, 400)
    lower = (-1 - intercept - w[0] * xx) / w[1]
    upper = (1 - intercept - w[0] * xx) / w[1]
    ax.fill_between(xx, lower, upper, color=PALE_BLUE, zorder=0)
    ax.plot(xx, (-intercept - w[0] * xx) / w[1], color=DARK, lw=2.3, zorder=2)
    ax.plot(xx, lower, color=MUTED, lw=1.5, ls=(0, (5, 4)), zorder=1)
    ax.plot(xx, upper, color=MUTED, lw=1.5, ls=(0, (5, 4)), zorder=1)
    for group, color, marker, name in [(-1, BLUE, "o", "类别 −1"), (1, OCHRE, "^", "类别 +1")]:
        mask = labels == group
        ax.scatter(points[mask, 0], points[mask, 1], color=color, marker=marker, s=180,
                   edgecolor="white", linewidth=1.2, zorder=4, label=name)
    ax.annotate("", xy=selected, xytext=foot,
                arrowprops={"arrowstyle": "<->", "color": GREEN, "lw": 2.4,
                            "shrinkA": 2, "shrinkB": 4}, zorder=7)
    # 直角标记沿切向与法向构造，不能用水平/竖直线随意拼接。
    size = .17
    right_angle = np.array([foot + size * tangent,
                            foot + size * (tangent + normal), foot + size * normal])
    ax.plot(right_angle[:, 0], right_angle[:, 1], color=GREEN, lw=1.5, zorder=7)
    ax.scatter(*foot, s=45, facecolor="white", edgecolor=GREEN, linewidth=1.5, zorder=8)
    ax.annotate("垂直距离", xy=(selected + foot) / 2, xytext=(2.73, 2.12),
                fontsize=PRIMARY_PT, color=GREEN,
                arrowprops={"arrowstyle": "-", "color": GREEN, "lw": 1.2})
    ax.annotate("决策边界", xy=(.35, (-intercept - w[0] * .35) / w[1]),
                xytext=(-.63, 3.62), fontsize=PRIMARY_PT, color=DARK,
                arrowprops={"arrowstyle": "-", "color": DARK, "lw": 1.1})
    fig.legend(*ax.get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.5, .99),
               ncol=2, frameon=False, fontsize=PRIMARY_PT, handletextpad=.35)
    fig.text(.5, .065, r"$d=1/\|w\|_{2}=1/\sqrt{2}$", ha="center", fontsize=PRIMARY_PT, color=GREEN)
    save(fig, 6, "svm-margin", "SVM 几何间隔按垂直于决策边界的最短距离计算。")


def residual_loss() -> None:
    residual = np.linspace(-3, 3, 601)
    fig = plt.figure(figsize=(8, 6.7))
    ax = fig.add_axes([.13, .16, .81, .78])
    axes_style(ax, grid=True)
    ax.plot(residual, np.abs(residual), color=BLUE, lw=3.1, label=r"绝对损失 $|e|$")
    ax.plot(residual, residual ** 2, color=OCHRE, lw=3.1, label=r"平方损失 $e^{2}$")
    ax.set_xlim(-3.2, 3.2); ax.set_ylim(-.3, 9.6)
    ax.set_xticks([-3, 0, 3]); ax.set_yticks([0, 3, 6, 9])
    ax.set_xlabel(r"残差 $e$", labelpad=9); ax.set_ylabel("损失", rotation=0, labelpad=18)
    ax.plot([2, 2], [0, 4], color=MUTED, lw=1.1, ls=(0, (3, 3)))
    ax.scatter([2], [2], color=BLUE, s=85, zorder=5)
    ax.scatter([2], [4], color=OCHRE, s=85, zorder=5)
    ax.text(2.16, 1.48, "2", color=BLUE, fontsize=PRIMARY_PT)
    ax.text(1.68, 4.30, "4", color=OCHRE, fontsize=PRIMARY_PT)
    ax.legend(loc="upper center", frameon=False, fontsize=PRIMARY_PT, handlelength=1.7)
    CHECKS["checks"]["residual_loss"] = {"example_residual": 2,
        "absolute_loss": 2, "squared_loss": 4,
        "interpretation": "图为单个残差的损失；MSE/MAE 是样本平均。"}
    save(fig, 7, "residual-loss", "同一个大残差在平方损失下受到更重惩罚。")


def regularization() -> None:
    center = np.array([2., .5])
    objective = lambda v: float(np.sum((v - center) ** 2))
    gradient = lambda v: 2 * (v - center)
    # 二维 L1 球用四条线性不等式精确表示，避免绝对值在零点的数值歧义。
    a = np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]], dtype=float)
    sol1 = minimize(objective, [.5, .1], jac=gradient, method="SLSQP",
                    constraints=[LinearConstraint(a, -np.inf, np.ones(4))],
                    options={"ftol": 1e-13, "maxiter": 1000})
    sol2 = minimize(objective, [.5, .1], jac=gradient, method="SLSQP",
                    constraints=[{"type": "ineq", "fun": lambda v: 1 - v @ v,
                                  "jac": lambda v: -2 * v}],
                    options={"ftol": 1e-13, "maxiter": 1000})
    expected1 = np.array([1., 0.]); expected2 = center / np.linalg.norm(center)
    assert sol1.success and sol2.success, (sol1.message, sol2.message)
    assert np.allclose(sol1.x, expected1, atol=1e-7)
    assert np.allclose(sol2.x, expected2, atol=1e-7)
    assert np.linalg.norm(sol1.x, 1) <= 1 + 1e-8
    assert np.linalg.norm(sol2.x) <= 1 + 1e-8
    CHECKS["checks"]["regularization"] = {"loss": "(beta1-2)^2+(beta2-0.5)^2",
        "unconstrained_optimum": center.tolist(), "constraint_radius": 1,
        "lasso": {"solution": sol1.x.tolist(), "analytic_solution": expected1.tolist(),
                  "loss_at_solution": objective(sol1.x), "solver_success": bool(sol1.success)},
        "ridge": {"solution": sol2.x.tolist(), "analytic_solution": expected2.tolist(),
                  "loss_at_solution": objective(sol2.x), "solver_success": bool(sol2.success)},
        "interpretation": "本例展示 L1 的坐标轴顶点可能产生零系数；并非所有 Lasso 解都稀疏。"}
    fig = plt.figure(figsize=(8, 6.0))
    t = np.linspace(0, 2 * np.pi, 600)
    for idx, (label, color, optimum) in enumerate([
            ("Lasso", BLUE, expected1), ("Ridge", OCHRE, expected2)]):
        ax = fig.add_axes([.055 + idx * .495, .23, .43, .65])
        ax.set_aspect("equal"); ax.set_xlim(-1.25, 2.55); ax.set_ylim(-1.4, 1.8)
        ax.axis("off")
        ax.axhline(0, color=GRID, lw=1); ax.axvline(0, color=GRID, lw=1)
        # 每组等高线的第一条都严格经过实际最优点。
        radius = np.linalg.norm(optimum - center)
        for j, r in enumerate([radius, radius + .38, radius + .76]):
            ax.plot(center[0] + r * np.cos(t), center[1] + r * np.sin(t),
                    color=MUTED if j == 0 else GRID, lw=1.7 if j == 0 else 1.2, zorder=1)
        if idx == 0:
            vertices = np.array([[1, 0], [0, 1], [-1, 0], [0, -1], [1, 0]])
            ax.fill(vertices[:, 0], vertices[:, 1], color=color, alpha=.12, zorder=2)
            ax.plot(vertices[:, 0], vertices[:, 1], color=color, lw=2.7, zorder=3)
        else:
            ax.fill(np.cos(t), np.sin(t), color=color, alpha=.12, zorder=2)
            ax.plot(np.cos(t), np.sin(t), color=color, lw=2.7, zorder=3)
        ax.scatter(*center, marker="*", s=210, color=DARK, zorder=6)
        ax.scatter(*optimum, s=115, color=color, edgecolor="white", linewidth=1.2, zorder=7)
        ax.text(1.95, .83, r"$\hat{\beta}$", fontsize=PRIMARY_PT, ha="center")
        ax.text(2.34, -.33, r"$\beta_{1}$", fontsize=PRIMARY_PT, ha="center")
        ax.text(-.25, 1.53, r"$\beta_{2}$", fontsize=PRIMARY_PT, ha="center")
        fig.text(.26 + idx * .495, .93, label, color=color, fontsize=PRIMARY_PT, ha="center")
    fig.text(.26, .115, "一个系数为 0", color=BLUE, fontsize=PRIMARY_PT, ha="center")
    fig.text(.755, .115, "两个系数均非 0", color=OCHRE, fontsize=PRIMARY_PT, ha="center")
    save(fig, 8, "regularization", "同一损失函数下，L1 与 L2 约束的实际最优点不同。")


def main() -> None:
    setup()
    baseline_path = RESULTS / f"figure-font-baseline-{STAMP}.json"
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    else:
        old = json.loads((RESULTS / "figure-checks.json").read_text(encoding="utf-8"))
        baseline = {"source": "复制到本暂存目录的原 figure-checks.json",
                    "checks": old["checks"]}
        baseline_path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for builder in [three_distances, unit_balls, cosine, knn, kmeans,
                        svm_margin, residual_loss, regularization]:
            builder()
        CHECKS["warnings"] = [str(w.message) for w in caught]
    assert not CHECKS["warnings"], CHECKS["warnings"]
    canonical = lambda data: json.dumps(data, ensure_ascii=False, sort_keys=True,
                                        separators=(",", ":")).encode("utf-8")
    old_digest = hashlib.sha256(canonical(baseline["checks"])).hexdigest()
    new_digest = hashlib.sha256(canonical(CHECKS["checks"])).hexdigest()
    assert old_digest == new_digest, "数学数据与基线发生变化"
    CHECKS["numerical_baseline_comparison"] = {
        "status": "identical", "baseline_sha256": old_digest, "new_sha256": new_digest,
        "scope": "checks 全部对象，包括教学数据、拟合结果、几何检验与解释字段",
        "baseline": baseline_path.relative_to(ROOT).as_posix(),
    }
    # 仅供验收的拼版：每幅图都按手机正文宽度 360 px 显示。
    thumbnails = []
    for item in CHECKS["figures"]:
        with Image.open(ROOT / item["png"]) as im:
            height = round(im.height * 360 / im.width)
            thumbnails.append(im.convert("RGB").resize((360, height), Image.Resampling.LANCZOS))
    row_heights = [max(thumbnails[i].height, thumbnails[i + 1].height) + 35
                   for i in range(0, 8, 2)]
    sheet = Image.new("RGB", (760, sum(row_heights) + 20), "#F1F4F6")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 19)
    y = 12
    for row in range(4):
        for col in range(2):
            idx = row * 2 + col
            x = 10 + col * 380
            draw.text((x, y), f"图 {idx + 1:02d} · 360 px", font=font, fill=DARK)
            sheet.paste(thumbnails[idx], (x, y + 29))
        y += row_heights[row]
    qa_path = OUT / f"qa-mobile360-{STAMP}.png"
    sheet.save(qa_path)
    CHECKS["mobile_preview"] = qa_path.relative_to(ROOT).as_posix()
    CHECKS["status"] = "passed"
    (RESULTS / "figure-checks.json").write_text(
        json.dumps(CHECKS, ensure_ascii=False, indent=2), encoding="utf-8")
    font_metadata = {"policy": CHECKS["font_policy"],
                     "figures": [{"number": item["number"], "png": item["png"],
                                  "typography": item["typography"]}
                                 for item in CHECKS["figures"]]}
    (RESULTS / f"figure-typography-{STAMP}.json").write_text(
        json.dumps(font_metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info("数学与文件检查通过；警告 %s 条", len(CHECKS["warnings"]))
    print(json.dumps({"status": CHECKS["status"], "figures": len(CHECKS["figures"]),
                      "warnings": CHECKS["warnings"],
                      "checks": CHECKS["checks"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
