from __future__ import annotations

import os
import sys
from html import escape
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QColor, QDesktopServices, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMenu, QMessageBox, QProgressBar, QPushButton,
    QPlainTextEdit, QScrollArea, QSplitter, QTableWidget, QTableWidgetItem,
    QTextBrowser, QTabWidget, QVBoxLayout, QWidget,
)

from file_analyzer import FileRecord, ScanCancelled, analyze_file, enumerate_files
from hex_viewer import HexViewer
from hex_editor import HexEditorWindow
from data_panels import DataInfoPanel, PatternPanel
from report_generator import export_html, export_json
from translations import translate, validate_translations

APP_NAME = "BYLICKILABS File Format Inspector"
APP_TITLE = "BYLICKILABS | FILE FORMAT INSPECTOR"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Thorsten Bylicki / BYLICKILABS"
GITHUB_URL = "https://github.com/bylickilabs/Desktop-Utility-Toolkit"
FACEBOOK_URL = "https://www.facebook.com/BylickiLabs"
LINKEDIN_URL = "https://www.linkedin.com/in/bylicki/"


class ScanWorker(QObject):
    collecting = Signal()
    total_ready = Signal(int)
    item_ready = Signal(object, int, int)
    completed = Signal(bool, int, str)

    def __init__(self, inputs: list[str]):
        super().__init__()
        self.inputs = inputs
        self.cancel_event = Event()

    def cancel(self):
        self.cancel_event.set()

    @Slot()
    def run(self):
        completed = 0
        try:
            self.collecting.emit()
            paths = list(enumerate_files(self.inputs, self.cancel_event))
            total = len(paths)
            self.total_ready.emit(total)
            for index, path in enumerate(paths, start=1):
                if self.cancel_event.is_set():
                    raise ScanCancelled
                record = analyze_file(path, self.cancel_event)
                completed += 1
                self.item_ready.emit(record, index, total)
            self.completed.emit(False, completed, "")
        except ScanCancelled:
            self.completed.emit(True, completed, "")
        except Exception as exc:
            self.completed.emit(False, completed, f"{type(exc).__name__}: {exc}")


