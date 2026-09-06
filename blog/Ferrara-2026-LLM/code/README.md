# 离线脚本

在本目录的父目录执行 `code/run_offline.ps1`；完整安装与输出说明见根目录 README。

路径以脚本自身位置为基准。所有 CSV 用 UTF-8 with BOM 写出、utf-8-sig 读取，组合键、原文和标签不因编码修复改变。

`workflow.py` 是输入检查、CSV、缓存和评估公共接口。四个编号脚本依次执行；`check_acceptance.py` 用合成内存数据检验关键风险，不能视为真实人工验证。

`SHA256SUMS.txt` 仅核对 3 份教学输入；有意修改数据或规则时应记录新版本并重新计算相应 SHA，不静默复用旧缓存。

真实评估接口 (须已有真实来源、规则和输入散列一致的标签)：

```powershell
& .\.venv\Scripts\python.exe code/03_evaluate.py `
    --human outputs/human-annotation-adjudicated.csv `
    --predictions outputs/model-predictions.csv
```

人工表要有实际独立阅读来源声明、匿名标注人、理由和规则版本；模型表要有真实在线来源、请求状态、输入与规则散列。当前包没有在线调用器或原始模型响应。四分类保留 uncertain，二分类排除任一端 uncertain；执行失败、缺失和未匹配键分别统计，分母为零返回 null。

绘图依赖固定在 requirements.txt，仅为已跑通的直接依赖版本，不是全部系统环境锁文件。图像宽 1000 px，使用已有中文字体；没有可用中文字体时直接报错。
