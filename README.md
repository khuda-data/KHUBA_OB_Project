# 충북 지역소멸 대응 AI 시뮬레이터 (MVP)

충청북도 읍·면·동 단위 지역소멸 대응을 위한 AI 기반 정책 시뮬레이션 웹 애플리케이션입니다.
AI 예측 / SHAP / What-if 계산은 공동 레포 [khuda-data/KHUBA_OB_Project](https://github.com/khuda-data/KHUBA_OB_Project) `main`에
머지된 메인개발 1의 서비스 레이어(`src/`)를 그대로 연동합니다.

UI는 `frontend/*/DESIGN.md` + `code.html`/`screen.png` 목업(상단 탭 네비게이션 + 좌측 "분석 필터" 사이드바)을
Streamlit 네이티브 멀티페이지(`st.navigation(position="top")`)로 재현했습니다. 목업에 있던 로그인 버튼,
가상의 "소멸위험지수", "일자리 창출 지원금" 같은 항목은 실제 AI 서비스 레이어에 없는 값이라 넣지 않았습니다 —
화면에 보이는 모든 수치는 `src/`가 계산한 실제 값입니다.

## 페이지 구성 (상단 탭, 클릭 시 실제로 URL이 바뀌며 페이지 전환)

1. **지역 선택** — 충북 전체 146개 읍·면·동을 AI 예측 순이동률 기준 색상으로 표시하는 개요 지도 + 시·군별 요약표
2. **현황 분석** — 선택 지역 지도 + 인구구조 / GIS 접근성 / 생활권 인프라 실데이터 카드
3. **AI 예측** — 다음 해 순이동률 예측 (XGBoost) + Local SHAP 모델 예측 기여도, AI 해석 박스
4. **시뮬레이션** — 정책 변수별 10/20/30% 개선 What-if 모델 기반 민감도 분석 + 시나리오 비교표 + AI 제언

지역(시·군/읍·면·동) 선택은 모든 페이지에 공통으로 뜨는 좌측 사이드바("분석 필터")에서 하며,
선택 상태는 페이지를 이동해도 유지됩니다.

## 실행 방법

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 앱 실행
streamlit run app.py
```

### macOS(Apple Silicon)에서 XGBoost 오류가 날 경우

XGBoost는 실행에 `libomp.dylib`(OpenMP)이 필요합니다. Homebrew가 있다면:

```bash
brew install libomp
```

Homebrew가 없다면, `scikit-learn`을 추가 설치한 뒤 동봉된 `run.sh`로 실행하세요
(scikit-learn 휠에 번들된 libomp 사본 경로를 자동으로 찾아 폴백으로 지정합니다).

```bash
pip install scikit-learn
./run.sh
```

## 프로젝트 구조

새 화면을 추가하거나 기존 화면을 고칠 때 건드릴 파일이 명확히 나뉘어 있습니다.
**화면 하나만 고치고 싶으면 `views/` 안의 해당 파일만 보면 됩니다.**

```
project-root/
├── app.py                  # 진입점 — 페이지 정의(st.navigation) + 공통 헤더/CSS/사이드바 호출만 담당
├── state.py                  # 세션 상태(선택된 시·군/읍·면·동) 초기화·조회 헬퍼
├── ai_module.py                # src.* AI 서비스 레이어 어댑터 (모델/데이터 캐싱 + 함수 매핑)
├── run.sh                       # macOS libomp 폴백 실행 스크립트
│
├── views/                        # 화면(페이지)별 콘텐츠 — 탭 하나 = 파일 하나
│   ├── region_select.py            # "지역 선택" 탭: 충북 전체 개요 지도 + 시·군별 요약
│   ├── status_overview.py           # "현황 분석" 탭: 선택 지역 지도 + 인구/GIS 카드
│   ├── ai_prediction.py              # "AI 예측" 탭: 예측 + SHAP 카드 + 해석 박스
│   └── whatif_simulation.py           # "시뮬레이션" 탭: What-if 슬라이더 + 시나리오 비교
│
├── components/                    # 여러 화면에서 재사용하는 UI 조각 (수정 시 모든 화면에 반영됨)
│   ├── sidebar.py                    # 좌측 "분석 필터" 패널 (시·군/읍·면·동 선택)
│   ├── metric_card.py                 # 지표 카드 (render_metric_card / render_metric_row)
│   ├── charts.py                       # Plotly 차트 (SHAP 바 차트, What-if 비교 차트)
│   ├── map_view.py                     # Folium 지도 (단일 지역 강조 / 전체 개요 choropleth)
│   └── insight_box.py                   # "해석" / "AI 분석 결과 해석" 박스(해시태그 칩)
│
├── assets/
│   └── styles.css                # 전역 CSS 한 곳에 모음 (frontend/*/DESIGN.md 색상 토큰 기반)
│
├── src/                    # 공동 레포 main에서 머지된 AI 서비스 레이어 (그대로 vendored)
│   ├── data_loader.py       # 모델 번들 / 지역 데이터 로딩, build_latest_region_data()
│   ├── region_service.py    # 시군·읍면동 조회, 지역 현황(get_region_summary)
│   ├── inference.py         # AI 예측 (predict_region)
│   ├── service.py           # 지역 현황 + 예측 통합 (get_region_result)
│   ├── shap_service.py      # Global/Local SHAP
│   ├── whatif_service.py    # What-if 시나리오 계산
│   └── scenario_service.py  # 대표 지역 시연용 시나리오
├── models/
│   └── final_model.pkl     # 학습된 모델 번들 (model/features/target)
├── data/
│   ├── chungbuk_dong.geojson   # 읍면동 행정경계 (지역코드=adm_cd2로 AI 데이터와 매칭)
│   ├── dong_data.py             # 지도용 GeoJSON 헬퍼 (좌표/경계는 GeoJSON에서 직접 파생)
│   └── 충북_최종학습데이터_E세트.csv  # AI 서비스 레이어 학습/조회용 데이터
├── frontend/               # 화면별 디자인 시스템 참고 자료 (DESIGN.md + 목업)
├── requirements.txt
└── README.md
```

### 자주 하는 수정 작업별 안내

| 하고 싶은 일 | 고칠 파일 |
|---|---|
| 카드에 새 지표 추가 | 해당 `views/*.py`에서 `render_metric_row([...])` 항목 추가 |
| 새 탭(페이지) 추가 | `views/`에 파일 추가 → `app.py`의 `pages` 리스트에 `st.Page(...)` 한 줄 추가 |
| 사이드바 필터 항목 추가 | `components/sidebar.py` |
| 색상/폰트/여백 등 디자인 변경 | `assets/styles.css` |
| AI 서비스 레이어 함수 새로 연동 | `ai_module.py`에 어댑터 함수 추가 (`src.*` 원본은 건드리지 않음) |

## 기술 스택

- Python, Streamlit, Folium, Plotly, Pandas, NumPy
- XGBoost, SHAP, joblib (AI 서비스 레이어)

## 팀

KHUDA OB 심화 프로젝트

## 주의사항

- `ai_module.py`는 AI 서비스 레이어(`src/`)를 그대로 호출하는 얇은 어댑터이며, Stub이 아닙니다.
- `src/`는 공동 레포에서 머지된 코드를 그대로 vendoring한 것이며, 로컬 Python 3.9 호환을 위해
  각 파일 맨 위에 `from __future__ import annotations` 한 줄만 추가했습니다(동작 변경 없음).
- 지도 표시 지역코드(GeoJSON `adm_cd2`)와 AI 데이터의 `지역코드`는 1:1로 매칭됩니다(146/153개 읍면동에 AI 데이터 존재).
- 모든 What-if 해석 문구는 **인과관계를 직접 단정하지 않습니다** ("모델 기반 민감도 분석"으로 표현).
- SHAP은 **"모델 예측 기여도"**로 표현하며, 원인으로 해석하지 않습니다.
