from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
import zipfile

HEADER_LIMIT = 8192

@dataclass(frozen=True)
class FormatResult:
    key: str
    label: str
    extensions: tuple[str, ...]
    evidence: str
    note: str = ""


FORMATS: dict[str, tuple[str, tuple[str, ...]]] = {
    "jpeg": ("JPEG", (".jpg", ".jpeg", ".jpe")),
    "png": ("PNG", (".png",)),
    "gif": ("GIF", (".gif",)),
    "webp": ("WebP", (".webp",)),
    "bmp": ("BMP", (".bmp",)),
    "tiff": ("TIFF", (".tif", ".tiff")),
    "pdf": ("PDF", (".pdf",)),
    "rtf": ("RTF", (".rtf",)),
    "zip": ("ZIP", (".zip",)),
    "docx": ("DOCX (OOXML)", (".docx",)),
    "xlsx": ("XLSX (OOXML)", (".xlsx",)),
    "pptx": ("PPTX (OOXML)", (".pptx",)),
    "odt": ("ODT (OpenDocument)", (".odt",)),
    "ods": ("ODS (OpenDocument)", (".ods",)),
    "odp": ("ODP (OpenDocument)", (".odp",)),
    "rar": ("RAR", (".rar",)),
    "7z": ("7-Zip", (".7z",)),
    "gzip": ("GZIP", (".gz", ".gzip")),
    "tar": ("TAR", (".tar",)),
    "wav": ("WAV", (".wav",)),
    "avi": ("AVI", (".avi",)),
    "flac": ("FLAC", (".flac",)),
    "ogg": ("Ogg", (".ogg", ".oga", ".ogv", ".opus")),
    "mp3": ("MP3", (".mp3",)),
    "mp4": ("MP4 / ISO BMFF", (".mp4", ".m4v", ".m4a")),
    "webm": ("WebM", (".webm",)),
    "mkv": ("Matroska", (".mkv", ".mka")),
    "pe-exe": ("Windows PE (EXE)", (".exe", ".scr", ".com")),
    "pe-dll": ("Windows PE (DLL)", (".dll", ".ocx", ".cpl")),
    "sqlite": ("SQLite 3", (".sqlite", ".sqlite3", ".db", ".db3")),
    "ttf": ("TrueType", (".ttf",)),
    "otf": ("OpenType", (".otf",)),
}

ZIP_CONTAINER_EXTENSIONS = frozenset({
    ".jar", ".war", ".ear", ".apk", ".aab", ".epub", ".odg", ".odf",
    ".vsix", ".xpi", ".crx", ".cbz", ".ipa", ".nupkg", ".whl",
    ".docm", ".xlsm", ".pptm", ".dotx", ".xltx", ".potx",
})


def result(key: str, evidence: str, note: str = "") -> FormatResult:
    label, extensions = FORMATS[key]
    return FormatResult(key, label, extensions, evidence, note)


def _identify_zip(path: Path) -> FormatResult:
    """Inspect central-directory member names; never extract or execute entries."""
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = set()
            max_entries = 10000
            count = 0
            for info in archive.infolist():
                count += 1
                if count > max_entries:
                    return result("zip", "ZIP local header / central directory", "zip_many_entries")
                names.add(info.filename.replace("\\", "/"))
            if "[Content_Types].xml" in names:
                if any(name.startswith("word/") for name in names):
                    return result("docx", "ZIP + [Content_Types].xml + word/")
                if any(name.startswith("xl/") for name in names):
                    return result("xlsx", "ZIP + [Content_Types].xml + xl/")
                if any(name.startswith("ppt/") for name in names):
                    return result("pptx", "ZIP + [Content_Types].xml + ppt/")
            if "mimetype" in names:
                item = archive.getinfo("mimetype")
                if item.file_size <= 256 and item.compress_size <= 1024:
                    mimetype = archive.read(item).decode("ascii", errors="replace").strip()
                    odf = {
                        "application/vnd.oasis.opendocument.text": "odt",
                        "application/vnd.oasis.opendocument.spreadsheet": "ods",
                        "application/vnd.oasis.opendocument.presentation": "odp",
                    }
                    if mimetype in odf:
                        return result(odf[mimetype], "ZIP + mimetype: " + mimetype)
            return result("zip", "ZIP local header / central directory", "zip_generic")
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, EOFError):
        return result("zip", "ZIP local header", "zip_unreadable")


