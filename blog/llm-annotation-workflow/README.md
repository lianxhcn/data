# LLM 生成的标签，能直接放进回归吗？

陈崇立 (暨南大学) 推文的配套资源。这里提供一套可直接运行的最小工作流，用 24 条中文教学数据和 4 组提示词，先比较各提示词的分类误差，再比较这些标签进入同一 logit 回归后的核心系数，从而判断研究结论在多大程度上依赖标注环节的选择。

核心观点是：LLM 返回的 0/1 并不是真实变量，而是特定模型与提示词下的估计值。标签标得准，并不自动保证回归结论可靠；前者看分类误差，后者看核心系数的符号、大小和显著性是否稳定。

## 文件用途

| 文件 | 用途 |
| --- | --- |
| [llm_annotation_workflow.py](llm_annotation_workflow.py) | 主脚本：标注、分类评估、logit 回归与系数敏感性图 |
| [requirements.txt](requirements.txt) | Python 依赖清单 |
| [environment.example](environment.example) | 环境变量示例，复制后填入自己的 key |
| [illustrative_demo.csv](illustrative_demo.csv) | 24 行中文教学数据，含人工标签 `HUMAN` |
| [prompt_variants_zh.csv](prompt_variants_zh.csv) | 4 组中文提示词 (零样本、判定规则、边界案例、结构化推理) |

## 运行方法

先创建独立环境并安装依赖：

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

第一步用 `mock` 模式离线跑通整条管线，不调用 API、不产生费用。`mock` 仅根据文本关键词打标签，用于验证数据读取、指标计算、回归和作图是否正常：

```bash
python llm_annotation_workflow.py --provider mock --data illustrative_demo.csv --prompts prompt_variants_zh.csv --formula "success ~ LLM_LABEL + lgoal + C(year) + C(subcategory)" --output-dir output/mock_demo
```

在 24 行教学数据上，mock 结果为：准确率 0.667、误报率 FPR 0、漏报率 FNR 0.667；logit 核心系数 -0.63、标准误 1.56、p 值 0.69、95% 置信区间 [-3.68, 2.42]，区间跨越 0。四个点估计重合，是因为 mock 不读取提示词内容，并非提示词没有作用。

第二步设置 API key 后切换到真实调用。脚本通过 OpenAI 兼容接口访问模型，`--max-rows` 和 `--prompt-limit` 用于控制小样本试跑的调用量：

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "你的 API key"
$env:LLM_MODEL = "服务商当前可用模型名"

python llm_annotation_workflow.py --provider openai --data illustrative_demo.csv --prompts prompt_variants_zh.csv --model $env:LLM_MODEL --formula "success ~ LLM_LABEL + lgoal + C(year) + C(subcategory)" --max-rows 24 --prompt-limit 4 --output-dir output/real_demo
```

脚本会缓存每次 API 的原始返回，避免中断后重复花费，也让每条标签可回溯到具体文本、提示词和模型。

## 数据字段

`illustrative_demo.csv` 采用 UTF-8 编码，各字段如下：

| 字段 | 含义 |
| --- | --- |
| `id` | 观测标识，1–24 |
| `text` | 待标注的项目文本 |
| `HUMAN` | 人工标签，1 表示有社会或环境收益，0 表示无 |
| `success` | 回归因变量，1 表示众筹成功，0 表示失败 |
| `lgoal` | 控制变量，筹资目标的对数 |
| `year` | 控制变量，项目年份 |
| `subcategory` | 控制变量，项目子类别 |

## 论文与方法来源

Carlson, N. A., & Burbano, V. C. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. *Strategic Management Journal, 47*(3), 699–725. [期刊论文](https://doi.org/10.1002/smj.70023)；[作者代码仓库](https://github.com/LLMAnnotationResearch/llm-annotation-framework)。

推文另介绍 Egami et al. 关于预测变量进入统计分析的一般框架：[2024 工作论文](https://naokiegami.com/paper/dsl_ss.pdf)。本目录不执行 DSL 校正，也不含论文的真实众筹数据。
