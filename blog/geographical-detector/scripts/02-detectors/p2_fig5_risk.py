import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_BLUE = "#B8CCDC"

means = np.array([2.5, 4.8, 5.3, 7.6])
se = np.array([0.35, 0.40, 0.38, 0.42])
x = np.arange(1, 5)

fig, ax = plt.subplots(figsize=(10.5, 7), dpi=150)

# 误差棒与均值点
ax.errorbar(x, means, yerr=se, fmt="o", color=DEEP_BLUE, ecolor=LIGHT_BLUE,
            elinewidth=2.4, capsize=8, markersize=13,
            markerfacecolor=DEEP_BLUE, markeredgecolor="white", markeredgewidth=1.4,
            zorder=4)
for xi, m in zip(x, means):
    ax.text(xi, m - 0.85, f"{m:.1f}", ha="center", fontsize=11,
            color=DEEP_BLUE, fontweight="bold")

# 相邻层对显著性括号
pairs = [(1, 2, "显著", DEEP_BLUE), (2, 3, "不显著", GOLD), (3, 4, "显著", DEEP_BLUE)]
top = means.max() + se.max()
for i, (a, b, label, c) in enumerate(pairs):
    yb = top + 0.5 + i * 0.9
    ax.plot([a, a, b, b], [yb - 0.25, yb, yb, yb - 0.25], color=c, lw=1.6)
    ax.text((a + b) / 2, yb + 0.18, label, ha="center", va="bottom",
            fontsize=10.5, color=c, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(["层 1", "层 2", "层 3", "层 4"], fontsize=12)
ax.set_ylabel("被解释变量分层均值", fontsize=11.5)
ax.set_ylim(0, top + 3.6)
ax.set_title("均值数值高低需经 t 检验确认，接近的分层可能差异不显著",
             fontsize=12, color=DEEP_BLUE, fontweight="bold", pad=12)
ax.grid(axis="y", color="#E6E6E6", lw=1)
ax.set_axisbelow(True)

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\02-四大探测器\code\p2_fig5_risk.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
