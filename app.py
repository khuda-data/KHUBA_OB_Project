"""
충북 읍·면·동 단위 지역소멸 대응 AI 시뮬레이터 (MVP) — 진입점
──────────────────────────────────────────────────────
메인개발 2 담당: 앱 구조 + 지역 선택 상태관리 + AI 서비스 레이어 연동 + 배포/QA

frontend/*/DESIGN.md 목업의 "상단 탭 네비게이션 + 좌측 분석 필터 사이드바" 구조를
Streamlit 네이티브 멀티페이지(st.navigation, position="top")로 재현한다.
클릭 시 실제로 페이지가 전환되며(URL도 페이지별로 바뀜), 화면별 내용은 views/*.py에,
공통 UI 조각은 components/*.py에 분리되어 있어 화면 하나를 고치는 데 다른 화면 코드를
건드릴 필요가 없다.

각 페이지가 실제로 하는 일은 views/*.py를 열어 보면 된다:
- views/region_select.py     지역 선택(충북 전체 개요 지도)
- views/status_overview.py    현황 분석(인구구조/GIS 접근성 카드)
- views/ai_prediction.py       AI 예측(예측값 + SHAP)
- views/whatif_simulation.py    시뮬레이션(What-if 정책 변수)

AI 예측 / SHAP / What-if 계산은 공동 레포(khuda-data/KHUBA_OB_Project) main에 머지된
메인개발 1의 src.* 서비스 함수를 ai_module.py를 통해 그대로 호출한다.
"""

from pathlib import Path

import streamlit as st

from components.sidebar import render_sidebar_filters
from state import init_region_state
from views import ai_prediction, region_select, status_overview, whatif_simulation

pages = [
    st.Page(region_select.render, title="지역 선택", url_path="region-select", default=True),
    st.Page(status_overview.render, title="현황 분석", url_path="status"),
    st.Page(ai_prediction.render, title="AI 예측", url_path="ai-prediction"),
    st.Page(whatif_simulation.render, title="시뮬레이션", url_path="simulation"),
]
# region_select.py에서 st.page_link()로 다른 페이지로 이동하는 카드형 버튼을 만들 때 쓸 수 있도록
# url_path -> st.Page 매핑을 세션에 저장해 둔다.
st.session_state["nav_pages"] = {p.url_path: p for p in pages}

pg = st.navigation(pages, position="top")

_ICON_PATH = Path(__file__).parent / "icon.png"
if not _ICON_PATH.exists():
    _ICON_PATH = Path(__file__).parent / "icon.jpg"
page_icon = str(_ICON_PATH) if _ICON_PATH.exists() else ":material/account_balance:"

st.set_page_config(
    page_title="충북 지역소멸 대응 AI 시뮬레이터",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

_CSS_PATH = Path(__file__).parent / "assets" / "styles.css"
st.markdown(f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="gov-header-container">
    <span class="gov-badge">충청북도 데이터 기반 정책 지원 시스템</span>
    <h1 class="gov-header-title">읍·면·동 단위 지역소멸 대응 AI 시뮬레이터</h1>
    <p class="gov-header-sub">인구감소지역 미세 분석 및 What-if 정책 시나리오 비교·분석 플랫폼</p>
</div>
""", unsafe_allow_html=True)

init_region_state()
render_sidebar_filters()

pg.run()

st.markdown("""
<div class="footer-text">
    충북 지역소멸 대응 AI 시뮬레이터 (MVP) · KHUDA OB 심화 프로젝트<br>
    본 시스템의 분석 결과는 AI 모델 기반 시뮬레이션이며, 정책 결정의 참고 자료로만 활용하시기 바랍니다.
</div>
""", unsafe_allow_html=True)
