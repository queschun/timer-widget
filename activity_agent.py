import pygetwindow as gw
import time
import requests
import sqlite3
from datetime import datetime

# --- 설정 및 DB 초기화 ---
DB_NAME = "timesheet.db"
MODEL_NAME = "gemma3:4b"

def init_db():
    """SQLite DB와 테이블을 생성합니다."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                window_title TEXT,
                category TEXT,
                duration_sec INTEGER
            )
        ''')
    print("✅ 타임시트 데이터베이스(SQLite)가 준비되었습니다.")

def ask_ai_category(window_title):
    """Ollama를 통해 창 제목의 카테고리를 판별합니다."""
    url = "http://localhost:11434/api/generate"
    prompt = f"다음 윈도우 창 제목을 보고 [학습, 업무, 휴식] 중 하나로 분류해줘. 다른 설명 없이 딱 한 단어만 대답해: '{window_title}'"
    try:
        response = requests.post(url, json={"model": MODEL_NAME, "prompt": prompt, "stream": False}, timeout=5)
        return response.json().get('response', '미분류').strip()
    except Exception as e:
        return f"연결오류({e})"

def start_monitoring():
    init_db()
    last_window = None
    last_title = ""
    start_time = datetime.now()

    print(f"🚀 타임시트 에이전트 가동 중... (모델: {MODEL_NAME})")
    print("창을 바꿔가며 활동해 보세요. 3초마다 체크합니다.")

    try:
        while True:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title:
                current_title = active_window.title
                
                # 창이 바뀌었을 때만 처리
                if current_title != last_title:
                    now = datetime.now()
                    if last_title: # 이전 작업 기록 저장
                        duration = int((now - start_time).total_seconds())
                        category = ask_ai_category(last_title)
                        
                        with sqlite3.connect(DB_NAME) as conn:
                            conn.execute('''
                                INSERT INTO activity_logs (start_time, end_time, window_title, category, duration_sec)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (start_time, now, last_title, category, duration))
                        print(f"💾 [저장] {category} | {last_title[:30]}... ({duration}초)")

                    last_title = current_title
                    start_time = now
            
            time.sleep(3) # CPU 자원 절약
    except KeyboardInterrupt:
        print("\n👋 모니터링을 안전하게 종료합니다.")

if __name__ == "__main__":
    start_monitoring()