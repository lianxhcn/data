"""离线公共接口：不访问网络，不读取凭据，不将 fixture 当作模型实测。"""
from pathlib import Path
from datetime import date
from collections import Counter
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
LABELS = ('implemented', 'planned', 'no_evidence', 'uncertain')
STATUSES = ('not_run', 'success', 'request_failed', 'parse_failed')
KEY = ('document_id', 'entity_id')
CONFIG = {'mode': 'offline_fixture', 'model': None, 'schema_version': '1',
          'codebook_version': 'v1', 'parser_version': '1'}


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f'CSV 表头为空或重复：{path}')
        rows = list(reader)
        if any(None in r or None in r.values() for r in rows):
            raise ValueError(f'CSV 列数不一致：{path}')
        return rows


def write_csv(path, fields, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def index_rows(rows, name):
    result = {}
    for n, row in enumerate(rows, 2):
        key = tuple(row.get(x, '').strip() for x in KEY)
        if not all(key):
            raise ValueError(f'{name} 第 {n} 行识别键缺失')
        if key in result:
            raise ValueError(f'{name} 重复识别键：{key}')
        result[key] = row
    return result


def validate_inputs(rows, expected):
    """问题全部列出，输入不做静默删行；空文本保留并使门槛失败。"""
    issues = []
    for name, data in [('materials', rows), ('expected', expected)]:
        try:
            index_rows(data, name)
        except ValueError as exc:
            issues.append(str(exc))
    for row in rows:
        key = '/'.join(row.get(x, '') for x in KEY)
        if not row.get('text', '').strip():
            issues.append(f'{key}: 空文本')
        value = row.get('publication_date', '')
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError()
            date.fromisoformat(value)
        except ValueError:
            issues.append(f'{key}: 无效发布日期 {value!r}')
        if row.get('origin') != 'synthetic_teaching_text':
            issues.append(f'{key}: 教学文本来源不符')
    for row in expected:
        if row.get('expected_label') not in LABELS:
            issues.append(f'预期类别不合法：{row}')
        if row.get('origin') != 'synthetic_expected_answer':
            issues.append('预期答案来源不符')
    a = {tuple(r.get(x) for x in KEY) for r in rows}
    b = {tuple(r.get(x) for x in KEY) for r in expected}
    if a != b:
        issues.append(f'输入与预期答案键集合不一致：{a ^ b}')
    if not rows:
        issues.append('输入为零条')
    return issues


def cache_key(row, rules, config):
    """包含完整上下文及规则/解析配置；实体、日期、规则变化均会失效。"""
    return digest({'key': [row[x] for x in KEY], 'text_hash': digest(row['text']),
                   'publication_date': row['publication_date'],
                   'rules_hash': digest(rules), 'config_hash': digest(config)})


def ratio(a, b):
    return a / b if b else None


def binary_metrics(tp, fn, fp, tn):
    return {'n': tp + fn + fp + tn, 'matrix': [[tp, fn], [fp, tn]],
            'accuracy': ratio(tp + tn, tp + fn + fp + tn),
            'precision': ratio(tp, tp + fp), 'recall': ratio(tp, tp + fn),
            'f1': ratio(2 * tp, 2 * tp + fp + fn)}


def evaluate(human, predictions):
    """先拒绝重复键，再按键对齐；指标仅覆盖符合来源条件的有效配对。"""
    hi = index_rows(human, 'human')
    pi = index_rows(predictions, 'predictions')
    report = {'human_n': len(hi), 'prediction_n': len(pi),
              'human_only_keys': [list(k) for k in sorted(hi.keys() - pi.keys())],
              'prediction_only_keys': [list(k) for k in sorted(pi.keys() - hi.keys())],
              'request_status_counts': dict(Counter(r.get('request_status', '') for r in predictions)),
              'human_label_counts': dict(Counter(r.get('human_label', '') or 'missing' for r in human)),
              'prediction_label_counts': dict(Counter(r.get('label', '') or 'missing' for r in predictions)),
              'four_class': None, 'implemented_binary': None,
              'denominator_zero_policy': 'null (未定义)，不填 100%',
              'exclusions_are_nonexclusive': True}
    paired, excluded, disagreements = [], Counter(), []
    for key in sorted(hi.keys() & pi.keys()):
        h, p = hi[key], pi[key]
        hl, pl = h.get('human_label', ''), p.get('label', '')
        status = p.get('request_status', '')
        if hl and hl not in LABELS:
            raise ValueError(f'非法人工类别：{key}')
        if pl and pl not in LABELS:
            raise ValueError(f'非法预测类别：{key}')
        if status not in STATUSES:
            raise ValueError(f'非法请求状态：{key}')
        reasons = []
        if not hl:
            reasons.append('human_label_missing')
        if not pl:
            reasons.append('prediction_label_missing')
        if status != 'success':
            reasons.append(status)
        if p.get('origin') != 'online_model':
            reasons.append('not_online_model')
        if h.get('annotation_origin') != 'independent_human' or not all(
                h.get(f, '').strip() for f in ('annotator_id', 'codebook_version', 'human_reason')):
            reasons.append('human_provenance_incomplete')
        if h.get('codebook_version') != p.get('codebook_version'):
            reasons.append('rule_version_mismatch')
        if h.get('input_hash') != p.get('input_hash') or not h.get('input_hash'):
            reasons.append('input_version_mismatch')
        if h.get('rules_hash') != p.get('rules_hash') or not h.get('rules_hash'):
            reasons.append('rules_hash_mismatch')
        if reasons:
            excluded.update(reasons)
            continue
        paired.append((hl, pl))
        if hl != pl:
            disagreements.append(dict(document_id=key[0], entity_id=key[1],
                                      human_label=hl, model_label=pl))
    report['exclusion_counts'] = dict(excluded)
    report['paired_eligible_n'] = len(paired)
    if paired:
        matrix = [[sum(a == x and b == y for a, b in paired) for y in LABELS] for x in LABELS]
        by_class = {}
        for i, label in enumerate(LABELS):
            tp = matrix[i][i]
            support = sum(matrix[i])
            predicted = sum(row[i] for row in matrix)
            by_class[label] = {'support': support, 'precision': ratio(tp, predicted),
                               'recall': ratio(tp, support), 'f1': ratio(2 * tp, support + predicted)}
        report['four_class'] = {'labels': LABELS, 'rows': 'human', 'columns': 'model',
                                'n': len(paired), 'matrix': matrix, 'by_class': by_class,
                                'accuracy': ratio(sum(a == b for a, b in paired), len(paired))}
        # 四分类保留 uncertain；二分类把任一端 uncertain 的配对排除并报告。
        binary = [(a == 'implemented', b == 'implemented') for a, b in paired
                  if a != 'uncertain' and b != 'uncertain']
        report['binary_uncertain_excluded_n'] = len(paired) - len(binary)
        report['implemented_binary'] = binary_metrics(
            sum(a and b for a, b in binary), sum(a and not b for a, b in binary),
            sum(not a and b for a, b in binary), sum(not a and not b for a, b in binary))
    report['status'] = 'EVALUATED_DECLARED_PROVENANCE' if paired else 'NOT_EVALUATED'
    report['provenance_note'] = '程序只能核对来源声明；声明是否属实仍须人工审计。'
    return report, disagreements
