# AI Agent 社会网络分析复现附件

本目录对应连享会推文《一句话完成社会网络分析？我让 AI Agent 实测了一遍》。它用 30 名博士生的教学模拟数据演示：检查两张关系表、构造有向加权网络、计算中心性与结构洞指标、识别社群、生成网络图，并导出 Stata 数据。

数据完全由 `scripts/generate_data.py` 使用固定随机种子生成，不是真实调查数据，也不能支持因果结论。

## 1. 目录

```text
data/       模拟节点表与边表
scripts/    数据生成、验证、分析和输出核验
prompts/    实际主提示词与三轮追问
outputs/    基准图形、表格和报告
stata/      Stata 19 导入示例
docs/       数据字典、方法说明和基准结果
run_all.py  一键运行入口
```

## 2. Windows 环境检查

建议使用 Python 3.11 或 3.12：

```powershell
where.exe python
python --version
python -m pip --version
```

若项目已经有可用环境，直接沿用，不必新建多个虚拟环境。

## 3. 安装与运行

在本目录打开 PowerShell：

```powershell
python -m pip install -r requirements.txt
python run_all.py
```

基准环境运行约需数秒。程序依次生成数据、验证数据、分析网络和验证输出。任何数据检查失败都会停止，不会静默删除异常值。

## 4. 查看结果

- `outputs/reports/data_validation.md`：字段、缺失、自环、重复边和孤立节点检查。
- `outputs/reports/analysis_results_zh.md`：关键统计量和排名。
- `outputs/reports/output_validation.md`：输出文件、数值、图片尺寸和基准检查。
- `outputs/tables/node_metrics.csv`：节点指标表。
- `outputs/tables/node_metrics.dta`：Stata 19 可读取的数据。
- `outputs/figures/network.png`：推文使用的正式网络图。

图中只显示 `weight >= 2` 的边以减少拥挤，所有指标仍基于完整网络。

## 5. Stata

从附件根目录启动 Stata，再运行：

```stata
do "stata/import_network_metrics.do"
```

脚本读取 `.dta`，添加变量标签，并按 `weighted_indegree` 降序列出前 10 名。路径均为相对路径。

## 6. 常见问题

- 中文路径若在旧终端中显示乱码，可先设置 `$env:PYTHONUTF8="1"` 和 `$env:PYTHONIOENCODING="utf-8"`。
- 中文字体缺失时，Matplotlib 会回退到 `SimHei` 或 `DejaVu Sans`；节点编号仍能正常显示。
- 必须从附件根目录运行 `python run_all.py`，不要单独复制脚本到其他目录。
- 依赖冲突时优先使用已有环境；确需隔离时，只在本目录创建一个 `.venv`。
- 图形布局固定随机种子。不同 Matplotlib 字体环境可能造成少量文字位置差异，但关键指标应一致。

## 7. 结果边界

代码可复现只说明相同输入和设定能生成相同输出。关系方向、网络边界、权重转换、社群算法和结构洞指标是否适合论文，仍需研究者结合理论判断。网络指标与结果变量相关，也不等于网络位置具有因果效应。

推文正式链接将在附件进入远程 `main` 后补充并核验。
