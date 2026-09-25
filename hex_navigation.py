from __future__ import annotations
from pathlib import Path

ROW_BYTES = 16
QT_SCROLL_LIMIT = 2_000_000_000


def read_hex_window(path: Path, first_row: int, rows: int) -> bytes:
    """Read only the requested visible rows, never the whole file."""
    if first_row < 0 or rows < 0:
        raise ValueError("Byte window is out of range")
    if not rows:
        return b""
    with Path(path).open("rb") as source:
        source.seek(first_row * ROW_BYTES)
        return source.read(rows * ROW_BYTES)


def scroll_limits(file_size: int, visible_rows: int) -> tuple[int, int]:
    total_rows = (max(0, file_size) + ROW_BYTES - 1) // ROW_BYTES
    last_row = max(0, total_rows - max(1, visible_rows))
    return last_row, min(last_row, QT_SCROLL_LIMIT)


def scroll_to_row(value: int, last_row: int, maximum: int) -> int:
    if last_row <= 0 or maximum <= 0:
        return 0
    return min(last_row, max(0, int(value)) * last_row // maximum)


def row_to_scroll(row: int, last_row: int, maximum: int) -> int:
    if last_row <= 0 or maximum <= 0:
        return 0
    return min(maximum, max(0, int(row)) * maximum // last_row)
