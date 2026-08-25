from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import build_latest_region_data, load_model_bundle, load_region_data
from src.service import get_region_result
from src.shap_service import get_local_shap
from src.whatif_service import (
    WHAT_IF_FEATURES,
    run_what_if_scenarios,
    summarize_what_if_scenarios,
)
from src.scenario_service import run_representative_scenarios


REGION_CODE = "지역코드"
EXPECTED_REGION_COUNT = 146
EXPECTED_RATES = {0.1, 0.2, 0.3}
ABS_TOL = 1e-12

REGRESSION_PREDICTIONS = {
    4311255000: -2.1026148796081543,
    4376025000: 0.07471337169408798,
    4315035000: 0.3260554373264313,
}

REGRESSION_WHAT_IF = {
    (4311131000, "교통거점_평균접근거리"): [
        0.08216649293899536,
        0.20424970984458923,
        0.32829549908638,
    ],
    (4380025000, "교육시설_평균접근거리"): [
        0.014055654406547546,
        0.014055654406547546,
        0.11344194412231445,
    ],
    (4313037000, "산업거점_평균접근거리"): [
        0.007948875427246094,
        0.0477750301361084,
        0.0817837119102478,
    ],
}


def _assert_finite(value, context: str) -> None:
    if not math.isfinite(float(value)):
        raise AssertionError(f"{context} is not finite: {value}")


def _assert_json(value, context: str) -> None:
    try:
        json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"{context} is not JSON serializable") from exc


def _assert_close(actual: float, expected: float, context: str) -> None:
    if not math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=ABS_TOL):
        raise AssertionError(f"{context}: expected {expected}, got {actual}")


