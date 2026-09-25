from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from threading import Event
from typing import Callable, Iterator

from data_analysis import DataAccumulator
from signature_database import HEADER_LIMIT, ZIP_CONTAINER_EXTENSIONS, detect

CHUNK_SIZE = 1024 * 1024


class ScanCancelled(Exception):
    pass


@dataclass
class FileRecord:
    path: str
    size: int = 0
    modified: str = ""
    sha256: str = ""
    detected: str = ""
    format_key: str = ""
    extension: str = ""
    evidence: str = ""
    status: str = "unknown"
    note: str = ""
    error: str = ""
    data_info: dict | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def enumerate_files(inputs: list[str], cancel: Event) -> Iterator[Path]:
    """Skip links to avoid cycles and unintended access outside chosen directories."""
    visited: set[str] = set()
    for raw in inputs:
        if cancel.is_set():
            raise ScanCancelled
        path = Path(raw)
        if path.is_symlink():
            continue
        if path.is_file():
            key = os.path.normcase(os.path.abspath(path))
            if key not in visited:
                visited.add(key)
                yield path
        elif path.is_dir():
            def on_error(error: OSError) -> None:
                pass
            for root, dirs, files in os.walk(path, topdown=True, followlinks=False, onerror=on_error):
                if cancel.is_set():
                    raise ScanCancelled
                dirs[:] = sorted(d for d in dirs if not (Path(root) / d).is_symlink())
                for name in sorted(files):
                    if cancel.is_set():
                        raise ScanCancelled
                    candidate = Path(root) / name
                    if candidate.is_symlink():
                        continue
                    key = os.path.normcase(os.path.abspath(candidate))
                    if key not in visited:
                        visited.add(key)
                        yield candidate


def analyze_file(path: Path, cancel: Event) -> FileRecord:
    record = FileRecord(path=str(path), extension=path.suffix.lower() or "—")
    try:
        if cancel.is_set():
            raise ScanCancelled
        stat = path.stat()
        record.size = stat.st_size
        record.modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds")
        digest = hashlib.sha256()
        stats = DataAccumulator()
        with path.open("rb") as stream:
            header = stream.read(HEADER_LIMIT)
            stream.seek(0)
            while True:
                if cancel.is_set():
                    raise ScanCancelled
                chunk = stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                digest.update(chunk)
                stats.update(chunk)
        record.sha256 = digest.hexdigest()
        record.data_info = stats.result()
        fmt = detect(path, header)
        if fmt is None:
            record.status = "unknown"
            record.note = "signature_unknown"
        else:
            record.detected = fmt.label
            record.format_key = fmt.key
            record.evidence = fmt.evidence
            record.note = fmt.note
            extension = path.suffix.lower()
            if not extension:
                record.status = "no_extension"
            elif fmt.key == "zip" and extension in ZIP_CONTAINER_EXTENSIONS:
                record.status = "ambiguous"
            elif fmt.note in {"zip_unreadable", "zip_many_entries", "mp3_probable", "bmff_container"}:
                record.status = "ambiguous"
            elif extension in fmt.extensions:
                record.status = "matched"
            else:
                record.status = "mismatch"
    except ScanCancelled:
        raise
    except (OSError, ValueError, OverflowError) as exc:
        record.status = "error"
        record.error = f"{type(exc).__name__}: {exc}"
    return record
