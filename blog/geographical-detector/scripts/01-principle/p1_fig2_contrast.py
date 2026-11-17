import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_GOLD = "#F0E0B0"
LIGHT_BLUE = "#B8CCDC"

# 四个离散层级的颜色，由浅到深
colors = [LIGHT_GOLD, GOLD, LIGHT_BLUE, DEEP_BLUE]
cmap = ListedColormap(colors)

rng = np.random.default_rng(7)
n = 12

# 左图：取值随机混杂
left = rng.integers(0, 4, size=(n, n))

# 右图：按区域成块，层内取值一致
right = np.zeros((n, n), dtype=int)
right[0:6, 0:6] = 3
right[0:6, 6:12] = 2
right[6:12, 0:6] = 1
right[6:12, 6:12] = 0

fig, axes = plt.subplots(1, 2, figsize=(12, 6.4), dpi=150)

for ax, data, title, sub in [
    (axes[0], left, "无清晰分层", "不同取值在空间上随机混杂，层内方差大"),
    (axes[1], right, "存在空间分层异质性", "层内取值趋同，层与层之间差异明显"),
]:
    ax.imshow(data, cmap=cmap, vmin=0, vmax=3)
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    ax.set_title(title, fontsize=14, fontweight="bold", color=DEEP_BLUE, pad=12)
    ax.text(n / 2 - 0.5, n + 1.1, sub, ha="center", va="top",
            fontsize=10.5, color="#1A1A1A")

# 图例
from matplotlib.patches import Patch
handles = [Patch(facecolor=colors[i], edgecolor="white", label=f"层级 {i+1}")
           for i in range(4)]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
           fontsize=10.5, bbox_to_anchor=(0.5, -0.02))

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\01-原理篇\code\p1_fig2_contrast.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
