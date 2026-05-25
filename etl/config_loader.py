"""Load and validate datasources configuration."""
import yaml
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "datasources.yml"


def load_datasources(config_path: Path | None = None) -> list[dict[str, Any]]:
    """Load datasources.yml and return list of source definitions."""
    path = config_path or CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("sources", [])


def get_source_by_id(source_id: str, sources: list[dict] | None = None) -> dict | None:
    """Find a single source definition by its id."""
    sources = sources or load_datasources()
    for src in sources:
        if src.get("id") == source_id:
            return src
    return None


def get_sources_by_schedule(schedule: str, sources: list[dict] | None = None) -> list[dict]:
    """Filter sources by update frequency (monthly, yearly, quarterly)."""
    sources = sources or load_datasources()
    return [s for s in sources if s.get("schedule") == schedule]
