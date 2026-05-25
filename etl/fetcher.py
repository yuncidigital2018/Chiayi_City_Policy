"""Data Fetcher — download raw data from configured sources."""
import csv
import io
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml
from lxml import html

from etl.config_loader import load_datasources, get_source_by_id

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Open Chiayi API base
OPEN_CHIAYI_API = "https://data.chiayi.gov.tw/opendata/api/getResource"

# User-Agent for respectful scraping
USER_AGENT = "ChiayiPolicyBot/1.0 (+https://github.com/yuncidigital2018/Chiayi_City_Policy)"


def fetch_source(source: dict[str, Any], force: bool = False) -> Path | None:
    """Fetch a single data source and save to data/raw/.

    Args:
        source: Source definition from datasources.yml
        force: If True, re-download even if cached file exists

    Returns:
        Path to saved file, or None if failed
    """
    source_id = source["id"]
    output_path = PROJECT_ROOT / source.get("output", f"data/raw/{source_id}.csv")

    # Check cache (NFR-1: fallback to last successful)
    if output_path.exists() and not force:
        logger.info(f"Cache hit for {source_id}: {output_path}")
        return output_path

    fetch_type = source.get("type", "download")
    logger.info(f"Fetching {source_id} (type={fetch_type})...")

    try:
        if fetch_type == "api" and source.get("oid"):
            data = _fetch_open_chiayi_api(source)
        elif fetch_type == "web_scrape":
            data = _fetch_and_parse_html(source)
        else:
            data = _fetch_download(source)

        if data:
            _save_raw(source_id, data, output_path)
            logger.info(f"Saved {source_id} → {output_path}")
            return output_path
        else:
            logger.warning(f"No data returned for {source_id}")
            return None

    except Exception as e:
        logger.error(f"Failed to fetch {source_id}: {e}")
        # NFR-1: fallback to cache
        if output_path.exists():
            logger.info(f"Using cached data for {source_id}")
            return output_path
        return None


def _fetch_open_chiayi_api(source: dict) -> str | None:
    """Fetch data from Open Chiayi API."""
    oid = source["oid"]
    params = {"oid": oid, "rid": source.get("rid", "")}
    resp = requests.get(
        OPEN_CHIAYI_API,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    # Open Chiayi returns {"success": true, "result": {"records": [...]}}
    result = data.get("result", {})
    records = result.get("records", [])
    if not records:
        return None

    # Convert to CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def _fetch_download(source: dict) -> str | None:
    """Direct file download (CSV/XML/XLS)."""
    url = source.get("url", "")
    if not url:
        logger.warning(f"No URL for source {source['id']}")
        return None

    resp = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    if "csv" in content_type or url.endswith(".csv"):
        return resp.text
    elif "xml" in content_type or url.endswith(".xml"):
        return resp.text
    else:
        # Try to decode as text
        return resp.text


def _fetch_and_parse_html(source: dict) -> str | None:
    """Fetch and parse HTML table data (for 戶政服務網 etc.)."""
    url = source.get("url", "")
    if not url:
        logger.warning(f"No URL for source {source['id']}")
        return None

    resp = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    resp.raise_for_status()

    tree = html.fromstring(resp.text)
    tables = tree.xpath("//table")
    if not tables:
        logger.warning(f"No tables found at {url}")
        return None

    # Parse the first table found
    table = tables[0]
    rows = table.xpath(".//tr")
    if not rows:
        return None

    # Extract headers and rows
    headers = [th.text_content().strip() for th in rows[0].xpath(".//th|.//td")]
    data_rows = []
    for row in rows[1:]:
        cells = [td.text_content().strip() for td in row.xpath(".//td")]
        if cells:
            data_rows.append(cells)

    # Convert to CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data_rows)
    return output.getvalue()


def _save_raw(source_id: str, data: str, output_path: Path) -> None:
    """Save raw data to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(data)


def fetch_all(sources: list[dict] | None = None, force: bool = False) -> dict[str, Path | None]:
    """Fetch all configured sources.

    Returns:
        Dict mapping source_id → saved file path (or None if failed)
    """
    sources = sources or load_datasources()
    results = {}
    for source in sources:
        path = fetch_source(source, force=force)
        results[source["id"]] = path
        time.sleep(1)  # Be respectful to the servers
    return results
