"""
AI 멀티모달 현장 안전 및 드론 사진 판독 모듈
- Google Gemini 1.5 Flash 모델 연동
- 산업안전보건기준에 관한 규칙 기반 위험 요소 자동 판독
"""

import os
import json
import base64
import requests

SAFETY_ANALYSIS_PROMPT = """
당신은 대한민국 산업안전보건법 및 중대재해처벌법 전문 공인 안전관리 기술사입니다.
제공된 현장 또는 드론 항공 사진을 정밀하게 분석하여 다음 6대 핵심 위험 요소를 판독하십시오:

1. [추락 위험] 비계, 슬래브 단부, 지붕 등의 안전난간 미설치, 작업발판 불량
2. [개구부 위험] 바닥 개구부 덮개 미고정 및 안전표지 부착 여부
3. [개인보호구] 근로자 안전모 턱끈 체결 여부, 고소작업 안전대 체결 여부
4. [중장비/충돌] 지게차, 굴착기 등 작업 반경 내 신호수/유도자 배치 여부
5. [화재/폭발] 화기 작업 주변 소화기 비치 및 인화물질 격리 여부
6. [환경/정리] 작업 통로 적치물 및 전도 위험 요소

반드시 아래 JSON 포맷으로만 응답하십시오:
{
  "inspection_title": "사진 주요 현장 및 작업 개요",
  "overall_risk_grade": "양호 / 주의 / 위험 / 치명적 중 하나",
  "detected_hazards": [
    {
      "hazard_type": "위험 분류 (예: 추락 위험, 보호구 미착용 등)",
      "legal_basis": "관련 법령 (예: 산업안전보건기준에 관한 규칙 제42조)",
      "description": "구체적인 부적합 현장 상황 설명",
      "risk_level": "보통 / 높음 / 치명적",
      "suggested_action": "즉각적인 시정 조치 방안"
    }
  ],
  "ppe_compliance": {
    "helmet_detected": true/false,
    "chinstrap_fastened": true/false,
    "safety_harness": true/false
  },
  "safety_score": 0~100 사이 정수,
  "summary_review": "현장 안전 종합 총평 및 권고사항 (3줄 이내)"
}
"""

def analyze_image_with_gemini(image_bytes, mime_type="image/jpeg", api_key=None):
    """
    Gemini 1.5 Flash를 이용한 멀티모달 이미지 안전점검 판독
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")

    # API 키가 등록되어 있는 경우 실제 Gemini 1.5 Flash 호출
    if key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": SAFETY_ANALYSIS_PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": encoded_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                }
            }
            
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                result_json = res.json()
                raw_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_text)
            else:
                return {
                    "error": f"API 호출 오류 (HTTP {res.status_code}): {res.text}"
                }
        except Exception as e:
            return {"error": f"분석 중 예외 발생: {str(e)}"}

    # API 키가 없을 때 제공하는 시뮬레이션 데모 결과 (즉시 체험용)
    return {
        "inspection_title": "드론 항공 촬영 고소작업 구역 점검 (데모 분석 모드)",
        "overall_risk_grade": "위험",
        "detected_hazards": [
            {
                "hazard_type": "추락 위험",
                "legal_basis": "산업안전보건기준에 관한 규칙 제42조 (추락의 방지)",
                "description": "슬래브 단부 외곽 6m 구간에 상부/중간 안전난간이 미설치된 상태임",
                "risk_level": "치명적",
                "suggested_action": "근로자 접근 즉시 차단 후 표준 규격 안전난간 및 폭목 설치"
            },
            {
                "hazard_type": "개인보호구 미흡",
                "legal_basis": "산업안전보건기준에 관한 규칙 제32조 (보호구의 착용)",
                "description": "철근 배근 작업자 중 1명 안전모 턱끈 풀림 상태 식별",
                "risk_level": "보통",
                "suggested_action": "현장 방송 또는 관리자 구두 지도로 턱끈 즉각 체결 조치"
            }
        ],
        "ppe_compliance": {
            "helmet_detected": True,
            "chinstrap_fastened": False,
            "safety_harness": True
        },
        "safety_score": 65,
        "summary_review": "단부 안전난간 미설치로 인한 중대재해(추락) 위험이 매우 높습니다. 작업 전 즉각적인 안전난간 보강 및 작업자 턱끈 체결 확인이 필수적입니다."
    }
