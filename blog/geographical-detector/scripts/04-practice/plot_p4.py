"""篇四配图：因子 q 值、交互热力图、风险均值、生态检验。"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from mydisc import disc_labels
from geodetector import GeoDetector

# 中文字体
for f in ["Microsoft YaHei", "SimHei"]:
    if any(f in fn.name for fn in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [f]
        break
plt.rcParams["axes.unicode_minus"] = False
# 全局字体下限：所有文字不小于 9 pt
plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11,
                     "xtick.labelsize": 10, "ytick.labelsize": 10,
                     "legend.fontsize": 10})

dat = pd.read_csv("ndvi_40.csv")
target = "NDVIchange"
best_params = {"Tempchange": ("quantile", 8), "Precipitation": ("equal", 7),
               "GDP": ("quantile", 8), "Popdensity": ("quantile", 8)}
categorical = ["Climatezone", "Mining"]
proc = pd.DataFrame({target: dat[target]})
for col, (m, k) in best_params.items():
    proc[col] = disc_labels(dat[col].values, m, k)
for col in categorical:
    proc[col] = dat[col]
factors = list(best_params.keys()) + categorical
model = GeoDetector(factors=factors, target=target).fit(proc)

# 图 1：因子 q 值条形图
q = model.q_values_.sort_values("q_value")
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.barh(q["variable"], q["q_value"], color="#0F3D5C")
ax.set_xlabel("q 值")
ax.set_title("因子探测器：各因子的空间解释力")
for b, v in zip(bars, q["q_value"]):
    ax.text(v + 0.01, b.get_y() + b.get_height() / 2, f"{v:.3f}", va="center")
ax.set_xlim(0, 0.98)
plt.tight_layout()
plt.savefig("p4_fig1_factor.png", dpi=150)
plt.close()

# 图 2：交互 q 热力图（浅金到深海蓝渐变）
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
iq = model.interaction_q_
gold_blue = LinearSegmentedColormap.from_list(
    "gold_blue", ["#F0E0B0", "#C9A24B", "#5E7FA0", "#0F3D5C"])
fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(iq.values, cmap=gold_blue, vmin=0, vmax=1)
ax.set_xticks(range(len(iq.columns))); ax.set_xticklabels(iq.columns, rotation=45, ha="right")
ax.set_yticks(range(len(iq.index))); ax.set_yticklabels(iq.index)
# 对角线用中性灰覆盖
for i in range(len(iq)):
    ax.add_patch(Rectangle((i - 0.5, i - 0.5), 1, 1, color="#E6E6E6", zorder=2))
for i in range(len(iq)):
    for j in range(len(iq)):
        v = iq.iloc[i, j]
        if i == j:
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=9, color="#1A1A1A", zorder=3)
        else:
            txt_color = "white" if v > 0.55 else "#1A1A1A"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=9, color=txt_color)
ax.set_title("交互探测器：双因子交互 q 值")
fig.colorbar(im, ax=ax, fraction=0.046)
plt.tight_layout()
plt.savefig("p4_fig2_interaction.png", dpi=150)
plt.close()

# 图 3：风险分层均值（深海蓝与深金黄两条折线）
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
line_colors = {"Precipitation": "#0F3D5C", "Tempchange": "#C99A2E"}
for ax, f in zip(axes, ["Precipitation", "Tempchange"]):
    means = proc.groupby(f)[target].mean()
    ax.plot(range(len(means)), means.values, "o-", color=line_colors[f],
            lw=2, markersize=7, label=f)
    for i, v in enumerate(means.values):
        ax.text(i, v + 0.012, f"{v:.2f}", ha="center", fontsize=9)
    ax.set_xlabel(f"{f} 分层"); ax.set_ylabel("NDVIchange 均值")
    ax.set_title(f"风险探测器：{f} 各分层均值")
    ax.legend(frameon=False)
plt.tight_layout()
plt.savefig("p4_fig3_risk.png", dpi=150)
plt.close()

# 图 4：生态检验热力图（深海蓝 + 深金黄）
from matplotlib.colors import ListedColormap
eco = model.ecological_result_
# 编码：0 不显著、1 显著、2 对角线
sig_mat = pd.DataFrame(np.full((len(factors), len(factors)), 2),
                       index=factors, columns=factors)
for _, r in eco.iterrows():
    code = 1 if r["significant"] else 0
    sig_mat.loc[r["factor_1"], r["factor_2"]] = code
    sig_mat.loc[r["factor_2"], r["factor_1"]] = code
OCEAN_BLUE = "#0F3D5C"   # 深海蓝：差异显著
DEEP_GOLD = "#C99A2E"    # 深金黄：不显著
DIAG_GRAY = "#E6E6E6"    # 对角线中性灰
cmap = ListedColormap([DEEP_GOLD, OCEAN_BLUE, DIAG_GRAY])
fig, ax = plt.subplots(figsize=(7, 6))
ax.imshow(sig_mat.values, cmap=cmap, vmin=0, vmax=2)
ax.set_xticks(range(len(factors))); ax.set_xticklabels(factors, rotation=45, ha="right")
ax.set_yticks(range(len(factors))); ax.set_yticklabels(factors)
for i in range(len(factors)):
    for j in range(len(factors)):
        code = sig_mat.iloc[i, j]
        if code == 2:
            ax.text(j, i, "—", ha="center", va="center",
                    fontsize=11, color="#9A9A9A")
        else:
            txt = "差异显著" if code == 1 else "不显著"
            txt_color = "white" if code == 1 else "#1A1A1A"
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=9, color=txt_color)
ax.set_title("生态探测器：两因子解释力差异是否显著")
plt.tight_layout()
plt.savefig("p4_fig4_ecological.png", dpi=150)
plt.close()
print("四张配图已生成")
