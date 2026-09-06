# Ferrara 2026：LLM 数据构造离线教学材料

配套推文：**AI 怎样把原始材料变成研究数据？从历史报纸到实证分析**。本目录提供 8 条教学文本、标注规则、空白人工表、离线接口检查和两张教学图。

[下载本目录的精简 ZIP](https://github.com/lianxhcn/data/raw/refs/heads/main/blog/Ferrara-2026-LLM/Ferrara-2026-LLM.zip)。解压后进入唯一的 `Ferrara-2026-LLM/` 文件夹即可运行，不必下载整个 data 仓库。

**全部企业、事件、预期标签和数值图均为教学构造。** 本材料不是 Ferrara 原作者复现包，不包含真实模型响应或独立人工验证结果。运行本目录不需要 API 密钥，也不会发起模型调用。

## 1. 文件说明

| 文件 | 用途 |
| --- | --- |
| `04-assets/materials.csv` | 8 条教学文本，以 document_id + entity_id 为记录键 |
| `04-assets/codebook.md` | implemented、planned、no_evidence、uncertain 四分类规则 |
| `04-assets/expected-demo-labels.csv` | 编写者案例答案，只用于离线接口，不是人工金标准 |
| `code/run_offline.ps1` | Windows 一键离线入口 |
| `code/01_check_inputs.py` | 识别键、空文本、发布日期、类别与来源散列检查 |
| `code/02_prepare_annotation.py` | 生成空白人工表与 synthetic_fixture，并检查离线缓存 |
| `code/03_evaluate.py` | 评估接口及独立教学矩阵的确定性核对 |
| `code/04_make_figures.py` | 用给定教学数值绘图 |
| `code/check_acceptance.py` | 重复键、缺失、失败、零分母等 11 项关键风险检查 |
| `outputs/` | 预生成的 3 份 CSV 与 2 张 PNG；运行后会增加检查报告 |
| `figs/uploaded-images.md` | 推文实际使用的图片链接 |

## 2. 在 Excel 中打开 CSV

本目录所有 CSV 均为 **UTF-8 with BOM**，便于 Windows Excel 识别中文；Python 使用 `encoding="utf-8-sig"` 读取。原始数据的日期字符串保持 `2025-06-01`，Excel 可能按本机显示格式呈现为 `2025/6/1`。

如果此前打开的是乱码旧版本，请关闭旧窗口，再打开本目录的新文件。不要从仍显示乱码的旧窗口保存覆盖新文件。若某个 Excel 版本仍未自动识别，可用“数据 → 从文本/CSV”导入，并选择 UTF-8 (65001)。日期和识别键需要原样保留时，在导入时把相应列指定为文本。

本次修复仅为原始 CSV 增加 BOM；8 条记录、中文原文、日期及预期标签逐字段保持一致。生成脚本同样使用 UTF-8 with BOM 写出 CSV。

## 3. 最小运行步骤

本次实际验证：Windows，Python 3.11.14，matplotlib 3.10.9、NumPy 2.4.2、Pillow 12.3.0 (2026-09-06)。运行输入检查、盲化和评估只需要 Python 标准库；绘图需要上述依赖和中文字体，本机使用 Microsoft YaHei。

在已经配置 Python 的 Windows 电脑上，先在本目录建立项目虚拟环境并安装依赖：

```powershell
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r code/requirements.txt
& .\code\run_offline.ps1
```

上述 `py` 需要 Windows Python 启动器；没有 `py` 时，可用已安装的 Python 命令替代。总入口优先使用项目 `.venv`；没有 `.venv` 时，可使用本机已有 `PYTHON_EXE` 环境变量。这里没有固定任何开发机绝对路径。

在其他系统中，可从本目录使用已安装依赖的 Python 依次运行：

```text
python code/01_check_inputs.py
python code/02_prepare_annotation.py
python code/03_evaluate.py
python code/check_acceptance.py
python code/04_make_figures.py
```

这些命令未在其他操作系统实测；绘图还需安装脚本支持的中文字体。

## 4. 结果看哪里

- `outputs/input-audit.md`：应显示输入 8 条、删除 0 条、检查通过。来源 SHA 清单仅覆盖随包的 3 个输入文件。
- `outputs/human-annotation.csv`：人工标签、证据、理由、标注人及规则版本留空。真实独立标注时只给标注者规则和该表，不提供答案或 fixture。
- `outputs/demo-predictions.csv`：`origin=synthetic_fixture`、`request_status=not_run`，直接复制教学答案，不能作为模型效果。
- `outputs/evaluation.json`：当前有效人工—模型配对为 0，状态 `NOT_EVALUATED`，效果指标为 null；空分歧表不代表人机一致。
- `outputs/teaching-metrics.json`：独立 100 篇教学矩阵 [[15,5],[10,70]]，准确率 0.85、精确率 0.60、召回率 0.75、F1=2/3。此矩阵独立于 8 条材料。
- `outputs/acceptance-checks.json`：11 项关键风险检查。内部测试标签为内存中的合成测试数据，没有代替人工标注。

重复运行会保留已存在且输入版本一致的人工表；一旦填写了人工表，空表验收将不再通过，应另存标注并单独执行评估。输入、日期、规则和配置变化会使离线缓存失效。缓存不代表模型调用，线上响应解析与付费运行不在本目录实现。

## 5. 教学图

行人工标签、列模型标签；橙色格是漏判，蓝色格是假阳性。

![100 篇教学文章的混淆矩阵，非模型实测](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/ferrara-ai-fig01-confusion-20260906-224420.png)

A/B 的正类报道数为 3/2，独立部署事件数为 1/2，至少一次证据为 1/1。去重后分母未知，不计算去重后占比。

![企业 A 与 B 在三种汇总口径下的教学比较](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/ferrara-ai-fig02-aggregation-20260906-224420.png)

这两张 PNG 也保存在 `outputs/`，可离线查看。脚本重画只生成新的本地文件，不自动上传或覆盖图床。

## 6. 来源与使用边界

Ferrara, A. (**2026**). A practitioner's guide to using large language models and generative AI in economic history. *RFBerlin Discussion Paper*, 171/26. [Link](https://www.rfberlin.com/wp-content/uploads/2026/06/26171-1.pdf), [PDF](https://www.rfberlin.com/wp-content/uploads/2026/06/26171-1.pdf), [Google](<https://scholar.google.com/scholar?q=A+Practitioner%27s+Guide+to+Using+Large+Language+Models+and+Generative+AI+in+Economic+History>).

[作者复现材料 V2 入口](https://doi.org/10.3886/E249897V2)在本次环境中返回 HTTP 403 (2026-09-06)，未下载或运行。本文自编教学流程的通过不等于完成作者复现，也不能替代真实样本和独立人工验证。

本目录自编代码与教学材料沿用 data 仓库已有的 [MIT 许可](https://github.com/lianxhcn/data/blob/main/LICENSE)。第三方论文仅给出来源链接，不复制全文；其权利不因本仓库许可改变。精简 ZIP 附带仓库原始 LICENSE 文本。
