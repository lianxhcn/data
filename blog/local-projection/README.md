# 局部投影法入门：复现材料

本目录存放连享会「局部投影法入门」系列推文（作者：陈点点）的可复现 Stata 脚本。系列共两篇：

1. 《局部投影法入门(1)：加息冲击与脉冲响应》——在时间序列框架下讲解局部投影 (LP)、LP-IV 与脉冲响应；
2. 《局部投影法入门(2)：交错处理与 LP-DID》——在面板框架下讲解双向固定效应的禁止比较问题与 LP-DiD 估计量。

## 目录结构

```text
local-projection/
  README.md
  repo-plan.yml
  code/
    lp1-monetary-irf.do     # 入门一：ivlpirf 官方命令与手写 ivreg2 循环
    lp2-staggered-did.do    # 入门二：模拟数据、TWFE、lpdid 与手写回归
```

## 数据来源

- 入门一使用 Stata 手册自带的 `usmacro3` 数据，脚本通过 `use https://www.stata-press.com/data/r19/usmacro3, clear` 在线读取，无需另行下载；
- 入门二使用模拟数据，由脚本开头的代码生成，真实处理效应已知，可直接检验各估计方法的偏差。

## 运行方式

- 入门一：在 Stata 中运行 `code/lp1-monetary-irf.do`。方法一的 `ivlpirf` 需要 Stata 19；方法二使用 `ivreg2`（`ssc install ivreg2`、`ssc install ranktest`），在 Stata 18 等较早版本即可运行。
- 入门二：在 Stata 中运行 `code/lp2-staggered-did.do`。需要 `reghdfe`（`ssc install reghdfe`、`ssc install ftools`）与 `lpdid`（`ssc install lpdid, replace`）。

## 配图

入门一的三张配图托管在阿里云 OSS（bucket `fig-lianxh`，区域 `oss-cn-shenzhen`）：

- 图 1（误差滚雪球）：`https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/chendiandian-lp-irf-fig1-202611171924.png`
- 图 2（LP 与 VAR 对比）：`https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/chendiandian-lp-irf-fig2-202611171924.png`
- 图 3（LP-IV 脉冲响应）：`https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/chendiandian-lp-irf-fig3-202611171924.png`

## 说明

本目录只包含 Stata 脚本与说明，不含数据和图片二进制：入门一数据在线读取，入门二数据由脚本生成，图片以上述 OSS 链接为准。具体改写与发布过程见系列文件夹《日志.md》。
