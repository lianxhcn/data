import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"

# True = 差异显著 (Y)，False = 不显著 (N)
sig = np.array([
    [0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0],
    [1, 1, 0, 0, 1],
    [0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0],
], dtype=bool)
labels = ["X1", "X2", "X3", "X4", "X5"]
n = len(labels)

fig, ax = plt.subplots(figsize=(9.8, 8.6), dpi=150)

for i in range(n):
    for j in range(n):
        if i == j:
            fc, tc, txt = "#E6E6E6", "#999999", "—"
        elif sig[i, j]:
            fc, tc, txt = DEEP_BLUE, "white", "Y"
        else:
            fc, tc, txt = GOLD, "white", "N"
        ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                   facecolor=fc, edgecolor="white", lw=1.4))
        ax.text(j, i, txt, ha="center", va="center", color=tc,
                fontsize=13, fontweight="bold")

ax.set_xlim(-0.5, n - 0.5); ax.set_ylim(n - 0.5, -0.5)
ax.set_xticks(range(n)); ax.set_yticks(range(n))
ax.set_xticklabels(labels, fontsize=11.5); ax.set_yticklabels(labels, fontsize=11.5)
ax.set_title("Y：解释力差异显著；N：差异不显著",
             fontsize=12, color=DEEP_BLUE, fontweight="bold", pad=12)

# 图例
from matplotlib.patches import Patch
handles = [
    Patch(facecolor=DEEP_BLUE, label="Y 显著"),
    Patch(facecolor=GOLD, label="N 不显著"),
    Patch(facecolor="#E6E6E6", label="对角线"),
]
ax.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
          fontsize=10.5, bbox_to_anchor=(0.5, -0.14))

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\02-四大探测器\code\p2_fig6_ecological.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
