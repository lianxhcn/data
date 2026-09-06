"""默认检查空人工表；教学矩阵单独验证，不生成对 8 条文本的效果声明。"""
import argparse
from workflow import ROOT, OUT, read_csv, save_json, write_csv, evaluate, binary_metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--human', type=str, default='outputs/human-annotation.csv')
    parser.add_argument('--predictions', type=str, default='outputs/demo-predictions.csv')
    args = parser.parse_args()
    report, disagreements = evaluate(read_csv(ROOT / args.human), read_csv(ROOT / args.predictions))
    save_json(OUT / 'evaluation.json', report)
    write_csv(OUT / 'disagreements.csv',
              ['document_id', 'entity_id', 'human_label', 'model_label'], disagreements)
    demo = binary_metrics(15, 5, 10, 70)
    assert demo['accuracy'] == .85 and demo['precision'] == .6 and demo['recall'] == .75
    assert abs(demo['f1'] - 2 / 3) < 1e-12
    save_json(OUT / 'teaching-metrics.json', dict(origin='synthetic_teaching_matrix',
              unrelated_to_materials_csv=True, rows='human', columns='model', **demo))
    print(f"实际标签评估：{report['status']}；教学矩阵校验 PASS；分歧 {len(disagreements)} 条。")


if __name__ == '__main__':
    main()
