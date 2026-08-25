"""
AI 서비스 레이어 어댑터
──────────────────────────────────────────────
공동 레포(khuda-data/KHUBA_OB_Project) main 브랜치에 머지된
메인개발 1의 src.* 서비스 함수를 Streamlit 앱이 쓰기 편한 형태로 감싼 얇은 어댑터입니다.

- 모델 번들(final_model.pkl)과 최신 지역 데이터(src.data_loader.build_latest_region_data)는
  프로세스당 1회만 로드해 st.cache_resource로 캐싱합니다.
- 지역코드/시군/읍면동 조회, 예측, SHAP, What-if 계산은 모두 src.* 함수를 그대로 호출합니다.
  반환 형식은 AI_Service_Layer_Integration_Guide.md 및 src/README.md 기준을 따릅니다.
"""

import streamlit as st

from src.data_loader import build_latest_region_data, load_model_bundle, load_region_data
from src.region_service import (
    get_sigungu_list as _get_sigungu_list,
    get_eupmyeondong_list as _get_eupmyeondong_list,
    get_region_code as _get_region_code,
)
from src.service import get_region_result as _get_region_result
from src.shap_service import global_shap as _global_shap, get_local_shap as _get_local_shap
from src.whatif_service import (
    WHAT_IF_FEATURES,
    run_what_if_scenarios as _run_what_if_scenarios,
    summarize_what_if_scenarios as _summarize_what_if_scenarios,
)
from src.scenario_service import run_representative_scenarios as _run_representative_scenarios


# What-if로 조정 가능한 정책 변수 (src.whatif_service.WHAT_IF_FEATURES 그대로 노출)
WHATIF_FEATURES = WHAT_IF_FEATURES


@st.cache_resource(show_spinner="AI 모델 및 지역 데이터를 불러오는 중...")
def _load_bundle():
    bundle = load_model_bundle()
    df = load_region_data(model_bundle=bundle)
    latest_df = build_latest_region_data(df)
    return bundle, latest_df


def get_sigungu_list() -> list:
    """시·군 목록 반환 (최신 지역 데이터 기준)."""
    _, latest_df = _load_bundle()
    return _get_sigungu_list(latest_df)


def get_eupmyeondong_list(sigungu: str) -> list:
    """선택 시·군의 읍·면·동 목록 반환."""
    _, latest_df = _load_bundle()
    return _get_eupmyeondong_list(latest_df, sigungu)


def get_region_code(sigungu: str, eupmyeondong: str) -> int:
    """시·군 + 읍·면·동으로 지역코드 조회."""
    _, latest_df = _load_bundle()
    return _get_region_code(latest_df, sigungu, eupmyeondong)


@st.cache_data(show_spinner=False)
def get_region_result(region_code: int) -> dict:
    """지역 현황(인구/접근성/생활권) + 다음 해 순이동률 예측을 함께 반환.

    반환 top-level key: region, population, accessibility, living_area, prediction
    """
    bundle, latest_df = _load_bundle()
    return _get_region_result(
        bundle["model"], latest_df, region_code, bundle["features"], bundle["target"]
    )


@st.cache_data(show_spinner=False)
def get_local_shap(region_code: int, top_k: int = 5) -> dict:
    """읍면동 단위 Local SHAP TOP-K 모델 예측 기여도 반환."""
    bundle, latest_df = _load_bundle()
    return _get_local_shap(
        bundle["model"], latest_df, region_code, bundle["features"], top_k=top_k
    )


@st.cache_data(show_spinner=False)
def get_global_shap(top_k: int = 8) -> dict:
    """지역별 최신 데이터 기준 Global SHAP 모델 예측 기여도 요약 반환."""
    bundle, latest_df = _load_bundle()
    X = latest_df[bundle["features"]]
    return _global_shap(bundle["model"], X, top_k=top_k)


@st.cache_data(show_spinner=False)
def run_what_if_scenarios(region_code: int, feature: str) -> list:
    """선택 정책 변수에 대해 10/20/30% 개선 모델 기반 민감도 분석 3건을 반환."""
    bundle, latest_df = _load_bundle()
    return _run_what_if_scenarios(
        bundle["model"], latest_df, region_code, feature, bundle["features"]
    )


def summarize_what_if_scenarios(scenarios: list) -> dict:
    """계산된 What-if 10/20/30% 결과의 방향성과 단조성을 요약."""
    return _summarize_what_if_scenarios(scenarios)


@st.cache_data(show_spinner=False)
def run_representative_scenarios() -> list:
    """대표 지역별 시연용 What-if 시나리오 목록 반환."""
    bundle, latest_df = _load_bundle()
    return _run_representative_scenarios(bundle["model"], latest_df, bundle["features"])


@st.cache_data(show_spinner="충북 전체 146개 지역 예측을 계산하는 중...")
def get_all_predictions() -> dict:
    """충북 전체 지역의 다음 해 순이동률 예측을 {지역코드: 예측값} 형태로 일괄 반환.

    지역 선택(개요) 화면의 전체 지도 색상 표시용. predict_region()과 동일한 모델/피처를
    지역 단위 반복 대신 벡터화해서 한 번에 계산한다.
    """
    bundle, latest_df = _load_bundle()
    predictions = bundle["model"].predict(latest_df[bundle["features"]])
    return dict(zip(latest_df["지역코드"].astype(int), predictions.astype(float)))
