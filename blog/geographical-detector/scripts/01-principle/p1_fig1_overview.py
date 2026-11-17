import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_GOLD = "#F0E0B0"
LIGHT_BLUE = "#B8CCDC"

fig, ax = plt.subplots(figsize=(13.5, 8), dpi=150)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, fc, ec, lw=1.6, rounded=0.02):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={rounded*100}",
        linewidth=lw, edgecolor=ec, facecolor=fc, mutation_aspect=1,
    )
    ax.add_patch(p)
    return p


# 顶部主框
box(30, 82, 40, 11, DEEP_BLUE, DEEP_BLUE)
ax.text(50, 89.5, "地理探测器", ha="center", va="center",
        color="white", fontsize=17, fontweight="bold")
ax.text(50, 84.3, "Geographical Detector", ha="center", va="center",
        color=LIGHT_GOLD, fontsize=11)

# 主干与分支连线
ax.plot([50, 50], [70, 82], color=GOLD, lw=2)
xs = [12.5, 37.5, 62.5, 87.5]
ax.plot([xs[0], xs[-1]], [70, 70], color=GOLD, lw=2)
for x in xs:
    ax.plot([x, x], [60, 70], color=GOLD, lw=2)

# 四个探测器方框
cards = [
    ("因子探测器", "Factor Detector",
     "因子 X 对 Y 的\n空间解释力有多大", "输出：q 值与显著性"),
    ("交互探测器", "Interaction Detector",
     "两因子叠加后\n解释力增强还是减弱", "输出：五种交互关系"),
    ("风险探测器", "Risk Detector",
     "不同分层的\n均值是否存在差异", "输出：层对 t 检验矩阵"),
    ("生态探测器", "Ecological Detector",
     "两因子解释力\n是否有显著差异", "输出：因子 F 检验矩阵"),
]
for x, (name, en, q, out) in zip(xs, cards):
    box(x - 11, 28, 22, 32, "white", DEEP_BLUE, lw=1.8)
    # 标题色条
    box(x - 11, 53, 22, 7, DEEP_BLUE, DEEP_BLUE)
    ax.text(x, 56.5, name, ha="center", va="center",
            color="white", fontsize=12.5, fontweight="bold")
    ax.text(x, 49.5, en, ha="center", va="center",
            color=GOLD, fontsize=9.5)
    ax.text(x, 42, q, ha="center", va="center",
            color="#1A1A1A", fontsize=10.5, linespacing=1.5)
    ax.text(x, 32.5, out, ha="center", va="center",
            color=DEEP_BLUE, fontsize=9.8, fontweight="bold")

# 底部共同逻辑说明
box(18, 10, 64, 9, LIGHT_GOLD, GOLD, lw=1.4)
ax.text(50, 14.5, "共同逻辑：以空间分层为输入，通过比较层内方差与整体方差完成推断",
        ha="center", va="center", color=DEEP_BLUE, fontsize=11.5, fontweight="bold")

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\01-原理篇\code\p1_fig1_overview.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
