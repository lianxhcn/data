"""检查输入质量及当前来源清单散列，不修改输入。"""
from workflow import ROOT, OUT, read_csv, validate_inputs, digest, save_json


def main():
    OUT.mkdir(exist_ok=True)
    rows = read_csv(ROOT / '04-assets/materials.csv')
    expected = read_csv(ROOT / '04-assets/expected-demo-labels.csv')
    issues = validate_inputs(rows, expected)
    checks = []
    for line in (ROOT / 'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines():
        expected_hash, name = line.split(maxsplit=1)
        path = ROOT / name
        actual = digest(path.read_bytes()) if path.exists() else None
        checks.append({'file': name, 'expected': expected_hash, 'actual': actual,
                       'matches': actual == expected_hash})
    save_json(OUT / 'source-integrity.json', checks)
    text = '# 输入审计\n\n'
    text += f'- 状态：{"PASS" if not issues else "FAIL"}。\n- 输入 {len(rows)} 条；预期答案 {len(expected)} 条；删除 0 条。\n'
    text += f'- 当前来源清单 SHA256：{sum(x["matches"] for x in checks)}/{len(checks)} 一致。\n'
    text += '- 检查组合识别键、空文本、真实日历日期、来源标记和预期类别。\n'
    text += '- D007 关键段落缺失但文本字段非空；其 uncertain 是内容状态。\n'
    text += '- 不自动从自然语言推断完整事件日期，也不将发布日期代填。\n\n'
    text += '\n'.join('- ' + x for x in issues) if issues else '未发现上述输入结构问题。\n'
    (OUT / 'input-audit.md').write_text(text, encoding='utf-8')
    print(text)
    if issues or not all(x['matches'] for x in checks):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
