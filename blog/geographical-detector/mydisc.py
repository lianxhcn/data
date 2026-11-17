"""地理探测器连续变量离散化（Python 实现）
equal/natural/quantile 基于 mapclassify；geometric/sd 为手写，与 R GD 对齐。
"""
import numpy as np
import mapclassify as mc


def _funx(x, n):
    x = np.asarray(x, float)
    x1 = x + 1.0
    b = (x1.max() / x1.min()) ** (1.0 / (n - 1))
    x0 = x1.min() / b
    return np.array([b ** i * x0 - 1.0 for i in range(1, n + 1)])


def _geometric_breaks(var, n):
    var = np.asarray(var, float)
    if var.min() >= 0:
        return _funx(var, n)
    rng = np.abs([var.min(), var.max()])
    kmax = int(np.argmax(rng))
    kmin = 1 - kmax
    n2 = int(np.floor((n + 1) / (1 + rng[kmin] / rng[kmax])))
    n1 = n + 1 - n2
    itv1 = _funx([0, rng[kmin]], n1 + 1)[1:]
    itv2 = _funx([0, rng[kmax]], n2 + 1)[1:]
    if kmin == 0:
        return np.concatenate([-itv1[::-1], itv2])
    return np.concatenate([-itv2[::-1], itv1])


def _sd_breaks(var, n):
    var = np.asarray(var, float)
    mu, sd = var.mean(), var.std(ddof=1)
    seqa = np.arange(2000, 0, -2)
    itv, m = np.array([]), n
    while len(itv) < n + 1:
        m += 1
        seqb = (m - 1) - seqa
        seqb = seqb[seqb >= 0]
        step = 2.0 if m <= 7 else 4.0
        b1 = (mu - seqb / step * sd)[::-1]
        b2 = mu + seqb / step * sd
        b1 = b1[b1 > var.min()]
        b2 = b2[b2 < var.max()]
        itv = np.concatenate([[var.min()],
                              np.unique(np.concatenate([b1, b2])),
                              [var.max()]])
    return itv


_CLASS = {"equal": mc.EqualInterval, "natural": mc.FisherJenks,
          "quantile": mc.Quantiles}


def disc_breaks(x, method, n):
    """返回 n 类对应的各类上界（n 个，含最大值、不含最小值）。"""
    x = np.asarray(x, float)
    if method in _CLASS:
        return _CLASS[method](x, k=n).bins
    if method == "geometric":
        return _geometric_breaks(x, n)[1:]
    if method == "sd":
        return _sd_breaks(x, n)[1:]
    raise ValueError(f"未知方法：{method}")


def disc_labels(x, method, n):
    """返回 0 起始的整数分层标签。"""
    x = np.asarray(x, float)
    return np.digitize(x, disc_breaks(x, method, n), right=True)
