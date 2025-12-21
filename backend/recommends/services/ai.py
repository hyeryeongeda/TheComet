import json
from django.conf import settings
from openai import OpenAI

GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

client = OpenAI(
    api_key=settings.GMS_KEY,
    base_url=GMS_BASE_URL,
)

def _safe_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None

def run_taste_ai(message: str, history: list | None = None):
    """
    JSON만 출력 강제:
    {
      "answer": "추천 이유 2~4문장",
      "filters": { "genre_names": [...], "keywords": [...], "min_vote": 0 }
    }
    """
    system = (
        "너는 영화 추천 챗봇이다.\n"
        "반드시 JSON만 출력한다(설명/마크다운/코드펜스 금지).\n"
        "형식:\n"
        "{\n"
        '  "answer": "2~4문장 한국어",\n'
        '  "filters": {\n'
        '    "genre_names": ["드라마","코미디"],\n'
        '    "keywords": ["힐링","가족"],\n'
        '    "min_vote": 0\n'
        "  }\n"
        "}\n"
    )

    msgs = [{"role": "system", "content": system}]
    if isinstance(history, list) and history:
        msgs += history[-10:]
    msgs.append({"role": "user", "content": message})

    model = getattr(settings, "GMS_MODEL", "gpt-4o-mini")

    res = client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=0.7,
    )

    raw = res.choices[0].message.content or ""
    data = _safe_json(raw) or {"answer": raw, "filters": {}}
    return data, raw
