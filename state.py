"""
세션 상태 헬퍼
──────────────────────────────────────────────
지역 선택(시·군 / 읍·면·동) 세션 상태를 한 곳에서 초기화·조회한다.
sidebar 컴포넌트가 값을 쓰고, 각 views/*.py 페이지는 여기서 읽기만 한다.
"""

import streamlit as st

import ai_module as ai

SIGU_KEY = "sigu"
DONG_KEY = "dong"


def init_region_state() -> None:
    """세션에 시·군/읍·면·동이 없으면 기본값으로 채운다."""
    sigu_list = ai.get_sigungu_list()
    default_sigu = "제천시" if "제천시" in sigu_list else sigu_list[0]

    if SIGU_KEY not in st.session_state:
        st.session_state[SIGU_KEY] = default_sigu
    if st.session_state[SIGU_KEY] not in sigu_list:
        st.session_state[SIGU_KEY] = default_sigu

    dong_list = ai.get_eupmyeondong_list(st.session_state[SIGU_KEY])
    if DONG_KEY not in st.session_state or st.session_state[DONG_KEY] not in dong_list:
        st.session_state[DONG_KEY] = dong_list[0]


def get_selected_region() -> dict:
    """현재 선택된 지역 정보(시·군, 읍·면·동, 지역코드)를 반환한다."""
    sigu = st.session_state[SIGU_KEY]
    dong = st.session_state[DONG_KEY]
    region_code = ai.get_region_code(sigu, dong)
    return {"sigu": sigu, "dong": dong, "region_code": region_code}
