from __future__ import annotations

from html import escape
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QTextEdit, QVBoxLayout, QWidget,
)

from hex_full_view import FullFileHexView

PAGE_BYTES = 256


class HexViewer(QWidget):
    def __init__(self, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.path: Path | None = None
        self.file_size = 0
        self.offset = 0
        self.sha256 = ""
        self.marked = b""
        self.full_file_mode = False
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.prev_button, self.next_button = QPushButton(), QPushButton()
        self.offset_label = QLabel()
        self.prev_button.clicked.connect(self.previous)
        self.next_button.clicked.connect(self.next)
        bar.addWidget(self.prev_button)
        bar.addWidget(self.offset_label, 1)
        bar.addWidget(self.next_button)
        layout.addLayout(bar)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text.setStyleSheet("font:12px Consolas,'Courier New',monospace; background:#101b2c; border:1px solid #30445d;")
        layout.addWidget(self.text, 1)

        self.full_tools = QWidget()
        full_tools_layout = QVBoxLayout(self.full_tools)
        full_tools_layout.setContentsMargins(0, 0, 0, 0)
        self.full_file_details = QLabel()
        self.full_file_details.setWordWrap(True)
        self.full_file_details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        full_tools_layout.addWidget(self.full_file_details)
        tools_line = QHBoxLayout()
        self.jump_label = QLabel()
        self.jump_input = QLineEdit()
        self.jump_input.setPlaceholderText("0x1000 / 4096")
        self.jump_input.setFixedWidth(170)
        self.jump_button = QPushButton()
        self.jump_button.clicked.connect(self.go_to_offset)
        self.jump_input.returnPressed.connect(self.go_to_offset)
        tools_line.addWidget(self.jump_label)
        tools_line.addWidget(self.jump_input)
        tools_line.addWidget(self.jump_button)
        tools_line.addStretch(1)
        full_tools_layout.addLayout(tools_line)
        layout.addWidget(self.full_tools)
        self.full_view = FullFileHexView()
        self.full_view.position_changed.connect(self._update_full_status)
        layout.addWidget(self.full_view, 1)
        self.full_tools.hide()
        self.full_view.hide()
        self.retranslate()

    def _update_full_status(self, begin: int, end: int, size: int):
        if self.full_file_mode:
            self.offset_label.setText(self.tr("hex_full_range").format(
                begin=begin, end=end, size=size
            ))

    def _update_full_details(self):
        if self.path is None:
            self.full_file_details.clear()
            return
        self.full_file_details.setText(self.tr("hex_full_details").format(
            path=str(self.path), sha256=self.sha256 or "—"
        ))

    def retranslate(self):
        self.prev_button.setText(self.tr("hex_prev"))
        self.next_button.setText(self.tr("hex_next"))
        self.jump_label.setText(self.tr("hex_full_jump"))
        self.jump_button.setText(self.tr("hex_full_go"))
        self._update_full_details()
        self.render_page()
        if self.full_file_mode:
            self._update_full_status(self.full_view.current_offset,
                                     min(self.file_size, self.full_view.current_offset + self.full_view._visible_rows * 16),
                                     self.file_size)

    def show_file(self, path: str | None, size: int = 0, sha256: str = ""):
        path_obj = Path(path) if path else None
        new_file = self.path != path_obj
        self.path = path_obj
        self.file_size = max(0, int(size)) if path_obj else 0
        self.sha256 = sha256
        if new_file:
            self.offset = 0
            self.marked = b""
        self._update_full_details()
        if self.full_file_mode:
            if new_file or self.full_view.file_size != self.file_size:
                self.full_view.show_file(self.path, self.file_size)
                self.full_view.mark_pattern(self.marked)
        self.render_page()

    def set_full_file_mode(self, enabled: bool):
        if self.full_file_mode == bool(enabled):
            return
        if enabled:
            self.full_file_mode = True
            self._update_full_details()
            self.full_view.show_file(self.path, self.file_size)
            self.full_view.mark_pattern(self.marked)
            self.full_view.jump_to_offset(self.offset)
        else:
            self.offset = (self.full_view.current_offset // PAGE_BYTES) * PAGE_BYTES
            self.full_file_mode = False
        self.text.setVisible(not enabled)
        self.prev_button.setVisible(not enabled)
        self.next_button.setVisible(not enabled)
        self.full_tools.setVisible(enabled)
        self.full_view.setVisible(enabled)
        self.render_page()

    def go_to_offset(self):
        entered = self.jump_input.text().strip().replace("_", "")
        try:
            position = int(entered, 16) if entered.lower().startswith("0x") else int(entered, 10)
            if position < 0 or position >= self.file_size:
                raise ValueError("Outside file")
        except ValueError:
            QMessageBox.warning(self, self.tr("hex_full_go"), self.tr("hex_full_bad_offset"))
            return
        self.full_view.jump_to_offset(position)
        self.full_view.setFocus()

    def mark_pattern(self, pattern: bytes):
        self.marked = pattern
        self.full_view.mark_pattern(pattern)
        self.render_page()

    def previous(self):
        self.offset = max(0, self.offset - PAGE_BYTES)
        self.render_page()

    def next(self):
        if self.offset + PAGE_BYTES < self.file_size:
            self.offset += PAGE_BYTES
            self.render_page()

    def render_page(self):
        if self.full_file_mode:
            self._update_full_status(self.full_view.current_offset,
                                     min(self.file_size, self.full_view.current_offset + self.full_view._visible_rows * 16),
                                     self.file_size)
            return
        enabled = self.path is not None
        self.prev_button.setEnabled(enabled and self.offset > 0)
        self.next_button.setEnabled(enabled and self.offset + PAGE_BYTES < self.file_size)
        self.offset_label.setText(self.tr("hex_offset").format(offset=self.offset, size=self.file_size))
        if not enabled:
            self.text.setPlainText(self.tr("hex_empty"))
            return
        try:
            with self.path.open("rb") as handle:
                handle.seek(self.offset)
                payload = handle.read(PAGE_BYTES)
        except OSError as exc:
            self.text.setPlainText(self.tr("hex_error").format(error=str(exc)))
            return
        occurrences = set()
        if self.marked:
            index = 0
            while (index := payload.find(self.marked, index)) != -1:
                occurrences.update(range(index, index + len(self.marked)))
                index += 1
        lines = []
        for i in range(0, len(payload), 16):
            data = payload[i:i+16]
            fragments = []
            for j, byte in enumerate(data):
                pos = self.offset + i + j
                color = ("#ffc5ff" if i+j in occurrences else "#73e5ed" if pos < 16 else
                         "#748fa5" if byte == 0 else "#ffc089" if byte == 255 else
                         "#aaf5ba" if 32 <= byte <= 126 else "#b2c9f5")
                fragments.append(f'<span style="color:{color}">{byte:02X}</span>')
            printable = escape("".join(chr(byte) if 32 <= byte <= 126 else "." for byte in data))
            lines.append(f'<span style="color:#889fb8">{self.offset+i:08X}</span>  '
                         + " ".join(fragments) + ("   " * (16-len(data))) +
                         f'  <span style="color:#b5c4d7">|{printable}|</span>')
        body = "<br>".join(lines) if lines else escape(self.tr("hex_empty_file"))
        self.text.setHtml('<pre style="font:12px Consolas,monospace;white-space:pre">' + body + '</pre>')
