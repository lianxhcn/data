import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_BLUE = "#B8CCDC"

rows = [
    ("X1", "0.62", "0.000", "***"),
    ("X2", "0.48", "0.002", "**"),
    ("X3", "0.31", "0.018", "*"),
    ("X4", "0.12", "0.094", "ns"),
    ("X5", "0.05", "0.312", "ns"),
]
headers = ["因子", "q 值", "p 值", "显著性"]

fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=150)
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

col_x = [0.5, 3.0, 5.2, 7.4]
col_w = [2.5, 2.2, 2.2, 2.1]
top = 8.6
head_h = 1.1
row_h = 1.15

# 表头
ax.add_patch(Rectangle((0.5, top - head_h), 9, head_h,
                       facecolor=DEEP_BLUE, edgecolor=DEEP_BLUE))
for cx, htext in zip(col_x, headers):
    ax.text(cx, top - head_h / 2, htext, ha="left", va="center",
            color="white", fontsize=12, fontweight="bold")

# 数据行
for i, r in enumerate(rows):
    y = top - head_h - (i + 1) * row_h
    fc = "white" if i % 2 == 0 else "#EAF1F7"
    ax.add_patch(Rectangle((0.5, y), 9, row_h, facecolor=fc, edgecolor=LIGHT_BLUE,
                           linewidth=0.8))
    sig_color = DEEP_BLUE if r[3] != "ns" else GOLD
    vals = list(r)
    for cx, v, j in zip(col_x, vals, range(4)):
        bold = (j == 0) or (j == 3)
        ax.text(cx, y + row_h / 2, v, ha="left", va="center",
                fontsize=11.5, color=sig_color if j == 3 else "#1A1A1A",
                fontweight="bold" if bold else "normal")

# 注释
ax.text(0.5, 1.5, "注：*、**、*** 分别表示在 10%、5%、1% 水平显著；ns 表示不显著",
        ha="left", va="center", fontsize=10, color="#555555")
ax.text(0.5, 0.5, "q 值与 p 值需同时报告，不能只给其中一个",
        ha="left", va="center", fontsize=10, color=DEEP_BLUE, fontweight="bold")

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\02-四大探测器\code\p2_fig2_factor_matrix.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
