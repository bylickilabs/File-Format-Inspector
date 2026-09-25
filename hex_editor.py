from __future__ import annotations

import os
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout,
)
from data_analysis import parse_hex_pattern, search_pattern_file
from hex_patch import write_patched_copy

PAGE_BYTES = 512
ROW_BYTES = 16

class SaveWorker(QObject):
    finished = Signal(str)

    def __init__(self, source: Path, destination: Path, changes: dict[int, tuple[int, int]]):
        super().__init__()
        self.source, self.destination, self.changes = source, destination, changes

    @Slot()
    def run(self):
        try:
            write_patched_copy(self.source, self.destination, self.changes)
            self.finished.emit("")
        except (OSError, ValueError, InterruptedError) as exc:
            self.finished.emit(f"{type(exc).__name__}: {exc}")


class SearchWorker(QObject):
    finished = Signal(object, bool, str)

    def __init__(self, source: Path, pattern: list[int | None]):
        super().__init__()
        self.source, self.pattern = source, pattern
        self.cancel = Event()

    @Slot()
    def run(self):
        try:
            hits, truncated = search_pattern_file(self.source, self.pattern, self.cancel)
            self.finished.emit(hits, truncated, "")
        except (OSError, ValueError) as exc:
            self.finished.emit([], False, str(exc))


