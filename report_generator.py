from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path

from file_analyzer import FileRecord


def export_json(destination: str, records: list[FileRecord], language: str) -> None:
    payload = {
        "application": "BYLICKILABS File Format Inspector",
        "version": "1.1.1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "language": language,
        "records": [record.to_dict() for record in records],
    }
    Path(destination).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def export_html(destination: str, records: list[FileRecord], tr) -> None:
    columns = ("path", "size", "extension", "detected", "status", "sha256", "evidence", "modified", "note", "error", "entropy", "unique", "printable", "zero", "sample")
    headings = {column: tr("report_" + column) for column in columns}
    rows = []
    for record in records:
        values = record.to_dict()
        data = record.data_info or {}
        values.update({
            "entropy": data.get("entropy_bits_per_byte", ""),
            "unique": data.get("unique_bytes", ""),
            "printable": data.get("printable_pct", ""),
            "zero": data.get("zero_pct", ""),
            "sample": data.get("sample_bytes", ""),
        })
        values["status"] = tr("status_" + record.status)
        values["note"] = tr("note_" + record.note) if record.note else ""
        cells = "".join(f"<td>{escape(str(values.get(col, '')))}</td>" for col in columns)
        rows.append("<tr>" + cells + "</tr>")
    head = "".join(f"<th>{escape(headings[col])}</th>" for col in columns)
    html = """<!doctype html><html lang="{language}"><head><meta charset="utf-8">
<title>{title}</title><style>body{{font-family:system-ui,sans-serif;background:#101927;color:#e8eef6;margin:2rem}}
h1{{color:#58dbe7}}p{{color:#a4b2c4}}table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{border:1px solid #3b4c64;padding:8px;text-align:left;word-break:break-word}}
th{{background:#1d3049}}tr:nth-child(even){{background:#182638}}</style></head>
<body><h1>{title}</h1><p>{count}</p><table><thead><tr>{head}</tr></thead>
<tbody>{rows}</tbody></table></body></html>""".format(
        language=escape(tr("language_code")),
        title=escape(tr("report_title")),
        count=escape(tr("report_count").format(count=len(records))),
        head=head,
        rows="\n".join(rows),
    )
    Path(destination).write_text(html, encoding="utf-8")