def detect(path: Path, header: bytes) -> FormatResult | None:
    """Identify by content; an unknown result is safer than a false assertion."""
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return result("png", "89 50 4E 47 0D 0A 1A 0A")
    if header.startswith(b"\xff\xd8\xff"):
        return result("jpeg", "FF D8 FF")
    if header.startswith((b"GIF87a", b"GIF89a")):
        return result("gif", header[:6].hex(" ").upper())
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return result("webp", "RIFF + WEBP")
    if header.startswith(b"BM"):
        return result("bmp", "42 4D")
    if header.startswith((b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+")):
        return result("tiff", header[:4].hex(" ").upper())
    if header.startswith(b"%PDF-"):
        return result("pdf", "%PDF-")
    if header.startswith(b"{\\rtf"):
        return result("rtf", "{\\rtf")
    if header.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return _identify_zip(path)
    if header.startswith((b"Rar!\x1a\x07\x00", b"Rar!\x1a\x07\x01\x00")):
        return result("rar", "RAR archive header")
    if header.startswith(b"7z\xbc\xaf\x27\x1c"):
        return result("7z", "37 7A BC AF 27 1C")
    if header.startswith(b"\x1f\x8b\x08"):
        return result("gzip", "1F 8B 08")
    if len(header) >= 262 and header[257:262] == b"ustar":
        return result("tar", "ustar at offset 257")
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WAVE":
        return result("wav", "RIFF + WAVE")
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"AVI ":
        return result("avi", "RIFF + AVI")
    if header.startswith(b"fLaC"):
        return result("flac", "66 4C 61 43")
    if header.startswith(b"OggS"):
        return result("ogg", "4F 67 67 53", "ogg_container")
    if header.startswith(b"ID3"):
        return result("mp3", "49 44 33 (ID3)")
    if len(header) >= 4 and header[0] == 0xff and (header[1] & 0xE6) == 0xE2:
        return result("mp3", "MPEG audio frame sync (heuristic)", "mp3_probable")
    if len(header) >= 12 and header[4:8] == b"ftyp":
        brand = header[8:12].decode("ascii", errors="replace")
        return result("mp4", "ISO BMFF ftyp: " + brand, "bmff_container")
    if header.startswith(b"\x1a\x45\xdf\xa3"):
        sample = header[:4096].lower()
        if b"webm" in sample:
            return result("webm", "EBML + DocType webm")
        if b"matroska" in sample:
            return result("mkv", "EBML + DocType matroska")
        return None
    if header.startswith(b"MZ") and len(header) >= 64:
        pe_offset = struct.unpack_from("<I", header, 0x3c)[0]
        if 0 <= pe_offset <= 4 * 1024 * 1024:
            try:
                with path.open("rb") as stream:
                    stream.seek(pe_offset)
                    pe = stream.read(24)
                if len(pe) >= 24 and pe.startswith(b"PE\x00\x00"):
                    characteristics = struct.unpack_from("<H", pe, 22)[0]
                    key = "pe-dll" if characteristics & 0x2000 else "pe-exe"
                    return result(key, "MZ + PE header + COFF characteristics")
            except OSError:
                pass
    if header.startswith(b"SQLite format 3\x00"):
        return result("sqlite", "SQLite format 3\\0")
    if header.startswith(b"\x00\x01\x00\x00"):
        return result("ttf", "00 01 00 00")
    if header.startswith(b"OTTO"):
        return result("otf", "4F 54 54 4F")
    return None
