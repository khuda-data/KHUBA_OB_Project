"""
좌측 "분석 필터" 사이드바
──────────────────────────────────────────────
frontend/*/DESIGN.md 목업의 좌측 고정 필터 패널을 재현한다.
모든 페이지 상단에서 호출되며, 선택된 시·군/읍·면·동을 st.session_state에 반영한다.
"""

import streamlit as st

import ai_module as ai
from data.dong_data import is_depopulation_area
from state import DONG_KEY, SIGU_KEY


def render_sidebar_filters() -> None:
    """사이드바에 지역 필터 UI를 그리고 st.session_state를 갱신한다."""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-title">
            <span class="sidebar-title-main">분석 필터</span>
            <span class="sidebar-title-sub">충청북도 지역소멸 대응</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-label">시·군 필터</div>', unsafe_allow_html=True)
        sigu_list = ai.get_sigungu_list()
        sigu_idx = sigu_list.index(st.session_state[SIGU_KEY]) if st.session_state[SIGU_KEY] in sigu_list else 0
        selected_sigu = st.selectbox(
            "시·군 선택", sigu_list, index=sigu_idx, key="sigu_select", label_visibility="collapsed",
        )
        st.session_state[SIGU_KEY] = selected_sigu

        st.markdown('<div class="sidebar-section-label">읍·면·동 필터</div>', unsafe_allow_html=True)
        dong_list = ai.get_eupmyeondong_list(selected_sigu)
        if st.session_state[DONG_KEY] not in dong_list:
            st.session_state[DONG_KEY] = dong_list[0]
        dong_idx = dong_list.index(st.session_state[DONG_KEY])
        selected_dong = st.selectbox(
            "읍·면·동 선택", dong_list, index=dong_idx, key="dong_select", label_visibility="collapsed",
        )
        st.session_state[DONG_KEY] = selected_dong

        if is_depopulation_area(selected_sigu):
            st.markdown('<span class="badge-danger">주의: 인구감소지역</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-success">일반지역</span>', unsafe_allow_html=True)
