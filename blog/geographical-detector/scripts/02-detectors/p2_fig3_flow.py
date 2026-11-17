import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import rcParams

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DEEP_BLUE = "#0F3D5C"
GOLD = "#C99A2E"
LIGHT_GOLD = "#F0E0B0"

fig, ax = plt.subplots(figsize=(12.5, 14), dpi=150)
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def rbox(x, y, w, h, fc, ec, fs_color="white", lw=1.6, rs=1.2):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rs}",
                       linewidth=lw, edgecolor=ec, facecolor=fc)
    ax.add_patch(p)
    return p


# 起点
rbox(22, 91, 44, 7, DEEP_BLUE, DEEP_BLUE)
ax.text(44, 94.5, "计算 q1、q2，叠加图层得到 q∩", ha="center", va="center",
        color="white", fontsize=12, fontweight="bold")

# 判断条件（左侧纵向）与结果（右侧）
conds = [
    (80, "q∩ < min(q1, q2) ?"),
    (64, "q∩ < max(q1, q2) ?"),
    (48, "q∩ < q1 + q2 ?"),
    (32, "q∩ = q1 + q2 ?"),
]
results = [
    (80, "非线性减弱", GOLD),
    (64, "单因子非线性减弱", GOLD),
    (48, "双因子增强", DEEP_BLUE),
    (32, "相互独立", GOLD),
]

cw, ch = 38, 8
cx = 8
for (y, qtext) in conds:
    rbox(cx, y - ch / 2, cw, ch, "white", DEEP_BLUE, lw=1.8)
    ax.text(cx + cw / 2, y, qtext, ha="center", va="center",
            color=DEEP_BLUE, fontsize=11.5, fontweight="bold")

# 结果框
rw, rh = 30, 7.5
rx = 66
for (y, name, c) in results:
    rbox(rx, y - rh / 2, rw, rh, c, c)
    ax.text(rx + rw / 2, y, name, ha="center", va="center",
            color="white", fontsize=11.5, fontweight="bold")

# 起点到判断1
ax.annotate("", xy=(cx + cw / 2, 84), xytext=(44, 91),
            arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=2))

# 判断之间的「否」纵向连线
ys = [80, 64, 48, 32]
for i in range(3):
    ax.annotate("", xy=(cx + cw / 2, ys[i + 1] + ch / 2),
                xytext=(cx + cw / 2, ys[i] - ch / 2),
                arrowprops=dict(arrowstyle="-|>", color=DEEP_BLUE, lw=1.8))
    ax.text(cx + cw / 2 - 3, (ys[i] + ys[i + 1]) / 2, "否",
            color=DEEP_BLUE, fontsize=10.5, fontweight="bold", ha="right")

# 每个判断的「是」横向箭头到结果
for y in ys:
    ax.annotate("", xy=(rx, y), xytext=(cx + cw, y),
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.8))
    ax.text((cx + cw + rx) / 2, y + 1.6, "是", color=GOLD,
            fontsize=10.5, fontweight="bold", ha="center")

# 判断4「否」→ 非线性增强（底部）
rbox(22, 12, 44, 8, DEEP_BLUE, DEEP_BLUE)
ax.text(44, 16, "非线性增强", ha="center", va="center",
        color="white", fontsize=12, fontweight="bold")
ax.annotate("", xy=(44, 20), xytext=(cx + cw / 2, 28),
            arrowprops=dict(arrowstyle="-|>", color=DEEP_BLUE, lw=1.8))
ax.text(cx + cw / 2 - 3, 24, "否", color=DEEP_BLUE,
        fontsize=10.5, fontweight="bold", ha="right")

# 左侧提示
ax.text(4, 96, "按 min、max、q1+q2 三个参照量逐级比较", fontsize=10.5,
        color="#555555", ha="left")

plt.tight_layout()
out = r"D:\doubao_project\blog-lianxh\地理探测器系列\02-四大探测器\code\p2_fig3_flow.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", out)
