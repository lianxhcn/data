# 因果推断的三大识别假设：复现材料

本目录存放连享会推文《因果推断的三大识别假设》（作者：连小白）的可复现脚本。推文在潜在结果框架下讲解一致性、强可忽略性与稳定单元处理值假设 (SUTVA)，例子覆盖就业培训、教育回报与产业政策。

## 目录结构

```text
causal-assumptions/
  README.md
  repo-plan.yml
  scripts/
    make_figures.py    # 用 matplotlib 绘制概念配图
    upload_oss.py      # 用 oss2 把配图直传到阿里云 OSS
    _gen_related.do    # 用 Stata 的 lianxh 命令检索相关推文
```

## 配图

正文配图托管在阿里云 OSS（bucket `fig-lianxh`，区域 `oss-cn-shenzhen`）：

- 图 1（偏差分解）：`https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/lianxiaobai-causal-assumptions-fig1-202611171751.png`
- 图 2（倾向得分重叠）：`https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/lianxiaobai-causal-assumptions-fig2-202611171751.png`

## 运行方式

- 绘制配图：`python scripts/make_figures.py`。依赖 matplotlib，脚本使用 Agg 无头后端，需要本机装有中文字体。
- 上传 OSS：`python scripts/upload_oss.py`。依赖 oss2，凭证从本机 PicGo 配置 `data.json` 读取，脚本内不硬编码密钥。
- 检索相关推文：在 Stata 中运行 `scripts/_gen_related.do`，需要先安装 `lianxh` 命令（`ssc install lianxh, replace`）。

## 说明

本目录只包含脚本与说明，不含原始数据和大体积图片二进制；图片以 OSS 链接为准。具体发布过程见原项目《日志.md》。
