import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_GOLD = "#F0E0B0"

fig, ax = plt.subplots(figsize=(14, 6.6), dpi=150)
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

nodes = [
    ("1", "因子探测器", "谁在起作用", "q 值、F 检验", "各因子 q 值与显著性"),
    ("2", "交互探测器", "因子如何共同作用", "叠加 q 值", "五种交互关系"),
    ("3", "风险探测器", "哪里风险更高", "t 统计量", "层对差异矩阵"),
    ("4", "生态探测器", "解释力有无差别", "F 统计量", "因子差异矩阵"),
]

w, h = 20, 46
gap = 4
x = 4
centers = []
for num, name, q, stat, out in nodes:
    # 卡片
    p = FancyBboxPatch((x, 32), w, h, boxstyle="round,pad=0,rounding_size=2",
                       linewidth=1.8, edgecolor=DEEP_BLUE, facecolor="white")
    ax.add_patch(p)
    # 顶部序号圆
    circ = plt.Circle((x + 3.2, 74), 2.4, color=GOLD, zorder=5)
    ax.add_patch(circ)
    ax.text(x + 3.2, 74, num, ha="center", va="center", color="white",
            fontsize=12, fontweight="bold", zorder=6)
    # 标题条
    head = FancyBboxPatch((x, 66), w, 8,
                          boxstyle="round,pad=0,rounding_size=2",
                          linewidth=0, facecolor=DEEP_BLUE)
    ax.add_patch(head)
    ax.text(x + w / 2 + 1.5, 70, name, ha="center", va="center",
            color="white", fontsize=12.5, fontweight="bold")
    # 内容
    ax.text(x + w / 2, 58, q, ha="center", va="center", fontsize=10.5,
            color="#1A1A1A", fontweight="bold")
    ax.text(x + w / 2, 49, f"统计量：{stat}", ha="center", va="center",
            fontsize=9.8, color=GOLD)
    ax.text(x + w / 2, 39, out, ha="center", va="center", fontsize=9.8,
            color=DEEP_BLUE, linespacing=1.4)
    centers.append(x + w)
    x += w + gap

# 箭头
for i in range(3):
    a = FancyArrowPatch((centers[i] + 0.6, 55),
                        (centers[i] + gap - 0.6, 55),
                        arrowstyle="-|>", mutation_scale=22,
                        color=GOLD, lw=2.2)
    ax.add_patch(a)

# 底部说明
ax.text(50, 20, "标准分析顺序：从整体格局到因子组合，再到具体区域与因子横向比较",
        ha="center", va="center", fontsize=12, color=DEEP_BLUE,
        fontweight="bold")
ax.text(50, 11, "四个探测器共享同一空间分层与方差比较逻辑，配合使用而非彼此替代",
        ha="center", va="center", fontsize=10.5, color="#1A1A1A")

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\02-四大探测器\code\p2_fig1_chain.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
