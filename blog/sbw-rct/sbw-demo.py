"""SBW 推文的独立教学示例，不是原论文复现包。

依赖：Python 3.12、NumPy、Matplotlib (仅绘图时需要)。
运行：python sbw-demo.py
绘图：python sbw-demo.py --font /path/to/chinese-font.otf
所有输出写入脚本所在目录；仅含一个二元处理前特征。
"""
from pathlib import Path
import argparse
import json
import platform
import numpy as np

ROOT = Path(__file__).resolve().parent
SEED = 20260907


def binary_sbw(x, a):
    """二元 X 的精确 SBW：每组的 X 构成对齐全样本。

    同一组、同一 X 单元内使用相同权重，能最小化权重平方和。
    每个处理组的权重平均数为 1。单元为空时直接报错。
    """
    x, a = np.asarray(x), np.asarray(a)
    if x.ndim != 1 or a.shape != x.shape or len(x) == 0:
        raise ValueError("x、a 必须是等长的非空一维数组")
    if not np.isin(x, [0, 1]).all() or not np.isin(a, [0, 1]).all():
        raise ValueError("本教学函数只接受取值为 0 或 1 的 x、a")
    target = x.mean()
    w = np.empty(len(x), dtype=float)
    for arm in (0, 1):
        m = a == arm
        if not m.any() or np.unique(x[m]).size != 2:
            raise ValueError("某处理组缺少一种 X，不能使用本函数做精确平衡")
        p = x[m].mean()
        w[m] = np.where(x[m] == 1, target / p, (1-target) / (1-p))
    return w


def estimate(x, a, y):
    """返回未调整与 SBW 的 RD、RR；RR 分母为零时不继续推断。"""
    w = binary_sbw(x, a)
    p0, p1 = [y[a == k].mean() for k in (0, 1)]
    q0, q1 = [np.average(y[a == k], weights=w[a == k]) for k in (0, 1)]
    if min(p0, p1, q0, q1) <= 0:
        raise ValueError("事件率为零，无法计算本例的 log(RR)")
    return np.array([p1-p0, q1-q0, p1/p0, q1/q0])


def simulate(rng, n, gamma):
    """边际就业率固定为 0.45、0.55；gamma 只改变 X 的预测能力。"""
    x = rng.binomial(1, 0.5, n)
    a = rng.binomial(1, 0.5, n)
    p = 0.45 + gamma * (x - 0.5) + 0.10 * a
    y = rng.binomial(1, p)
    return x, a, y


def main(font=None):
    # 手算案例：未培训收入为 20+40X，培训给每个人增加 10。
    x = np.array([0, 1, 1, 1, 0, 0, 0, 1])
    a = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    y = 20 + 40*x + 10*a
    w = binary_sbw(x, a)
    means = [np.average(y[a == k], weights=w[a == k]) for k in (0, 1)]
    xc = x-x.mean()
    design = np.column_stack([np.ones(len(x)), a, xc, a*xc])
    lin_ate = np.linalg.lstsq(design, y, rcond=None)[0][1]
    win = (y[a == 1, None] > y[a == 0]).astype(float)
    mw = np.sum(win * np.outer(w[a == 1], w[a == 0])) / 16
    assert np.allclose(means, [40, 50]) and np.isclose(lin_ate, 10)
    assert np.isclose(mw, .75)
    toy = dict(x=x.tolist(), a=a.tolist(), y=y.tolist(), weights=w.tolist(),
               raw_ate=float(y[a == 1].mean()-y[a == 0].mean()),
               sbw_ate=float(means[1]-means[0]), lin_ate=float(lin_ate), mw=float(mw))
    np.savetxt(ROOT/'sbw-toy.csv', np.column_stack([x,a,y,w]), delimiter=',',
               header='x,a,y,weight', comments='', fmt='%.12g')

    # 重复生成独立实验，比较估计量的抽样波动；不以一次估计值证明效率。
    rng = np.random.default_rng(SEED)
    m, n = 5000, 400
    mc, summary = {}, {}
    for label, gamma in [('weak', 0.0), ('strong', 0.5)]:
        values = np.vstack([estimate(*simulate(rng,n,gamma)) for _ in range(m)])
        mc[label] = values
        sds = values[:, :2].std(axis=0, ddof=1)
        summary[label] = dict(
            mean_rd=values[:,:2].mean(axis=0).tolist(),
            sd_rd=sds.tolist(),
            relative_efficiency_gain=float((sds[0]/sds[1])**2-1),
            sd_reduction=float(1-sds[1]/sds[0]),
            variance_reduction=float(1-(sds[1]/sds[0])**2),
            equivalent_unadjusted_n=float(n*(sds[0]/sds[1])**2),
            sd_log_rr=np.log(values[:,2:]).std(axis=0,ddof=1).tolist())
        np.savetxt(ROOT/f'sbw-mc-{label}.csv', values, delimiter=',',
                   header='rd_raw,rd_sbw,rr_raw,rr_sbw',comments='')

    # 一个新实验的完整非参数 bootstrap：每次重算目标构成与权重。
    rng_data = np.random.default_rng(SEED+1)
    x,a,y = simulate(rng_data,n,.5)
    point = estimate(x,a,y)
    boot_rng = np.random.default_rng(SEED+2)
    b = 2000
    boot = []
    for _ in range(b):
        j = boot_rng.integers(0,n,n)
        boot.append(estimate(x[j],a[j],y[j]))
    boot = np.asarray(boot)
    se_rd = boot[:,1].std(ddof=1)
    se_log_rr = np.log(boot[:,3]).std(ddof=1)
    report = dict(seed=SEED,n=n,mc_repetitions=m,bootstrap_repetitions=b,
                  python=platform.python_version(),numpy=np.__version__,toy=toy,
                  mc=summary,bootstrap=dict(
                      point=point.tolist(),se_rd=float(se_rd),
                      ci_rd=(point[1]+np.array([-1,1])*1.96*se_rd).tolist(),
                      ci_rr=np.exp(np.log(point[3])+np.array([-1,1])*1.96*se_log_rr).tolist(),
                      failed_replicates=0))
    (ROOT/'sbw-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    np.savetxt(ROOT/'sbw-bootstrap.csv',boot,delimiter=',',
               header='rd_raw,rd_sbw,rr_raw,rr_sbw',comments='')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if font:
        draw(font,mc)


