import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
import numpy as np
from scipy.ndimage import gaussian_filter

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_GOLD = "#F0E0B0"
LIGHT_BLUE = "#B8CCDC"

# 干旱(浅金) -> 金 -> 浅蓝 -> 湿润(深蓝)
cmap = LinearSegmentedColormap.from_list(
    "precip", [LIGHT_GOLD, GOLD, LIGHT_BLUE, DEEP_BLUE], N=256)

rng = np.random.default_rng(3)
rows, cols = 14, 16
ii, jj = np.meshgrid(np.arange(rows), np.arange(cols), indexing="ij")
# 西北 (左上) 低、东南 (右下) 高的梯度
grad = 1 - (0.45 * (ii / (rows - 1)) + 0.55 * (1 - jj / (cols - 1)))
noise = gaussian_filter(rng.normal(0, 1, size=(rows, cols)), sigma=1.4)
precip = 120 + grad * 1500 + noise * 70
precip = np.clip(precip, 80, 1650)

fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)
im = ax.imshow(precip, cmap=cmap, vmin=100, vmax=1600)

# 等降水量线 200/400/800
cs = ax.contour(precip, levels=[200, 400, 800], colors="white",
                linewidths=2, alpha=0.95)
ax.clabel(cs, fmt=lambda v: f"{int(v)} mm", fontsize=11, inline=True)

# 方位标注
ax.annotate("西北内陆\n(少雨)", xy=(0.5, 0.5), xytext=(0.2, 2.2),
            fontsize=12, color="#1A1A1A", fontweight="bold", ha="center")
ax.annotate("东南沿海\n(多雨)", xy=(cols - 1, rows - 1),
            xytext=(cols - 2.2, rows - 2.6),
            fontsize=12, color="white", fontweight="bold", ha="center")

ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)

# 四层分区图例
handles = [
    Patch(facecolor=LIGHT_GOLD, edgecolor="white", label="干旱区 (<200 mm)"),
    Patch(facecolor=GOLD, edgecolor="white", label="半干旱区 (200—400 mm)"),
    Patch(facecolor=LIGHT_BLUE, edgecolor="white", label="半湿润区 (400—800 mm)"),
    Patch(facecolor=DEEP_BLUE, edgecolor="white", label="湿润区 (>800 mm)"),
]
ax.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
          fontsize=10, bbox_to_anchor=(0.5, -0.16))

cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cbar.set_label("年降水量 (mm)", fontsize=10.5)
cbar.ax.tick_params(labelsize=9.5)

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\01-原理篇\code\p1_fig3_precip.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
