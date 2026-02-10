"""
윈도우용 파이썬 타이머 위젯
- 10분 업무 / 10분 휴식 타이머
- 60분 목표 대비 진행률 표시
"""

import sys
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

        btn_layout.addWidget(work_btn)
        btn_layout.addWidget(rest_btn)
        layout.addLayout(btn_layout)

        # 하단: 60분 목표 대비 진행률
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(28)
        layout.addWidget(self.progress_bar)

    def start_timer(self, seconds: int, is_work: bool):
        self.remaining_seconds = seconds
        self._current_session_is_work = is_work
        self.timer.start(1000)

    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.time_label.setText(self.format_time(self.remaining_seconds))

            # 업무 모드일 때만 60분 목표에 누적
            if self._current_session_is_work:
                self.elapsed_work_seconds += 1
                progress = min(100, int(self.elapsed_work_seconds / self.goal_total_seconds * 100))
                self.progress_bar.setValue(progress)

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.time_label.setText("00:00")

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
