# 충북 인구이동 예측 AI 서비스 레이어

충북 읍면동별 인구/GIS/생활권 데이터를 기반으로 다음 해 순이동률을 예측하고, 모델 예측에 대한 SHAP 기여도와 모델 기반 What-if 시나리오를 제공하는 MVP용 Python 서비스 모듈입니다.

이 모듈은 프론트엔드나 API 서버에서 바로 호출할 수 있도록 데이터 로딩, 지역 조회, 예측, SHAP, What-if 결과를 JSON 직렬화 가능한 dict/list 형태로 반환합니다.

## 폴더 구조

```text
project/
  .gitignore
  README.md
  requirements.txt
  src/
    __init__.py
    data_loader.py
    region_service.py
    inference.py
    service.py
    shap_service.py
    whatif_service.py
    scenario_service.py
  data/
    충북_최종학습데이터_E세트.csv
  models/
    final_model.pkl
```

`external/ict_ai2/`는 AI2 코드 참고용 local clone이며 최종 실행에는 필요하지 않습니다.

## 설치

```bash
pip install -r requirements.txt
```

## 필요한 데이터/모델 파일

- `models/final_model.pkl`
- `data/충북_최종학습데이터_E세트.csv`

`final_model.pkl`은 다음 key를 가진 dict여야 합니다.

```text
model
features
target
```

현재 target은 `타깃_다음해_순이동률`입니다.

## 주요 서비스 함수

`src.data_loader`
- `load_model_bundle()`
- `load_region_data()`
- `build_latest_region_data()`

`src.region_service`
- `get_sigungu_list()`
- `get_eupmyeondong_list()`
- `get_region_code()`
- `get_region_summary()`

`src.inference`
- `predict_region()`

`src.service`
- `get_region_result()`

`src.shap_service`
- `global_shap()`
- `get_local_shap()`

`src.whatif_service`
- `run_what_if()`
- `run_what_if_scenarios()`
- `run_what_if_scenarios_wide()`

`src.scenario_service`
- `run_representative_scenarios()`

## 사용 예시

```python
import json

from src.data_loader import (
    build_latest_region_data,
    load_model_bundle,
    load_region_data,
)
from src.region_service import get_eupmyeondong_list, get_region_code, get_sigungu_list
from src.service import get_region_result
from src.shap_service import get_local_shap
from src.whatif_service import run_what_if_scenarios
from src.scenario_service import run_representative_scenarios

bundle = load_model_bundle()
df = load_region_data(model_bundle=bundle)
latest_df = build_latest_region_data(df)

sigungu_list = get_sigungu_list(latest_df)
eupmyeondong_list = get_eupmyeondong_list(latest_df, "청주시")
region_code = get_region_code(latest_df, "청주시", "산남동")

region_result = get_region_result(
    bundle["model"],
    latest_df,
    region_code,
    bundle["features"],
    bundle["target"],
)

local_shap = get_local_shap(
    bundle["model"],
    latest_df,
    region_code,
    bundle["features"],
    top_k=5,
)

whatif = run_what_if_scenarios(
    bundle["model"],
    latest_df,
    region_code,
    "교육시설_평균접근거리",
    bundle["features"],
)

representative = run_representative_scenarios(
    bundle["model"],
    latest_df,
    bundle["features"],
)

json.dumps(region_result, ensure_ascii=False)
json.dumps(local_shap, ensure_ascii=False)
json.dumps(whatif, ensure_ascii=False)
json.dumps(representative, ensure_ascii=False)
```

## 반환 형태

`get_region_result()`는 다음 top-level key를 반환합니다.

```text
region
population
accessibility
living_area
prediction
```

`get_local_shap()`는 지역 정보, prediction, Local SHAP top features를 반환합니다.

`run_what_if_scenarios()`는 10%, 20%, 30% 개선 조건의 list를 반환합니다.

`run_representative_scenarios()`는 대표 지역별 시연용 What-if 시나리오 list를 반환합니다.

## 해석 주의사항

SHAP은 모델 예측에 대한 feature별 기여도를 설명하는 방법입니다. 원인 또는 정책 효과로 해석하지 않습니다.

What-if는 특정 입력 feature를 바꿨을 때 같은 학습 모델의 예측값이 어떻게 달라지는지 확인하는 모델 기반 What-if 시나리오이자 모델 기반 민감도 분석입니다. 실제 정책 시행의 인과효과를 보장하지 않습니다.

예를 들어 “교육시설 평균 접근거리를 낮춘 조건에서 모델 예측 순이동률이 어떻게 변화하는지 확인한다”처럼 표현합니다.

## 점검 명령

```bash
python -m src.data_loader
```

모델 타입, feature 수, target, CSV shape, 지역 수, 연도 목록, latest 데이터 요약을 출력합니다.
