from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QFontMetrics
from PySide6.QtWidgets import QAbstractScrollArea

from hex_navigation import (
    ROW_BYTES, read_hex_window, scroll_limits, scroll_to_row, row_to_scroll,
)

class FullFileHexView(QAbstractScrollArea):
    """Paint hex and ASCII for any file offset using a virtual scrollbar."""

    position_changed = Signal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.path: Path | None = None
        self.file_size = 0
        self.marked = b""
        self._first_row = 0
        self._last_row = 0
        self._scroll_max = 0
        self._visible_rows = 1
        self._error: str | None = None
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        self.setFont(font)
        self._font_metrics = QFontMetrics(font)
        self._char_width = max(1, self._font_metrics.horizontalAdvance("0"))
        self._row_height = max(16, self._font_metrics.lineSpacing() + 4)
        self.setStyleSheet("background:#101b2c; border:1px solid #30445d;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self.horizontalScrollBar().valueChanged.connect(lambda *_: self.viewport().update())
        self._recalculate_scrollbars()

    @property
    def current_offset(self) -> int:
        return self._first_row * ROW_BYTES

    def show_file(self, path: Path | None, size: int = 0):
        self.path = path
        self.file_size = max(0, int(size)) if path is not None else 0
        self._first_row = 0
        self._error = None
        self._recalculate_scrollbars()
        self._notify_position()
        self.viewport().update()

    def mark_pattern(self, pattern: bytes):
        self.marked = pattern[:256]
        self.viewport().update()

    def jump_to_offset(self, offset: int):
        if self.file_size <= 0:
            self._first_row = 0
        else:
            self._first_row = max(0, min(int(offset) // ROW_BYTES, self._last_row))
        self._set_scrollbar_for_row()
        self._notify_position()
        self.viewport().update()

    def _set_scrollbar_for_row(self):
        bar = self.verticalScrollBar()
        bar.blockSignals(True)
        bar.setValue(row_to_scroll(self._first_row, self._last_row, self._scroll_max))
        bar.blockSignals(False)

    def _notify_position(self):
        begin = self.current_offset
        end = min(self.file_size, begin + self._visible_rows * ROW_BYTES)
        self.position_changed.emit(begin, end, self.file_size)

    def _recalculate_scrollbars(self):
        viewport_height = max(1, self.viewport().height())
        self._visible_rows = max(1, (viewport_height - 8) // self._row_height)
        self._last_row, self._scroll_max = scroll_limits(self.file_size, self._visible_rows)
        self._first_row = min(self._first_row, self._last_row)
        vertical = self.verticalScrollBar()
        vertical.blockSignals(True)
        vertical.setRange(0, self._scroll_max)
        vertical.setPageStep(max(1, min(self._scroll_max + 1, self._visible_rows)))
        vertical.setSingleStep(1)
        vertical.setValue(row_to_scroll(self._first_row, self._last_row, self._scroll_max))
        vertical.blockSignals(False)
        content_width = 12 + (18 + 2 + ROW_BYTES * 3 + 3 + ROW_BYTES) * self._char_width
        horizontal = self.horizontalScrollBar()
        horizontal.setRange(0, max(0, content_width - self.viewport().width()))
        horizontal.setPageStep(self.viewport().width())
        self._notify_position()

    def _on_scroll(self, position: int):
        self._first_row = scroll_to_row(position, self._last_row, self._scroll_max)
        self._notify_position()
        self.viewport().update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._recalculate_scrollbars()
        self.viewport().update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta:
            steps = max(1, abs(delta) // 120)
            self.jump_to_offset((self._first_row + ( -3 * steps if delta > 0 else 3 * steps)) * ROW_BYTES)
            event.accept()
        elif event.pixelDelta().y():
            movement = max(1, abs(event.pixelDelta().y()) // self._row_height)
            self.jump_to_offset((self._first_row + (-movement if event.pixelDelta().y() > 0 else movement)) * ROW_BYTES)
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        step = max(1, self._visible_rows - 1)
        if key in (Qt.Key.Key_Down, Qt.Key.Key_Up, Qt.Key.Key_PageDown,
                   Qt.Key.Key_PageUp, Qt.Key.Key_Home, Qt.Key.Key_End):
            if key == Qt.Key.Key_Down:
                next_row = self._first_row + 1
            elif key == Qt.Key.Key_Up:
                next_row = self._first_row - 1
            elif key == Qt.Key.Key_PageDown:
                next_row = self._first_row + step
            elif key == Qt.Key.Key_PageUp:
                next_row = self._first_row - step
            elif key == Qt.Key.Key_Home:
                next_row = 0
            else:
                next_row = self._last_row
            self.jump_to_offset(next_row * ROW_BYTES)
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.fillRect(self.viewport().rect(), QColor("#101b2c"))
        painter.setFont(self.font())
        if self.path is None or self.file_size == 0:
            painter.setPen(QColor("#98adbf"))
            painter.drawText(12, 24, "—")
            return
        visible_bytes = self._visible_rows * ROW_BYTES
        try:
            payload = read_hex_window(self.path, self._first_row, self._visible_rows)
            self._error = None
            prefix = b""
            suffix = b""
            if self.marked:
                extra = len(self.marked) - 1
                with self.path.open("rb") as source:
                    beginning = max(0, self.current_offset - extra)
                    source.seek(beginning)
                    inspected = source.read(self.current_offset - beginning + len(payload) + extra)
                    prefix = inspected[:self.current_offset - beginning]
                    suffix = inspected[len(prefix) + len(payload):]
        except OSError as exc:
            self._error = str(exc)
            painter.setPen(QColor("#ff9f9f"))
            painter.drawText(12, 24, self._error)
            return
        matches: set[int] = set()
        if self.marked:
            inspected = prefix + payload + suffix
            search_start = 0
            while (hit := inspected.find(self.marked, search_start)) != -1:
                relative = hit - len(prefix)
                matches.update(range(max(0, relative), min(len(payload), relative + len(self.marked))))
                search_start = hit + 1
        x_shift = self.horizontalScrollBar().value()
        x0 = 10 - x_shift
        xbytes = x0 + self._char_width * 20
        xascii = xbytes + self._char_width * (ROW_BYTES * 3 + 3)
        metrics = self._font_metrics
        for line in range(0, len(payload), ROW_BYTES):
            rowdata = payload[line:line + ROW_BYTES]
            y = 6 + (line // ROW_BYTES) * self._row_height + metrics.ascent()
            painter.setPen(QColor("#889fb8"))
            painter.drawText(x0, y, f"{self.current_offset + line:016X}")
            for column, byte in enumerate(rowdata):
                absolute = self.current_offset + line + column
                color = ("#ffc5ff" if line + column in matches else
                         "#73e5ed" if absolute < 16 else
                         "#748fa5" if byte == 0 else
                         "#ffc089" if byte == 255 else
                         "#aaf5ba" if 32 <= byte <= 126 else "#b2c9f5")
                painter.setPen(QColor(color))
                painter.drawText(xbytes + column * self._char_width * 3, y, f"{byte:02X}")
            painter.setPen(QColor("#b5c4d7"))
            ascii_content = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in rowdata)
            painter.drawText(xascii, y, f"|{ascii_content}|")