class HexEditorWindow(QDialog):
    """Independent floating window, 512-byte page with per-byte editing and color key."""

    def __init__(self, path: str, tr, parent=None):
        super().__init__(parent)
        self.path = Path(path)
        self.tr = tr
        self.size = self.path.stat().st_size
        self.offset = 0
        self.changes: dict[int, tuple[int, int]] = {}
        self._loading = False
        self._thread: QThread | None = None
        self._worker: SaveWorker | None = None
        self._search_thread: QThread | None = None
        self._search_worker: SearchWorker | None = None
        self._pattern_offsets: set[int] = set()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.resize(1190, 770)
        self.setMinimumSize(760, 440)
        outer = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.prev = QPushButton()
        self.next_button = QPushButton()
        self.jump_label = QLabel()
        self.jump = QLineEdit("0")
        self.jump.setFixedWidth(135)
        self.jump.setPlaceholderText("0x100 / 256")
        self.go = QPushButton()
        self.save = QPushButton()
        self.prev.clicked.connect(self.previous)
        self.next_button.clicked.connect(self.next)
        self.go.clicked.connect(self.go_to_offset)
        self.jump.returnPressed.connect(self.go_to_offset)
        self.save.clicked.connect(self.save_as)
        for widget in (self.prev, self.next_button, self.jump_label, self.jump, self.go, self.save):
            bar.addWidget(widget)
        bar.addStretch()
        outer.addLayout(bar)
        searchbar = QHBoxLayout()
        self.pattern_label = QLabel()
        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("4D 5A ?? 00")
        self.search_button = QPushButton()
        self.hits = QComboBox()
        self.hits.setMinimumWidth(130)
        self.search_button.clicked.connect(self.search_pattern)
        self.hits.activated.connect(self.jump_to_hit)
        searchbar.addWidget(self.pattern_label)
        searchbar.addWidget(self.pattern_input, 1)
        searchbar.addWidget(self.search_button)
        searchbar.addWidget(self.hits)
        outer.addLayout(searchbar)
        self.instruction = QLabel()
        self.instruction.setWordWrap(True)
        outer.addWidget(self.instruction)
        self.grid = QTableWidget(0, ROW_BYTES + 2)
        self.grid.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.grid.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed)
        self.grid.verticalHeader().setVisible(False)
        self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grid.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.grid.horizontalHeader().setSectionResizeMode(17, QHeaderView.ResizeMode.ResizeToContents)
        self.grid.itemChanged.connect(self.byte_edited)
        self.grid.setStyleSheet("QTableWidget{background:#101b2c;color:#e8eef7;gridline-color:#293c56;font:12px Consolas,'Courier New',monospace;} QHeaderView::section{background:#21364e;color:#cbe6f4;padding:5px;}")
        outer.addWidget(self.grid, 1)
        self.legend = QLabel()
        self.legend.setWordWrap(True)
        outer.addWidget(self.legend)
        self.status = QLabel()
        outer.addWidget(self.status)
        self.retranslate()
        self.render_page()

    def retranslate(self):
        self.setWindowTitle(f"{self.tr('editor_title')} – {self.path.name}")
        self.prev.setText(self.tr("hex_prev"))
        self.next_button.setText(self.tr("hex_next"))
        self.jump_label.setText(self.tr("editor_offset"))
        self.go.setText(self.tr("editor_go"))
        self.save.setText(self.tr("editor_save"))
        self.instruction.setText(self.tr("editor_instructions"))
        self.pattern_label.setText(self.tr("editor_pattern"))
        self.search_button.setText(self.tr("editor_search"))
        self.legend.setText(self.tr("editor_legend"))
        self.grid.setHorizontalHeaderLabels(["OFFSET"] + [f"{i:02X}" for i in range(ROW_BYTES)] + ["ASCII"])
        self._update_status()

    def _update_status(self):
        self.status.setText(self.tr("editor_status").format(offset=self.offset, size=self.size, count=len(self.changes)))

    def set_pattern_offsets(self, offsets: set[int]):
        self._pattern_offsets = offsets
        self.render_page()

    def highlight_pattern(self, pattern: bytes):
        self._pattern_offsets = set()
        if pattern:
            with self.path.open("rb") as handle:
                handle.seek(self.offset)
                data = handle.read(PAGE_BYTES)
            start = 0
            while True:
                ix = data.find(pattern, start)
                if ix < 0:
                    break
                self._pattern_offsets.update(range(self.offset + ix, self.offset + ix + len(pattern)))
                start = ix + 1
        self.render_page()

    def render_page(self):
        self._loading = True
        try:
            with self.path.open("rb") as handle:
                handle.seek(self.offset)
                data = handle.read(PAGE_BYTES)
            self.grid.setRowCount((len(data) + ROW_BYTES - 1) // ROW_BYTES)
            for r in range(self.grid.rowCount()):
                start = r * ROW_BYTES
                self.grid.setItem(r, 0, self._fixed_item(f"{self.offset + start:08X}"))
                ascii_chars = []
                for c in range(ROW_BYTES):
                    i = start + c
                    if i >= len(data):
                        self.grid.setItem(r, c + 1, self._fixed_item(""))
                        ascii_chars.append(" ")
                        continue
                    absolute = self.offset + i
                    old = data[i]
                    byte = self.changes.get(absolute, (old, old))[1]
                    ascii_chars.append(chr(byte) if 32 <= byte <= 126 else ".")
                    item = QTableWidgetItem(f"{byte:02X}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setToolTip(f"0x{absolute:X} / {absolute}")
                    fg, bg = self.byte_style(absolute, byte)
                    item.setForeground(QColor(fg))
                    item.setBackground(QColor(bg))
                    self.grid.setItem(r, c + 1, item)
                self.grid.setItem(r, 17, self._fixed_item("".join(ascii_chars)))
            self.prev.setEnabled(self.offset > 0)
            self.next_button.setEnabled(self.offset + PAGE_BYTES < self.size)
            self._update_status()
        except OSError as exc:
            self.status.setText(self.tr("hex_error").format(error=str(exc)))
        finally:
            self._loading = False

    @staticmethod
    def _fixed_item(text: str):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def byte_style(self, index: int, value: int):
        if index in self.changes:
            return "#ffe087", "#63442b"
        if index in self._pattern_offsets:
            return "#ffc5ff", "#553050"
        if index < 16:
            return "#73e5ed", "#1a3d49"
        if value == 0:
            return "#788fa5", "#162539"
        if value == 255:
            return "#ffbd7c", "#3e2e32"
        if 32 <= value <= 126:
            return "#aaf5ba", "#19312e"
        return "#b2c9f5", "#202b44"

    def byte_edited(self, item):
        if self._loading or self._thread is not None or not 1 <= item.column() <= ROW_BYTES:
            return
        absolute = self.offset + item.row() * ROW_BYTES + item.column() - 1
        try:
            raw = item.text().strip()
            if len(raw) != 2:
                raise ValueError
            value = int(raw, 16)
            if not 0 <= value <= 255:
                raise ValueError
            with self.path.open("rb") as handle:
                handle.seek(absolute)
                data = handle.read(1)
            if not data:
                raise ValueError
            original = self.changes.get(absolute, (data[0], data[0]))[0]
            if value == original:
                self.changes.pop(absolute, None)
            else:
                self.changes[absolute] = (original, value)
        except (ValueError, OSError):
            QMessageBox.warning(self, self.tr("editor_title"), self.tr("editor_invalid"))
        self.render_page()

    def previous(self):
        self.offset = max(0, self.offset - PAGE_BYTES)
        self.render_page()

    def next(self):
        if self.offset + PAGE_BYTES < self.size:
            self.offset += PAGE_BYTES
            self.render_page()

    def jump_to(self, position: int):
        self.offset = (min(max(0, position), max(0, self.size - 1)) // PAGE_BYTES) * PAGE_BYTES
        self.render_page()
        if self.grid.rowCount():
            self.grid.setCurrentCell((position - self.offset) // ROW_BYTES,
                                     (position - self.offset) % ROW_BYTES + 1)

    def go_to_offset(self):
        raw = self.jump.text().strip().lower()
        try:
            position = int(raw, 16) if raw.startswith("0x") else int(raw, 10)
            if position < 0 or position >= self.size:
                raise ValueError
            self.jump_to(position)
        except ValueError:
            QMessageBox.warning(self, self.tr("editor_title"), self.tr("editor_bad_offset"))

    def search_pattern(self):
        if self._search_thread is not None:
            return
        try:
            pattern = parse_hex_pattern(self.pattern_input.text())
        except ValueError as exc:
            QMessageBox.warning(self, self.tr("editor_title"), str(exc))
            return
        self.hits.clear()
        self.search_button.setEnabled(False)
        self.status.setText(self.tr("editor_searching"))
        self._search_thread = QThread(self)
        self._search_worker = SearchWorker(self.path, pattern)
        self._search_worker.moveToThread(self._search_thread)
        self._search_thread.started.connect(self._search_worker.run)
        self._search_worker.finished.connect(self.search_finished)
        self._search_worker.finished.connect(self._search_thread.quit)
        self._search_thread.finished.connect(self._search_worker.deleteLater)
        self._search_thread.finished.connect(self._search_thread.deleteLater)
        self._search_thread.finished.connect(self._search_cleaned)
        self._search_thread.start()

    def search_finished(self, offsets, truncated, error):
        if error:
            QMessageBox.warning(self, self.tr("editor_title"), error)
        else:
            for offset in offsets:
                self.hits.addItem(f"0x{offset:08X}", offset)
            if offsets:
                self.jump_to(int(offsets[0]))
            self.status.setText(self.tr("editor_hits").format(count=len(offsets),
                                extra=self.tr("editor_hit_limit") if truncated else ""))

    def _search_cleaned(self):
        self._search_worker = None
        self._search_thread = None
        self.search_button.setEnabled(True)

    def jump_to_hit(self, index):
        position = self.hits.itemData(index)
        if position is not None:
            self.jump_to(int(position))

    def save_as(self):
        if not self.changes or self._thread is not None:
            QMessageBox.information(self, self.tr("editor_title"), self.tr("editor_no_changes"))
            return
        proposal = str(self.path.with_name(self.path.stem + "_edited" + self.path.suffix))
        target, _ = QFileDialog.getSaveFileName(self, self.tr("editor_save"), proposal, self.tr("files_filter"))
        if not target:
            return
        destination = Path(target)
        if self.path.resolve() == destination.resolve() or (destination.exists() and os.path.samefile(self.path, destination)):
            QMessageBox.warning(self, self.tr("editor_title"), self.tr("editor_no_source"))
            return
        if destination.exists() and QMessageBox.question(self, self.tr("editor_title"),
                 self.tr("editor_replace").format(path=target)) != QMessageBox.StandardButton.Yes:
            return
        self._thread = QThread(self)
        self._worker = SaveWorker(self.path, destination, dict(self.changes))
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(lambda error: self.save_finished(error, target))
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._save_cleaned)
        self.grid.setEnabled(False)
        self.save.setEnabled(False)
        self.status.setText(self.tr("editor_saving"))
        self._thread.start()

    def save_finished(self, error: str, target: str):
        if error:
            QMessageBox.warning(self, self.tr("editor_title"), self.tr("file_error").format(error=error))
        else:
            QMessageBox.information(self, self.tr("editor_title"), self.tr("editor_saved").format(path=target))

    def _save_cleaned(self):
        self._thread = None
        self._worker = None
        self.grid.setEnabled(True)
        self.save.setEnabled(True)
        self._update_status()

    def closeEvent(self, event):
        if self._thread is not None or self._search_thread is not None:
            if self._search_worker is not None:
                self._search_worker.cancel.set()
            event.ignore()
        elif self.changes and QMessageBox.question(self, self.tr("editor_title"),
                      self.tr("editor_discard")) != QMessageBox.StandardButton.Yes:
            event.ignore()
        else:
            event.accept()
