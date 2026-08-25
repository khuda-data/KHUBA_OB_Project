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
    region_result = ai.get_region_result(region_code)
    prediction = region_result["prediction"]

    st.markdown(f'<div class="gov-header-title" style="font-size:1.3rem;">{dong} What-if 정책 시뮬레이션</div>', unsafe_allow_html=True)
    st.caption(
        "정책 변수를 조절해 AI 모델의 예측 순이동률 변화를 확인하는 모델 기반 민감도 분석입니다. "
        "실제 정책 시행의 인과효과를 보장하지 않습니다.",
        help=(
            "순이동률이란? 특정 지역에서 전입자 수와 전출자 수의 차이를 인구 대비 비율로 나타낸 지표입니다. "
            "양수(+)면 순유입(전입이 전출보다 많음, 인구 증가 방향), 음수(-)면 순유출(전출이 전입보다 많음, "
            "인구 감소 방향)을 의미합니다."
        ),
    )
    st.caption(
        f"기준 데이터: {prediction['base_year']}년 · "
        f"예측 대상: {prediction['prediction_year']}년"
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
    scenario_summary = ai.summarize_what_if_scenarios(scenarios)
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
            st.markdown("**조건 변경 후 모델 예측**")
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
    if not scenario_summary["direction_consistent"] or not scenario_summary["monotonic"]:
        recommendation = (
            "개선율에 따른 예측 변화가 일관되지 않아 신중한 해석이 필요합니다. "
            f"가장 큰 예측 변화는 <b>{best_rate}% 조건</b>에서 "
            f"<b>{scenario_summary['best_change']:+.2f}%p</b>입니다."
        )
    elif scenario_summary["all_positive"]:
        recommendation = (
            "개선율 증가에 따라 모델 예측값이 일관되게 증가하는 패턴입니다. "
            f"가장 큰 예측 변화는 <b>{best_rate}% 조건</b>에서 "
            f"<b>{scenario_summary['best_change']:+.2f}%p</b>입니다."
        )
    elif scenario_summary["all_negative"]:
        recommendation = (
            "해당 조건에서 예측값이 증가하는 패턴은 확인되지 않습니다. "
            f"가장 작은 예측 변화는 <b>{scenario_summary['worst_change']:+.2f}%p</b>입니다."
        )
    else:
        recommendation = scenario_summary["interpretation"]

    ai_insight_box(
        title="모델 기반 시뮬레이션 분석",
        body_html=recommendation + " 이는 '정책 인과효과'가 아닌 모델 기반 민감도 분석 결과이며, 실제 정책 시행 결과와는 차이가 있을 수 있습니다.",
        tags=[pretty(target_feature).replace(" ", "_"), f"{best_rate}%_개선"],
    )

    info_box(
        "<b>해석:</b> What-if는 특정 입력 변수를 바꿨을 때 같은 학습 모델의 예측값이 어떻게 달라지는지 확인하는 "
        "모델 기반 민감도 분석입니다. 실제 정책 시행의 인과효과를 보장하지 않습니다."
    )
