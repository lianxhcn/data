"""多个处理前协变量的 SBW 应用示例，独立实现，不是原论文复现包。

依赖：numpy scipy pandas；适用个体独立随机分配、共同完整分析样本。
生成 CSV：python sbw_apply.py --make-demo sbw-trial.csv
读取 CSV：python sbw_apply.py --csv sbw-trial.csv --bootstrap 2000 --out results
快捷示例：python sbw_apply.py --demo --bootstrap 1000
真实数据：python sbw_apply.py --csv my_trial.csv --bootstrap 2000
CSV 列：A, age, education, pre_income, income, employed。
A 和 employed 为 0/1；education 为受教育年限；收入两列使用相同单位。
默认只平衡 age、education、pre_income 的均值；不使用处理后变量。
输出写入 --out 指定目录，默认脚本旁的 sbw-application-results。
不处理整群/分层随机化、缺失数据、抽样权重或生存删失。
"""
from pathlib import Path
import argparse
import json
import platform
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import linprog, minimize

COVARIATES = ["age", "education", "pre_income"]
METRICS = ["income_ate", "employment_rd", "employment_rr", "income_mw"]


def sbw_weights(x, a):
    """最小化平方距离，精确对齐全样本均值，权重非负且组内均值为 1。

    先求等式约束的最小二乘解；若存在实质负值，求解非负二次规划。
    仅将 -1e-10 到 0 的数值舍入误差归零，随后再次核对所有约束。
    常数、组内完全共线、不可行或未收敛时直接报错。
    """
    x, a = np.asarray(x, dtype=float), np.asarray(a)
    if x.ndim == 1:
        x = x[:, None]
    if x.ndim != 2 or len(x) == 0 or a.shape != (len(x),):
        raise ValueError("X 必须是非空矩阵，A 必须与 X 行数一致")
    if not np.isfinite(x).all() or not np.isin(a, [0, 1]).all():
        raise ValueError("X 必须为有限数值，A 必须取 0/1")
    scale = x.std(axis=0)
    if np.any(scale < 1e-12):
        raise ValueError("协变量中有常数列；请先检查变量定义")
    z = (x - x.mean(axis=0)) / scale
    w = np.empty(len(a))
    for arm in (0, 1):
        m = a == arm
        h = np.column_stack([np.ones(m.sum()), z[m]])
        if len(h) == 0 or np.linalg.matrix_rank(h) < h.shape[1]:
            raise ValueError(f"A={arm} 组为空或协变量完全共线")
        # H' w = (N_a, 0, ..., 0)：X 已按全样本均值中心化。
        target = np.r_[len(h), np.zeros(x.shape[1])]
        wa = 1 + np.linalg.lstsq(h.T, target - h.sum(axis=0), rcond=None)[0]
        if wa.min() < -1e-10:
            feasible = linprog(np.zeros(len(h)), A_eq=h.T, b_eq=target,
                               bounds=(0, None), method="highs")
            if not feasible.success:
                raise ValueError(f"A={arm} 组找不到精确非负平衡权重：{feasible.message}")
            fit = minimize(lambda v: 0.5 * np.sum((v - 1)**2), feasible.x,
                           jac=lambda v: v - 1, method="SLSQP",
                           bounds=[(0, None)] * len(h),
                           constraints={"type": "eq", "fun": lambda v: h.T @ v - target,
                                        "jac": lambda v: h.T},
                           options={"ftol": 1e-11, "maxiter": 1000})
            if not fit.success:
                raise ValueError(f"A={arm} 组优化未收敛：{fit.message}")
            wa = fit.x
        if wa.min() < -1e-10:
            raise ValueError("出现负权重，拒绝继续估计")
        wa = np.maximum(wa, 0)  # 只清理已通过上行检查的浮点舍入误差
        error = np.max(np.abs(h.T @ wa - target)) / len(h)
        if error > 1e-8:
            raise ValueError(f"权重未达到数值精确平衡，标准化最大误差={error:g}")
        w[m] = wa
    return w


def weighted_mw(y, a, w):
    """两组独立抽取的排序比较，处理组更高记 1，相同记 1/2。"""
    y0, y1 = y[a == 0], y[a == 1]
    w0, w1 = w[a == 0], w[a == 1]
    order = np.argsort(y0)
    y0, w0 = y0[order], w0[order]
    cum = np.r_[0, np.cumsum(w0)]
    lo, hi = np.searchsorted(y0, y1, "left"), np.searchsorted(y0, y1, "right")
    scores = (cum[lo] + 0.5 * (cum[hi] - cum[lo])) / cum[-1]
    return np.average(scores, weights=w1)


def effects(data, w):
    a = data.A.to_numpy()
    income, employed = data.income.to_numpy(), data.employed.to_numpy()
    mu = [np.average(income[a == k], weights=w[a == k]) for k in (0, 1)]
    p = [np.average(employed[a == k], weights=w[a == k]) for k in (0, 1)]
    if min(p) <= 0:
        raise ValueError("某组就业率为零，无法使用 log(RR) 推断")
    return np.array([mu[1]-mu[0], p[1]-p[0], p[1]/p[0], weighted_mw(income,a,w)])


def validate_data(data):
    required = ["A", *COVARIATES, "income", "employed"]
    if any(c not in data for c in required):
        raise ValueError(f"CSV 需要以下列：{required}")
    data = data[required].apply(pd.to_numeric, errors="raise").copy()
    if not np.isfinite(data.to_numpy()).all():
        raise ValueError("样本包含缺失或无限值，请先确定共同分析样本与缺失处理方案")
    for col in ("A", "employed"):
        if not data[col].isin([0, 1]).all():
            raise ValueError(f"{col} 必须取 0/1")
    return data


