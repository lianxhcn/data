# 用两张小网络练习五种中心性

本目录是连享会推文《朋友多，就更有影响力吗？用两张小网络手算五种中心性》的配套练习材料。读者可在 GitHub 上直接查看边表、Python 代码和逐节点结果，也可下载后在本地重新计算。

## 1. 目录结构

```text
agent-make-net-data/
├─ README.md
├─ requirements.txt
├─ code/
│  └─ centrality_demo.py
├─ data/
│  ├─ directed_edges.csv
│  └─ undirected_edges.csv
└─ results/
   ├─ betweenness_sensitivity.csv
   ├─ pagerank_iterations.csv
   └─ undirected_centrality_results.csv
```

## 2. 文件说明

- `data/undirected_edges.csv` 包含 11 个节点、12 条无向边，用于计算度、中介、接近和特征向量中心性。
- `data/directed_edges.csv` 包含 8 个节点、9 条有向边，用于比较入度与 PageRank。
- `code/centrality_demo.py` 读取两份边表，计算五种中心性，并完成增加 `E-G` 旁路的中介中心性敏感性实验。
- `results/undirected_centrality_results.csv` 保存无向网络的逐节点结果和手算所需的中间量。
- `results/betweenness_sensitivity.csv` 对比原网络与增加 `E-G` 后 B 的中介中心性。
- `results/pagerank_iterations.csv` 保存 PageRank 初值、前两轮迭代值和收敛值。

## 3. 本地运行

建议使用 Python 3.10 或更高版本。进入本目录后执行：

```bash
python -m pip install -r requirements.txt
python code/centrality_demo.py
```

脚本会重写 `results/` 中的 3 份 CSV。如果只想查看结果，可直接在 GitHub 上打开这些 CSV，无需安装 Python。

## 4. 应当得到什么

脚本运行后，终端应显示：

- 度中心性最高的节点是 A，结果为 0.4。
- 中介中心性最高的节点是 B，结果约为 0.485185。
- 接近中心性最高的节点是 C，结果约为 0.476190。
- 特征向量中心性最高的节点是 D，结果约为 0.446531。
- 增加 `E-G` 后，B 的度仍为 3，中介中心性由约 0.485185 降至 0.151852。
- 有向网络中 A 的入度最高，G 的 PageRank 最高，收敛值约为 0.328731。

## 5. GitHub 在线阅读

推送完成后，可通过以下目录访问全部材料：

<https://github.com/lianxhcn/data/tree/main/blog/agent-sna-data/agent-make-net-data>

直接链接：

- [Python 代码](https://github.com/lianxhcn/data/blob/main/blog/agent-sna-data/agent-make-net-data/code/centrality_demo.py)
- [无向网络边表](https://github.com/lianxhcn/data/blob/main/blog/agent-sna-data/agent-make-net-data/data/undirected_edges.csv)
- [有向网络边表](https://github.com/lianxhcn/data/blob/main/blog/agent-sna-data/agent-make-net-data/data/directed_edges.csv)
- [无向中心性结果](https://github.com/lianxhcn/data/blob/main/blog/agent-sna-data/agent-make-net-data/results/undirected_centrality_results.csv)
- [中介中心性敏感性结果](https://github.com/lianxhcn/data/blob/main/blog/agent-sna-data/agent-make-net-data/results/betweenness_sensitivity.csv)
- [PageRank 迭代结果](https://github.com/lianxhcn/data/blob/main/blog/agent-sna-data/agent-make-net-data/results/pagerank_iterations.csv)

中心性是网络结构的描述性测量。在实证研究中，边的方向、权重、网络边界和指标选择仍需由研究者根据机制判断。
