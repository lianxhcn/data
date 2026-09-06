"""关键风险的确定性检查；内部合成标签不写入人工表，也不视为人工验证。"""
from copy import deepcopy
from workflow import (ROOT, OUT, CONFIG, read_csv, index_rows, validate_inputs,
                      cache_key, binary_metrics, evaluate, save_json)


def main():
    passed = []
    rows = read_csv(ROOT / '04-assets/materials.csv')
    expected = read_csv(ROOT / '04-assets/expected-demo-labels.csv')
    rules = (ROOT / '04-assets/codebook.md').read_bytes()
    human = read_csv(OUT / 'human-annotation.csv')
    predictions = read_csv(OUT / 'demo-predictions.csv')
    assert len(rows) == len(expected) == len(human) == len(predictions) == 8
    passed.append('输入、预期答案、盲化表、fixture 各 8 条')
    try:
        evaluate(human + [human[0]], predictions)
    except ValueError as exc:
        assert '重复识别键' in str(exc)
    else:
        raise AssertionError('未拒绝重复人工键')
    try:
        evaluate(human, predictions + [predictions[0]])
    except ValueError as exc:
        assert '重复识别键' in str(exc)
    else:
        raise AssertionError('未拒绝重复预测键')
    passed.append('两侧重复键均被拒绝，不产生笛卡尔积')
    invalid = deepcopy(rows)
    invalid[0]['text'] = ''
    invalid[1]['publication_date'] = '2025-02-30'
    assert len(validate_inputs(invalid, expected)) == 2
    passed.append('空文本、无效日历日期被报告，不静默删除')
    fields = ['human_label', 'human_evidence_quote', 'human_reason',
              'annotator_id', 'codebook_version', 'annotation_origin']
    assert all(not r[f] for r in human for f in fields)
    assert not {'expected_label', 'label', 'model_label'} & human[0].keys()
    passed.append('盲化表人工字段全空、无答案或模型标签列')
    assert all(r['origin'] == 'synthetic_fixture' and r['request_status'] == 'not_run'
               for r in predictions)
    report, _ = evaluate(human, predictions)
    assert report['four_class'] is None and report['implemented_binary'] is None
    passed.append('空人工标签与 fixture 不生成模型效果')
    base = cache_key(rows[0], rules, CONFIG)
    assert base == cache_key(rows[0], rules, CONFIG)
    variants = [(dict(rows[0], text=rows[0]['text'] + '变化'), rules, CONFIG),
                (rows[0], rules + b'v2', CONFIG),
                (rows[0], rules, dict(CONFIG, parser_version='2')),
                (dict(rows[0], publication_date='2025-06-02'), rules, CONFIG)]
    assert all(base != cache_key(*v) for v in variants)
    passed.append('缓存稳定；文本、日期、规则或配置改变均失效')
    empty = binary_metrics(0, 0, 0, 0)
    assert all(empty[f] is None for f in ['accuracy', 'precision', 'recall', 'f1'])
    negative = binary_metrics(0, 20, 0, 80)
    assert negative['precision'] is None and negative['recall'] == 0 and negative['accuracy'] == .8
    passed.append('零分母输出 null，全负类不误报精确率 100%')
    # 以下只在内存中使用合成声明覆盖计算分支，绝不写成人工金标准。
    h, p = deepcopy(human), deepcopy(predictions)
    for a, b in zip(h, p):
        a.update(human_label=b['label'], human_reason='合成测试', annotator_id='TEST_ONLY',
                 annotation_origin='independent_human', codebook_version='v1')
        b.update(origin='online_model', request_status='success')
    p[0].update(label='', request_status='request_failed')
    p[1].update(label='', request_status='parse_failed')
    report, _ = evaluate(h, p)
    assert report['four_class']['n'] == 6 and report['implemented_binary']['n'] == 5
    assert report['binary_uncertain_excluded_n'] == 1
    assert report['exclusion_counts']['request_failed'] == report['exclusion_counts']['parse_failed'] == 1
    assert report['prediction_label_counts']['missing'] == 2
    passed.append('请求失败、解析失败、缺失分别计数；四分类含不确定，二分类排除')
    h[2]['input_hash'] = 'changed'
    h[3]['rules_hash'] = 'changed'
    report, _ = evaluate(h, p)
    assert report['exclusion_counts']['input_version_mismatch'] == 1
    assert report['exclusion_counts']['rules_hash_mismatch'] == 1
    passed.append('输入与规则散列不一致的配对被排除')
    report, _ = evaluate(h[:-1], p)
    assert report['prediction_only_keys'] == [['D008', 'I']]
    passed.append('未匹配键显式报告')
    gold, pred = [], []
    pairs = [('implemented', 'implemented')] * 15 + [('implemented', 'no_evidence')] * 5
    pairs += [('no_evidence', 'implemented')] * 10 + [('no_evidence', 'no_evidence')] * 70
    for i, (a, b) in enumerate(pairs):
        row = dict(document_id=str(i), entity_id='TEST', input_hash='test', rules_hash='test',
                   codebook_version='v1')
        gold.append(dict(row, human_label=a, annotator_id='TEST_ONLY', human_reason='合成测试',
                         annotation_origin='independent_human'))
        pred.append(dict(row, label=b, request_status='success', origin='online_model'))
    report, disagreements = evaluate(gold, pred)
    assert report['implemented_binary'] == binary_metrics(15, 5, 10, 70)
    assert report['four_class']['accuracy'] == .85 and len(disagreements) == 15
    passed.append('合成 100 对标签端到端得到 15/5/10/70，分歧 15 条')
    save_json(OUT / 'acceptance-checks.json', dict(status='PASS', checks=passed,
              test_data_origin='synthetic_in_memory_only', independent_human_validation=False))
    print('\n'.join(passed))


if __name__ == '__main__':
    main()
