<!--
建议标题：ReproAI：一套面向 Stata、R 和 Python 复现包的提交前预检工具
备选标题：复现包提交前怎么查？ReproAI 的功能、工作流与使用边界
作者信息：丁闪闪 (连享会)
稿件状态：最终待发
资料核对日期：2026-08-23
说明：本文介绍 ReproAI 的公开功能与边界；Stata 受控实测另文发布。
-->


> **作者：** 丁闪闪 (连享会)<br>
> **邮箱：** <lianxhcn@163.com>

&emsp;

- **Title**: ReproAI：一套面向 Stata、R 和 Python 复现包的提交前预检工具
- **Keywords**: ReproAI, Stata, R, Python, 复现包, 静态检查


一套代码在作者电脑上能够运行，不等于它已经是一个可以交付的复现包。换一台电脑以后，绝对路径可能失效，辅助脚本可能缺失，随机过程可能没有固定种子，README 可能没有说明入口和依赖，论文中的表图也未必能追溯到具体代码。这些问题不一定涉及复杂的计量方法，却会让数据编辑、审稿人和后续复现者耗费大量时间。

[ReproAI](https://reproai.org/) 试图处理的正是这个环节。更准确地说，它不是“自动复现论文”的按钮，而是一套面向作者的复现包提交前预检工具。研究者把包含代码、数据说明和输出文件的目录交给它，ReproAI 会进行静态扫描，按优先级提出修改建议，在安全边界允许时改写一个副本，并可按需执行一次运行冒烟测试。官方公开资料明确列出对 Stata、R 和 Python 复现包的支持。

本文配套的 Stata 受控测试材料已经公开在 [lianxhcn/data 的 ReproAI Stata 项目](https://github.com/lianxhcn/data/tree/main/blog/reproai-stata)。目录中保留了已独立运行的参考包、预先冻结缺陷的测试包、ReproAI 原始报告、检测矩阵和运行记录；读者可以直接核对本文所说的工作流，也可以进一步查看第二篇推文中的实测结果。

本文先把 ReproAI 的定位、功能、安装方式和使用边界讲清楚。第二篇推文基于上述材料，报告一个人为构造的 Stata 缺陷包中，它实际能发现什么、会漏掉什么。两篇文章发布后，都可通过 [ReproAI 站内搜索](https://www.lianxh.cn/search.html?s=reproai) 查找。

![图 1 ReproAI 官网首页：工具定位、主要命令与 P0-P4 优先级示例](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/reproai-overview-fig01-home-20260824-214221.jpg)

> 图 1：ReproAI 官网首页，截取于 2026 年 8 月 23 日。来源：[ReproAI 官网](https://reproai.org/)。

## 1. 从“能运行”到“能交付”

论文复现通常包含两个不同层次的问题。

第一个层次是科学问题：数据处理是否合理，样本筛选是否透明，模型设定和识别策略是否成立，表格中的数字能否支持正文结论。第二个层次是复现包工程问题：文件是否齐全，运行顺序是否明确，路径能否迁移，软件环境是否记录，随机过程能否重现，生成的表图能否被定位。

ReproAI Prep 主要处理第二个层次。它希望在作者公开材料或向期刊提交复现包之前，先发现那些会增加下游复现成本的问题。这个定位很重要：它可以帮研究者整理和预检材料，但不会代替研究者判断样本、模型和结论。

从工作流程看，ReproAI 更适合放在下面这个位置：

```text
研究代码基本完成
      ↓
整理复现包并撰写 README
      ↓
ReproAI Prep 静态检查与副本修订
      ↓
在干净环境中独立运行并核对结果
      ↓
提交期刊或公开存档
```

因此，ReproAI 不是复现工作的终点，而是把“作者机器上的工作目录”整理成“他人更容易接手的复现包”的中间环节。

## 2. ReproAI Prep 是什么？

ReproAI Prep 由两部分组成：一部分是安装在 Claude Code 或 OpenAI Codex 中的插件，负责接收研究者的要求、解释报告并协助修改；另一部分是 Python 3.10 及以上版本运行的确定性检查引擎，负责规则、期刊配置和结构化报告。这样的分工意味着，问题是否触发规则并不完全交给大语言模型临场判断，语言模型主要承担解释、生成修改方案和组织工作流。

官方 GitHub README 还把 ReproAI 品牌分成两个相互独立的组件：

- **ReproAI Prep**：作者端的预检和材料整理工具，也是当前公开 GitHub 仓库的内容；
- **ReproAI Cert**：按官方说明，它是下游认证组件，用于更严格的执行追踪和认证流程，另行维护。

本文只介绍公开可核查的 ReproAI Prep。不要因为产品名称中有 “Repro” 或官方说明中出现 “Cert”，就把 Prep 的静态检查写成“已经通过复现认证”。二者在工作流中的位置和证据强度并不相同。

截至 2026 年 8 月 23 日，ReproAI Prep 的公开仓库采用 [MIT License](https://github.com/reproai/reproai/blob/main/LICENSE)，其 [README](https://github.com/reproai/reproai#what-it-checks-rule-set) 列出 45 条作者可预防规则，覆盖包结构、代码写法、运行环境和期刊材料规范。规则和期刊配置会更新，正式使用时应以本机安装版本和当前官方文档为准。

## 3. 它不仅支持 Stata，也面向 R 和 Python

ReproAI 官方把输入对象写成 “Stata / R / Python replication package”。也就是说，它检查的是完整复现包，而不是只检查某一种语言中的单个脚本。

| 工具 | 官方支持状态 | 本文如何处理 |
|---|---|---|
| Stata | 官方明确列出 | 另文使用 Stata 缺陷包做独立实测 |
| R | 官方明确列出 | 本文介绍官方功能，不声称已经独立测试 |
| Python | 官方明确列出 | 本文介绍官方功能，不声称已经独立测试 |

三种语言的语法不同，但复现包会遇到许多共同问题：入口脚本不清楚、文件依赖断裂、路径写死、软件版本未记录、输出没有落盘、表图与代码缺少对应关系、README 不符合目标期刊要求。ReproAI 的文件清单、依赖图、结果映射和期刊合规检查主要针对这些跨语言问题。

具体规则仍会带有语言特征。例如，官方公开规则提到 Stata 的版本声明、用户命令和 `merge` 写法，也提到已经移除的 R 包。公开 README 虽然明确列出 Python 支持，但没有像 Stata 那样展开同等数量的 Python 专属规则示例。比较稳妥的理解是：ReproAI 提供一个共同的复现包检查框架，再由规则库识别不同语言中的典型风险；三种语言的具体覆盖范围仍应以当前规则和实际报告为准。

## 4. 四步工作流：检查、排序、修订、运行

ReproAI Prep 的核心工作流可以压缩成四步。

![图 2 ReproAI Prep 的四步工作流与人工判断边界](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/reproai-overview-fig02-workflow-20260824-214221.png)

> 图 2：作者根据 [ReproAI Prep 官方工作流](https://github.com/reproai/reproai#what-it-does) 整理绘制，资料核对日期为 2026 年 8 月 23 日。SVG 源文件随文提供，便于后续修改。

### 4.1 静态检查

`check` 会读取文件清单、脚本依赖、入口、表图输出、孤立文件、规则库和目标期刊配置。官方 README 当前说明，一次检查可生成四类 JSON 报告：项目结构、修改建议、期刊合规情况和风险登记。

静态检查的关键词是“不运行研究代码”。它可以看到脚本引用了一个不存在的文件，也可以发现某个路径写成了本机绝对路径；但仅凭静态文本，它未必能判断数据合并是否符合研究设计。

### 4.2 按优先级给出建议

每项发现会被标记为 P0–P4。P0 表示下游复现成本中的阻断级风险，P4 更接近格式和材料规范。报告还会区分两类问题：`defect` 表示可能实际增加复现失败风险，`normalization` 表示存在一种更标准、更便于交付的写法。

这个区分有助于避免把所有提示都当成“代码错误”。缺失文件与 README 排版不规范显然不是同一等级，研究者应优先处理会改变运行结果或阻断执行的问题。

### 4.3 在副本上修订

`fix` 的设计原则是改写副本，不直接覆盖原始复现包。它只能在语义保持的安全边界内提出或执行修改，再重新检查，并把差异交给作者审阅。是否实际生成副本、修改哪些内容，取决于具体 advisory；涉及数据、样本或随机实现的事项通常仍需作者决定。

“可以修订”不等于“每项都能自动修复”。补充缺失文件、决定随机种子、改变数据回退逻辑或解释样本删除，往往需要作者提供信息。遇到这些问题，负责任的工具应该停止在建议层面，而不是猜测研究者意图。

### 4.4 按需运行冒烟测试

`debug` 是可选的运行步骤。它检查修订副本能否启动、代码是否报错、预期表图是否出现；它不逐项核对论文中的表图、系数或结论。运行发生错误时，官方说明要求工具解释原因、给出选项并让作者决定，而不是静默改写研究逻辑。

除了四个核心命令，`map` 用于把论文中的表图与代码产物对应起来，`update` 用于查看更新方法，`contribute` 可帮助用户整理漏检、误报或新期刊规则，并生成由用户自行确认提交的 GitHub issue。

![图 3 ReproAI 官方仓库对 Stata/R/Python、四步工作流和使用边界的说明](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/reproai-overview-fig03-github-20260824-214221.jpg)

> 图 3：ReproAI 官方 GitHub README 的 “What it does” 部分，截取于 2026 年 8 月 23 日。来源：[ReproAI GitHub](https://github.com/reproai/reproai#what-it-does)。

## 5. 如何安装并开始第一次检查？

最稳妥的入口不是复制一段可能过期的安装命令，而是让 Claude Code 或 Codex 读取官方维护的 `INSTALL_FOR_AI.md`，按当前宿主完成安装，并报告实际版本。可以直接向 AI 助手提出下面的要求：

```text
请安装或更新 ReproAI。读取官方 INSTALL_FOR_AI.md，
按当前宿主的 Claude Code 或 OpenAI Codex 分支执行，
完成官方验证，并报告插件、Python 引擎和规则版本。
```

官方安装说明：[INSTALL_FOR_AI.md](https://github.com/reproai/reproai/blob/main/INSTALL_FOR_AI.md)。

安装后，把工作目录设置为复现包根目录，再调用对应入口。Claude Code 的命令通常采用冒号形式；在 Codex 中，则让助手调用已安装的 ReproAI Skill。不同版本的具体入口应以安装后的说明为准。例如：

```text
# Claude Code 文档中的形式
/reproai:check . --venue aea

# OpenAI Codex 中的自然语言请求
请在当前复现包根目录运行 ReproAI 检查，目标期刊为 AEA。
```

![图 4 ReproAI 官网给出的命令行与桌面应用两种使用方式](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/reproai-overview-fig04-usage-20260824-214221.jpg)

> 图 4：ReproAI 官网的 “How to use” 部分，截取于 2026 年 8 月 23 日。来源：[ReproAI 官网](https://reproai.org/#usage)。

第一次使用时，建议只做三件事：先运行静态检查，阅读 P0 和 P1；再打开结构化报告核对每条建议的文件位置和证据；确认哪些修改不会改变研究含义以后，才在副本上调用修订。不要一开始就要求工具“把所有问题自动改完”。

如果目标期刊已有配置，可以增加相应的 venue 参数。官方示例列出 AEA、Econometric Society、JASA、World Bank、APSR、AJPS 和 JOP 等；期刊要求会变化，提交前仍应回到期刊官网核对最新的数据与代码政策。

## 6. 使用边界：预检不等于复现认证

理解 ReproAI，最关键的不是记住命令，而是区分它提供了什么证据。

| ReproAI Prep 可以提供 | 不能据此推出 |
|---|---|
| 文件、入口和依赖的静态扫描 | 数据构造一定正确 |
| 按优先级整理结构性风险 | 样本限制具有研究依据 |
| 目标期刊材料清单 | 已满足期刊全部实质要求 |
| 在副本上提出或执行安全修改 | 每个问题都能一键修复 |
| 可选冒烟测试与产物检查 | 论文表格中的系数已逐项匹配 |
| 表图与代码的映射建议 | 识别策略和科学结论已经验证 |

官方 README 说得很明确：`check`、`comply` 和 `fix` 属于静态命令，不执行分析；只有用户主动调用 `debug` 时才会运行修订副本，而且它仍只是冒烟测试。ReproAI Prep 不比较论文与程序中的系数，也不签发“可复现”结论。

研究者仍需独立完成至少四类工作：在干净环境中从头运行；将实际输出与论文逐项核对；审查数据处理、样本筛选和模型设定；记录受限数据、软件环境和无法自动验证的步骤。把这些任务省略以后，即使静态报告全部变绿，也不能据此声称研究已经完成复现。

## 7. 官方入口、论文出处与后续实测

### 官方入口

- 官网：[https://reproai.org/](https://reproai.org/)
- GitHub：[https://github.com/reproai/reproai](https://github.com/reproai/reproai)
- 官方 README：[What it does](https://github.com/reproai/reproai#what-it-does)
- 安装说明：[INSTALL_FOR_AI.md](https://github.com/reproai/reproai/blob/main/INSTALL_FOR_AI.md)

### 论文出处

ReproAI 官网建议引用 Xu and Yang ([2026](https://doi.org/10.48550/arXiv.2602.16733)) 的工作论文 *Scaling Reproducibility: An AI-Assisted Workflow for Large-Scale Replication and Reanalysis*。按 [arXiv 论文页](https://arxiv.org/abs/2602.16733)（核对日期：2026 年 8 月 23 日），该文为 v3，2026 年 2 月 17 日首次提交，2026 年 6 月 1 日修订。

需要区分的是，这篇论文研究的是一个更宽的全论文复现工作流，包括材料获取、环境重建、代码执行和论文表格点估计匹配。论文 [摘要](https://arxiv.org/abs/2602.16733) 报告的样本包含 384 项研究和 3,523 个实证模型。这些数字说明作者开展了大规模 AI 辅助复现研究，但不能直接解释为 ReproAI Prep 静态检查的准确率或修复成功率。

### 后续：用 Stata 缺陷包做受控测试

另文使用 Stata 自带的 `auto.dta` 构造一个可公开的小型复现包。我们先把数据导出为 `raw/auto_domestic.csv` 和 `raw/auto_foreign.csv`，再用 `import delimited` 读入并正确 `append`。随后冻结一份缺陷清单，构造带有路径、文件依赖、随机种子、输出映射、README、数据回退和样本透明度等问题的副本，再用 ReproAI 完成检查和修订尝试。

这样的安排可以把两个问题分开：本文回答“ReproAI 官方声称能做什么、边界在哪里”，另文回答“在一个事先写死缺陷的 Stata 小型测试中，它实际上发现了什么”。前者是工具介绍，后者才是独立实测。

### 参考文献

1. ReproAI. (**2026**). *ReproAI Prep: Author-facing replication-package pre-diagnose tool* (version and rule set checked on 2026-08-23). [Link](https://github.com/reproai/reproai), [PDF](), [Google](<https://scholar.google.com/scholar?q=ReproAI+Prep+author-facing+replication-package+pre-diagnose+tool>). [Website](https://reproai.org/), [Install](https://github.com/reproai/reproai/blob/main/INSTALL_FOR_AI.md).
2. Xu, Y., & Yang, L. Y. (**2026**). *Scaling Reproducibility: An AI-Assisted Workflow for Large-Scale Replication and Reanalysis* (arXiv:2602.16733, v3). arXiv. [Link](https://doi.org/10.48550/arXiv.2602.16733), [PDF](https://arxiv.org/pdf/2602.16733), [Google](<https://scholar.google.com/scholar?q=Scaling+Reproducibility%3A+An+AI-Assisted+Workflow+for+Large-Scale+Replication+and+Reanalysis>).

## 8. 相关推文

> 说明：可用 `lianxh 复现` 生成如下推文列表；安装最新版命令为
> `ssc install lianxh, replace`。

  - 林枫, 2024, [社会科学研究复现包中的自述文档模板](https://www.lianxh.cn/details/1451.html).
  - 连享会, 2020, [连享会：论文重现复现网站大全](https://www.lianxh.cn/details/232.html).
  - 汪京, 2024, [Stata代码规范指南](https://www.lianxh.cn/details/1377.html).
  - 丁闪闪, 2026, [代码审计：如何从源头确保你的论文可复现？](https://www.lianxh.cn/details/1739.html).
  - 杨奈特, 2026, [SNAP02-社会网络分析：如何规划我的学习路径？](https://www.lianxh.cn/details/1884.html).
  - 王珞嘉, 2022, [如何永久保存论文中的链接？](https://www.lianxh.cn/details/917.html).
  - 连小白, 2026, [没有 Claude Code，如何实现 Skills？ChatGPT、DeepSeek、豆包](https://www.lianxh.cn/details/1794.html).
  - 连玉君, 陈鑫梅, 2020, [可重复性研究：如何保证你的研究结果可重现？](https://www.lianxh.cn/details/124.html).
  - 郭思媛, 2024, [论文复现时如何与原文作者沟通？](https://www.lianxh.cn/details/1443.html).
  - 马雨驰, 2023, [如何整理一份规范的论文复现文档？](https://www.lianxh.cn/details/1180.html).
