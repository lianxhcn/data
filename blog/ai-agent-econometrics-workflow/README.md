# AI Agent 计量代码协作工作流

连享会推文《AI Agent 写计量代码靠谱吗？一套可复现的协作工作流》的附件。

[下载完整练习包](https://raw.githubusercontent.com/lianxhcn/data/main/blog/ai-agent-econometrics-workflow/workflow-kit-v03.zip) · [查看四份提示词](https://github.com/lianxhcn/data/tree/main/blog/ai-agent-econometrics-workflow/prompts)

## 使用步骤

1. 下载上面的 ZIP 并完整解压；打开包含 master.do 的文件夹。
2. 准备已安装可用的 Stata 19，在新会话中切换到解压目录。
3. 执行 do master.do。首次需要联网获取 Stata 官方 nlswork 示例数据；coefplot 缺失时才尝试 SSC 安装。后续使用本地数据快照。
4. 查看 05-logs/run.log 的本次时间、错误、样本量和系数；查看 02-figs/publish/fig1_coef.png。
5. 按阶段使用 prompts 中的模板。填写方括号字段；返修模板中的 tenure>=1 是假设练习，未提供这项新估计的结果。

```stata
display c(stata_version)
* 替换为实际解压目录
cd "C:/work/paper-demo"
do "master.do"
```

若 webuse 报 r(677)，在浏览器从 [Stata 官方链接](https://www.stata-press.com/data/r19/nlswork.dta) 下载到 04-data/nlswork.dta；Windows 也可运行 03-code/download_data.ps1。不要把 HTML 错误页面改名为数据文件。

## 文件与验证

- master.do：依次调用准备、检查、回归脚本。
- 03-code/：真实测试过的分析代码及同源后备下载脚本。
- prompts/01-clarify.md、02-implement.md、03-verify.md、04-revise.md：任务澄清、实施、验收、返修。
- run.ps1：Windows 可选入口，需要当前会话中的 STATA_EXE 指向实际程序；不必使用此入口。

实测环境：Windows，StataNow/MP 19.5，coefplot 1.8.5；验证日期 2026-09-28。原始 28,534 条记录，完整观测样本 19,010 条，FE 个体及聚类数 4,134。tenure 系数 0.009，聚类标准误 0.001，按日志显示精度。

主模型未控制年份固定效应，结果是条件关联。末尾 pooled OLS bootstrap 仅演示 seed，不能作为 FE 的稳健性检验。代码每次覆盖工作目录中的输出，请先保留基准版本。

没有旧输出的副本已在同机完成重跑；未实测 macOS/Linux。新电脑应重新核对版本、数据来源和结果。公开包不含机器路径日志、许可证信息或第三方数据快照。

自有代码和说明沿用仓库 MIT 许可，第三方数据遵循原来源条件；首次取数失败应据实记录。
