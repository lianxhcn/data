# 资源指引：从模板走向可用工作流

本文档只列出适合进一步试用的官方入口或项目主页。工具能力会变化；下列链接的 `retrieved_date` 均为 `2026-08-27`。无论使用哪一种工具，先用本目录的固定问题和人工标注位置做小规模核验。

## 1. 不写代码：NotebookLM

- [Google NotebookLM：添加或发现资料](https://support.google.com/notebooklm/answer/16215270?co=GENIE.Platform%3DDesktop&hl=en-GB)
- `retrieved_date: 2026-08-27`
- 适合先对少量公开或可处理的文档进行带引文的问答与笔记整理。
- 使用前核对资料的版权、机构规则与敏感性；引用位置仍需打开原文复核，不能把生成摘要直接写进正式综述。

## 2. 想把检索接入自己的应用：OpenAI Vector Store Search

- [OpenAI Vector Store Search 官方 API 文档](https://developers.openai.com/api/reference/typescript/resources/vector_stores/methods/search)
- `retrieved_date: 2026-08-27`
- 适合需要通过 API 上传、检索并在自身脚本或应用中处理文件的读者。
- 先阅读当前的数据处理、文件上传和计费规则；不要上传受限数据、个人信息或未获许可的材料。

## 3. 希望从 Python 工作流开始：LlamaIndex

- [LlamaIndex GitHub 仓库](https://github.com/run-llama/llama_index)
- `retrieved_date: 2026-08-27`
- 适合希望把文档加载、切块、检索和评估纳入 Python 项目的人。
- 先用一个可人工核验的小语料库；框架不能替代对切块、检索结果和引用位置的检查。

## 4. 需要可视化搭建与检索流程：RAGFlow

- [RAGFlow 文档与快速开始](https://ragflow.cc/docs)
- `retrieved_date: 2026-08-27`
- 适合希望试验文档解析、知识库与检索问答流程的读者。
- 部署前应评估计算资源、数据权限和本地/云端边界；不应把未授权材料作为测试语料。

## 一个可重复的选择顺序

1. 先用 `sources_template.csv` 整理 10 篇文献，并人工标出 5 个问题的证据位置。
2. 用 `minimal_retrieval.py` 理解「问题—候选片段—来源定位」这条最小链路。
3. 若只需阅读与笔记，可先试 NotebookLM；若需要脚本化或接入项目，再比较 API 与 Python 框架；若需可视化部署，再评估 RAGFlow。
4. 无论选什么工具，都用 `evaluation_checklist.md` 记录漏检、误命中和越界回答。