def run_analysis(data, repetitions=1000, seed=20260910):
    if repetitions < 2:
        raise ValueError("bootstrap 次数至少为 2；正式分析宜采用较多次数")
    data = validate_data(data)
    x, a = data[COVARIATES].to_numpy(), data.A.to_numpy()
    w = sbw_weights(x, a)
    point, raw = effects(data, w), effects(data, np.ones(len(data)))
    balance, diagnostics = [], []
    for arm in (0, 1):
        m = a == arm
        after = np.average(x[m], axis=0, weights=w[m])
        for j, name in enumerate(COVARIATES):
            balance.append(dict(arm=arm, covariate=name, target=x[:,j].mean(),
                                before=x[m,j].mean(), after=after[j]))
        diagnostics.append(dict(arm=arm, n=int(m.sum()), weight_sum=float(w[m].sum()),
                                max_weight=float(w[m].max()),
                                zero_share=float((w[m] <= 1e-10).mean()),
                                weight_ess=float(w[m].sum()**2 / (w[m]**2).sum())))
    rng = np.random.default_rng(seed)
    draws = []
    for b in range(repetitions):
        j = rng.integers(0, len(data), len(data))
        d = data.iloc[j].reset_index(drop=True)
        try:
            # 每次使用重抽样数据重新求全样本目标均值与各组权重。
            wb = sbw_weights(d[COVARIATES].to_numpy(), d.A.to_numpy())
            draws.append(effects(d, wb))
        except ValueError as exc:
            raise ValueError(f"第 {b+1} 次 bootstrap 失败；没有删除失败样本：{exc}") from exc
    draws = np.asarray(draws)
    transformed, center = draws.copy(), point.copy()
    transformed[:,2], center[2] = np.log(draws[:,2]), np.log(point[2])
    se = transformed.std(axis=0, ddof=1)
    intervals = np.column_stack([center - 1.96*se, center + 1.96*se])
    intervals[2] = np.exp(intervals[2])
    summary = pd.DataFrame(dict(metric=METRICS, unadjusted=raw, sbw=point,
                                se_working_scale=se, ci_low=intervals[:,0],
                                ci_high=intervals[:,1],
                                se_scale=["original", "original", "log_RR", "original"]))
    # 差值/MW 使用未截断 Wald 区间，RR 在对数尺度推断后转回。
    data["sbw"] = w
    return summary, data, pd.DataFrame(balance), draws, diagnostics


def demo_data():
    """仅用于验证多协变量流程，不用于替换正文原有精度比较。"""
    rng = np.random.default_rng(20260911)
    n = 600
    age = rng.integers(20, 56, n)
    education = rng.integers(9, 19, n)
    pre_income = rng.uniform(1, 8, n)  # 收入单位：万元
    a = rng.binomial(1, 0.5, n)
    income = (0.8*pre_income + 0.08*education + 0.02*(age-35)
              + 0.6*a + rng.normal(0, 1, n))
    logit = -0.4 + 0.3*(pre_income-4.5) + 0.06*(education-13.5) + 0.4*a
    employed = rng.binomial(1, 1 / (1 + np.exp(-logit)))
    return pd.DataFrame(dict(A=a, age=age, education=education, pre_income=pre_income,
                             income=income, employed=employed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", type=Path)
    source.add_argument("--demo", action="store_true")
    source.add_argument("--make-demo", type=Path,
                        help="只生成并保存模拟 CSV，不进行估计；已有文件不覆盖")
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).resolve().parent / "sbw-application-results")
    args = parser.parse_args()
    if args.make_demo:
        if args.make_demo.exists():
            parser.error("目标 CSV 已存在；请换一个文件名，或直接用 --csv 读取")
        args.make_demo.parent.mkdir(parents=True, exist_ok=True)
        demo_data().to_csv(args.make_demo, index=False, encoding="utf-8-sig")
        saved = pd.read_csv(args.make_demo)
        print(f"已保存并重新读取 {len(saved)} 行、{len(saved.columns)} 列：{args.make_demo}")
        print(saved.head().to_string(index=False))
        return
    data = demo_data() if args.demo else pd.read_csv(args.csv)
    summary, weighted, balance, draws, diagnostics = run_analysis(data, args.bootstrap)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.demo:
        data.to_csv(args.out / "demo-trial.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.out / "effects.csv", index=False, encoding="utf-8-sig")
    weighted.to_csv(args.out / "weighted-data.csv", index=False, encoding="utf-8-sig")
    balance.to_csv(args.out / "balance.csv", index=False, encoding="utf-8-sig")
    np.savetxt(args.out / "bootstrap.csv", draws, delimiter=",",
               header=",".join(METRICS), comments="")
    report = dict(python=platform.python_version(), numpy=np.__version__,
                  scipy=scipy.__version__, pandas=pd.__version__,
                  bootstrap_repetitions=args.bootstrap, bootstrap_seed=20260910,
                  failed_replicates=0, weight_diagnostics=diagnostics,
                  scope="independent individual randomization; complete common sample")
    (args.out / "diagnostics.json").write_text(json.dumps(report, indent=2) + "\n")
    print(summary.to_string(index=False))
    print("\n权重诊断：", json.dumps(diagnostics, ensure_ascii=False))
    print("输出目录：", args.out.resolve())


if __name__ == "__main__":
    main()
