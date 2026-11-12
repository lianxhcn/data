# 机器学习中的距离：配套计算材料

艾米丽 (连享会) 推文《机器学习中的距离：从几何直觉到常见模型》的附件。全部数据为自设教学数据，无需下载外部数据或提供 API 密钥。Notebook 已包含 8 个代码单元的运行输出。

## 下载与文件

下载 [完整附件 ZIP](ml-basic-distance-attachments.zip) 并解压，保留 `scripts/` 和 `results/` 子目录。也可克隆本仓库，在 `blog/ml-basic-distance/` 中运行。请勿只下载 Notebook。

| 文件 | 用途 |
| --- | --- |
| [codes.ipynb](codes.ipynb) | 距离、尺度、余弦、SVM 垂足、正则化及练习；含已执行输出 |
| [requirements.txt](requirements.txt) | Python 依赖及已验证版本 |
| [scripts/build_figures.py](scripts/build_figures.py) | 8 张教学图的计算、绘制与核验 |
| [results/figure-font-baseline-20261109-004303.json](results/figure-font-baseline-20261109-004303.json) | 制图脚本读取的数学基线，必须保留 |

## 运行

使用 Python 3.12，在解压后的 `ml-basic-distance/` 目录创建独立环境。以下为 Windows PowerShell 命令：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

使用 VS Code 或已有 Jupyter 环境打开该文件夹，选择上述 Python 环境，然后从头运行 `codes.ipynb`。Notebook 应从该目录启动；其第一个代码单元会检查制图源码是否存在。

第 8 个代码单元调用制图脚本，生成 8 张 PNG、同源 SVG 及核验日志。也可在本目录单独运行：

```powershell
python -X utf8 scripts/build_figures.py
```

脚本自动建立 `figs/raw/`、`results/` 和 `logs/`，重复运行会更新生成文件。不要删除数学基线 JSON；脚本在重绘前读取该文件。

## 字体、验证与边界

源码使用 Windows 微软雅黑字体 `C:/Windows/Fonts/msyh.ttc`。完整重绘需要此字体；在其他系统上，可先执行前 7 个数值计算单元，完整绘图需要相应适配字体路径。本附件保留原始 Notebook、制图代码和数学基线，未改写算法或教学数据。

原项目已使用 Python 3.12.16 顺序执行全部 8 个代码单元，数值与几何检查通过。版本信息见 `requirements.txt`；发布前还对本附件目录进行了独立运行检查。

这些例子用于核对距离、范数和模型的几何含义，未开展样本外预测效果评价。附件发布不代表推文已在公众号或网站发布。
