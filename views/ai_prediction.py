"""'AI 예측' 페이지 — 예측 카드 + SHAP 카드 2단 배치 + AI 분석 결과 해석."""

import streamlit as st

import ai_module as ai
from components.charts import make_shap_chart, pretty
from components.insight_box import ai_insight_box
from state import get_selected_region


def render() -> None:
    selected = get_selected_region()
    sigu, dong, region_code = selected["sigu"], selected["dong"], selected["region_code"]

    st.markdown(f'<div class="gov-header-title" style="font-size:1.3rem;">{sigu} {dong} AI 예측 및 요인 분석</div>', unsafe_allow_html=True)
    st.caption("XGBoost 기반 모델로 다음 해 순이동률을 예측하고, SHAP(모델 예측 기여도)로 주요 영향 요인을 분석합니다.")

    region_result = ai.get_region_result(region_code)
    pred_val = region_result["prediction"]["value"]
    local_shap = ai.get_local_shap(region_code, top_k=5)
    top_features = local_shap["top_features"]

    col_pred, col_shap = st.columns(2)

    with col_pred:
        st.markdown('<div class="gov-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown("**다음 해 순이동률 예측**")
        st.metric(
            label="예측 순이동률",
            value=f"{pred_val:+.2f}%",
            delta=f"{pred_val:+.2f}%p",
            delta_color="inverse",
        )
        status = "순유출 (인구 감소 예측)" if pred_val < 0 else "순유입 (인구 증가 예측)"
        status_color = "#dc2626" if pred_val < 0 else "#16a34a"
        st.markdown(
            f'<span style="color:{status_color}; font-weight:700;">{status}</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"예측 모델: XGBoost Regressor · 타깃: {region_result['prediction']['target']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_shap:
        st.markdown('<div class="gov-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown(f"**SHAP 영향 요인 분석 (상위 {len(top_features)}개 변수)**")
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
        st.markdown('</div>', unsafe_allow_html=True)

    top_feature = top_features[0]
    direction = "낮추는" if top_feature["shap_value"] < 0 else "높이는"
    tag_names = [pretty(item["feature"]).replace(" ", "_") for item in top_features[:3]]

    ai_insight_box(
        title="AI 분석 결과 해석",
        body_html=(
            f"{dong}의 다음 해 순이동률은 <b>{pred_val:+.2f}%</b>로 예측됩니다. "
            f"SHAP 분석 결과, 예측에 가장 큰 영향을 미친 요인은 "
            f"<b>{pretty(top_feature['feature'])}</b>이며, 이는 예측값을 {direction} 방향으로 작용하고 있습니다. "
            f"SHAP는 원인이 아닌 <b>모델 예측 기여도</b>를 나타내는 지표입니다."
        ),
        tags=tag_names,
    )

    with st.expander("충북 전체 지역 기준 Global SHAP 보기"):
        global_shap = ai.get_global_shap(top_k=8)
        global_shap_dict = {item["feature"]: item["mean_shap"] for item in global_shap["top_features"]}
        fig_global = make_shap_chart(global_shap_dict, "충북 전체 — 모델 예측 기여도")
        st.plotly_chart(fig_global, width="stretch")