class DropLabel(QLabel):
    dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(75)
        self.setWordWrap(True)
        self.setObjectName("dropZone")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and any(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.dropped.emit(paths)
            event.acceptProposedAction()


class AboutDialog(QDialog):
    def __init__(self, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setMinimumSize(710, 650)
        self.setWindowTitle(self.tr("about_title"))
        outer = QVBoxLayout(self)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setStyleSheet("border: 0; background: #101b2c; color: #e5edf7; padding: 12px;")
        outer.addWidget(self.browser)
        close = QPushButton(self.tr("about_close"))
        close.clicked.connect(self.accept)
        outer.addWidget(close)
        self.populate()

    def populate(self):
        sections = [
            "overview", "features", "statistics", "patterns", "editing", "formats", "processing", "results", "limits",
            "privacy", "reports", "technology", "links",
        ]
        html = [f"<h1 style='color:#61d8ec'>{escape(APP_NAME)}</h1>",
                f"<p><b>{escape(self.tr('detail_status'))}:</b> v{escape(APP_VERSION)} &nbsp; "
                f"<b>{escape(APP_AUTHOR)}</b></p>"]
        for section in sections:
            title = self.tr("about_" + section)
            body = self.tr("about_" + section + "_text")
            if section == "technology":
                body = body.format(version=APP_VERSION, author=APP_AUTHOR)
            html.append(f"<h2 style='color:#61d8ec'>{escape(title)}</h2><p style='line-height:1.5'>{escape(body)}</p>")
        self.browser.setHtml("".join(html))


class DetachedHexPreviewWindow(QMainWindow):
    """Real, independent top-level window owning the *same* HexViewer as the tab.

    The viewer is returned to its previous layout before the floating window
    can be destroyed. Therefore page/selection/highlight state is preserved.
    """

    def __init__(self, viewer: HexViewer, restore_viewer, open_editor, tr):
        super().__init__(None)
        self._viewer = viewer
        self._restore_viewer = restore_viewer
        self._tr = tr
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.resize(1350, 850)
        self.setMinimumSize(760, 450)
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#101927; color:#e5edf7; font-family:'Segoe UI',Arial,sans-serif; }
            QPushButton { background:#20374d; color:#e5edf7; padding:8px 12px; border:1px solid #385977; border-radius:5px; }
            QPushButton:hover { background:#29475e; border-color:#62d8e9; }
        """)
        self._container = QWidget(self)
        self._layout = QVBoxLayout(self._container)
        toolbar = QHBoxLayout()
        self._dock_button = QPushButton()
        self._dock_button.clicked.connect(self.close)
        self._editor_button = QPushButton()
        self._editor_button.clicked.connect(open_editor)
        toolbar.addWidget(self._dock_button)
        toolbar.addWidget(self._editor_button)
        toolbar.addStretch(1)
        self._layout.addLayout(toolbar)
        self._layout.addWidget(viewer, 1)
        self.setCentralWidget(self._container)
        self._viewer.set_full_file_mode(True)
        self.retranslate()

    def retranslate(self):
        self.setWindowTitle(f"{APP_TITLE} | {self._tr('hex_float_title')}")
        self._dock_button.setText(self._tr('hex_redock'))
        self._editor_button.setText(self._tr('hex_editor_open'))

    def closeEvent(self, event):
        viewer = self._viewer
        if viewer is not None:
            self._viewer = None
            self._layout.removeWidget(viewer)
            viewer.set_full_file_mode(False)
            viewer.setParent(None)
            self._restore_viewer(viewer)
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "de"
        self.sources: list[str] = []
        self.records: list[FileRecord] = []
        self._thread: QThread | None = None
        self._worker: ScanWorker | None = None
        self._closing_after_scan = False
        self._editors: list[HexEditorWindow] = []
        self._floating_preview: DetachedHexPreviewWindow | None = None
        self.setWindowTitle(f"{APP_TITLE} | {APP_VERSION}")
        self.resize(1250, 820)
        self.setMinimumSize(880, 630)
        self._build_ui()
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#101927; color:#e5edf7; font-family:'Segoe UI',Arial,sans-serif; font-size:12px; }
            QPushButton { background:#20374d; border:1px solid #385977; color:#e5edf7; padding:8px 12px; border-radius:5px; }
            QPushButton:hover { border-color:#62d8e9; background:#29475e; }
            QPushButton:disabled { color:#7d8998; background:#192535; border-color:#283649; }
            QLabel#dropZone { background:#172639; border:2px dashed #43617f; border-radius:7px; color:#a5c5d9; }
            QTableWidget, QPlainTextEdit, QTextBrowser { background:#121e2f; border:1px solid #334a65; gridline-color:#26374b; selection-background-color:#26597e; }
            QHeaderView::section { background:#1f354c; padding:7px; border:0; border-right:1px solid #334a65; }
            QGroupBox { border:1px solid #304b66; border-radius:6px; margin-top:12px; padding-top:9px; }
            QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; color:#7fdfef; }
            QProgressBar { text-align:center; border:1px solid #304b66; border-radius:3px; background:#172639; }
            QProgressBar::chunk { background:#2f99b8; }
            QMenu { background:#1c2e42; border:1px solid #385977; }
            QMenu::item:selected { background:#2b5874; }
        """)
        self.retranslate()

    def tr(self, key: str) -> str:
        return translate(self.language, key)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setSpacing(9)
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        self.title_label = QLabel(APP_TITLE)
        self.title_label.setStyleSheet("font-size:20px; font-weight:700; color:#64dcec;")
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet("color:#a4bcd0;")
        title_col.addWidget(self.title_label)
        title_col.addWidget(self.subtitle_label)
        header.addLayout(title_col, 1)
        self.github_button = QPushButton("GitHub ↗")
        self.facebook_button = QPushButton("Facebook ↗")
        self.linkedin_button = QPushButton("LinkedIn ↗")
        self.github_button.clicked.connect(lambda: self.open_link(GITHUB_URL))
        self.facebook_button.clicked.connect(lambda: self.open_link(FACEBOOK_URL))
        self.linkedin_button.clicked.connect(lambda: self.open_link(LINKEDIN_URL))
        for button in (self.github_button, self.facebook_button, self.linkedin_button):
            header.addWidget(button)
        self.info_button = QPushButton()
        self.info_button.clicked.connect(self.open_info)
        header.addWidget(self.info_button)
        self.lang_button = QPushButton()
        self.lang_button.clicked.connect(self.open_language_menu)
        header.addWidget(self.lang_button)
        outer.addLayout(header)

        actions = QHBoxLayout()
        self.files_button = QPushButton()
        self.files_button.clicked.connect(self.add_files)
        self.folder_button = QPushButton()
        self.folder_button.clicked.connect(self.add_folder)
        self.scan_button = QPushButton()
        self.scan_button.clicked.connect(self.start_scan)
        self.stop_button = QPushButton()
        self.stop_button.clicked.connect(self.cancel_scan)
        self.clear_button = QPushButton()
        self.clear_button.clicked.connect(self.clear_all)
        for button in (self.files_button, self.folder_button, self.scan_button, self.stop_button, self.clear_button):
            actions.addWidget(button)
        actions.addStretch(1)
        outer.addLayout(actions)

        self.drop_zone = DropLabel()
        self.drop_zone.dropped.connect(self.add_sources)
        outer.addWidget(self.drop_zone)
        self.source_count = QLabel()
        outer.addWidget(self.source_count)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        outer.addWidget(self.progress)
        self.status_label = QLabel()
        outer.addWidget(self.status_label)

        splitter = QSplitter(Qt.Orientation.Vertical)
        self.table = QTableWidget(0, 6)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self.show_selection)
        splitter.addWidget(self.table)

        details_split = QSplitter(Qt.Orientation.Horizontal)
        self.details_group = QGroupBox()
        details_layout = QVBoxLayout(self.details_group)
        self.details_text = QPlainTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        details_layout.addWidget(self.details_text)
        details_split.addWidget(self.details_group)
        self.analysis_tabs = QTabWidget()
        self.hex_group = QWidget()
        hex_layout = QVBoxLayout(self.hex_group)
        self.hex_layout = hex_layout
        popbar = QHBoxLayout()
        self.detach_button = QPushButton()
        self.detach_button.clicked.connect(self.open_detached_preview)
        self.editor_button = QPushButton()
        self.editor_button.clicked.connect(self.open_detached_editor)
        popbar.addStretch(1)
        popbar.addWidget(self.detach_button)
        popbar.addWidget(self.editor_button)
        hex_layout.addLayout(popbar)
        self.hex_widget = HexViewer(self.tr)
        hex_layout.addWidget(self.hex_widget)
        self.analysis_tabs.addTab(self.hex_group, "")
        self.data_panel = DataInfoPanel(self.tr)
        self.analysis_tabs.addTab(self.data_panel, "")
        self.pattern_panel = PatternPanel(self.tr, self.highlight_pattern)
        self.analysis_tabs.addTab(self.pattern_panel, "")
        details_split.addWidget(self.analysis_tabs)
        details_split.setSizes([470, 750])
        splitter.addWidget(details_split)
        splitter.setSizes([350, 270])
        outer.addWidget(splitter, 1)

        bottom = QHBoxLayout()
        self.footer_label = QLabel()
        self.footer_label.setStyleSheet("color:#98adbf;")
        bottom.addWidget(self.footer_label, 1)
        self.json_button = QPushButton()
        self.json_button.clicked.connect(lambda: self.save_report("json"))
        self.html_button = QPushButton()
        self.html_button.clicked.connect(lambda: self.save_report("html"))
        bottom.addWidget(self.json_button)
        bottom.addWidget(self.html_button)
        outer.addLayout(bottom)
        self._set_busy(False)

    def retranslate(self):
        for widget, key in (
            (self.subtitle_label, "subtitle"), (self.files_button, "open_files"),
            (self.folder_button, "open_folder"), (self.scan_button, "start"),
            (self.stop_button, "cancel"), (self.clear_button, "clear"),
            (self.drop_zone, "drop"), (self.info_button, "info"),
            (self.json_button, "export_json"), (self.html_button, "export_html"),
            (self.details_group, "details"),
        ):
            if isinstance(widget, QGroupBox):
                widget.setTitle(self.tr(key))
            else:
                widget.setText(self.tr(key))
        self.lang_button.setText(f"{self.tr('lang')}  {self.language.upper()} ▾")
        self.source_count.setText(self.tr("selected").format(count=len(self.sources)))
        self.footer_label.setText(self.tr("footer").format(name=APP_NAME, version=APP_VERSION, author=APP_AUTHOR))
        for index, key in enumerate(("col_name", "col_detected", "col_extension", "col_size", "col_status", "col_path")):
            self.table.setHorizontalHeaderItem(index, QTableWidgetItem(self.tr(key)))
        for row, record in enumerate(self.records):
            item = self.table.item(row, 4)
            if item:
                item.setText(self.tr("status_" + record.status))
        self.hex_widget.retranslate()
        self.analysis_tabs.setTabText(0, self.tr("tab_hex"))
        self.analysis_tabs.setTabText(1, self.tr("tab_data"))
        self.analysis_tabs.setTabText(2, self.tr("tab_patterns"))
        self.detach_button.setText(self.tr("hex_detach"))
        self.editor_button.setText(self.tr("hex_editor_open"))
        if self._floating_preview is not None:
            self._floating_preview.retranslate()
        self.data_panel.retranslate()
        self.pattern_panel.retranslate()
        for editor in list(self._editors):
            editor.retranslate()
        self.show_selection()
        if not self.records and not (self._thread and self._thread.isRunning()):
            self.status_label.setText(self.tr("ready"))

    def open_language_menu(self):
        menu = QMenu(self)
        de = menu.addAction(self.tr("lang_de"))
        en = menu.addAction(self.tr("lang_en"))
        de.setCheckable(True)
        en.setCheckable(True)
        de.setChecked(self.language == "de")
        en.setChecked(self.language == "en")
        de.triggered.connect(lambda: self.set_language("de"))
        en.triggered.connect(lambda: self.set_language("en"))
        menu.exec(self.lang_button.mapToGlobal(self.lang_button.rect().bottomLeft()))

    def set_language(self, language: str):
        if language in {"de", "en"}:
            self.language = language
            self.retranslate()

    def open_info(self):
        AboutDialog(self.tr, self).exec()

    def open_link(self, url: str):
        if not QDesktopServices.openUrl(QUrl(url)):
            QMessageBox.warning(self, APP_NAME, self.tr("open_error").format(url=url))

    def add_sources(self, paths: list[str]):
        if self._thread is not None:
            return
        known = {os.path.normcase(os.path.abspath(x)) for x in self.sources}
        for raw in paths:
            path = Path(raw)
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                continue
            normalized = os.path.normcase(os.path.abspath(raw))
            if normalized not in known:
                self.sources.append(str(path))
                known.add(normalized)
        self.source_count.setText(self.tr("selected").format(count=len(self.sources)))

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, self.tr("choose_files"), "", self.tr("files_filter"))
        self.add_sources(paths)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr("choose_folder"))
        if folder:
            self.add_sources([folder])

    def _set_busy(self, busy: bool):
        for button in (self.files_button, self.folder_button, self.scan_button, self.clear_button):
            button.setEnabled(not busy)
        self.stop_button.setEnabled(busy)
        self.drop_zone.setAcceptDrops(not busy)
        self.json_button.setEnabled(not busy and bool(self.records))
        self.html_button.setEnabled(not busy and bool(self.records))

    def start_scan(self):
        if self._thread is not None:
            return
        if not self.sources:
            QMessageBox.information(self, APP_NAME, self.tr("nothing_selected"))
            return
        self.records.clear()
        self.table.setRowCount(0)
        self.hex_widget.show_file(None)
        self.data_panel.show_info(None)
        self.pattern_panel.show_patterns(None)
        self.details_text.clear()
        self.progress.setRange(0, 0)
        self.status_label.setText(self.tr("collecting"))
        self._thread = QThread(self)
        self._worker = ScanWorker(self.sources.copy())
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.collecting.connect(lambda: self.status_label.setText(self.tr("collecting")))
        self._worker.total_ready.connect(self.on_total_ready)
        self._worker.item_ready.connect(self.on_item_ready)
        self._worker.completed.connect(self.on_scan_complete)
        self._worker.completed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self.on_thread_finished)
        self._set_busy(True)
        self._thread.start()

    def cancel_scan(self):
        if self._worker:
            self._worker.cancel()
            self.stop_button.setEnabled(False)

    def on_total_ready(self, total: int):
        self.progress.setRange(0, max(1, total))
        self.progress.setValue(0)
        if total == 0:
            self.status_label.setText(self.tr("no_files"))

    def on_item_ready(self, record: FileRecord, index: int, total: int):
        self.records.append(record)
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [Path(record.path).name, record.detected or "—", record.extension,
                  f"{record.size:,}", self.tr("status_" + record.status), record.path]
        for col, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            if col == 3:
                item.setData(Qt.ItemDataRole.UserRole, record.size)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if col == 4:
                if record.status in {"error", "mismatch"}:
                    item.setForeground(QColor("#ffbb77"))
                elif record.status == "matched":
                    item.setForeground(QColor("#80e6ac"))
            self.table.setItem(row, col, item)
        self.progress.setValue(index)
        self.status_label.setText(self.tr("analyzing").format(index=index, total=total, name=Path(record.path).name))
        if index == 1:
            self.table.selectRow(0)

    def on_scan_complete(self, cancelled: bool, count: int, error: str):
        if error:
            self.status_label.setText(self.tr("file_error").format(error=error))
            QMessageBox.warning(self, APP_NAME, self.status_label.text())
        else:
            key = "cancelled" if cancelled else "done"
            self.status_label.setText(self.tr(key).format(count=count))
            if count == 0 and not cancelled:
                self.status_label.setText(self.tr("no_files"))

    def on_thread_finished(self):
        self._worker = None
        self._thread = None
        self._set_busy(False)
        if self._closing_after_scan:
            self.close()

    def clear_all(self):
        if self._thread is not None:
            return
        self.sources.clear()
        self.records.clear()
        self.table.setRowCount(0)
        self.hex_widget.show_file(None)
        self.data_panel.show_info(None)
        self.pattern_panel.show_patterns(None)
        self.details_text.clear()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.source_count.setText(self.tr("selected").format(count=0))
        self.status_label.setText(self.tr("ready"))
        self._set_busy(False)

    def show_selection(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.records):
            self.details_text.setPlainText(self.tr("details_empty"))
            self.hex_widget.show_file(None)
            self.data_panel.show_info(None)
            self.pattern_panel.show_patterns(None)
            self.detach_button.setEnabled(self._floating_preview is not None)
            self.editor_button.setEnabled(True)
            return
        record = self.records[row]
        fields = (
            ("detail_path", record.path), ("detail_size", f"{record.size:,} bytes"),
            ("detail_modified", record.modified or "—"),
            ("detail_extension", record.extension), ("detail_detected", record.detected or "—"),
            ("detail_evidence", record.evidence or "—"),
            ("detail_status", self.tr("status_" + record.status)),
            ("detail_sha256", record.sha256 or "—"),
        )
        detail_lines = [f"{self.tr(key)}: {value}" for key, value in fields]
        if record.note:
            detail_lines.append(f"{self.tr('detail_note')}: {self.tr('note_' + record.note)}")
        if record.error:
            detail_lines.append(f"{self.tr('detail_error')}: {record.error}")
        self.details_text.setPlainText("\n\n".join(detail_lines))
        if self.hex_widget.path is None or str(self.hex_widget.path) != record.path:
            self.hex_widget.show_file(record.path, record.size, record.sha256)
        self.data_panel.show_info(record)
        self.pattern_panel.show_patterns(record)
        can_open = Path(record.path).is_file()
        self.detach_button.setEnabled(can_open or self._floating_preview is not None)
        self.editor_button.setEnabled(True)

    def highlight_pattern(self, pattern: bytes):
        self.hex_widget.mark_pattern(pattern)
        self.analysis_tabs.setCurrentIndex(0)

        for editor in list(self._editors):
            if self.hex_widget.path and editor.path == self.hex_widget.path:
                try:
                    editor.highlight_pattern(pattern)
                except OSError:
                    pass

    def open_detached_preview(self):
        """Move the existing viewer from the tab into a real floating window."""
        if self._floating_preview is not None:
            self._floating_preview.showNormal()
            self._floating_preview.raise_()
            self._floating_preview.activateWindow()
            return
        if self.hex_widget.path is None or not self.hex_widget.path.is_file():
            QMessageBox.information(self, APP_NAME, self.tr("hex_select_file"))
            return

        self.hex_layout.removeWidget(self.hex_widget)
        self.hex_widget.setParent(None)
        try:
            window = DetachedHexPreviewWindow(
                self.hex_widget, self.restore_hex_preview, self.open_detached_editor, self.tr
            )
        except Exception as exc:
            self.restore_hex_preview(self.hex_widget)
            QMessageBox.warning(self, APP_NAME, self.tr("file_error").format(error=str(exc)))
            return
        self._floating_preview = window
        window.show()
        window.raise_()
        window.activateWindow()

    def restore_hex_preview(self, viewer: HexViewer):
        """Return the *same* widget when docking or closing the floating view."""
        old_window = self._floating_preview
        self._floating_preview = None
        self.hex_layout.addWidget(viewer, 1)
        viewer.show()
        if old_window is not None:
            old_window.deleteLater()
        self.detach_button.setText(self.tr("hex_detach"))
        self.show_selection()

    def open_detached_editor(self):
        """Open the file in an independent HEX editor, with visible failure feedback."""
        row = self.table.currentRow()
        if 0 <= row < len(self.records):
            path = Path(self.records[row].path)
        else:
            chosen, _ = QFileDialog.getOpenFileName(
                self, self.tr("hex_editor_choose_file"), "", self.tr("files_filter")
            )
            if not chosen:
                return
            path = Path(chosen)
        if not path.is_file():
            QMessageBox.warning(self, APP_NAME, self.tr("file_error").format(
                error=self.tr("hex_editor_missing_file")))
            return

        for existing in self._editors:
            if existing.path == path:
                existing.showNormal()
                existing.raise_()
                existing.activateWindow()
                return
        try:
            editor = HexEditorWindow(str(path), self.tr, None)
            self._editors.append(editor)
            editor.destroyed.connect(
                lambda *_: self._editors.remove(editor) if editor in self._editors else None
            )
            editor.show()
            editor.raise_()
            editor.activateWindow()
        except Exception as exc:
            QMessageBox.critical(self, APP_NAME, self.tr("hex_editor_launch_error").format(
                error=f"{type(exc).__name__}: {exc}"))

    def save_report(self, extension: str):
        if not self.records or self._thread is not None:
            QMessageBox.information(self, APP_NAME, self.tr("nothing_export"))
            return
        default = f"BYLICKILABS_File_Format_Inspector_Report.{extension}"
        filter_text = self.tr("json_filter" if extension == "json" else "html_filter")
        destination, _ = QFileDialog.getSaveFileName(self, self.tr("choose_report"), default, filter_text)
        if not destination:
            return
        if not destination.lower().endswith("." + extension):
            destination += "." + extension
        try:
            if extension == "json":
                export_json(destination, self.records, self.language)
            else:
                export_html(destination, self.records, self.tr)
            self.status_label.setText(self.tr("saved").format(path=destination))
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, APP_NAME, self.tr("file_error").format(error=str(exc)))

    def closeEvent(self, event):
        if self._floating_preview is not None:
            self._floating_preview.close()
        for editor in list(self._editors):
            if not editor.close():
                event.ignore()
                return
        if self._thread is not None:
            self._closing_after_scan = True
            self.cancel_scan()
            event.ignore()
        else:
            event.accept()


def main():
    validate_translations()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("BYLICKILABS")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
