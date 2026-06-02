"""桌面 Overlay 基础窗口"""

import sys
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QImage, QCursor
from PyQt6.QtWidgets import QApplication, QWidget

from shared.config import DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS
from shared.recorder import FrameRecorder


class OverlayWindow(QWidget):
    """透明悬浮层基类，子类实现 draw_scene()"""

    def __init__(self, title="VibeFX", width=None, height=None, fps=DEFAULT_FPS):
        super().__init__()
        self.W = width or DEFAULT_WIDTH
        self.H = height or DEFAULT_HEIGHT
        self.fps = fps
        self.click_through = False
        self.fullscreen_mode = False
        self.frame_count = 0

        # 窗口属性
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.resize(self.W, self.H)

        # 居中显示
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.move((geo.width() - self.W) // 2, (geo.height() - self.H) // 2)

        # 录制器
        self.recorder = FrameRecorder(prefix=title.replace(" ", "_"))

        # 定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000 // self.fps)

        # 拖拽
        self._drag_pos = None

    def _tick(self):
        self.update_scene()
        self.frame_count += 1
        self.update()

    def update_scene(self):
        """子类每帧更新逻辑"""
        pass

    def draw_scene(self, painter: QPainter):
        """子类绘制逻辑"""
        pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw_scene(painter)
        painter.end()

        # 录制帧
        if self.recorder.recording:
            img = self.grabFramebuffer()
            self.recorder.capture(img)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.close()
            QApplication.quit()
        elif key == Qt.Key.Key_R:
            self.recorder.toggle()
        elif key == Qt.Key.Key_S:
            img = self.grabFramebuffer()
            self.recorder.screenshot(img)
        elif key == Qt.Key.Key_F:
            self._toggle_fullscreen()
        elif key == Qt.Key.Key_T:
            self._toggle_click_through()
        elif key == Qt.Key.Key_Space:
            self.on_regenerate()

    def on_regenerate(self):
        """子类重写：Space 重新随机"""
        pass

    def _toggle_fullscreen(self):
        if self.fullscreen_mode:
            self.showNormal()
            self.resize(self.W, self.H)
            self.fullscreen_mode = False
        else:
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.geometry()
                self.move(geo.x(), geo.y())
                self.resize(geo.width(), geo.height())
            self.fullscreen_mode = True

    def _toggle_click_through(self):
        self.click_through = not self.click_through
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        if self.click_through:
            flags |= Qt.WindowType.WindowTransparentForInput
        self.setWindowFlags(flags)
        self.show()
        print(f"[穿透] {'开' if self.click_through else '关'}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
