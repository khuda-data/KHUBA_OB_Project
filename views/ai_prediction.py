"""'AI 예측' 페이지 — 예측 카드 + SHAP 카드 2단 배치 + AI 분석 결과 해석."""

import streamlit as st

import ai_module as ai
from components.charts import PLOTLY_CONFIG, make_shap_chart, pretty
from components.insight_box import ai_insight_box
from components.metric_card import render_signed_value
from state import get_selected_region


def render() -> None:
    selected = get_selected_region()
    sigu, dong, region_code = selected["sigu"], selected["dong"], selected["region_code"]

    st.markdown(f'<div class="gov-header-title" style="font-size:1.3rem;">{sigu} {dong} AI 예측 및 기여도 분석</div>', unsafe_allow_html=True)
    st.caption(
        "다음 해 순이동률을 예측하고, 모델 예측에 대한 변수별 기여도를 확인합니다.",
        help=(
            "순이동률이란? 특정 지역에서 전입자 수와 전출자 수의 차이를 인구 대비 비율로 나타낸 지표입니다. "
            "양수(+)면 순유입(전입이 전출보다 많음, 인구 증가 방향), 음수(-)면 순유출(전출이 전입보다 많음, "
            "인구 감소 방향)을 의미합니다."
        ),
    )

    region_result = ai.get_region_result(region_code)
    prediction = region_result["prediction"]
    pred_val = prediction["value"]
    local_shap = ai.get_local_shap(region_code, top_k=5)
    top_features = local_shap["top_features"]

    col_pred, col_shap = st.columns(2)

    with col_pred:
        with st.container(border=True):
            st.markdown("**다음 해 순이동률 예측**")
            st.caption(
                f"기준 데이터: {prediction['base_year']}년 → "
                f"예측 대상: {prediction['prediction_year']}년"
            )
            status = "순유입 (인구 증가 예측)" if pred_val >= 0 else "순유출 (인구 감소 예측)"
            arrow = "▲" if pred_val >= 0 else "▼"
            render_signed_value(
                value_text=f"{pred_val:+.2f}%",
                is_positive=pred_val >= 0,
                badge_text=f"{arrow} {status}",
                caption=f"예측 모델: XGBoost Regressor · 타깃: {prediction['target']}",
            )

    with col_shap:
        with st.container(border=True):
            st.markdown(f"**SHAP 모델 예측 기여도 분석 (상위 {len(top_features)}개 변수)**")
            for item in top_features:
                sign = "+" if item["shap_value"] >= 0 else ""
                color = "#0055aa" if item["shap_value"] >= 0 else "#dc2626"
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; padding:0.3rem 0; "
                    f"border-bottom:1px solid #f1f5f9;'>"
                    f"<span>{pretty(item['feature'])}</span>"
                    f"<span style='color:{color}; font-weight:700;'>{sign}{item['shap_value']:.3f}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    top_feature = top_features[0]
    contribution_direction = "음(-)의" if top_feature["shap_value"] < 0 else "양(+)의"
    tag_names = [pretty(item["feature"]).replace(" ", "_") for item in top_features[:3]]

    ai_insight_box(
        title="AI 분석 결과 해석",
        body_html=(
            f"{dong}의 다음 해 순이동률은 <b>{pred_val:+.2f}%</b>로 예측됩니다. "
            f"SHAP 분석 결과, 예측값에 가장 크게 기여한 변수는 "
            f"<b>{pretty(top_feature['feature'])}</b>이며, 이 변수는 예측값에 {contribution_direction} 기여를 보이고 있습니다. "
            f"SHAP는 원인이 아닌 <b>모델 예측 기여도</b>를 나타내는 지표입니다."
        ),
        tags=tag_names,
    )

    with st.expander("지역별 최신 데이터 기준 Global SHAP 보기"):
        st.caption("현재 분석 대상 충북 읍·면·동의 지역별 최신 데이터에서 산출한 모델 예측 기여도의 절대값 평균입니다.")
        global_shap = ai.get_global_shap(top_k=8)
        # 양/음이 상쇄되는 mean_shap이 아닌, 절대값 평균(mean_abs_shap)으로 피처 중요도를 표시한다.
        global_shap_dict = {item["feature"]: item["mean_abs_shap"] for item in global_shap["top_features"]}
        fig_global = make_shap_chart(global_shap_dict, "지역별 최신 데이터 — 모델 예측 기여도(절대값 평균)")
        st.plotly_chart(fig_global, use_container_width=True, config=PLOTLY_CONFIG)
