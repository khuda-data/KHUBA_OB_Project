"""'시뮬레이션' 페이지 — What-if 정책 변수 설정 + 시나리오 비교 + 시나리오별 비교 해석."""

import pandas as pd
import streamlit as st

import ai_module as ai
from components.charts import PLOTLY_CONFIG, make_whatif_comparison_chart, pretty
from components.insight_box import ai_insight_box, info_box
from components.metric_card import render_signed_value
from state import get_selected_region


def render() -> None:
    selected = get_selected_region()
    sigu, dong, region_code = selected["sigu"], selected["dong"], selected["region_code"]

    st.markdown(f'<div class="gov-header-title" style="font-size:1.3rem;">{dong} What-if 정책 시뮬레이션</div>', unsafe_allow_html=True)
    st.caption(
        "정책 변수를 조절해 AI 모델의 예측 순이동률 변화를 확인하는 모델 기반 민감도 분석입니다. "
        "실제 정책 시행의 인과효과를 보장하지 않습니다."
    )

    col_setting, col_chart = st.columns([1, 1.2])

    with col_setting:
        with st.container(border=True):
            st.markdown("**정책 변수 설정**")
            st.caption("시뮬레이션에 적용할 정책 변수와 개선율을 선택하세요.")

            target_feature = st.selectbox(
                "개선 정책 변수", ai.WHATIF_FEATURES, format_func=pretty, key="whatif_feature",
            )
            rate_option = st.select_slider(
                "개선율", options=[10, 20, 30], value=20, format_func=lambda x: f"{x}%", key="whatif_rate",
            )

    scenarios = ai.run_what_if_scenarios(region_code, target_feature)
    rate_to_scenario = {round(s["improvement_rate"] * 100): s for s in scenarios}
    selected_scenario = rate_to_scenario[rate_option]

    base_pred = selected_scenario["original_prediction"]
    after_pred = selected_scenario["whatif_prediction"]
    diff = selected_scenario["change"]
    scenario_values = {round(s["improvement_rate"] * 100): s["whatif_prediction"] for s in scenarios}

    with col_chart:
        with st.container(border=True):
            st.markdown("**시나리오별 예측 순이동률 변화**")
            fig = make_whatif_comparison_chart(base_pred, scenario_values, target_feature)
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    result_c1, result_c2 = st.columns(2)
    with result_c1:
        with st.container(border=True):
            st.markdown("**기존 예측값**")
            render_signed_value(value_text=f"{base_pred:+.2f}%", is_positive=base_pred >= 0)
    with result_c2:
        with st.container(border=True):
            st.markdown("**정책 적용 후**")
            render_signed_value(
                value_text=f"{after_pred:+.2f}%",
                is_positive=after_pred >= 0,
                badge_text=f"변화량 {diff:+.2f}%p",
                badge_positive=diff >= 0,
            )

    st.caption(
        f"{pretty(target_feature)}: "
        f"{selected_scenario['original_value']:,.0f}m → {selected_scenario['new_value']:,.0f}m "
        f"({rate_option}% 개선 조건)"
    )

    st.markdown("**시나리오 비교 상세**")
    table_rows = [{
        "구분": "Base",
        "개선율": "0%",
        f"{pretty(target_feature)}": f"{scenarios[0]['original_value']:,.0f}m",
        "예측 순이동률": f"{base_pred:+.2f}%",
        "변화량": "-",
    }]
    for s in scenarios:
        rate_pct = round(s["improvement_rate"] * 100)
        table_rows.append({
            "구분": f"시나리오 ({rate_pct}%)",
            "개선율": f"{rate_pct}%",
            f"{pretty(target_feature)}": f"{s['new_value']:,.0f}m",
            "예측 순이동률": f"{s['whatif_prediction']:+.2f}%",
            "변화량": f"{s['change']:+.2f}%p",
        })
    st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

    best_scenario = max(scenarios, key=lambda s: s["change"])
    best_rate = round(best_scenario["improvement_rate"] * 100)
    if best_scenario["change"] > 0:
        recommendation = (
            f"현재 데이터 기반 분석 결과, <b>{pretty(target_feature)}을(를) {best_rate}% 개선</b>하는 조건에서 "
            f"예측 순이동률이 <b>{best_scenario['change']:+.2f}%p</b>로 가장 긍정적인 변화를 보이는 시나리오로 해석됩니다."
        )
    else:
        recommendation = (
            f"선택한 조건({pretty(target_feature)})에서는 10~30% 개선 시나리오 모두 예측 순이동률 개선 효과가 "
            f"뚜렷하게 나타나지 않는 것으로 해석됩니다. 다른 정책 변수도 함께 비교해 보세요."
        )

    ai_insight_box(
        title="모델 기반 시뮬레이션 분석",
        body_html=recommendation + " 이는 '정책 인과효과'가 아닌 모델 기반 민감도 분석 결과이며, 실제 정책 시행 효과와는 차이가 있을 수 있습니다.",
        tags=[pretty(target_feature).replace(" ", "_"), f"{best_rate}%_개선"],
    )

    info_box(
        "<b>해석:</b> What-if는 특정 입력 변수를 바꿨을 때 같은 학습 모델의 예측값이 어떻게 달라지는지 확인하는 "
        "모델 기반 민감도 분석입니다. 실제 정책 시행의 인과효과를 보장하지 않습니다."
    )
