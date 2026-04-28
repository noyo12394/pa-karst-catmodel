"""Input/output helpers for DBF and CSV files."""

from __future__ import annotations

import csv
import struct
from pathlib import Path
from typing import Any

FieldDef = tuple[str, str, int, int]


def read_dbf(path: Path) -> tuple[list[FieldDef], list[dict[str, Any]]]:
    """Read a dBase DBF file using only the Python standard library."""
    with path.open("rb") as handle:
        header = handle.read(32)
        if len(header) < 32:
            raise ValueError(f"{path} is too small to be a DBF file")

        record_count = struct.unpack("<I", header[4:8])[0]
        header_length = struct.unpack("<H", header[8:10])[0]
        record_length = struct.unpack("<H", header[10:12])[0]

        fields: list[FieldDef] = []
        while True:
            descriptor = handle.read(32)
            if not descriptor:
                raise ValueError(f"{path} ended before the DBF field terminator")
            if descriptor[0] == 0x0D:
                break

            name = descriptor[0:11].split(b"\x00", 1)[0].decode("latin1").strip()
            ftype = chr(descriptor[11])
            length = descriptor[16]
            decimals = descriptor[17]
            fields.append((name, ftype, length, decimals))

        handle.seek(header_length)
        records: list[dict[str, Any]] = []
        for _ in range(record_count):
            raw = handle.read(record_length)
            if len(raw) < record_length:
                break
            if raw[:1] == b"*":
                continue

            offset = 1
            record: dict[str, Any] = {}
            for name, ftype, length, decimals in fields:
                cell = raw[offset : offset + length]
                offset += length
                text = cell.decode("latin1", errors="ignore").strip()

                if text == "":
                    record[name] = None
                elif ftype in {"N", "F"}:
                    record[name] = _parse_numeric(text, decimals)
                elif ftype == "C":
                    record[name] = text
                else:
                    record[name] = text
            records.append(record)

    return fields, records


def write_csv(
    rows: list[dict[str, Any]], path: Path, fieldnames: list[str] | None = None
) -> None:
    """Write dictionaries to a CSV file with a stable header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of dictionaries."""
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _parse_numeric(text: str, decimals: int) -> int | float | None:
    if text in {"*", "."}:
        return None
    try:
        if decimals > 0 or "." in text or "e" in text.lower():
            return float(text)
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None
