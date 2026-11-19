# onlyuseful：从 do-file 自动精简数据集的复现材料

本目录存放连享会推文《Stata：从 do-file 自动精简数据集——onlyuseful》的 Stata 复现脚本。`onlyuseful` 通过 PowerShell 对分析 do-file 做文本匹配，自动生成只保留所用变量的精简脚本，也可在批处理模式下直接输出精简后的 .dta 文件。

## 目录结构

```text
onlyuseful/
  README.md
  code/
    01-install.do       # 安装 onlyuseful，下载官方示例
    02-dry-run.do       # 场景一：dry run，生成精简脚本并核对变量数
    03-batch.do         # 场景二：批处理直接生成精简数据
    04-wildcard.do      # 场景三：构造通配符测试数据并运行
    wild_analysis.do    # 被扫描的分析脚本，含 year* 与 yearof
```

## 运行方式

1. 先准备一个**纯英文、无空格**的工作目录，例如 `C:/onlyuseful-demo`。`onlyuseful` 不支持含空格或桌面 (Desktop) 的路径。
2. 打开 `code/` 下的 do 文件，把开头的 `local root` 改为该工作目录的完整路径 (使用正斜杠)；运行 `03-batch.do` 前，再把 `local stataexe` 改为你本机 Stata 可执行文件的完整路径。
3. 依次运行：

```stata
do code/01-install.do   // 安装命令并下载官方示例 (mydata.dta、analysis_script1/2.do)
do code/02-dry-run.do   // 12 个变量精简为 7 个
do code/03-batch.do     // 批处理保留 8 个变量，生成 reduced_data.dta
do code/04-wildcard.do  // 通配符场景，仅 year2000 保留
```

## 预期结果

- dry run：`mydata.dta` 含 74 个观测、12 个变量，精简后内存中保留 7 个变量，命令丢弃其余 5 个。
- 批处理：保留 8 个变量，其中 `displacement` 仅因出现在注释里而保留；输出 **reduced_data.dta**、dropscript.do、dropscript.log。
- 通配符：`year*` 与缩写 `yearof` 均无法识别，精简脚本只保留完整写出的 `year2000`。

## 环境与边界

- 脚本在 Stata 19、Windows 环境下测试通过。`onlyuseful` 依赖 Windows 上的 PowerShell，若脚本被执行策略拦截，请按推文第 3.3 节调整当前用户的执行策略。
- `r(k_drop)` 由 `keep` 产生，仅在 Stata 16 及之后版本可用。
- 官方示例数据 `mydata.dta` 由 Stata 内置的 auto.dta 保存得到，通过 `net get dm0117` 下载，本目录不重复提供数据文件。
