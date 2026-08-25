"""'현황 분석' 페이지 — 선택 지역 지도 + 인구구조 / GIS 접근성 카드."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

import ai_module as ai
from components.map_view import create_region_map
from components.metric_card import render_metric_row
from state import get_selected_region


def render() -> None:
    selected = get_selected_region()
    sigu, dong, region_code = selected["sigu"], selected["dong"], selected["region_code"]

    region_result = ai.get_region_result(region_code)
    base_year = region_result["region"]["year"]
    population = region_result["population"]
    accessibility = region_result["accessibility"]
    living_area = region_result["living_area"]

    st.markdown('<div class="gov-section-title"> 충북 읍·면·동 지도</div>', unsafe_allow_html=True)
    m = create_region_map(sigu, dong, region_code)
    st_folium(m, width=None, height=460, returned_objects=[])

    st.markdown(f"<div class='gov-section-title'> {dong} 인구구조</div>", unsafe_allow_html=True)
    st.caption(f"기준 데이터: {base_year}년")
    render_metric_row([
        ("총 인구", f"{int(population['총인구']):,}", "명"),
        ("청년 비율", f"{population['청년비율']:.1f}", "%"),
        ("고령화율", f"{population['고령화율']:.1f}", "%"),
        ("전년 대비 인구증감률", f"{population['인구증감률_전년']:+.2f}", "%"),
    ])

    st.markdown(f"<div class='gov-section-title'> {dong} GIS 접근성</div>", unsafe_allow_html=True)
    render_metric_row([
        ("의료시설 평균접근거리", f"{accessibility['의료_평균접근거리']:,.0f}", "m"),
        ("응급의료 평균접근거리", f"{accessibility['응급의료_평균접근거리']:,.0f}", "m"),
        ("교육시설 평균접근거리", f"{accessibility['교육시설_평균접근거리']:,.0f}", "m"),
        ("교통거점 평균접근거리", f"{accessibility['교통거점_평균접근거리']:,.0f}", "m"),
    ])

    with st.expander("인구구조 · GIS 접근성 · 생활권 인프라 상세 데이터 보기"):
        detail_rows = []
        for label, value in population.items():
            detail_rows.append({"구분": "인구구조", "항목": label, "값": value})
        for label, value in accessibility.items():
            detail_rows.append({"구분": "GIS 접근성", "항목": label, "값": value})
        for label, value in living_area.items():
            detail_rows.append({"구분": "생활권 인프라", "항목": label, "값": value})
        st.dataframe(pd.DataFrame(detail_rows), width="stretch", hide_index=True)
