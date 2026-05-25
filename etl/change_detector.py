"""Change Detection — detect data changes and produce a summary report.

Run after the pipeline to compare current vs previous processed data.
Outputs a JSON summary to stdout for use by CI or notification systems.
"""
import json
import logging
import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SNAPSHOT_FILE = PROJECT_ROOT / "data" / ".data_snapshot.json"


def _file_hash(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:12]


def _table_summary(path: Path) -> dict[str, Any]:
    """Quick summary stats of a CSV."""
    try:
        df = pd.read_csv(path, encoding="utf-8")
        return {
            "rows": len(df),
            "columns": list(df.columns),
            "hash": _file_hash(path),
        }
    except Exception as e:
        return {"error": str(e), "hash": _file_hash(path)}


def take_snapshot() -> dict[str, dict]:
    """Take a snapshot of all processed CSVs."""
    snapshot = {}
    for csv_file in sorted(PROCESSED_DIR.glob("*.csv")):
        snapshot[csv_file.stem] = _table_summary(csv_file)
    return snapshot


def load_previous_snapshot() -> dict[str, dict] | None:
    """Load the previous snapshot from disk."""
    if not SNAPSHOT_FILE.exists():
        return None
    try:
        return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_snapshot(snapshot: dict) -> None:
    """Save current snapshot to disk."""
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")


def detect_changes() -> dict[str, Any]:
    """Compare current data against previous snapshot.

    Returns:
        {
            "has_changes": bool,
            "added": [table_name, ...],
            "removed": [table_name, ...],
            "modified": [{"table": str, "old_rows": int, "new_rows": int, "row_change": int}, ...],
            "unchanged": [table_name, ...],
        }
    """
    previous = load_previous_snapshot()
    current = take_snapshot()

    if previous is None:
        save_snapshot(current)
        return {
            "has_changes": True,
            "added": list(current.keys()),
            "removed": [],
            "modified": [],
            "unchanged": [],
            "note": "First run — no previous snapshot",
        }

    added = [t for t in current if t not in previous]
    removed = [t for t in previous if t not in current]
    modified = []
    unchanged = []

    for table in current:
        if table in previous:
            curr = current[table]
            prev = previous[table]
            if curr.get("hash") != prev.get("hash"):
                modified.append({
                    "table": table,
                    "old_rows": prev.get("rows", 0),
                    "new_rows": curr.get("rows", 0),
                    "row_change": curr.get("rows", 0) - prev.get("rows", 0),
                })
            else:
                unchanged.append(table)

    # Save new snapshot
    save_snapshot(current)

    return {
        "has_changes": bool(added or removed or modified),
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def format_report(changes: dict) -> str:
    """Format change report as human-readable text."""
    if not changes["has_changes"]:
        return "✅ 資料無異動"

    lines = ["📊 資料更新報告", ""]

    if changes.get("note"):
        lines.append(f"ℹ️  {changes['note']}")
        lines.append("")

    if changes["added"]:
        lines.append(f"🆕 新增資料表 ({len(changes['added'])}):")
        for t in changes["added"]:
            lines.append(f"  • {t}")
        lines.append("")

    if changes["modified"]:
        lines.append(f"📝 資料異動 ({len(changes['modified'])}):")
        for m in changes["modified"]:
            sign = "+" if m["row_change"] >= 0 else ""
            lines.append(f"  • {m['table']}: {m['old_rows']} → {m['new_rows']} rows ({sign}{m['row_change']})")
        lines.append("")

    if changes["removed"]:
        lines.append(f"🗑️ 移除 ({len(changes['removed'])}):")
        for t in changes["removed"]:
            lines.append(f"  • {t}")
        lines.append("")

    if changes["unchanged"]:
        lines.append(f"✅ 未異動: {', '.join(changes['unchanged'])}")

    return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    changes = detect_changes()
    report = format_report(changes)
    print(report)
    # Also output JSON for CI consumption
    print("\n---JSON---")
    print(json.dumps(changes, ensure_ascii=False, indent=2))
