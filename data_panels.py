from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextBrowser, QVBoxLayout, QWidget


class Histogram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = [0] * 256
        self.setMinimumHeight(110)

    def set_values(self, values):
        self.values = values if values and len(values) == 256 else [0]*256
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#111d2e"))
        painter.setPen(QColor("#7b95b0"))
        painter.drawText(8, 13, "00")
        painter.drawText(max(8, self.width()-27), self.height()-5, "FF")
        peak = max(self.values) if self.values else 0
        if not peak:
            return
        left, top, height = 20, 20, max(10, self.height()-38)
        width = max(1, self.width()-30)
        painter.setPen(Qt.PenStyle.NoPen)
        for byte, count in enumerate(self.values):
            x1 = left + int(byte * width / 256)
            x2 = left + int((byte+1) * width / 256)
            bar = max(1, round((count/peak)*height)) if count else 0
            color = "#7e96ad" if byte == 0 else "#ffba80" if byte == 255 else "#75e0b1" if 32 <= byte <= 126 else "#73b5ed"
            painter.fillRect(x1, top+height-bar, max(1, x2-x1), bar, QColor(color))


class DataInfoPanel(QWidget):
    def __init__(self, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        layout = QVBoxLayout(self)
        self.summary = QTextBrowser()
        self.summary.setOpenExternalLinks(False)
        self.summary.setStyleSheet("background:#121e2f;color:#e3ebf6;")
        layout.addWidget(self.summary, 1)
        self.histogram_label = QLabel()
        layout.addWidget(self.histogram_label)
        self.histogram = Histogram()
        layout.addWidget(self.histogram)
        self.legend_title = QLabel()
        self.legend_title.setObjectName("dataHistogramLegendTitle")
        self.legend_title.setStyleSheet("color:#c3d8e8;font-weight:600;padding-top:3px;")
        layout.addWidget(self.legend_title)
        self.legend_container = QWidget()
        self.legend_container.setObjectName("dataHistogramLegend")
        legend_grid = QGridLayout(self.legend_container)
        legend_grid.setContentsMargins(0, 0, 0, 0)
        legend_grid.setHorizontalSpacing(12)
        legend_grid.setVerticalSpacing(5)
        self.legend_labels = {}
        for position, (key, color) in enumerate((
            ("data_legend_zero", "#7e96ad"),
            ("data_legend_ascii", "#75e0b1"),
            ("data_legend_other", "#73b5ed"),
            ("data_legend_ff", "#ffba80"),
        )):
            entry = QWidget()
            entry_layout = QHBoxLayout(entry)
            entry_layout.setContentsMargins(0, 0, 0, 0)
            entry_layout.setSpacing(7)
            swatch = QLabel()
            swatch.setObjectName(key + "Swatch")
            swatch.setFixedSize(13, 13)
            swatch.setStyleSheet(f"background-color:{color}; border-radius:2px;")
            label = QLabel()
            label.setObjectName(key)
            label.setWordWrap(True)
            label.setStyleSheet("color:#dce9f5;")
            entry_layout.addWidget(swatch)
            entry_layout.addWidget(label, 1)
            legend_grid.addWidget(entry, position // 2, position % 2)
            self.legend_labels[key] = label
        layout.addWidget(self.legend_container)
        self.legend_note = QLabel()
        self.legend_note.setObjectName("dataHistogramLegendNote")
        self.legend_note.setWordWrap(True)
        self.legend_note.setStyleSheet("color:#a7bfd2;font-size:11px;")
        layout.addWidget(self.legend_note)
        self._retranslate_legend()
        self.show_info(None)

    def show_info(self, record):
        self.record = record
        data = record.data_info if record else None
        if not data:
            self.summary.setPlainText(self.tr("data_empty"))
            self.histogram.set_values(None)
            self.histogram_label.setText(self.tr("data_histogram"))
            return
        fields = (
            ("data_size", f'{data["bytes_analyzed"]:,}'),
            ("data_entropy", f'{data["entropy_bits_per_byte"]:.6f} / 8'),
            ("data_unique", str(data["unique_bytes"])),
            ("data_printable", f'{data["printable_pct"]:.3f}%'),
            ("data_zero", f'{data["zero_pct"]:.3f}%'),
            ("data_mean", str(data["mean_byte"])),
            ("data_std", str(data["std_byte"])),
            ("data_uniform", f'{data["chi_square_pvalue_uniform"]:.4g}' if data["chi_square_pvalue_uniform"] is not None else "—"),
            ("data_sample", f'{data["sample_bytes"]:,}'),
            ("data_top", ", ".join(f'{key}: {count:,}' for key, count in data["top_bytes"])),
        )
        html = ["<div style='font-family:Segoe UI;line-height:1.5'>"]
        for key, value in fields:
            html.append(f'<div><b style="color:#79ddeb">{escape(self.tr(key))}:</b> {escape(value)}</div>')
        windows = data["sample_window_entropy"]
        if windows:
            chart = " ".join(f'{x:.2f}' for x in windows[:32])
            html.append(f'<p><b style="color:#79ddeb">{escape(self.tr("data_windows"))}:</b><br>{escape(chart)}</p>')
        html.append(f'<p style="color:#e7bc80">{escape(self.tr("data_caveat"))}</p></div>')
        self.summary.setHtml("".join(html))
        self.histogram.set_values(data["histogram"])
        self.histogram_label.setText(self.tr("data_histogram"))

    def _retranslate_legend(self):
        self.legend_title.setText(self.tr("data_legend_title"))
        for key, label in self.legend_labels.items():
            label.setText(self.tr(key))
        self.legend_note.setText(self.tr("data_legend_note"))

    def retranslate(self):
        self._retranslate_legend()
        self.show_info(getattr(self, "record", None))


class PatternPanel(QWidget):
    """Repeated 4-byte sequences and other evidence from first SAMPLE_LIMIT bytes."""
    def __init__(self, tr, on_pattern, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.on_pattern = on_pattern
        layout = QVBoxLayout(self)
        self.caption = QLabel()
        self.caption.setWordWrap(True)
        layout.addWidget(self.caption)
        self.pattern_table = QTableWidget(0, 2)
        self.pattern_table.verticalHeader().setVisible(False)
        self.pattern_table.horizontalHeader().setStretchLastSection(True)
        self.pattern_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pattern_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pattern_table.setMaximumHeight(175)
        self.pattern_table.cellClicked.connect(self._selected)
        layout.addWidget(self.pattern_table)
        self.text = QTextBrowser()
        self.text.setStyleSheet("background:#121e2f;color:#e3ebf6;")
        layout.addWidget(self.text, 1)
        self.show_patterns(None)

    def show_patterns(self, record):
        self.record = record
        data = record.data_info if record else None
        self.caption.setText(self.tr("pattern_caption"))
        self.pattern_table.setHorizontalHeaderLabels([self.tr("pattern_hex"), self.tr("pattern_count")])
        self.pattern_table.setRowCount(0)
        if not data:
            self.text.setPlainText(self.tr("data_empty"))
            return
        p = data["patterns"]
        for entry in p["repeated_4byte"]:
            row = self.pattern_table.rowCount()
            self.pattern_table.insertRow(row)
            self.pattern_table.setItem(row, 0, QTableWidgetItem(entry["hex"]))
            self.pattern_table.setItem(row, 1, QTableWidgetItem(str(entry["count"])))
        items = [f'<h3 style="color:#7edbea">{escape(self.tr("pattern_strings"))}</h3>']
        for entry in p["ascii_strings"]:
            items.append(f'<div>0x{entry["offset"]:X}: {escape(entry["text"])}</div>')
        items.append(f'<h3 style="color:#7edbea">{escape(self.tr("pattern_zeros"))}</h3>')
        for entry in p["zero_runs"]:
            items.append(f'<div>0x{entry["offset"]:X}: {entry["length"]} B</div>')
        items.append(f'<h3 style="color:#7edbea">{escape(self.tr("pattern_periods"))}</h3>')
        for entry in p["periods"]:
            items.append(f'<div>{entry["lag"]} B: {entry["similarity"]*100:.1f}%</div>')
        if not any(p.values()):
            items.append(escape(self.tr("pattern_none")))
        self.text.setHtml("".join(items))

    def _selected(self, row, column):
        item = self.pattern_table.item(row, 0)
        if item:
            self.on_pattern(bytes.fromhex(item.text()))

    def retranslate(self):
        self.show_patterns(getattr(self, "record", None))
