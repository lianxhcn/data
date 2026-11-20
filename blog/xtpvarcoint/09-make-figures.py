# -*- coding: utf-8 -*-
"""
正式配图：基于 Stata 实测与修复后的数值
  图 1 fig1-eigen.png  伴随矩阵特征根与单位圆
  图 2 fig2-irf.png    invest 对各冲击的脉冲响应
  图 3 fig3-fevd.png   invest 方程预测误差方差分解
配色：深海蓝 + 深金黄；散点空心圆；全局字体不小于 9 pt；原生宽度 <=1000 px
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# ---------- 全局字体与配色 ----------
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "Arial", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 11          # 全局基准，大于 9 pt
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["legend.fontsize"] = 10

DEEP_BLUE = "#1F3A5F"
GOLD = "#C08A2E"
LIGHT_BLUE = "#6E8FB8"
GRAY = "#9AA3AD"

# 输出目录：脚本所在目录下的 figures，可按需修改为其他路径
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

# ---------- 图 1：特征根与单位圆 ----------
A1 = np.array([
    [0.904739364,  0.016664365,  1.86276557],
    [-3.02141449,  0.431106638,  7.97176906],
    [0.575372775, -0.01144528,   1.02459957],
])
A2 = np.array([
    [-1.5330546,  -0.006098188, -1.36700277],
    [-2.23567445, -0.28680257,  -6.63570675],
    [0.002070284, -0.010074143, -0.117599172],
])
K = 3
C = np.zeros((2*K, 2*K))
C[:K, :K] = A1
C[:K, K:] = A2
C[K:, :K] = np.eye(K)
eig = np.linalg.eigvals(C)

fig, ax = plt.subplots(figsize=(7.2, 7.2), dpi=120)
unit = Circle((0, 0), 1, fill=False, linestyle="--", edgecolor=GRAY,
              linewidth=1.6, label="单位圆")
ax.add_patch(unit)
ax.axhline(0, color=GRAY, linewidth=0.8)
ax.axvline(0, color=GRAY, linewidth=0.8)

for z in eig:
    unstable = abs(z) > 1
    ax.scatter(z.real, z.imag, s=110,
               facecolors="none",
               edgecolors=GOLD if unstable else DEEP_BLUE,
               linewidths=2.0, zorder=3,
               label="圆外特征根 (%.4f)" % abs(z) if unstable else None)
# 稳定点图例（手动补一个代表）
ax.scatter([], [], facecolors="none", edgecolors=DEEP_BLUE,
           linewidths=2.0, s=110, label="圆内特征根")

ax.set_xlim(-1.35, 1.45)
ax.set_ylim(-1.35, 1.35)
ax.set_aspect("equal")
ax.set_xlabel("实部 Re")
ax.set_ylabel("虚部 Im")
ax.set_title("伴随矩阵特征根与单位圆")
ax.legend(loc="upper left", framealpha=0.9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1-eigen.png"), dpi=120)
plt.close(fig)

# ---------- 图 2：invest 脉冲响应 ----------
h = np.arange(9)
irf_ii = [1.0000, 0.9047, 0.3069, 0.2306, 0.7103, 1.0259, 0.9064, 0.8145, 1.1221]
irf_im = [0.0000, 0.0167, -0.0052, -0.0532, -0.0591, -0.0224, -0.0048, -0.0318, -0.0636]
irf_ik = [0.0000, 1.8628, 2.3597, 1.3820, 0.7588, 1.5049, 2.6062, 2.8894, 2.7106]

fig, ax = plt.subplots(figsize=(8.2, 5.6), dpi=120)
ax.plot(h, irf_ii, marker="o", mfc="none", color=DEEP_BLUE, linewidth=1.8,
        label="invest 冲击")
ax.plot(h, irf_im, marker="s", mfc="none", color=LIGHT_BLUE, linewidth=1.6,
        label="mvalue 冲击")
ax.plot(h, irf_ik, marker="^", mfc="none", color=GOLD, linewidth=1.8,
        label="kstock 冲击")
ax.axhline(0, color=GRAY, linewidth=0.9)
ax.set_xticks(h)
ax.set_xlabel("预测期 h")
ax.set_ylabel("invest 的脉冲响应")
ax.set_title("invest 对各变量冲击的脉冲响应（简化式）")
ax.legend(loc="upper left", framealpha=0.9)
ax.grid(True, linestyle=":", alpha=0.45)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2-irf.png"), dpi=120)
plt.close(fig)

# ---------- 图 3：invest 方差分解（堆叠面积） ----------
fevd_i = np.array([1.0000, 0.3439, 0.1747, 0.1522, 0.1765, 0.2034, 0.1743, 0.1475, 0.1473])
fevd_m = np.array([0.0000, 0.0001, 0.0000, 0.0002, 0.0005, 0.0004, 0.0003, 0.0002, 0.0003])
fevd_k = np.array([0.0000, 0.6561, 0.8253, 0.8476, 0.8231, 0.7962, 0.8255, 0.8522, 0.8525])

fig, ax = plt.subplots(figsize=(8.2, 5.6), dpi=120)
ax.stackplot(h, fevd_i, fevd_m, fevd_k,
             colors=[DEEP_BLUE, LIGHT_BLUE, GOLD],
             labels=["invest 冲击", "mvalue 冲击", "kstock 冲击"],
             alpha=0.92, edgecolor="white", linewidth=0.6)
ax.set_xlim(0, 8)
ax.set_ylim(0, 1)
ax.set_xticks(h)
ax.set_xlabel("预测期 h")
ax.set_ylabel("预测误差方差占比")
ax.set_title("invest 方程预测误差方差分解（简化式）")
ax.legend(loc="upper right", framealpha=0.9)
ax.grid(True, linestyle=":", alpha=0.35)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3-fevd.png"), dpi=120)
plt.close(fig)

print("三张配图已生成：")
for fn in ["fig1-eigen.png", "fig2-irf.png", "fig3-fevd.png"]:
    p = os.path.join(OUT, fn)
    print(" ", p, os.path.getsize(p), "bytes")
