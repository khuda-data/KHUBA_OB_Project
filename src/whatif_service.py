from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .inference import predict_region, prepare_model_input
from .region_service import get_region_row


WHAT_IF_FEATURES = [
    "교육시설_평균접근거리",
    "산업거점_평균접근거리",
    "응급의료_평균접근거리",
    "교통거점_평균접근거리",
]
ALLOWED_IMPROVEMENT_RATES = [0.1, 0.2, 0.3]
DEFAULT_CONSISTENCY_TOLERANCE = 1e-9


def _to_finite_float(value, name: str) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"What-if value is not finite: {name}")
    return result


def _validate_what_if_inputs(
    feature: str,
    improvement_rate: float,
    features: list[str],
) -> float:
    if feature not in WHAT_IF_FEATURES:
        raise ValueError(f"Feature is not allowed for What-if scenarios: {feature}")
    if feature not in features:
        raise ValueError(f"Feature is not in model features: {feature}")

    try:
        normalized_rate = float(improvement_rate)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"improvement_rate must be one of {ALLOWED_IMPROVEMENT_RATES}: "
            f"{improvement_rate}"
        ) from exc

    if not any(np.isclose(normalized_rate, allowed) for allowed in ALLOWED_IMPROVEMENT_RATES):
        raise ValueError(
            f"improvement_rate must be one of {ALLOWED_IMPROVEMENT_RATES}: "
            f"{improvement_rate}"
        )

    return normalized_rate


def _predict_one(model, model_input: pd.DataFrame, context: str) -> float:
    if not hasattr(model, "predict"):
        raise ValueError(f"model must provide a predict method, got {type(model).__name__}")

    try:
        prediction = model.predict(model_input)
    except Exception as exc:
        raise ValueError(f"model.predict failed during {context}") from exc

    prediction_array = np.asarray(prediction).reshape(-1)
    if prediction_array.size != 1:
        raise ValueError(
            f"Expected exactly one prediction during {context}, "
            f"got {prediction_array.size}"
        )

    return _to_finite_float(prediction_array[0], f"{context} prediction")


def run_what_if(
    model,
    latest_df: pd.DataFrame,
    region_code: int | str,
    feature: str,
    improvement_rate: float,
    features: list[str],
) -> dict:
    """Run one model-based What-if sensitivity scenario for a distance feature."""
    normalized_rate = _validate_what_if_inputs(feature, improvement_rate, features)

    try:
        normalized_region_code = int(region_code)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"region_code must be convertible to int: {region_code}") from exc

    row = get_region_row(latest_df, normalized_region_code)
    original_value = _to_finite_float(
        pd.to_numeric(row[feature], errors="coerce"),
        feature,
    )

    original_model_input = prepare_model_input(row, features)
    original_prediction = predict_region(
        model,
        latest_df,
        normalized_region_code,
        features,
    )["prediction"]

    # Keep the direct model-input path validated for this scenario calculation.
    direct_original_prediction = _predict_one(
        model,
        original_model_input,
        "original What-if baseline",
    )
    if not np.isclose(original_prediction, direct_original_prediction):
        raise ValueError(
            "Baseline prediction mismatch between predict_region and direct model input"
        )

    new_value = original_value * (1 - normalized_rate)

    whatif_row = row.copy()
    whatif_row[feature] = new_value
    whatif_model_input = prepare_model_input(whatif_row, features)
    whatif_prediction = _predict_one(
        model,
        whatif_model_input,
        "What-if scenario",
    )
    change = whatif_prediction - original_prediction

    result = {
        "region_code": normalized_region_code,
        "year": int(row["연도"]),
        "시군": str(row["시군"]),
        "읍면동": str(row["읍면동"]),
        "feature": str(feature),
        "improvement_rate": _to_finite_float(normalized_rate, "improvement_rate"),
        "original_value": _to_finite_float(original_value, "original_value"),
        "new_value": _to_finite_float(new_value, "new_value"),
        "original_prediction": _to_finite_float(
            original_prediction,
            "original_prediction",
        ),
        "whatif_prediction": _to_finite_float(
            whatif_prediction,
            "whatif_prediction",
        ),
        "change": _to_finite_float(change, "change"),
    }
    json.dumps(result, ensure_ascii=False)
    return result


def run_what_if_scenarios(
    model,
    latest_df: pd.DataFrame,
    region_code: int | str,
    feature: str,
    features: list[str],
) -> list[dict]:
    """Run 10%, 20%, and 30% model-based What-if scenarios."""
    results = [
        run_what_if(
            model=model,
            latest_df=latest_df,
            region_code=region_code,
            feature=feature,
            improvement_rate=rate,
            features=features,
        )
        for rate in ALLOWED_IMPROVEMENT_RATES
    ]
    json.dumps(results, ensure_ascii=False)
    return results


