import requests

# Ollama 로컬 API 호출 테스트
url = "http://localhost:11434/api/generate"
data = {
    "model": "gemma3:4b",
    "prompt": "안녕! 너는 누구니? 한국어로 짧게 대답해줘.",
    "stream": False
}

try:
    res = requests.post(url, json=data)
    print("🤖 AI 답변:", res.json()['response'])
except Exception as e:
    print("❌ 오류 발생:", e)