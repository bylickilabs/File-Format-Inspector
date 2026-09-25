from __future__ import annotations
from pathlib import Path
from threading import Event
import os
import tempfile

def write_patched_copy(source: Path, destination: Path, changes: dict[int, tuple[int, int]],
                       cancel: Event | None = None):
    """Stream source into a temp file and atomically replace destination after validation.

    Source is never opened for writing. Each edited byte is checked against the
    original value observed when the editor opened the corresponding page.
    """
    if not changes:
        raise ValueError("No staged changes")
    if source.resolve() == destination.resolve() or (destination.exists() and os.path.samefile(source, destination)):
        raise ValueError("The source file cannot be overwritten; choose another destination.")
    if source.is_symlink() or destination.is_symlink():
        raise ValueError("Symbolic-link inputs and outputs are not supported.")
    fd, temp = tempfile.mkstemp(prefix="._bylickilabs_hex_", suffix=".tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as output, source.open("rb") as incoming:
            offset = 0
            sorted_offsets = sorted(changes)
            pos = 0
            while True:
                if cancel is not None and cancel.is_set():
                    raise InterruptedError("Save cancelled")
                chunk = incoming.read(1024 * 1024)
                if not chunk:
                    break
                data = bytearray(chunk)
                while pos < len(sorted_offsets) and sorted_offsets[pos] < offset + len(data):
                    index = sorted_offsets[pos]
                    old, new = changes[index]
                    if index < offset or data[index - offset] != old:
                        raise ValueError(f"Source changed at offset 0x{index:X}; save aborted.")
                    data[index - offset] = new
                    pos += 1
                output.write(data)
                offset += len(data)
            if pos != len(sorted_offsets):
                raise ValueError("Source became shorter while editing; save aborted.")
            output.flush()
            os.fsync(output.fileno())
        if source.resolve() == destination.resolve():
            raise ValueError("Cannot overwrite source")
        os.replace(temp, destination)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

