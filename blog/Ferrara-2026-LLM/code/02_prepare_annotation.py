"""生成空白盲化表及明确标注来源的 fixture；重复运行保护已填写人工表。"""
from workflow import (ROOT, OUT, KEY, CONFIG, read_csv, write_csv, save_json,
                      index_rows, validate_inputs, cache_key, digest)
import json


def main():
    rows = read_csv(ROOT / '04-assets/materials.csv')
    expected = read_csv(ROOT / '04-assets/expected-demo-labels.csv')
    issues = validate_inputs(rows, expected)
    if issues:
        raise ValueError('\n'.join(issues))
    rules = (ROOT / '04-assets/codebook.md').read_bytes()
    answers = index_rows(expected, 'expected')
    human, predictions, cache = [], [], []
    human_fields = ['human_label', 'human_evidence_quote', 'human_reason',
                    'annotator_id', 'codebook_version', 'annotation_origin']
    for row in rows:
        input_hash = digest({f: row[f] for f in (*KEY, 'publication_date', 'text')})
        h = {f: row[f] for f in (*KEY, 'publication_date', 'text')}
        h.update(input_hash=input_hash, rules_hash=digest(rules))
        h.update({f: '' for f in human_fields})
        human.append(h)
        key = cache_key(row, rules, CONFIG)
        # 直接使用编写者预期答案，仅用于数据接口；没有伪造原始 API 响应。
        p = {f: row[f] for f in KEY}
        p.update(label=answers[tuple(row[f] for f in KEY)]['expected_label'],
                 evidence_quote='', reason='直接复制教学预期答案，仅检查离线接口。',
                 event_date='', is_pilot='', request_status='not_run',
                 origin='synthetic_fixture', codebook_version='v1',
                 input_hash=input_hash, rules_hash=digest(rules), cache_key=key)
        predictions.append(p)
        path = OUT / 'cache' / (key + '.json')
        if path.exists():
            if json.loads(path.read_text(encoding='utf-8')) != p:
                raise ValueError('缓存内容与当前预期不一致，拒绝静默复用')
            cache.append('hit')
        else:
            save_json(path, p)
            cache.append('miss')
    path = OUT / 'human-annotation.csv'
    if path.exists():
        existing = read_csv(path)
        base_fields = [f for f in human[0] if f not in human_fields]
        if [{f: r.get(f) for f in base_fields} for r in existing] != [
                {f: r[f] for f in base_fields} for r in human]:
            raise ValueError('已有人工表的材料或规则版本不同；请另存后再生成')
        human_state = 'preserved_existing'
    else:
        write_csv(path, list(human[0]), human)
        human_state = 'created_blank'
    write_csv(OUT / 'demo-predictions.csv', list(predictions[0]), predictions)
    save_json(OUT / 'offline-config.json', CONFIG)
    result = dict(input_n=len(rows), fixture_n=len(predictions), human_state=human_state,
                  cache_hits=cache.count('hit'), cache_misses=cache.count('miss'),
                  api_calls=0, config_hash=digest(CONFIG), rules_hash=digest(rules))
    save_json(OUT / 'preparation-result.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
