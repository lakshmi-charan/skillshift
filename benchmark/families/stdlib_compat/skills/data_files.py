"""Read and write JSON and CSV data files."""
import csv
import json
import os
import tempfile
from pathlib import Path


def read_json(path, default=None):
    """Parse a UTF-8 JSON file; return `default` if the file does not exist."""
    p = Path(path)
    if not p.exists():
        return default
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_json_atomic(path, data):
    """Write `data` as indented, key-sorted JSON; readers never see a partially written file."""
    p = Path(path)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=p.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def write_csv_records(path, records, fieldnames=None):
    """Write a list of dicts as CSV with a header row (columns: `fieldnames` or first record's keys)."""
    records = list(records)
    if fieldnames is None:
        fieldnames = list(records[0]) if records else []
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            w.writerow(r)


def read_csv_records(path):
    """Read a CSV file with a header row into a list of dicts (values are strings)."""
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))
