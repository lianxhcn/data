#!/usr/bin/env python3
"""LLM 文本标注的验证与提示词敏感性分析。

本脚本服务于连享会文章《LLM 生成的标签，能直接放进回归吗？》。
它有两个目的：

1. 将文本依次交给多组 prompt 和同一个 LLM，形成多个版本的 LLM_LABEL；
2. 在人工验证样本上计算分类指标，并将各版本标签放入同一条回归式，比较
   核心系数是否对 prompt 敏感。

设计原则：
- 不删除非 ASCII 字符，中文文本可直接输入；
- 每个 prompt 使用同一批观测，避免把样本变化误当作 prompt 效应；
- 缓存每次 API 返回，便于中断后续跑，也便于复核；
- 既保存第一阶段分类指标，也保存第二阶段回归结果。

真实调用需要设置 OPENAI_API_KEY。`--provider mock` 仅用于检查本地流程，
不能代替真实 LLM 的研究结果。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm


REQUIRED_PROMPT_COLUMNS = {"prompt"}


@dataclass
class RunConfig:
    """记录本次运行参数，写入 metadata 文件以便复现。"""

    data: str
    prompts: str
    output_dir: str
    model: str
    provider: str
    text_column: str
    id_column: str
    human_label_column: str
    formula: str | None
    regression_family: str
    coefficient_of_interest: str
    cluster_column: str | None
    prompt_limit: int | None
    max_rows: int | None
    temperature: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LLM 文本标注、人工验证与提示词敏感性分析",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--data", required=True, help="CSV 文件路径或可公开访问的 CSV URL")
    parser.add_argument("--prompts", required=True, help="prompt CSV 文件路径或 URL")
    parser.add_argument("--output-dir", default="output", help="结果文件保存目录")
    parser.add_argument(
        "--provider",
        choices=["openai", "mock"],
        default="openai",
        help="openai 为真实 API；mock 仅用于本地流程测试",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("LLM_MODEL", ""),
        help="服务商的模型名。真实调用时必须提供，可写入环境变量 LLM_MODEL",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="保存 API key 的环境变量名",
    )
    parser.add_argument(
        "--base-url-env",
        default="OPENAI_BASE_URL",
        help="可选：OpenAI 兼容服务的 base URL 环境变量名",
    )
    parser.add_argument("--text-column", default="text", help="待标注文本列")
    parser.add_argument("--id-column", default="id", help="观测唯一标识列；缺失时自动生成")
    parser.add_argument(
        "--human-label-column",
        default="HUMAN",
        help="人工验证标签列；该列可只在验证子样本中有值",
    )
    parser.add_argument(
        "--formula",
        default=None,
        help="下游回归式，例如 'success ~ LLM_LABEL + lgoal + C(year) + C(subcategory)'",
    )
    parser.add_argument(
        "--regression-family",
        choices=["binomial", "gaussian"],
        default="binomial",
        help="binomial 为 logit；gaussian 为 OLS",
    )
    parser.add_argument(
        "--coefficient-of-interest",
        default="LLM_LABEL",
        help="需要提取的核心系数名",
    )
    parser.add_argument(
        "--cluster-column",
        default=None,
        help="可选：聚类稳健标准误的聚类变量，例如 firm_id",
    )
    parser.add_argument("--prompt-limit", type=int, default=None, help="仅运行前若干个 prompt，用于低成本试跑")
    parser.add_argument("--max-rows", type=int, default=None, help="仅使用前若干行数据，用于低成本试跑")
    parser.add_argument("--temperature", type=float, default=0.0, help="LLM temperature 参数")
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="两次真实 API 调用之间的暂停秒数；遇到服务商限速时可适当调大",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="不读取或写入缓存。正常研究不建议使用，以免重复花费 API 成本",
    )
    return parser.parse_args()


def read_csv_source(source: str) -> pd.DataFrame:
    """读取本地或公开 URL 的 CSV；保留非 ASCII 文本。

    新建的中文数据建议统一保存为 UTF-8。这里同时保留 cp1252 和 latin-1 回退，
    是为了能够直接读取原作者仓库中较早的 Kickstarter 样本。
    """
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(source, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error or UnicodeDecodeError("utf-8", b"", 0, 1, "Cannot decode CSV")


def ensure_inputs(
    data: pd.DataFrame,
    prompts: pd.DataFrame,
    text_column: str,
    id_column: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """检查输入，并补齐观测 ID 与 prompt ID。"""
    if text_column not in data.columns:
        raise ValueError(f"数据中找不到文本列 `{text_column}`。现有列为: {list(data.columns)}")
    if not REQUIRED_PROMPT_COLUMNS.issubset(prompts.columns):
        raise ValueError("prompt 文件至少应包含 `prompt` 一列。")

    data = data.copy()
    prompts = prompts.copy()
    data[text_column] = data[text_column].fillna("").astype(str)
    data = data.loc[data[text_column].str.strip().ne("")].copy()

    if id_column not in data.columns:
        data[id_column] = [f"obs_{i:06d}" for i in range(1, len(data) + 1)]
    data[id_column] = data[id_column].astype(str)
    if data[id_column].duplicated().any():
        raise ValueError(f"`{id_column}` 含有重复值，无法安全写入缓存。")

    if "prompt_id" not in prompts.columns:
        prompts.insert(0, "prompt_id", [f"p{i:03d}" for i in range(1, len(prompts) + 1)])
    if "strategy" not in prompts.columns:
        prompts["strategy"] = "unspecified"
    prompts["prompt"] = prompts["prompt"].fillna("").astype(str)
    prompts = prompts.loc[prompts["prompt"].str.strip().ne("")].copy()
    if prompts["prompt_id"].duplicated().any():
        raise ValueError("`prompt_id` 含有重复值。")
    return data, prompts


def render_prompt(template: str, text: str) -> str:
    """将文本放入明确边界中，减少任务指令与原文混淆。"""
    wrapped_text = f"<TEXT_TO_CLASSIFY>\n{text}\n</TEXT_TO_CLASSIFY>"
    if "{{text}}" in template:
        return template.replace("{{text}}", wrapped_text)
    return f"{template}\n\n{wrapped_text}"


def parse_binary_json(content: str) -> int:
    """只接受 JSON 的 0/1 标签，避免从解释文字中误抓数字。"""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"模型没有返回合法 JSON: {content[:200]}") from exc
    label = payload.get("label")
    if str(label) not in {"0", "1"}:
        raise ValueError(f"JSON 中的 `label` 必须是 0 或 1，实际得到: {label!r}")
    return int(label)


class OpenAICompatibleClassifier:
    """通过 OpenAI Python SDK 调用 OpenAI 或兼容接口。"""

    def __init__(self, api_key: str, base_url: str | None, model: str, temperature: float):
        if not model:
            raise ValueError("真实调用时需通过 --model 或 LLM_MODEL 指定模型名。")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("请先运行 `pip install -r requirements.txt` 安装 openai。") from exc

        kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model
        self.temperature = temperature

    def __call__(self, prompt: str) -> tuple[int, str]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是社会科学研究的文本编码助手。"
                        "严格按用户要求返回 JSON，不要输出额外文字。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        return parse_binary_json(content), content


class MockClassifier:
    """不联网的流程测试器。

    它使用极其粗糙的关键词规则，目的仅是让读者验证 CSV、回归和作图管线。
    输出绝不能被解释为任何 LLM 的性能。
    """

    POSITIVE_WORDS = (
        "sustainable", "environment", "organic", "community", "fair", "recycle",
        "绿色", "低碳", "环境", "社区", "公益", "公平", "可持续", "节能", "减排",
    )

    def __call__(self, prompt: str) -> tuple[int, str]:
        # 只检查待分类原文，不检查 prompt 中可能出现的“环境”“社会”等定义词。
        text_part = prompt.split("<TEXT_TO_CLASSIFY>", maxsplit=1)[-1]
        text_part = text_part.split("</TEXT_TO_CLASSIFY>", maxsplit=1)[0]
        text_lower = text_part.lower()
        label = int(any(word.lower() in text_lower for word in self.POSITIVE_WORDS))
        raw = json.dumps({"label": label, "note": "mock provider; not an LLM"}, ensure_ascii=False)
        return label, raw


class JsonlCache:
    """按 record、prompt、model 和文本内容缓存预测，避免重复调用。"""

    def __init__(self, path: Path, enabled: bool = True):
        self.path = path
        self.enabled = enabled
        self.items: dict[str, dict[str, Any]] = {}
        if enabled and path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    item = json.loads(line)
                    self.items[item["cache_key"]] = item
                except (json.JSONDecodeError, KeyError):
                    # 单条缓存损坏时保留其他正常结果，而不是让整个任务失败。
                    continue

    @staticmethod
    def key(record_id: str, prompt_id: str, model: str, text: str, template: str) -> str:
        payload = "\u241f".join([record_id, prompt_id, model, text, template])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> dict[str, Any] | None:
        return self.items.get(key) if self.enabled else None

    def add(self, item: dict[str, Any]) -> None:
        if not self.enabled:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        self.items[item["cache_key"]] = item


def annotate_all(
    data: pd.DataFrame,
    prompts: pd.DataFrame,
    classifier: Callable[[str], tuple[int, str]],
    config: RunConfig,
    sleep_seconds: float,
    cache: JsonlCache,
) -> pd.DataFrame:
    """对每一行和每个 prompt 生成一个标签，形成 long-format 结果。"""
    records: list[dict[str, Any]] = []
    total = len(data) * len(prompts)
    done = 0

    for prompt_row in prompts.itertuples(index=False):
        prompt_id = str(prompt_row.prompt_id)
        strategy = str(prompt_row.strategy)
        template = str(prompt_row.prompt)
        for _, row in data.iterrows():
            record_id = str(row[config.id_column])
            source_text = str(row[config.text_column])
            cache_key = cache.key(record_id, prompt_id, config.model or config.provider, source_text, template)
            cached = cache.get(cache_key)
            if cached is not None:
                label = cached["label"]
                raw_output = cached.get("raw_output", "")
                status = "cache"
            else:
                rendered = render_prompt(template, source_text)
                try:
                    label, raw_output = classifier(rendered)
                    status = "ok"
                except Exception as exc:  # 保留失败观测与错误文本，后续可以诊断而非静默丢弃。
                    label = np.nan
                    raw_output = f"ERROR: {type(exc).__name__}: {exc}"
                    status = "error"
                cache.add(
                    {
                        "cache_key": cache_key,
                        "record_id": record_id,
                        "prompt_id": prompt_id,
                        "model": config.model or config.provider,
                        "label": label,
                        "raw_output": raw_output,
                    }
                )
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)

            result = row.to_dict()
            result.update(
                {
                    "prompt_id": prompt_id,
                    "strategy": strategy,
                    "LLM_LABEL": label,
                    "api_status": status,
                    "raw_output": raw_output,
                }
            )
            records.append(result)
            done += 1
            if done % 20 == 0 or done == total:
                print(f"已处理 {done}/{total} 次标注调用", flush=True)
    return pd.DataFrame(records)


def classification_metrics(
    subset: pd.DataFrame,
    human_label_column: str,
) -> dict[str, float | int]:
    """计算标准二分类指标；FPR/FNR 的分母分别是实际负类/正类。"""
    if human_label_column not in subset.columns:
        return {"n_validation": 0, "accuracy": np.nan, "precision": np.nan, "recall": np.nan,
                "false_positive_rate": np.nan, "false_negative_rate": np.nan,
                "true_positive": 0, "true_negative": 0, "false_positive": 0, "false_negative": 0}

    valid = subset[[human_label_column, "LLM_LABEL"]].dropna().copy()
    valid = valid[valid[human_label_column].isin([0, 1]) & valid["LLM_LABEL"].isin([0, 1])]
    if valid.empty:
        return {"n_validation": 0, "accuracy": np.nan, "precision": np.nan, "recall": np.nan,
                "false_positive_rate": np.nan, "false_negative_rate": np.nan,
                "true_positive": 0, "true_negative": 0, "false_positive": 0, "false_negative": 0}

    y = valid[human_label_column].astype(int)
    yhat = valid["LLM_LABEL"].astype(int)
    tp = int(((y == 1) & (yhat == 1)).sum())
    tn = int(((y == 0) & (yhat == 0)).sum())
    fp = int(((y == 0) & (yhat == 1)).sum())
    fn = int(((y == 1) & (yhat == 0)).sum())
    n = len(valid)
    return {
        "n_validation": n,
        "accuracy": (tp + tn) / n,
        "precision": tp / (tp + fp) if tp + fp else np.nan,
        "recall": tp / (tp + fn) if tp + fn else np.nan,
        "false_positive_rate": fp / (fp + tn) if fp + tn else np.nan,
        "false_negative_rate": fn / (fn + tp) if fn + tp else np.nan,
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
    }


def fit_downstream_regression(
    subset: pd.DataFrame,
    formula: str | None,
    family: str,
    coefficient_of_interest: str,
    cluster_column: str | None,
) -> dict[str, Any]:
    """用同一条回归式比较各 prompt 下的核心系数。"""
    empty: dict[str, Any] = {
        "n_regression": 0,
        "coefficient": np.nan,
        "std_error": np.nan,
        "p_value": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "converged": False,
        "regression_status": "not_requested",
    }
    if not formula:
        return empty

    try:
        reg_data = subset.dropna(subset=["LLM_LABEL"]).copy()
        if family == "binomial":
            model = smf.glm(formula=formula, data=reg_data, family=sm.families.Binomial())
        else:
            model = smf.ols(formula=formula, data=reg_data)

        if cluster_column:
            if cluster_column not in reg_data.columns:
                raise ValueError(f"找不到聚类变量 `{cluster_column}`")
            fitted = model.fit(cov_type="cluster", cov_kwds={"groups": reg_data[cluster_column]})
        else:
            # 没有聚类变量时，至少报告异方差稳健标准误。
            fitted = model.fit(cov_type="HC1")

        if coefficient_of_interest not in fitted.params.index:
            raise ValueError(
                f"回归中找不到 `{coefficient_of_interest}`。可用系数为: {list(fitted.params.index)}"
            )
        ci = fitted.conf_int().loc[coefficient_of_interest]
        return {
            "n_regression": int(fitted.nobs),
            "coefficient": float(fitted.params[coefficient_of_interest]),
            "std_error": float(fitted.bse[coefficient_of_interest]),
            "p_value": float(fitted.pvalues[coefficient_of_interest]),
            "ci_low": float(ci.iloc[0]),
            "ci_high": float(ci.iloc[1]),
            "converged": bool(getattr(fitted, "converged", True)),
            "regression_status": "ok",
        }
    except Exception as exc:
        empty["regression_status"] = f"error: {type(exc).__name__}: {exc}"
        return empty


def summarize_by_prompt(
    predictions: pd.DataFrame,
    config: RunConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """按 prompt 汇总第一阶段指标与第二阶段回归结果。"""
    metric_rows: list[dict[str, Any]] = []
    regression_rows: list[dict[str, Any]] = []
    for (prompt_id, strategy), subset in predictions.groupby(["prompt_id", "strategy"], dropna=False):
        metric_row = {"prompt_id": prompt_id, "strategy": strategy}
        metric_row.update(classification_metrics(subset, config.human_label_column))
        metric_rows.append(metric_row)

        regression_row = {"prompt_id": prompt_id, "strategy": strategy}
        regression_row.update(
            fit_downstream_regression(
                subset,
                config.formula,
                config.regression_family,
                config.coefficient_of_interest,
                config.cluster_column,
            )
        )
        regression_rows.append(regression_row)
    return pd.DataFrame(metric_rows), pd.DataFrame(regression_rows)


def plot_coefficients(regression: pd.DataFrame, output_path: Path) -> None:
    """画出 prompt 对应的回归系数与 95% 置信区间。"""
    plot_df = regression.loc[regression["regression_status"].eq("ok")].copy()
    plot_df = plot_df.dropna(subset=["coefficient", "ci_low", "ci_high"])
    if plot_df.empty:
        print("没有可作图的回归结果，跳过系数图。")
        return

    # Windows 常见中文字体优先；在没有中文字体的 Linux 环境中自动切换到英文标签，
    # 使输出图不会显示方块或产生大量缺字警告。
    installed_fonts = {font.name for font in font_manager.fontManager.ttflist}
    cjk_candidates = ["Microsoft YaHei", "Noto Sans CJK SC", "SimHei", "PingFang SC"]
    cjk_font = next((font for font in cjk_candidates if font in installed_fonts), None)
    if cjk_font:
        plt.rcParams["font.sans-serif"] = [cjk_font, "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
        x_label = "LLM_LABEL 的回归系数及 95% 置信区间"
        y_label = "Prompt"
        title = "提示词敏感性：同一模型、同一样本、不同 prompt"
    else:
        x_label = "Regression coefficient of LLM_LABEL (95% CI)"
        y_label = "Prompt"
        title = "Prompt sensitivity: same model and sample"

    plot_df = plot_df.sort_values("coefficient").reset_index(drop=True)
    fig_height = max(3.0, 0.55 * len(plot_df) + 1.4)
    fig, ax = plt.subplots(figsize=(8.2, fig_height))
    y = np.arange(len(plot_df))
    xerr = np.vstack(
        [plot_df["coefficient"] - plot_df["ci_low"], plot_df["ci_high"] - plot_df["coefficient"]]
    )
    ax.errorbar(
        plot_df["coefficient"],
        y,
        xerr=xerr,
        fmt="o",
        color="#1F5A94",
        ecolor="#83A8C5",
        capsize=3,
        markersize=5,
    )
    ax.axvline(0, color="#5A5A5A", linewidth=1, linestyle="--")
    labels = [f"{row.prompt_id} ({row.strategy})" for row in plot_df.itertuples()]
    ax.set_yticks(y, labels)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    if args.provider == "openai" and not args.model:
        raise SystemExit("真实调用时必须使用 --model 或环境变量 LLM_MODEL 指定模型名。")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = RunConfig(
        data=args.data,
        prompts=args.prompts,
        output_dir=str(output_dir),
        model=args.model,
        provider=args.provider,
        text_column=args.text_column,
        id_column=args.id_column,
        human_label_column=args.human_label_column,
        formula=args.formula,
        regression_family=args.regression_family,
        coefficient_of_interest=args.coefficient_of_interest,
        cluster_column=args.cluster_column,
        prompt_limit=args.prompt_limit,
        max_rows=args.max_rows,
        temperature=args.temperature,
    )

    data = read_csv_source(args.data)
    prompts = read_csv_source(args.prompts)
    data, prompts = ensure_inputs(data, prompts, args.text_column, args.id_column)
    if args.max_rows:
        data = data.head(args.max_rows).copy()
    if args.prompt_limit:
        prompts = prompts.head(args.prompt_limit).copy()
    if data.empty or prompts.empty:
        raise SystemExit("数据或 prompt 为空，无法运行。")

    if args.provider == "openai":
        api_key = os.getenv(args.api_key_env)
        if not api_key:
            raise SystemExit(f"环境变量 {args.api_key_env} 为空。请在本机设置 API key 后重试。")
        classifier: Callable[[str], tuple[int, str]] = OpenAICompatibleClassifier(
            api_key=api_key,
            base_url=os.getenv(args.base_url_env) or None,
            model=args.model,
            temperature=args.temperature,
        )
    else:
        classifier = MockClassifier()

    cache = JsonlCache(output_dir / "prediction_cache.jsonl", enabled=not args.no_cache)
    print(f"开始运行：{len(data)} 条文本 × {len(prompts)} 个 prompt。")
    predictions = annotate_all(data, prompts, classifier, config, args.sleep_seconds, cache)
    metrics, regression = summarize_by_prompt(predictions, config)

    predictions.to_csv(output_dir / "predictions_long.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(output_dir / "metrics_by_prompt.csv", index=False, encoding="utf-8-sig")
    regression.to_csv(output_dir / "regression_by_prompt.csv", index=False, encoding="utf-8-sig")
    plot_coefficients(regression, output_dir / "coefficient_sensitivity.png")
    metadata = asdict(config)
    metadata.update(
        {
            "run_finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "n_texts": int(len(data)),
            "n_prompts": int(len(prompts)),
            "n_annotation_calls": int(len(predictions)),
        }
    )
    (output_dir / "run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n已生成：")
    print(f"- {output_dir / 'predictions_long.csv'}")
    print(f"- {output_dir / 'metrics_by_prompt.csv'}")
    print(f"- {output_dir / 'regression_by_prompt.csv'}")
    print(f"- {output_dir / 'coefficient_sensitivity.png'} (若回归成功)")
    print("\n请优先查看：metrics_by_prompt.csv 中的 FPR/FNR，以及 regression_by_prompt.csv 中系数方向、区间和 p 值。")


if __name__ == "__main__":
    main()
