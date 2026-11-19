# 三重差分 (DDD) 系列推文：复现材料

本目录存放连享会「三重差分 (DDD)」系列推文的可复现数据与 Stata 脚本。系列共 4 篇，由浅入深，从 2×2×2 的基本设定讲到交错处理下的估计：

1. 《三重差分 (DDD) 之一：到底在估什么》
2. 《三重差分 (DDD) 之二：什么时候会失效》
3. 《三重差分 (DDD) 之三：Stata 实现与结果呈现》
4. 《三重差分 (DDD) 之四：交错处理下的估计》

各篇材料按序号放在独立子文件夹中，后续篇目发布后陆续补充。

## 目录结构

```text
ddd-triple-diff/
  README.md
  checksums.sha256
  01-three-uses/
    code/
      01_dgp.do           # 生成教学数据 ddd_sim.dta
      01_verify.do        # 核验八格均值、三重交互回归与两步法
      01_sample_size.do   # 样本量 Monte Carlo 模拟
    data/
      ddd_sim.dta         # 2 省 × 2 组 × 2 期，每格 1 250，共 10 000 个观测
    logs/                 # 三个 do 文件对应的运行日志
  02-diagnostics/
    code/
      01_event_study.do   # 事件研究：差分平行趋势成立与被破坏两场景
      02_composition.do   # 构成效应：零效应下的伪三重差分
    data/
      event_results.csv   # 事件研究各年系数与标准误
      event_results.dta
      composition_results.csv  # 朴素与基线分组两种估计
    logs/                 # 两个 do 文件对应的运行日志
  03-stata-workflow/
    code/
      01_three_specs.do   # 三种写法对照：手工三重交互、两个 DD 相减、两步法与手动 bootstrap
      02_event_study.do   # 多期面板事件研究：基准年、预趋势检验与动态效应
      03_inference_sim.do # 少簇推断模拟：聚类稳健与野生聚类 bootstrap 拒绝率
    data/
      ddd_sim.dta         # 沿用第一篇的 2×2×2 教学数据，10 000 个观测
      boot_twostep.dta    # 500 次手动 bootstrap 的 DDD 估计
      event_ddd.dta       # 事件研究各年系数与标准误
      event_ddd.csv
      sim_cluster.dta     # 聚类稳健拒绝率明细 (200 次 × 5 设定)
      sim_wild.dta        # 野生聚类 bootstrap 拒绝率明细 (100 次 × 4 设定)
```

## 数据说明

`ddd_sim.dta` 为模拟数据，包含 6 个变量：`id`、`province` (试点省 / 非试点省)、`group` (B 组受政策影响 / A 组不受政策影响)、`post` (政策实施后)、`y` (结果变量)。

数据生成过程 (DGP) 为：

```text
y = 1.0 + 0.20*province + 0.30*group + 0.50*post
    + 0.30*province*post + 0.10*province*group*post + epsilon,  epsilon ~ N(0, 0.35^2)
```

其中三重交互项的真值为 0.10，`province*post` 的 0.30 表示两省之间与政策无关的共同增长差异。随机种子为 98。

第二篇的两个模拟分别对应两类失效，均不依赖第一篇的数据：

- `01_event_study.do`：2 省 × 2 组 × 6 年，每格 800 人，共 19 200 个观测，政策在第 3 年后实施。场景 A 差分平行趋势成立，场景 B 给试点省 B 组加一项每年递增 0.10、与政策无关的线性趋势；两场景真实政策效应均为 0.10，随机种子为 202。
- `02_composition.do`：2 省 × 2 期，6 000 个个体追踪两期，共 12 000 个观测。政策不影响任何个体结果，但试点省 A 组原有 600 名低类型个体在政策后重划入 B 组，真实三重差分为零，随机种子为 313。

第三篇在同一份 `ddd_sim.dta` 上跑通并对照三种 Stata 写法，同时给出事件研究与少簇推断模拟：

- `01_three_specs.do`：手工三重交互 (饱和回归与两种 `reghdfe` 吸收)、两个子样本 DD 再相减 (`suest` 联合检验)、先构造相对结果再回归的朴素两步法，以及用 `postfile` 手动实现的 500 次 bootstrap。三种写法点估计均为 0.100074，完整方差口径标准误为 0.0281，朴素两步法的 0.0199 属偏窄口径，bootstrap 种子为 303。
- `02_event_study.do`：2 省 × 2 组 × 8 年，每格 800 人，共 25 600 个观测，政策在第 4 年后实施。以第 4 年为基准年，预趋势联合检验给出 $F(3,25568)=0.16$，$p=0.9245$，政策后动态效应为 0.069、0.114、0.126、0.102，随机种子为 236。
- `03_inference_sim.do`：31 省 × 2 组 × 6 期 × 每格 100 人，共 37 200 个观测，原假设为真。聚类稳健拒绝率随处理省数由 20 降到 1 而从 0.030 升至 0.685，野生聚类 bootstrap 在处理省数为 10、5、2、1 时拒绝率为 0.030、0.060、0、0，处理身份在种子 17 下一次性随机排序确定。

## 运行方式

1. 首次运行前，打开对应篇目 `code/` 下的 do 文件，把开头的 `local root` 改为本机该文件夹的完整路径 (使用正斜杠)。
2. 第一篇依次运行：

```stata
do code/01_dgp.do          // 生成 data/ddd_sim.dta
do code/01_verify.do       // 核验：DDD = 0.100，稳健标准误 0.028
do code/01_sample_size.do  // 样本量模拟，耗时较长
```

第二篇依次运行：

```stata
do code/01_event_study.do  // 事件研究两场景，导出 event_results
do code/02_composition.do  // 构成效应，导出 composition_results
```

第三篇依次运行：

```stata
do code/01_three_specs.do    // 三种写法对照与手动 bootstrap，约 12 秒
do code/02_event_study.do    // 事件研究，导出 event_ddd
do code/03_inference_sim.do  // 少簇推断模拟，完整运行耗时较长
```

第一篇和第二篇的脚本在 Stata 19 下测试通过，仅使用 Stata 官方命令，无需安装外部包。第三篇需要先安装外部命令 `reghdfe`、`ftools`、`boottest`、`estout` (可选 `coefplot`)，安装命令为：

```stata
ssc install reghdfe, replace
ssc install ftools, replace
ssc install boottest, replace
ssc install estout, replace
```

## 校验

`checksums.sha256` 记录本目录全部文件的 SHA-256 摘要。下载后可在 PowerShell 中运行以下命令核对完整性：

```powershell
Get-FileHash -Algorithm SHA256 (Get-ChildItem -Recurse -File)
```
