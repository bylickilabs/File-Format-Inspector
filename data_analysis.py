from __future__ import annotations

from collections import Counter
import re
from pathlib import Path
from threading import Event

import numpy as np
from scipy.stats import chisquare, entropy as scipy_entropy
from scipy.signal import find_peaks

SAMPLE_LIMIT = 128 * 1024
WINDOW_SIZE = 4096


class DataAccumulator:
    """Incremental histogram; never retains more than SAMPLE_LIMIT sample bytes."""

    def __init__(self):
        self.counts = np.zeros(256, dtype=np.int64)
        self.size = 0
        self.sample = bytearray()

    def update(self, payload: bytes):
        if not payload:
            return
        self.counts += np.bincount(np.frombuffer(payload, dtype=np.uint8), minlength=256)
        self.size += len(payload)
        left = SAMPLE_LIMIT - len(self.sample)
        if left > 0:
            self.sample.extend(payload[:left])

    def result(self) -> dict:
        n = self.size
        counts = self.counts
        probability = counts / n if n else np.zeros(256, dtype=np.float64)
        ent = float(scipy_entropy(counts, base=2)) if n else 0.0
        chi_p = float(chisquare(counts).pvalue) if n else None
        sample = bytes(self.sample)
        samples = np.frombuffer(sample, dtype=np.uint8)
        windows = [round(float(scipy_entropy(np.bincount(samples[i:i+WINDOW_SIZE], minlength=256), base=2)), 4)
                   for i in range(0, len(samples), WINDOW_SIZE)]
        top_bytes = [(f"{int(i):02X}", int(counts[i])) for i in np.argsort(counts)[::-1][:8] if counts[i]]
        return {
            "bytes_analyzed": n,
            "entropy_bits_per_byte": round(ent, 6),
            "mean_byte": round(float(np.dot(np.arange(256, dtype=np.float64), probability)), 4) if n else 0.0,
            "std_byte": round(float(np.sqrt(np.dot((np.arange(256)-np.dot(np.arange(256), probability))**2, probability))), 4) if n else 0.0,
            "printable_pct": round(100 * int(counts[32:127].sum()) / n, 3) if n else 0.0,
            "zero_pct": round(100 * int(counts[0]) / n, 3) if n else 0.0,
            "unique_bytes": int(np.count_nonzero(counts)),
            "chi_square_pvalue_uniform": chi_p,
            "histogram": counts.astype(int).tolist(),
            "top_bytes": top_bytes,
            "sample_bytes": len(sample),
            "window_size": WINDOW_SIZE,
            "sample_window_entropy": windows,
            "patterns": inspect_patterns(sample),
        }


def inspect_patterns(sample: bytes) -> dict:
    """All output limited to beginning of file; no arbitrary execution/parsing."""
    if not sample:
        return {"repeated_4byte": [], "ascii_strings": [], "zero_runs": [], "periods": []}
    a = np.frombuffer(sample[:65536], dtype=np.uint8)
    repeated = []
    if len(a) >= 4:
        windows = np.lib.stride_tricks.sliding_window_view(a, 4)
        patterns, occurrences = np.unique(windows, axis=0, return_counts=True)
        sorted_indices = np.argsort(occurrences)[::-1]
        for pos in sorted_indices:
            count = int(occurrences[pos])
            if count < 3 or len(repeated) == 8:
                break
            repeated.append({"hex": patterns[pos].tobytes().hex(" ").upper(), "count": count})
    strings = [{"offset": match.start(), "text": match.group().decode("ascii", "replace")[:90]}
               for match in list(re.finditer(rb"[\x20-\x7e]{6,}", sample))[:12]]
    zeros = [{"offset": match.start(), "length": len(match.group())}
             for match in list(re.finditer(rb"\x00{16,}", sample))[:12]]

    periods = []
    if len(a) >= 512:
        view = a[:min(8192, len(a))]
        lags = np.arange(2, 129)
        scores = np.array([float(np.mean(view[lag:] == view[:-lag])) for lag in lags])
        peak_indices, _ = find_peaks(scores, height=0.70, distance=2)
        ranked = sorted(peak_indices, key=lambda i: scores[i], reverse=True)[:6]
        periods = [{"lag": int(lags[i]), "similarity": round(float(scores[i]), 4)} for i in ranked]
    return {"repeated_4byte": repeated, "ascii_strings": strings, "zero_runs": zeros, "periods": periods}


def parse_hex_pattern(value: str) -> list[int | None]:
    """Hex bytes separated by whitespace; ?? means one wildcard byte."""
    tokens = value.strip().split()
    if not 1 <= len(tokens) <= 256:
        raise ValueError("Expected 1–256 hex bytes separated by spaces (?? = wildcard).")
    if any(not re.fullmatch(r"(?:[\da-fA-F]{2}|\?\?)", token) for token in tokens):
        raise ValueError("Invalid pattern. Example: 4D 5A ?? 00")
    if all(token == "??" for token in tokens):
        raise ValueError("At least one pattern byte must be specified.")
    return [None if token == "??" else int(token, 16) for token in tokens]


def search_pattern_file(path: Path, pattern: list[int | None], cancel: Event | None = None,
                        max_hits: int = 200) -> tuple[list[int], bool]:
    """Overlapping cross-chunk search with bounded memory and result count."""
    if not pattern or all(byte is None for byte in pattern):
        raise ValueError("A nonempty pattern with at least one known byte is required")
    compiled = re.compile(b"(?=(" + b"".join(b"." if byte is None else re.escape(bytes([byte])) for byte in pattern) + b"))", re.DOTALL)
    overlap = len(pattern) - 1
    tail = b""
    offset = 0
    hits: list[int] = []
    with path.open("rb") as handle:
        while True:
            if cancel is not None and cancel.is_set():
                return hits, True
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            data = tail + chunk
            base = offset - len(tail)
            for match in compiled.finditer(data):
                absolute = base + match.start()
                if absolute + len(pattern) <= offset:
                    continue
                hits.append(absolute)
                if len(hits) >= max_hits:
                    return hits, True
            offset += len(chunk)
            tail = data[-overlap:] if overlap else b""
    return hits, False
