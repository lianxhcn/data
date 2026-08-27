"""一个不依赖外部包的最小检索示例。

目的：把研究材料切成可定位的片段，按问题中的关键词给片段排序，
并把最相关片段连同来源信息交给后续人工或生成回答环节。

本脚本只演示词元重合检索，不调用大模型，也不自动生成答案。
"""

from __future__ import annotations

import re


DOCUMENTS = [
    {
        "source": "paper_A.pdf, p. 8, Table 4",
        "text": "论文 A 使用分期实施 DID 估计政策冲击对企业创新的影响，表 4 报告正向系数。",
    },
    {
        "source": "paper_B.pdf, p. 12, Table 6",
        "text": "论文 B 以专利申请量度量创新，并把融资约束作为机制变量。",
    },
    {
        "source": "paper_C.pdf, p. 5",
        "text": "论文 C 讨论政策背景，但未报告企业专利结果，也未采用 DID。",
    },
]


def tokens(text: str) -> set[str]:
    """提取中文连续片段、英文单词与常用缩写，供最小示例评分。"""
    return set(re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]+|\d+", text.lower()))


def score(query_tokens: set[str], document: dict[str, str]) -> int:
    """按共有词元数量评分；真实项目应替换为 BM25、向量或混合检索。"""
    return len(query_tokens & tokens(document["text"]))


def retrieve(query: str, top_k: int = 2) -> list[dict[str, str]]:
    """返回带来源定位的前 k 个候选片段。"""
    query_tokens = tokens(query)
    ranked = sorted(
        DOCUMENTS,
        key=lambda doc: score(query_tokens, doc),
        reverse=True,
    )
    return [doc for doc in ranked[:top_k] if score(query_tokens, doc) > 0]


def main() -> None:
    query = "哪些论文使用 DID 估计政策冲击对企业创新的影响？"
    results = retrieve(query)

    print(f"问题：{query}\n")
    print("检索到的候选片段：")
    for index, doc in enumerate(results, start=1):
        print(f"{index}. {doc['text']}")
        print(f"   来源：{doc['source']}")

    if not results:
        print("\n材料不足：没有找到支持该问题的片段。")


if __name__ == "__main__":
    main()
