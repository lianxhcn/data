import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_GOLD = "#F0E0B0"
LIGHT_BLUE = "#B8CCDC"

rng = np.random.default_rng(11)
means = [3, 8, 13]
n_each = 16
groups = []
for m in means:
    groups.append(rng.normal(m, 0.75, size=n_each))
allv = np.concatenate(groups)
grand = allv.mean()

fig = plt.figure(figsize=(12.5, 7), dpi=150)
gs = fig.add_gridspec(1, 2, width_ratios=[2.4, 1], wspace=0.18)
ax = fig.add_subplot(gs[0, 0])
axb = fig.add_subplot(gs[0, 1])

# 左：分层散点与层均值
for i, (m, g) in enumerate(zip(means, groups), start=1):
    xj = rng.uniform(-0.22, 0.22, size=len(g)) + i
    ax.scatter(xj, g, s=42, color=LIGHT_BLUE, edgecolor=DEEP_BLUE,
               linewidth=0.8, zorder=3)
    ax.hlines(m, i - 0.38, i + 0.38, color=DEEP_BLUE, lw=3, zorder=4)
    ax.text(i + 0.42, m, f"层均值 {m}", va="center", fontsize=10.5,
            color=DEEP_BLUE, fontweight="bold")

ax.axhline(grand, color=GOLD, ls="--", lw=2, zorder=2)
ax.text(3.45, grand + 0.25, f"总均值 {grand:.1f}", color=GOLD,
        fontsize=10.5, fontweight="bold")

# 层间差异标注（放在两层之间的空隙处）
for i in range(2):
    xb = i + 1.5
    ax.annotate("", xy=(xb, means[i + 1] - 0.6),
                xytext=(xb, means[i] + 0.6),
                arrowprops=dict(arrowstyle="<->", color=GOLD, lw=1.6))
    ax.text(xb, (means[i] + means[i + 1]) / 2, "层间\n差异", color=GOLD,
            fontsize=9.5, ha="center", va="center", fontweight="bold")

ax.set_xlim(0.5, 4.2)
ax.set_ylim(0, 16)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(["层 1", "层 2", "层 3"], fontsize=11.5)
ax.set_ylabel("被解释变量 Y", fontsize=11.5)
ax.set_title("层内点紧密围绕层均值，层均值之间明显分开",
             fontsize=12.5, color=DEEP_BLUE, fontweight="bold", pad=10)
ax.grid(axis="y", color="#E6E6E6", lw=1)
ax.set_axisbelow(True)

# 右：平方和堆叠
ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
sst = ((allv - grand) ** 2).sum()
ssb = sst - ssw
q = ssb / sst

axb.bar([1], [ssw], color=LIGHT_BLUE, edgecolor=DEEP_BLUE, width=0.5)
axb.bar([1], [ssb], bottom=[ssw], color=GOLD, edgecolor=GOLD, width=0.5)
axb.text(1, ssw + 2.5, f"SSW 层内 {ssw:.0f}", ha="center", va="bottom",
         fontsize=10, color=DEEP_BLUE, fontweight="bold")
axb.text(1, ssw + ssb / 2, f"SSB\n层间\n{ssb:.0f}", ha="center", va="center",
         fontsize=10.5, color="white", fontweight="bold")
axb.text(1, sst + 22, f"SST = SSW + SSB = {sst:.0f}", ha="center", va="bottom",
         fontsize=10.5, color="#1A1A1A")
axb.text(1, sst + 46, "总平方和分解", ha="center", va="bottom",
         fontsize=12.5, color=DEEP_BLUE, fontweight="bold")
axb.text(1, -16, f"q = 1 − SSW/SST = {q:.2f}", ha="center", va="top",
         fontsize=12, color=DEEP_BLUE, fontweight="bold")
axb.set_xlim(0.4, 1.6)
axb.set_ylim(-28, sst + 58)
axb.axis("off")

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\01-原理篇\code\p1_fig4_variance.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out, "q=", round(q, 3))
