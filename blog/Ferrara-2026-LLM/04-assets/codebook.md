# 教学标注规则 v1

用途：演示输入检查、标注表生成与类别解析。所有企业、事件和文本均为教学构造。预期标签是编写者按本规则指定的案例答案，不是独立人工测试标签。

单位：document_id + entity_id，每个输入是一篇文章内对一个指定目标企业的判断。

目标：目标企业自身业务中是否出现已使用 AI 的报道证据；包含已开展的业务试点，但保留 is_pilot。销售或开发 AI 产品不自动构成自身业务采用。行业展望不算计划。

- implemented：已经业务使用，含已运行试点。
- planned：仅有未来计划，没有已使用证据。
- no_evidence：文本可读但没有目标企业相关明确证据。不是断言真实世界没有采用。
- uncertain：缺文、归属不明或矛盾无法裁定。

已使用与未来计划并存时选 implemented。只处理当前文本，不联网补事实。evidence_quote 必须是原文片段；no_evidence 时可为空。事件日期无明确依据时 null，不用发布日期补齐。试点性质无法判断时 is_pilot=null。

另设 request_status 区分 not_run、success、request_failed、parse_failed。本批初始状态为 not_run。不要将失败解释为 no_evidence。

输出字段：document_id、entity_id、label、evidence_quote、reason、event_date、is_pilot、request_status、origin、codebook_version。origin 若用于离线构造必须为 synthetic_fixture；真实在线调用另记实际来源，禁止覆盖教学来源说明。
