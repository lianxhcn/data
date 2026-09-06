"""按任务给定数据生成教学数值图，并校验字体字形及文件尺寸。"""
from datetime import datetime
from pathlib import Path
import json
import shutil
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
from matplotlib.patches import Rectangle
from PIL import Image
from workflow import ROOT, OUT, save_json, binary_metrics

BLUE, ORANGE, INK = '#366b93', '#c77930', '#202a33'


def main():
    # 从已安装字体中选择中文字体；不下载字体，不写死开发机字体路径。
    available = {f.name: f.fname for f in font_manager.fontManager.ttflist}
    font = next((x for x in ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC',
                             'Source Han Sans SC', 'SimSun'] if x in available), None)
    if not font:
        raise RuntimeError('没有找到中文字体，请配置项目可用的中文字体后重试')
    plt.rcParams.update({'font.family': font, 'font.size': 15, 'text.color': INK,
                         'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                         'axes.unicode_minus': False, 'savefig.facecolor': 'white'})
    warnings.filterwarnings('error', message='Glyph .* missing from font')
    OUT.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    # 唯一命名的原始图仅保存在项目内部，任务固定输出名为其可交付副本。
    raw = ROOT / 'figs/raw'
    raw.mkdir(parents=True, exist_ok=True)
    generated = []

    def export(fig, fixed, number, purpose):
        chars = {ord(c) for t in fig.findobj(matplotlib.text.Text) for c in t.get_text() if ord(c) > 127}
        missing = chars - set(FT2Font(available[font]).get_charmap())
        if missing:
            raise RuntimeError(f'字体缺失字形：{missing}')
        source = raw / f'ferrara-ai-fig{number:02d}-{purpose}-{stamp}.png'
        fig.savefig(source, dpi=100)
        shutil.copyfile(source, OUT / fixed)
        with Image.open(source) as img:
            assert img.width == 1000 and source.stat().st_size < 1_000_000
            dimensions = [img.width, img.height]
        generated.append(dict(path='outputs/' + fixed, raw_path=source.relative_to(ROOT).as_posix(),
                              dimensions=dimensions, bytes=source.stat().st_size,
                              font=font, missing_glyphs=0, origin='synthetic_teaching_example'))
        plt.close(fig)

    fig = plt.figure(figsize=(10, 9.1))
    fig.text(.08, .94, '100 篇教学文章的分类结果', fontsize=25, weight='bold')
    fig.text(.08, .887, '正类：已采用证据  |  行为人工标签，列为模型标签', fontsize=16)
    ax = fig.add_axes([.26, .28, .64, .52])
    ax.set_xlim(0, 2)
    ax.set_ylim(2, 0)
    cells = [(0, 0, 15, '正确识别', '#edf2f5', INK),
             (1, 0, 5, '漏判 (假阴性)', '#faeadb', ORANGE),
             (0, 1, 10, '误报 (假阳性)', '#dceaf4', BLUE),
             (1, 1, 70, '正确排除', '#edf2f5', INK)]
    for x, y, n, label, fill, color in cells:
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor=fill, edgecolor='white', linewidth=5))
        ax.text(x + .5, y + .44, str(n), fontsize=44, ha='center', va='center', color=color, weight='bold')
        ax.text(x + .5, y + .76, label, fontsize=17, ha='center', va='center', color=color)
    ax.set_xticks([.5, 1.5], ['模型正类', '模型负类'], fontsize=18)
    ax.xaxis.tick_top()
    ax.set_yticks([.5, 1.5], ['人工正类\n20 篇', '人工负类\n80 篇'], fontsize=18)
    ax.tick_params(length=0, pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(.08, .185, '准确率 85%     精确率 60%     召回率 75%', fontsize=22, weight='bold')
    fig.text(.08, .126, '精确率：15 / 25     召回率：15 / 20', fontsize=17)
    fig.text(.08, .055, '教学构造，非模型实测；独立于 8 条演示材料。', fontsize=15)
    export(fig, 'figure-confusion.png', 1, 'confusion')

    fig, axes = plt.subplots(3, 1, figsize=(10, 10))
    fig.subplots_adjust(left=.19, right=.90, top=.81, bottom=.13, hspace=.86)
    fig.text(.08, .944, '两家企业的三种汇总指标', fontsize=25, weight='bold')
    fig.text(.08, .892, 'A：10 篇报道，3 篇正类指向同一部署事件', fontsize=17)
    fig.text(.08, .853, 'B：4 篇报道，2 篇正类指向两个独立事件', fontsize=17)
    panels = [('采用正类报道数 (篇)', [3, 2], 3.5, [0, 1, 2, 3]),
              ('独立部署事件数 (个)', [1, 2], 3.5, [0, 1, 2, 3]),
              ('至少一次采用证据 (0/1)', [1, 1], 1.18, [0, 1])]
    for ax, (title, values, upper, ticks) in zip(axes, panels):
        ax.barh([0, 1], values, height=.46, color=[BLUE, ORANGE])
        ax.set_yticks([0, 1], ['企业 A', '企业 B'], fontsize=17)
        ax.invert_yaxis()
        ax.set_xlim(0, upper)
        ax.set_xticks(ticks)
        ax.set_title(title, loc='left', fontsize=19, pad=11, color=INK)
        ax.set_axisbelow(True)
        ax.grid(axis='x', color='#e6e8e9', linewidth=.8)
        for y, n in enumerate(values):
            ax.text(n + .03 * upper, y, str(n), va='center', fontsize=22, weight='bold')
        for s in ['top', 'right', 'left']:
            ax.spines[s].set_visible(False)
        ax.spines['bottom'].set_color('#9da5ab')
        ax.tick_params(axis='y', length=0, pad=10)
    fig.text(.08, .052, '教学构造；指标口径不同，排序也可能不同。', fontsize=16)
    export(fig, 'figure-aggregation.png', 2, 'aggregation')
    save_json(OUT / 'figure-manifest.json', generated)
    save_json(OUT / 'figure-data.json', {
        'origin': 'synthetic_teaching_example',
        'confusion': binary_metrics(15, 5, 10, 70),
        'aggregation': [{'entity': 'A', 'total_reports': 10, 'positive_reports': 3,
                         'independent_events': 1, 'any_evidence': 1},
                        {'entity': 'B', 'total_reports': 4, 'positive_reports': 2,
                         'independent_events': 2, 'any_evidence': 1}],
        'deduplicated_share': None, 'reason': '去重后分母未知，不计算占比'})
    print(json.dumps(generated, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
