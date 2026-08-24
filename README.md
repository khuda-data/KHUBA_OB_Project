# 🏛️ 충북 지역소멸 대응 AI 시뮬레이터 (MVP)

충청북도 읍·면·동 단위 지역소멸 대응을 위한 AI 기반 정책 시뮬레이션 웹 애플리케이션입니다.
AI 예측 / SHAP / What-if 계산은 공동 레포 [khuda-data/KHUBA_OB_Project](https://github.com/khuda-data/KHUBA_OB_Project) `main`에
머지된 메인개발 1의 서비스 레이어(`src/`)를 그대로 연동합니다.

## 주요 기능

1. **지역 선택** — 충북 시·군 및 읍·면·동 단위 선택 (Folium 지도 시각화, AI 서비스 레이어의 최신 지역 데이터 기준)
2. **지역 현황** — 인구구조 / GIS 접근성 / 생활권 인프라 실데이터 대시보드
3. **AI 예측** — 다음 해 순이동률 AI 예측 (XGBoost, `final_model.pkl`)
4. **SHAP 요인분석** — Global / Local SHAP 기반 모델 예측 기여도
5. **What-if 시뮬레이션** — 정책 변수별 10/20/30% 개선 모델 기반 민감도 분석

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

```
project-root/
├── app.py               # Streamlit 메인 UI (지역 선택 상태관리, 지도, 지표 카드, AI 분석 탭)
├── ai_module.py          # src.* AI 서비스 레이어 어댑터 (모델/데이터 캐싱 + 함수 매핑)
├── run.sh                 # macOS libomp 폴백 실행 스크립트
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
