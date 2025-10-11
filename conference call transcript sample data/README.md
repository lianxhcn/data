本文件夹提供电话会议转录文本（conference call transcript）的示例数据。

codes.json 文件汇总了从 Seeking Alpha 网站获取的所有企业代码，以及每家企业可获取的转录文本数量。

test_json 文件夹包含部分企业的转录文本 URL 链接，以 JSON 格式存储，每个企业对应一个独立文件。所涵盖的企业代码包括：["A", "AA", "AAALY", "AABKF", "AACAF", "AACAY", "AACG"]。

sample_transcript 文件夹中存储了基于 test_json 内 URL 爬取得到的转录文本原文。每个企业子文件夹中的 failed.json 文件记录了未能成功抓取的链接，这些链接通常指向非纯文本格式内容（如 PDF 文件）。
需说明的是，这些未能抓取的内容通常已在其他可访问的纯文本转录中涵盖，不影响数据集的完整性。例如，[Alcoa Corporation 2025 Q2 - Results - Earnings Call Presentation](https://seekingalpha.com/article/4787139-aareal-bank-ag-2025-q1-results-earnings-call-presentation) 对应的 PDF 文件虽无法直接抓取，但其完整内容已在 此纯文本转录链接 https://seekingalpha.com/article/4787140-aareal-bank-ag-aabkf-q1-2025-earnings-call-transcript 中提供，并已成功爬取。
这一情况源于 Seeking Alpha 平台的处理方式：部分电话会议在提供纯文本转录之外，会另行发布经整理的 PDF 版本，但两者内容一致。
