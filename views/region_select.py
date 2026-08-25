"""'지역 선택' 페이지 — 충청지역 전체 개요 지도 + 시군별 요약."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

import ai_module as ai
from components.map_view import create_overview_map
from state import get_selected_region


def render() -> None:
    st.markdown('<div class="gov-section-title"> 충청지역 전체 개요</div>', unsafe_allow_html=True)
    st.caption(
        "색상은 AI 모델이 예측한 다음 해 순이동률입니다. 좌측 사이드바에서 시·군/읍·면·동을 선택하면 다른 페이지에서 해당 지역의 상세 분석을 볼 수 있습니다.",
        help=(
            "순이동률이란? 특정 지역에서 전입자 수와 전출자 수의 차이를 인구 대비 비율로 나타낸 지표입니다. "
            "양수(+)면 순유입(전입이 전출보다 많음, 인구 증가 방향), 음수(-)면 순유출(전출이 전입보다 많음, "
            "인구 감소 방향)을 의미합니다."
        ),
    )

    predictions = ai.get_all_predictions()
    m = create_overview_map(predictions)
    st_folium(m, width=None, height=520, returned_objects=[])

    selected = get_selected_region()
    with st.container(border=True):
        st.markdown(f"현재 선택된 지역: **{selected['sigu']} {selected['dong']}** — 아래에서 상세 내용을 확인하세요.")
        pages = st.session_state.get("nav_pages", {})
        link_c1, link_c2, link_c3 = st.columns(3)
        with link_c1:
            if "status" in pages:
                st.page_link(pages["status"], label="현황 분석", icon=":material/query_stats:")
                st.caption("인구구조 · GIS 접근성 데이터")
        with link_c2:
            if "ai-prediction" in pages:
                st.page_link(pages["ai-prediction"], label="AI 예측", icon=":material/smart_toy:")
                st.caption("순이동률 예측 · SHAP 요인 분석")
        with link_c3:
            if "simulation" in pages:
                st.page_link(pages["simulation"], label="시뮬레이션", icon=":material/tune:")
                st.caption("What-if 정책 변수 민감도 분석")

    st.markdown('<div class="gov-section-title"> 시·군별 예측 요약</div>', unsafe_allow_html=True)

    bundle_rows = []
    for sigu in ai.get_sigungu_list():
        dong_list = ai.get_eupmyeondong_list(sigu)
        codes = [ai.get_region_code(sigu, dong) for dong in dong_list]
        values = [predictions[c] for c in codes if c in predictions]
        if not values:
            continue
        bundle_rows.append({
            "시·군": sigu,
            "읍면동 수": len(values),
            "평균 예측 순이동률(%)": round(sum(values) / len(values), 2),
            "최저 예측(%)": round(min(values), 2),
            "최고 예측(%)": round(max(values), 2),
        })

    df = pd.DataFrame(bundle_rows).sort_values("평균 예측 순이동률(%)")
    st.dataframe(df, width="stretch", hide_index=True)
