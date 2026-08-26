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
            <span class="sidebar-title-sub">충북 지역소멸 대응</span>
        </div>
        """, unsafe_allow_html=True)

        pages = st.session_state.get("nav_pages", {})
        if "region-select" in pages:
            st.page_link(
                pages["region-select"],
                label="충북 전체 보기",
                icon=":material/map:",
            )

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
            st.caption(
                '<span class="badge-danger">주의: 인구감소지역</span>',
                unsafe_allow_html=True,
                help=(
                    "행정안전부가 2021년 10월 지정한 전국 89개 인구감소지역 중 하나입니다 "
                    "(충북 6곳: 제천시·보은군·옥천군·영동군·괴산군·단양군)."
                ),
            )
        else:
            st.caption(
                '<span class="badge-success">일반지역</span>',
                unsafe_allow_html=True,
                help="행정안전부가 지정한 인구감소지역(충북 6곳) 목록에 포함되지 않은 지역입니다.",
            )
