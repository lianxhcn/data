# -*- coding: utf-8 -*-
"""因果识别假设的五幅教学示意图。

运行: python code/make_figures.py [--output-dir 项目目录] [--stamp YYYYMMDDHHmm]
依赖: numpy、matplotlib、Pillow；字体: Microsoft YaHei。
图中全部文案来自配图要求与提示词.md，只调整换行与版式。
图3使用人为设定、归一化的平滑密度示意，并非真实样本的核密度估计。
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.text import Text
from PIL import Image, ImageDraw, ImageOps

DPI = 200
TREAT = "#355C7D"
ACCENT = "#E07A5F"
GRAY = "#9AA3AB"
LIGHT = "#E9EEF3"
INK = "#2B2B2B"
plt.rcParams.update({"font.sans-serif": ["Microsoft YaHei"],
                     "axes.unicode_minus": False, "mathtext.fontset": "dejavusans",
                     "svg.fonttype": "none", "savefig.facecolor": "white"})

NAMES = ["potential-outcomes", "bias-decomposition", "overlap", "interference", "treatment-versions"]
CAP2 = "朴素均值差 = ATT + 选择偏差；本例中选择偏差为负，组间比较低估处理效应。"
CAP5 = "同一处理标签下存在多个版本，各版本对应不同潜在结果，统一处理效应无法定义。"
RECORDS = []


def canvas(w, h):
    fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, w), ylim=(h, 0))
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def text(ax, x, y, s, size=58, color=INK, ha="center", weight="normal", **kw):
    return ax.text(x, y, s, fontsize=size * 72 / DPI, color=color,
                   ha=ha, va="center", fontweight=weight, linespacing=1.35,
                   zorder=5, **kw)


def box(ax, x, y, w, h, fc="white", ec=TREAT, dashed=False):
    p = FancyBboxPatch((x, y), w, h,
                      boxstyle="round,pad=0,rounding_size=20",
                      facecolor=fc, edgecolor=ec, linewidth=1.8,
                      linestyle=(0, (5, 4)) if dashed else "-", zorder=3)
    ax.add_patch(p)
    return p


def arrow(ax, p1, p2, color=TREAT, dashed=False, rad=0, lw=1.9):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=20,
                        linewidth=lw, color=color,
                        linestyle=(0, (5, 4)) if dashed else "-",
                        connectionstyle=f"arc3,rad={rad}",
                        shrinkA=0, shrinkB=0, zorder=2)
    ax.add_patch(a)
    return a


def circle(ax, x, y, r, treated=False, label=None):
    p = Circle((x, y), r, facecolor=TREAT if treated else "white",
               edgecolor=TREAT if treated else GRAY, linewidth=1.8, zorder=3)
    ax.add_patch(p)
    text(ax, x, y, label or ("D = 1" if treated else "D = 0"),
         size=51, color="white" if treated else GRAY)
    return p


def fig1(mobile=False):
    if not mobile:
        fig, ax = canvas(2200, 1240)
        c = Circle((300, 620), 155, facecolor=LIGHT, edgecolor=TREAT, linewidth=1.8)
        ax.add_patch(c)
        text(ax, 300, 620, "个体 i", 66)
        box(ax, 1450, 230, 620, 270, TREAT)
        box(ax, 1450, 780, 620, 270, ec=GRAY, dashed=True)
        text(ax, 1760, 145, "实际处理状态", 60, TREAT)
        text(ax, 1760, 330, r"$Y_{i}(1)$", 84, "white")
        text(ax, 1760, 430, "可观测结果", 60, "white")
        text(ax, 1760, 880, r"$Y_{i}(0)$", 84, GRAY)
        text(ax, 1760, 980, "反事实结果", 60, GRAY)
        text(ax, 1760, 1135, "反事实，不可观测", 60, GRAY)
        arrow(ax, (446, 568), (1445, 365))
        arrow(ax, (446, 672), (1445, 915), GRAY, dashed=True)
        text(ax, 960, 300, "D = 1，参加培训", 62, TREAT)
        text(ax, 960, 1030, "D = 0，未参加培训", 62, GRAY)
    else:
        fig, ax = canvas(1200, 1300)
        c = Circle((190, 650), 118, facecolor=LIGHT, edgecolor=TREAT, linewidth=1.7)
        ax.add_patch(c)
        text(ax, 190, 650, "个体 i", 54)
        box(ax, 650, 245, 480, 270, TREAT)
        box(ax, 650, 850, 480, 270, ec=GRAY, dashed=True)
        text(ax, 890, 155, "实际处理状态", 50, TREAT)
        text(ax, 890, 345, r"$Y_{i}(1)$", 72, "white")
        text(ax, 890, 445, "可观测结果", 52, "white")
        text(ax, 890, 950, r"$Y_{i}(0)$", 72, GRAY)
        text(ax, 890, 1050, "反事实结果", 52, GRAY)
        text(ax, 890, 1210, "反事实，不可观测", 50, GRAY)
        arrow(ax, (293, 591), (643, 380))
        arrow(ax, (293, 709), (643, 985), GRAY, dashed=True)
        text(ax, 440, 330, "D = 1，\n参加培训", 50, TREAT)
        text(ax, 440, 1030, "D = 0，\n未参加培训", 50, GRAY)
    return fig


def fig2(mobile=False):
    if not mobile:
        fig, ax = canvas(2200, 1240)
        ys = [230, 565, 860]
        for y, col, eq, desc, dash in [
            (ys[0], TREAT, r"$E[Y(1)\mid D=1]$，", "处理组观测结果", False),
            (ys[1], ACCENT, r"$E[Y(0)\mid D=0]$，", "对照组观测结果", False),
            (ys[2], GRAY, r"$E[Y(0)\mid D=1]$，", "处理组反事实基线", True)]:
            text(ax, 80, y-45, eq, 65, col, ha="left")
            text(ax, 80, y+45, desc, 58, col, ha="left")
            ax.plot([760, 2090], [y, y], color=col, lw=1.7,
                    linestyle=(0, (6, 4)) if dash else "-", zorder=1)
        arrow(ax, (1120, ys[0]), (1120, ys[1]), INK)
        text(ax, 1175, 400, "朴素均值差", 58, INK, ha="left")
        # ATT 与负选择偏差放在同一右侧分解区，微错开避免覆盖。
        arrow(ax, (1710, ys[0]), (1710, ys[2]), TREAT)
        text(ax, 1710, 150, "ATT", 65, TREAT)
        arrow(ax, (1870, ys[1]), (1870, ys[2]), ACCENT)
        text(ax, 1925, 715, "选择偏差\n$<0$", 56, ACCENT, ha="left")
        text(ax, 1100, 1055,
             "朴素均值差 = ATT + 选择偏差；\n本例中选择偏差为负，组间比较低估处理效应。", 58)
    else:
        fig, ax = canvas(1200, 1580)
        ys = [245, 680, 1090]
        labels = [(TREAT, r"$E[Y(1)\mid D=1]$，", "处理组观测结果"),
                  (ACCENT, r"$E[Y(0)\mid D=0]$，", "对照组观测结果"),
                  (GRAY, r"$E[Y(0)\mid D=1]$，", "处理组反事实基线")]
        for y, (col, eq, desc) in zip(ys, labels):
            text(ax, 65, y-110, eq, 55, col, ha="left")
            text(ax, 65, y-35, desc, 50, col, ha="left")
            ax.plot([70, 1120], [y, y], color=col, lw=1.6,
                    linestyle=(0, (6, 4)) if col == GRAY else "-")
        arrow(ax, (560, ys[0]), (560, ys[1]), INK)
        text(ax, 610, 455, "朴素\n均值差", 51, ha="left")
        arrow(ax, (890, ys[0]), (890, ys[2]), TREAT)
        text(ax, 890, 140, "ATT", 57, TREAT)
        arrow(ax, (1015, ys[1]), (1015, ys[2]), ACCENT)
        text(ax, 790, 895, "选择偏差\n$<0$", 49, ACCENT, ha="right")
        text(ax, 600, 1270, "朴素均值差 = ATT + 选择偏差；", 51)
        text(ax, 600, 1370, "本例中选择偏差为负，", 51)
        text(ax, 600, 1470, "组间比较低估处理效应。", 51)
    return fig


def bump(x, center, halfwidth):
    """紧支撑 C-infinity 平滑密度；零点外严格为零。"""
    z = (x-center)/halfwidth
    y = np.zeros_like(x)
    valid = abs(z) < 1
    y[valid] = np.exp(-1/(1-z[valid]**2))
    return y / np.trapezoid(y, x)


def density_panel(fig, rect, separated, mobile):
    ax = fig.add_axes(rect)
    x = np.linspace(0, 1, 2001)
    if separated:
        d1, d0 = bump(x, .8, .16), bump(x, .2, .16)
    else:
        d1, d0 = bump(x, .55, .42), bump(x, .42, .40)
    for y, col in [(d1, TREAT), (d0, ACCENT)]:
        ax.fill_between(x, y, color=col, alpha=.18)
        ax.plot(x, y, color=col, lw=2.1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, max(d1.max(), d0.max()) * 1.12)
    ax.set_yticks([])
    ax.set_xticks([0, .2, .4, .6, .8, 1])
    ax.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1"])
    ax.tick_params(axis="x", labelsize=(48 if mobile else 49)*72/DPI,
                   colors=INK, length=5, pad=10)
    for k in ["top", "right"]:
        ax.spines[k].set_visible(False)
    for k in ["bottom", "left"]:
        ax.spines[k].set_color(INK)
        ax.spines[k].set_linewidth(1.25)
    ax.set_xlabel("倾向得分 $e(X)$", fontsize=(50 if mobile else 54)*72/DPI,
                  labelpad=18, color=INK)
    ax.set_ylabel("密度", fontsize=(50 if mobile else 54)*72/DPI,
                  labelpad=18, color=INK)
    return ax


def fig3(mobile=False):
    w, h = (1200, 1740) if mobile else (2600, 1100)
    fig, ax = canvas(w, h)
    if mobile:
        panels = [("重叠充分，可进行有效比较", 90, .60, False),
                  ("完全分离，正值性严重不足", 940, .13, True)]
        for title, ty, bottom, separated in panels:
            text(ax, 630, ty, title, 49)
            # 图例放在图面上方的独立行，避免遮挡曲线。
            ax.plot([235, 300], [ty+95, ty+95], color=TREAT, lw=2)
            text(ax, 320, ty+95, "处理组 D = 1", 47, ha="left")
            ax.plot([695, 760], [ty+95, ty+95], color=ACCENT, lw=2)
            text(ax, 780, ty+95, "对照组 D = 0", 47, ha="left")
            density_panel(fig, [.15, bottom, .79, .245], separated, True)
    else:
        for title, cx, rect, separated in [
            ("重叠充分，可进行有效比较", 690, [.065, .20, .405, .54], False),
            ("完全分离，正值性严重不足", 1970, [.555, .20, .405, .54], True)]:
            text(ax, cx, 100, title, 62)
            ax.plot([cx-410, cx-325], [210, 210], color=TREAT, lw=2.1)
            text(ax, cx-300, 210, "处理组 D = 1", 55, ha="left")
            ax.plot([cx+120, cx+205], [210, 210], color=ACCENT, lw=2.1)
            text(ax, cx+230, 210, "对照组 D = 0", 55, ha="left")
            density_panel(fig, rect, separated, False)
    return fig


def network(ax, cx, top, width, height, spillover, size=55):
    # 同一局部坐标在两联中重复，确保节点布局逐点对应。
    pos = [(cx-width*.29, top+height*.17, True),
           (cx+width*.29, top+height*.17, True),
           (cx, top+height*.47, False),
           (cx-width*.34, top+height*.79, False),
           (cx+width*.34, top+height*.79, False)]
    r = width*.103
    nodes = []
    for x,y,t in pos:
        p = Circle((x,y), r, facecolor=TREAT if t else "white",
                   edgecolor=TREAT if t else GRAY, linewidth=1.8, zorder=3)
        ax.add_patch(p)
        text(ax,x,y,"D = 1" if t else "D = 0",size,"white" if t else GRAY)
        nodes.append(p)
    if spillover:
        for i,j,rad in [(0,2,.1),(0,3,-.1),(1,2,-.1),(1,4,.1)]:
            s,t = np.array(pos[i][:2]),np.array(pos[j][:2])
            a = FancyArrowPatch(tuple(s), tuple(t), patchA=nodes[i], patchB=nodes[j],
                                arrowstyle="-|>", mutation_scale=20, linewidth=1.8,
                                color=ACCENT, linestyle=(0,(5,4)),
                                connectionstyle=f"arc3,rad={rad}", shrinkA=3,
                                shrinkB=4, zorder=2)
            ax.add_patch(a)


def fig4(mobile=False):
    if not mobile:
        fig, ax = canvas(2600, 1100)
        network(ax, 660, 100, 1100, 780, False, 62)
        network(ax, 1940, 100, 1100, 780, True, 62)
        text(ax, 660, 950, "无干扰：个体结果只取决于\n自身处理状态", 60)
        text(ax, 1940, 950, "存在溢出：处理组通过供给、\n信息与网络影响对照组", 60)
    else:
        fig, ax = canvas(1200, 1690)
        network(ax, 600, 30, 1050, 650, False, 54)
        network(ax, 600, 830, 1050, 650, True, 54)
        text(ax, 600, 720, "无干扰：个体结果只取决于\n自身处理状态", 51)
        text(ax, 600, 1540, "存在溢出：处理组通过供给、\n信息与网络影响对照组", 51)
    return fig


def fig5(mobile=False):
    if not mobile:
        fig, ax = canvas(2200, 1240)
        box(ax, 115, 465, 450, 250, TREAT)
        text(ax, 340, 545, "处理标签", 62, "white")
        text(ax, 340, 645, "D = 1", 65, "white")
        for y, tag, desc, label, col in [
            (115,"版本 A","短期技能班",r"$Y_{i}(1_{A})$",TREAT),
            (460,"版本 B","长期认证班",r"$Y_{i}(1_{B})$",ACCENT),
            (805,"版本 C","不同机构课程",r"$Y_{i}(1_{C})$",GRAY)]:
            box(ax, 870, y, 590, 230)
            text(ax,1165,y+70,tag,60,TREAT)
            text(ax,1165,y+160,desc,60)
            arrow(ax,(568,590),(865,y+115),GRAY)
            box(ax,1710,y,380,230,LIGHT,col)
            text(ax,1900,y+115,label,78,col)
            arrow(ax,(1465,y+115),(1705,y+115),GRAY)
        text(ax,1100,1140,
             "同一处理标签下存在多个版本，各版本对应不同潜在结果，\n统一处理效应无法定义。",57)
    else:
        fig, ax = canvas(1200, 1540)
        box(ax,365,65,470,185,TREAT)
        text(ax,600,125,"处理标签",53,"white")
        text(ax,600,200,"D = 1",56,"white")
        # 手机版将共同处理标签置顶，三个版本与结果仍逐行对应。
        ax.plot([160,160],[310,1115],color=GRAY,lw=1.6,zorder=1)
        arrow(ax,(600,255),(160,310),GRAY)
        for y,tag,desc,label,col in [
            (390,"版本 A","短期技能班",r"$Y_{i}(1_{A})$",TREAT),
            (690,"版本 B","长期认证班",r"$Y_{i}(1_{B})$",ACCENT),
            (990,"版本 C","不同机构课程",r"$Y_{i}(1_{C})$",GRAY)]:
            box(ax,270,y,450,220)
            text(ax,495,y+65,tag,53,TREAT)
            text(ax,495,y+150,desc,51)
            arrow(ax,(160,y+110),(265,y+110),GRAY)
            box(ax,875,y,265,220,LIGHT,col)
            text(ax,1007,y+110,label,64,col)
            arrow(ax,(725,y+110),(870,y+110),GRAY)
        text(ax,600,1320,"同一处理标签下存在多个版本，",50)
        text(ax,600,1400,"各版本对应不同潜在结果，",50)
        text(ax,600,1480,"统一处理效应无法定义。",50)
    return fig


def check_text(fig):
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    W,H = fig.canvas.get_width_height()
    labels, outside = [], []
    for t in fig.findobj(match=Text):
        if not t.get_visible() or not t.get_text():
            continue
        bb=t.get_window_extent(ren)
        # 隐藏的坐标轴标题不参与验收；其余所有可见字必须落在画布内。
        if bb.width < 1 or bb.height < 1:
            continue
        labels.append({"text":t.get_text(),"bbox_px":[round(float(v),2) for v in bb.bounds],
                       "font_px":round(t.get_fontsize()*DPI/72,2)})
        if bb.x0 < 0 or bb.y0 < 0 or bb.x1 > W or bb.y1 > H:
            outside.append(t.get_text())
    if outside:
        raise RuntimeError(f"文字越界: {outside}")
    return labels


def save(fig, num, mobile, root, stamp):
    labels = check_text(fig)
    name=f"fig{num:02d}-{NAMES[num-1]}.png"
    if mobile:
        unique=f"lianxiaobai-causal-assumptions-mobile-fig{num}-{stamp}.png"
        path=root/"figs/mobile"/unique
    else:
        unique=f"lianxiaobai-causal-assumptions-fig{num}-{stamp}.png"
        path=root/"figs/raw"/unique
    fig.savefig(path, dpi=DPI, facecolor="white")
    # PNG 无损压缩，不改变尺寸、分辨率与像素。
    with Image.open(path) as im:
        im.convert("RGB").save(path,optimize=True,dpi=(DPI,DPI))
    source=root/"figs/source"/unique.replace(".png",".svg")
    fig.savefig(source,format="svg",facecolor="white")
    if not mobile:
        shutil.copy2(path,root/"images"/name)
    with Image.open(path) as im:
        size=list(im.size)
        preview=ImageOps.contain(im.convert("RGB"),(360,2000),Image.Resampling.LANCZOS)
        preview.save(root/"figs/qa"/f"fig{num:02d}-{'mobile' if mobile else 'desktop'}-360.png")
    RECORDS.append({"figure":num,"variant":"mobile" if mobile else "desktop",
                    "local_path":str(path.relative_to(root)),"compatibility_image":None if mobile else f"images/{name}",
                    "source_svg":str(source.relative_to(root)),"pixels":size,"dpi":DPI,
                    "bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                    "text_bounds_checked":True,"labels":labels})
    plt.close(fig)


def contact_sheet(root, mobile):
    files=[root/"figs/qa"/f"fig{i:02d}-{'mobile' if mobile else 'desktop'}-360.png" for i in range(1,6)]
    images=[Image.open(p).convert("RGB") for p in files]
    maxh=max(im.height for im in images)
    out=Image.new("RGB",(360*5,maxh+36),"white")
    draw=ImageDraw.Draw(out)
    for i,im in enumerate(images):
        out.paste(im,(i*360,36))
        draw.text((i*360+10,10),f"Figure {i+1}: {'mobile' if mobile else 'desktop'} @ 360px",fill=INK)
    out.save(root/"figs/qa"/f"{'mobile' if mobile else 'desktop'}-contact-sheet.png")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--stamp",default=datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d%H%M"))
    args=parser.parse_args()
    root=args.output_dir.resolve()
    for folder in ["images","figs/raw","figs/mobile","figs/source","figs/qa"]:
        (root/folder).mkdir(parents=True,exist_ok=True)
    for mobile in [False,True]:
        for n,fn in enumerate([fig1,fig2,fig3,fig4,fig5],1):
            save(fn(mobile),n,mobile,root,args.stamp)
        contact_sheet(root,mobile)
    manifest={"generated_at_beijing":datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "specification":"配图要求与提示词.md / 给ChatGPT的配图说明.md",
              "naming_convention":"父目录 README.md: 作者拼音-标题关键词-fig序号-YYYYMMDDHHmm.png",
              "font":"Microsoft YaHei; DejaVu Sans mathtext",
              "palette":{"treated":TREAT,"accent":ACCENT,"counterfactual":GRAY,"fill":LIGHT,"ink":INK},
              "figure_3_method":"人为设定紧支撑 C-infinity bump 密度，数值积分归一化；左图两曲线有重叠，右图支撑分别为[0.04,0.36]与[0.64,0.96]，严格分离；并非真实数据或核密度估计结果。",
              "semantic_notes":["保留全部指定文案，只做换行。图5关于统一处理效应的表述待作者裁定。",
                                "图2 ATT 与负偏差两箭头在第二列微错位，避免覆盖。",
                                "图4的陶土橙虚线仅表达潜在溢出路径；两联圆形节点位置完全一致。",
                                "图5灰色箭头是处理版本的定义映射，非不可观测状态或实际因果路径。"],
              "figures":RECORDS}
    (root/"generation-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"output_dir":str(root),"files":[{k:r[k] for k in ["figure","variant","local_path","pixels","bytes"]} for r in RECORDS]},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