def summarize_what_if_scenarios(
    scenarios: list[dict],
    tolerance: float = DEFAULT_CONSISTENCY_TOLERANCE,
) -> dict:
    """Summarize consistency of precomputed model-based What-if scenarios."""
    if not scenarios:
        raise ValueError("scenarios must be a non-empty list")

    try:
        tol = abs(float(tolerance))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"tolerance must be numeric: {tolerance}") from exc

    sorted_scenarios = sorted(
        scenarios,
        key=lambda scenario: _to_finite_float(
            scenario["improvement_rate"],
            "improvement_rate",
        ),
    )
    changes = [
        _to_finite_float(scenario["change"], "change")
        for scenario in sorted_scenarios
    ]
    rates = [
        _to_finite_float(scenario["improvement_rate"], "improvement_rate")
        for scenario in sorted_scenarios
    ]

    signs = [
        1 if change > tol else -1 if change < -tol else 0
        for change in changes
    ]
    non_zero_signs = {sign for sign in signs if sign != 0}
    has_zero_or_near_zero = any(sign == 0 for sign in signs)
    all_near_zero = all(sign == 0 for sign in signs)
    direction_consistent = len(non_zero_signs) <= 1
    all_positive = bool(non_zero_signs) and non_zero_signs == {1}
    all_negative = bool(non_zero_signs) and non_zero_signs == {-1}

    nondecreasing = all(
        later >= earlier - tol
        for earlier, later in zip(changes, changes[1:])
    )
    nonincreasing = all(
        later <= earlier + tol
        for earlier, later in zip(changes, changes[1:])
    )
    monotonic = nondecreasing or nonincreasing

    best_index = max(range(len(changes)), key=lambda index: changes[index])
    best_rate = rates[best_index]
    best_change = max(changes)
    worst_change = min(changes)

    if all_near_zero:
        interpretation = "해당 조건에서는 모델 예측값의 변화가 거의 나타나지 않습니다."
    elif not direction_consistent or not monotonic:
        interpretation = "개선율에 따른 예측 변화 방향이 일관되지 않아 신중한 해석이 필요합니다."
    elif monotonic and all_positive and has_zero_or_near_zero:
        interpretation = "일부 구간의 변화는 매우 작지만, 전반적으로 동일한 방향의 예측 변화가 나타납니다."
    elif monotonic and all_positive:
        interpretation = "개선율 증가에 따라 모델 예측값이 일관되게 증가하는 패턴입니다."
    elif monotonic and all_negative:
        interpretation = "개선율 증가에 따라 모델 예측값이 일관되게 감소하는 패턴입니다."
    else:
        interpretation = "일부 구간의 변화는 매우 작지만, 전반적으로 동일한 방향의 예측 변화가 나타납니다."

    result = {
        "direction_consistent": bool(direction_consistent),
        "monotonic": bool(monotonic),
        "all_positive": bool(all_positive),
        "all_negative": bool(all_negative),
        "has_zero_or_near_zero": bool(has_zero_or_near_zero),
        "best_rate": _to_finite_float(best_rate, "best_rate"),
        "best_change": _to_finite_float(best_change, "best_change"),
        "worst_change": _to_finite_float(worst_change, "worst_change"),
        "interpretation": interpretation,
    }
    json.dumps(result, ensure_ascii=False)
    return result


def run_what_if_scenarios_wide(
    model,
    latest_df: pd.DataFrame,
    region_code: int | str,
    feature: str,
    features: list[str],
) -> dict:
    """Return 10/20/30% What-if scenario changes in one JSON-friendly dict."""
    scenarios = run_what_if_scenarios(
        model=model,
        latest_df=latest_df,
        region_code=region_code,
        feature=feature,
        features=features,
    )
    first = scenarios[0]

    result = {
        "region_code": first["region_code"],
        "year": first["year"],
        "시군": first["시군"],
        "읍면동": first["읍면동"],
        "feature": first["feature"],
        "original_value": first["original_value"],
        "original_prediction": first["original_prediction"],
        "scenarios": [
            {
                "improvement_rate": item["improvement_rate"],
                "new_value": item["new_value"],
                "whatif_prediction": item["whatif_prediction"],
                "change": item["change"],
            }
            for item in scenarios
        ],
    }
    json.dumps(result, ensure_ascii=False)
    return result
