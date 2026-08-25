from __future__ import annotations

import json

import numpy as np

from .whatif_service import run_what_if_scenarios


REPRESENTATIVE_REGIONS = {
    "교육시설_평균접근거리": 4380025000,
    "산업거점_평균접근거리": 4313037000,
    "응급의료_평균접근거리": None,
    "교통거점_평균접근거리": 4311131000,
}

SCENARIO_CONFIG = {
    "교육시설_평균접근거리": {
        "scenario_name": "교육시설 접근성 개선",
        "improvement_rates": [0.1, 0.2, 0.3],
        "description": "교육시설 평균 접근거리를 단계적으로 낮춘 조건에서 모델 예측 변화를 확인하는 시연용 What-if 시나리오",
    },
    "산업거점_평균접근거리": {
        "scenario_name": "산업거점 접근성 개선",
        "improvement_rates": [0.1, 0.2, 0.3],
        "description": "산업거점 평균 접근거리를 단계적으로 낮춘 조건에서 모델 예측 변화를 확인하는 시연용 What-if 시나리오",
    },
    "응급의료_평균접근거리": {
        "scenario_name": "응급의료 접근성 개선",
        "improvement_rates": [0.1, 0.2, 0.3],
        "description": "응급의료 평균 접근거리를 단계적으로 낮춘 조건에서 모델 예측 변화를 확인하는 시연용 What-if 시나리오",
    },
    "교통거점_평균접근거리": {
        "scenario_name": "교통거점 접근성 개선",
        "improvement_rates": [0.1, 0.2, 0.3],
        "description": "교통거점 평균 접근거리를 단계적으로 낮춘 조건에서 모델 예측 변화를 확인하는 시연용 What-if 시나리오",
    },
}


def _validate_scenarios(scenarios: list[dict], feature: str) -> None:
    if len(scenarios) != 3:
        raise ValueError(f"Expected three scenarios for feature={feature}, got {len(scenarios)}")

    for scenario in scenarios:
        for key in [
            "original_value",
            "new_value",
            "original_prediction",
            "whatif_prediction",
            "change",
        ]:
            if not np.isfinite(float(scenario[key])):
                raise ValueError(f"Representative scenario contains non-finite value: {key}")


def run_representative_scenarios(
    model,
    latest_df,
    features,
    representative_regions: dict | None = None,
    scenario_config: dict | None = None,
) -> list[dict]:
    """Run configured model-based What-if sensitivity scenarios for representative regions."""
    regions = representative_regions or REPRESENTATIVE_REGIONS
    config = scenario_config or SCENARIO_CONFIG
    results = []

    for feature, scenario_meta in config.items():
        region_code = regions.get(feature)
        if region_code is None:
            continue

        scenarios = run_what_if_scenarios(
            model=model,
            latest_df=latest_df,
            region_code=region_code,
            feature=feature,
            features=features,
        )
        _validate_scenarios(scenarios, feature)

        first = scenarios[0]
        result = {
            "feature": feature,
            "scenario_name": str(scenario_meta["scenario_name"]),
            "region_code": int(region_code),
            "시군": str(first["시군"]),
            "읍면동": str(first["읍면동"]),
            "description": str(scenario_meta["description"]),
            "scenarios": scenarios,
        }
        json.dumps(result, ensure_ascii=False)
        results.append(result)

    json.dumps(results, ensure_ascii=False)
    return results
