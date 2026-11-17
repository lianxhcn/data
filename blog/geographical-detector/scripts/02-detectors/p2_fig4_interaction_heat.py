import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_GOLD = "#F0E0B0"

# 金 -> 深蓝 自定义渐变
cmap = LinearSegmentedColormap.from_list(
    "inter", [LIGHT_GOLD, "#C9A24B", "#5E7FA0", DEEP_BLUE], N=256)

M = np.array([
    [0.10, 0.28, 0.36, 0.52, 0.66],
    [0.28, 0.20, 0.44, 0.58, 0.72],
    [0.36, 0.44, 0.30, 0.66, 0.80],
    [0.52, 0.58, 0.66, 0.45, 0.88],
    [0.66, 0.72, 0.80, 0.88, 0.60],
])
labels = ["X1", "X2", "X3", "X4", "X5"]
n = len(labels)

fig, ax = plt.subplots(figsize=(9.8, 8.6), dpi=150)
im = ax.imshow(M, cmap=cmap, vmin=0.05, vmax=0.9)

# 对角线覆盖中性浅灰
for i in range(n):
    ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1,
                               facecolor="#E6E6E6", edgecolor="white", lw=1))

# 文字
for i in range(n):
    for j in range(n):
        if i == j:
            tc = "#1A1A1A"
        else:
            tc = "white" if M[i, j] > 0.55 else "#1A1A1A"
        ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center",
                color=tc, fontsize=11, fontweight="bold")

ax.set_xticks(range(n)); ax.set_yticks(range(n))
ax.set_xticklabels(labels, fontsize=11.5); ax.set_yticklabels(labels, fontsize=11.5)
ax.set_title("对角线为单因子 q 值，非对角线为交互 q 值",
             fontsize=12, color=DEEP_BLUE, fontweight="bold", pad=12)

# 边框网格
for i in range(n + 1):
    ax.axhline(i - 0.5, color="white", lw=1.2)
    ax.axvline(i - 0.5, color="white", lw=1.2)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("q 值", fontsize=10.5)
cbar.ax.tick_params(labelsize=9.5)

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\02-四大探测器\code\p2_fig4_interaction_heat.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
