# 基准结果

固定随机种子 `20260811` 下，预期结果为：

- 节点数：30。
- 有向边数：88。
- 孤立节点：2 (`S29`、`S30`)。
- 密度：0.1011。
- 互惠性：0.2955。
- 弱连通分量：3。

其余排名以 `outputs/reports/analysis_results_zh.md` 和 `outputs/tables/node_metrics.csv` 为准。运行 `python run_all.py` 后，`output_validation.md` 应显示全部检查通过。