def main() -> int:
    failures: list[str] = []
    json_ok = True
    prediction_success = 0
    local_shap_success = 0
    whatif_success = 0
    summary_success = 0
    base_year_counts: Counter[int] = Counter()
    prediction_year_counts: Counter[int] = Counter()

    try:
        bundle = load_model_bundle()
        df = load_region_data(model_bundle=bundle)
        latest_df = build_latest_region_data(df)
        model = bundle["model"]
        features = bundle["features"]
        target = bundle["target"]
        region_codes = latest_df[REGION_CODE].astype(int).tolist()

        if len(region_codes) != EXPECTED_REGION_COUNT:
            raise AssertionError(
                f"Expected {EXPECTED_REGION_COUNT} latest regions, got {len(region_codes)}"
            )
    except Exception as exc:
        print("AI HEALTH CHECK")
        print(f"DATA / MODEL: FAIL ({type(exc).__name__}: {exc})")
        print("FINAL: FAIL")
        return 1

    for region_code in region_codes:
        try:
            result = get_region_result(model, latest_df, region_code, features, target)
            prediction = result["prediction"]
            _assert_finite(prediction["value"], f"prediction region={region_code}")
            if prediction["target"] != target:
                raise AssertionError(f"target mismatch region={region_code}")
            if prediction["prediction_year"] != prediction["base_year"] + 1:
                raise AssertionError(f"year metadata mismatch region={region_code}")
            base_year_counts[int(prediction["base_year"])] += 1
            prediction_year_counts[int(prediction["prediction_year"])] += 1
            _assert_json(result, f"region_result region={region_code}")
            prediction_success += 1
        except Exception as exc:
            json_ok = False
            failures.append(f"Prediction region={region_code}: {type(exc).__name__}: {exc}")

        try:
            local_shap = get_local_shap(model, latest_df, region_code, features, top_k=5)
            top_features = local_shap["top_features"]
            if len(top_features) != 5:
                raise AssertionError(f"expected 5 top features, got {len(top_features)}")
            abs_values = [float(item["abs_shap"]) for item in top_features]
            if abs_values != sorted(abs_values, reverse=True):
                raise AssertionError("Local SHAP abs_shap is not descending")
            for item in top_features:
                _assert_finite(item["feature_value"], f"local SHAP feature_value region={region_code}")
                _assert_finite(item["shap_value"], f"local SHAP shap_value region={region_code}")
                _assert_finite(item["abs_shap"], f"local SHAP abs_shap region={region_code}")
            _assert_json(local_shap, f"local_shap region={region_code}")
            local_shap_success += 1
        except Exception as exc:
            json_ok = False
            failures.append(f"Local SHAP region={region_code}: {type(exc).__name__}: {exc}")

        for feature in WHAT_IF_FEATURES:
            try:
                scenarios = run_what_if_scenarios(model, latest_df, region_code, feature, features)
                if len(scenarios) != 3:
                    raise AssertionError(f"expected 3 scenarios, got {len(scenarios)}")
                for scenario in scenarios:
                    rate = float(scenario["improvement_rate"])
                    if rate not in EXPECTED_RATES:
                        raise AssertionError(f"unexpected improvement_rate={rate}")
                    _assert_finite(scenario["original_prediction"], "original_prediction")
                    _assert_finite(scenario["whatif_prediction"], "whatif_prediction")
                    _assert_finite(scenario["change"], "change")
                    _assert_json(scenario, f"What-if scenario region={region_code} feature={feature}")
                    whatif_success += 1

                summary = summarize_what_if_scenarios(scenarios)
                if not isinstance(summary["direction_consistent"], bool):
                    raise AssertionError("direction_consistent must be bool")
                if not isinstance(summary["monotonic"], bool):
                    raise AssertionError("monotonic must be bool")
                if float(summary["best_rate"]) not in EXPECTED_RATES:
                    raise AssertionError(f"unexpected best_rate={summary['best_rate']}")
                _assert_finite(summary["best_change"], "best_change")
                _assert_finite(summary["worst_change"], "worst_change")
                if not str(summary["interpretation"]):
                    raise AssertionError("interpretation is empty")
                _assert_json(summary, f"What-if summary region={region_code} feature={feature}")
                summary_success += 1
            except Exception as exc:
                json_ok = False
                failures.append(
                    f"What-if region={region_code} feature={feature}: {type(exc).__name__}: {exc}"
                )

    representative_success = 0
    try:
        representative = run_representative_scenarios(model, latest_df, features)
        expected = {
            ("교육시설_평균접근거리", 4380025000),
            ("산업거점_평균접근거리", 4313037000),
            ("교통거점_평균접근거리", 4311131000),
        }
        actual = {(item["feature"], int(item["region_code"])) for item in representative}
        if actual != expected:
            raise AssertionError(f"representative scenarios mismatch: {actual}")
        for item in representative:
            if len(item["scenarios"]) != 3:
                raise AssertionError(f"expected 3 representative scenarios: {item}")
        _assert_json(representative, "representative scenarios")
        representative_success = len(representative)
    except Exception as exc:
        json_ok = False
        failures.append(f"Representative scenarios: {type(exc).__name__}: {exc}")

    regression_ok = True
    for region_code, expected in REGRESSION_PREDICTIONS.items():
        try:
            result = get_region_result(model, latest_df, region_code, features, target)
            _assert_close(
                result["prediction"]["value"],
                expected,
                f"prediction regression region={region_code}",
            )
        except Exception as exc:
            regression_ok = False
            failures.append(f"Regression prediction region={region_code}: {type(exc).__name__}: {exc}")

    for (region_code, feature), expected_changes in REGRESSION_WHAT_IF.items():
        try:
            scenarios = run_what_if_scenarios(model, latest_df, region_code, feature, features)
            for scenario, expected_change in zip(scenarios, expected_changes):
                _assert_close(
                    scenario["change"],
                    expected_change,
                    f"What-if regression region={region_code} feature={feature}",
                )
        except Exception as exc:
            regression_ok = False
            failures.append(
                f"Regression What-if region={region_code} feature={feature}: "
                f"{type(exc).__name__}: {exc}"
            )

    expected_base_years = {2022: 2, 2023: 2, 2024: 142}
    expected_prediction_years = {2023: 2, 2024: 2, 2025: 142}
    if dict(sorted(base_year_counts.items())) != expected_base_years:
        failures.append(f"base_year distribution mismatch: {dict(sorted(base_year_counts.items()))}")
    if dict(sorted(prediction_year_counts.items())) != expected_prediction_years:
        failures.append(
            f"prediction_year distribution mismatch: {dict(sorted(prediction_year_counts.items()))}"
        )

    final_ok = not failures and json_ok and regression_ok

    print("AI HEALTH CHECK")
    print(f"Regions: {len(region_codes)}/{EXPECTED_REGION_COUNT} {'PASS' if len(region_codes) == EXPECTED_REGION_COUNT else 'FAIL'}")
    print(f"Prediction: {prediction_success}/{EXPECTED_REGION_COUNT} {'PASS' if prediction_success == EXPECTED_REGION_COUNT else 'FAIL'}")
    print(f"Local SHAP: {local_shap_success}/{EXPECTED_REGION_COUNT} {'PASS' if local_shap_success == EXPECTED_REGION_COUNT else 'FAIL'}")
    print(f"What-if scenarios: {whatif_success}/1752 {'PASS' if whatif_success == 1752 else 'FAIL'}")
    print(f"What-if summaries: {summary_success}/584 {'PASS' if summary_success == 584 else 'FAIL'}")
    print(f"Representative scenarios: {representative_success}/3 {'PASS' if representative_success == 3 else 'FAIL'}")
    print(f"JSON serialization: {'PASS' if json_ok else 'FAIL'}")
    print(f"Regression: {'PASS' if regression_ok else 'FAIL'}")
    print(f"base_year distribution: {dict(sorted(base_year_counts.items()))}")
    print(f"prediction_year distribution: {dict(sorted(prediction_year_counts.items()))}")
    if failures:
        print("Failures:")
        for failure in failures[:20]:
            print(f"- {failure}")
    print(f"FINAL: {'PASS' if final_ok else 'FAIL'}")
    return 0 if final_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
