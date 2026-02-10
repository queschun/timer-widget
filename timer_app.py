"""
윈도우용 파이썬 타이머 위젯
- 10분 업무 / 10분 휴식 타이머
- 60분 목표 대비 진행률 표시
"""

import sys
import time
import winsound

from win11toast import toast
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class TimerWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        # 윈도우 속성 설정
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 크기: 400x400 픽셀 (약 10cm x 10cm)
        self.setFixedSize(400, 400)

        # 드래그를 위한 변수
        self.drag_position = None

        # 타이머 상태
        self.remaining_seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)

        # 60분 목표 대비 진행 시간 (초)
        self.goal_total_seconds = 60 * 60  # 3600초
        self.elapsed_work_seconds = 0
        self._current_session_is_work = False

        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 배경 스타일 (50% 반투명) + 가독성 높은 흰색 텍스트
        central.setStyleSheet("""
            QWidget#central {
                background-color: rgba(40, 44, 52, 128);
                border-radius: 10px;
            }
            QPushButton {
                background-color: rgba(97, 175, 239, 180);
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 13pt;
            }
            QPushButton:hover {
                background-color: rgba(97, 175, 239, 220);
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: rgba(77, 155, 219, 255);
                color: #ffffff;
            }
            QPushButton#restBtn {
                background-color: rgba(129, 199, 132, 180);
                color: #ffffff;
            }
            QPushButton#restBtn:hover {
                background-color: rgba(129, 199, 132, 220);
                color: #ffffff;
            }
            QPushButton#restBtn:pressed {
                background-color: rgba(109, 179, 112, 255);
                color: #ffffff;
            }
            QPushButton#exitBtn {
                background-color: rgba(158, 158, 158, 180);
                font-size: 11pt;
            }
            QPushButton#exitBtn:hover {
                background-color: rgba(180, 80, 80, 200);
            }
            QPushButton#exitBtn:pressed {
                background-color: rgba(160, 60, 60, 255);
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                background-color: rgba(60, 64, 72, 200);
                color: #ffffff;
                font-size: 12pt;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 5px;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #61afef,
                    stop:1 #56b6c2
                );
            }
        """)
        central.setObjectName("central")

        # 상단: 남은 시간 표시 (큰 폰트)
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI", 80, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #ffffff;")
        self.time_label.setMinimumHeight(100)
        layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 버튼: 10분 업무, 10분 휴식
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        work_btn = QPushButton("10분 업무")
        work_btn.setObjectName("workBtn")
        work_btn.clicked.connect(lambda: self.start_timer(10 * 60, is_work=True))

        rest_btn = QPushButton("10분 휴식")
        rest_btn.setObjectName("restBtn")
        rest_btn.clicked.connect(lambda: self.start_timer(10 * 60, is_work=False))

        exit_btn = QPushButton("종료")
        exit_btn.setObjectName("exitBtn")
        exit_btn.clicked.connect(self.close_app)

        btn_layout.addWidget(work_btn)
        btn_layout.addWidget(rest_btn)
        btn_layout.addWidget(exit_btn)
        layout.addLayout(btn_layout)

        # 하단: 60분 목표 대비 진행률
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(28)
        layout.addWidget(self.progress_bar)

    def close_app(self):
        """앱 종료."""
        self.timer.stop()
        QApplication.quit()

    def start_timer(self, seconds: int, is_work: bool):
        """타이머 시작. 이미 실행 중이면 시간을 초기화하고 새 세션으로 전환."""
        self.remaining_seconds = seconds
        self._current_session_is_work = is_work
        self.time_label.setText(self.format_time(seconds))

        if not self.timer.isActive():
            self.timer.start(1000)
        # 실행 중이어도 remaining_seconds 갱신으로 update_countdown이 새 값 사용

    def update_countdown(self):
        """QTimer 콜백: 1초마다 남은 시간 감소, MM:SS 실시간 업데이트."""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.time_label.setText(self.format_time(self.remaining_seconds))

            # 업무 모드일 때만 60분 목표에 누적
            if self._current_session_is_work:
                self.elapsed_work_seconds += 1
                progress = min(100, int(self.elapsed_work_seconds / self.goal_total_seconds * 100))
                self.progress_bar.setValue(progress)

            # 0이 된 직후: 00:00 화면 먼저 보여준 뒤 알람
            if self.remaining_seconds == 0:
                self.time_label.setText("00:00")
                QApplication.processEvents()
                self.timer.stop()
                self.timer_finished()

    def timer_finished(self):
        """0초 도달 시 비프음, 시스템 알림, 콘솔 출력, UI 초기화가 동시에 실행."""
        # 1. 비프음: 1000Hz, 0.5초, 0.1초 간격으로 3번 반복
        try:
            for i in range(3):
                winsound.Beep(1000, 500)
                if i < 2:
                    time.sleep(0.1)
        except Exception as e:
            print(f"[사운드 오류] {e}")

        # 2. 시스템 알림 (win11toast) + 시스템 사운드
        try:
            toast("타이머 종료", "업무 시간이 끝났습니다!", audio="ms-winsound-notification-reminder")
        except Exception as e:
            print(f"[알림 오류] {e}")

        # 3. 콘솔 출력 및 UI 초기화
        print("업무 종료!")
        self.time_label.setText("10:00")

    def format_time(self, seconds: int) -> str:
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_position is not None:
            diff = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + diff)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    widget = TimerWidget()
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