def draw(font,mc):
    # 精确图形由手算数据及以上真实运行的模拟结果生成。
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from datetime import datetime
    from zoneinfo import ZoneInfo
    font_manager.fontManager.addfont(font)
    family=font_manager.FontProperties(fname=font).get_name()
    plt.rcParams.update({'font.family':family,'font.size':27,'axes.unicode_minus':False,
                         'axes.spines.top':False,'axes.spines.right':False})
    stamp=datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d-%H%M%S')
    blue,orange,ink='#2166A5','#B87524','#192B3B'
    fig,ax=plt.subplots(figsize=(11,9.6),dpi=100)
    fig.subplots_adjust(left=.19,right=.95,top=.86,bottom=.11)
    ys=[3.5,2.65,1.1,.25]
    for y,p in zip(ys,[.25,.75,.5,.5]):
        ax.barh(y,p,color=orange,height=.5)
        ax.barh(y,1-p,left=p,color=blue,height=.5)
        ax.text(p/2,y,f'{int(p*100)}%',ha='center',va='center',color='white')
        ax.text(p+(1-p)/2,y,f'{int((1-p)*100)}%',ha='center',va='center',color='white')
    ax.set_yticks(ys,['处理组','对照组','处理组','对照组'])
    ax.set_xlim(0,1);ax.set_ylim(-.5,4.15);ax.set_xticks([])
    for s in ax.spines.values():s.set_visible(False)
    ax.tick_params(axis='y',length=0,pad=14)
    ax.text(0,4.08,'调整前：样本人数占比',fontsize=29,color=ink)
    ax.text(0,1.7,'调整后：组内权重占比',fontsize=29,color=ink)
    fig.text(.19,.945,'培训前收入较低',color=orange,fontsize=28)
    fig.text(.58,.945,'培训前收入较高',color=blue,fontsize=28)
    fig.text(.19,.048,'两组均对齐全样本的 50% / 50% 构成',fontsize=25,color=ink)
    f1=f'sbw-fig01-balance-{stamp}.png';fig.savefig(ROOT/f1);plt.close(fig)

    # 使用与 v01 完全相同的模拟数据，展示标准差与样本量近似换算。
    sd=mc['strong'][:,:2].std(axis=0,ddof=1)
    needed=400*(sd[0]/sd[1])**2
    fig=plt.figure(figsize=(11,11.8),dpi=100)
    fig.text(.07,.955,'同样 400 人，估计能精确多少？',fontsize=33,color=ink)
    fig.text(.07,.900,'处理前特征能较好预测就业；重复 5,000 次',fontsize=25,color=ink)
    fig.text(.07,.829,f'估计值的标准差下降 {100*(1-sd[1]/sd[0]):.1f}%',fontsize=29,color=ink)
    ax=fig.add_axes([.22,.605,.70,.17])
    for y,value,color in [(1,100*sd[0],orange),(0,100*sd[1],blue)]:
        ax.barh(y,value,height=.48,color=color)
        ax.text(value+.10,y,f'{value:.2f}',va='center',fontsize=27,color=ink)
    ax.set_yticks([1,0],['未调整','SBW']);ax.set_ylim(-.6,1.6)
    ax.set_xlim(0,6.2);ax.set_xticks([0,2,4,6])
    ax.set_xlabel('标准差 (百分点)',fontsize=25,labelpad=8)
    ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0,pad=13)
    fig.text(.07,.467,'达到同等精度，未调整约需多招 136 人',fontsize=28,color=ink)
    ax=fig.add_axes([.22,.242,.70,.17])
    for y,value,color in [(1,needed,orange),(0,400,blue)]:
        ax.barh(y,value,height=.48,color=color)
        ax.text(value+9,y,f'{value:.0f}',va='center',fontsize=27,color=ink)
    ax.set_yticks([1,0],['未调整','SBW']);ax.set_ylim(-.6,1.6)
    ax.set_xlim(0,650);ax.set_xticks([0,200,400,600])
    ax.set_xlabel('所需样本量 (人，近似换算)',fontsize=25,labelpad=8)
    ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0,pad=13)
    fig.text(.07,.098,'按标准误随样本量平方根的倒数下降换算。',fontsize=23,color=ink)
    fig.text(.07,.055,'仅对应本次模拟；无预测作用的变量几乎没有收益。',fontsize=23,color=ink)
    f2=f'sbw-fig02-sampling-{stamp}.png';fig.savefig(ROOT/f2);plt.close(fig)
    (ROOT/'sbw-figures.json').write_text(json.dumps([f1,f2],indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--font',help='中文字体的本地路径；省略时只计算，不绘图')
    main(p.parse_args().font)
