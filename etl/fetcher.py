"""Data Fetcher — download raw data from configured sources."""
import csv
import io
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import urllib3
from lxml import html

import importlib

from etl.config_loader import load_datasources, get_source_by_id

# Suppress SSL warnings for government sites with bad certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    output_rel = source.get("output", f"data/raw/{source_id}.csv")
    output_path = PROJECT_ROOT / output_rel

    # Check cache (NFR-1: fallback to last successful)
    if output_path.exists() and not force:
        logger.info(f"Cache hit for {source_id}: {output_path}")
        return output_path

    fetch_type = source.get("type", "download")

    # Skip sample type (data already exists)
    if fetch_type == "sample":
        if output_path.exists():
            logger.info(f"Sample data already exists for {source_id}")
            return output_path
        logger.warning(f"Sample data not found for {source_id}")
        return None

    logger.info(f"Fetching {source_id} (type={fetch_type})...")

    try:
        if fetch_type == "api":
            data = _fetch_open_chiayi_api(source)
        elif fetch_type == "web_scrape":
            data = _fetch_and_parse_html(source)
        elif fetch_type == "download":
            data = _fetch_download(source)
        elif fetch_type == "scraper":
            data = _run_scraper_module(source)
        else:
            data = None

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


def _request_with_retry(
    source_id: str,
    max_retries: int,
    method: str,
    url: str,
    **kwargs,
) -> str | None:
    """HTTP request with exponential backoff retry."""
    import time as _time

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.request(
                method, url,
                headers={"User-Agent": USER_AGENT},
                timeout=kwargs.pop("timeout", 30),
                verify=False,
                **kwargs,
            )
            resp.raise_for_status()
            text = resp.text.strip()
            if not text or len(text) < 10:
                logger.warning(f"{source_id}: empty response (attempt {attempt})")
                return None
            return text
        except requests.RequestException as e:
            last_error = e
            if attempt < max_retries:
                wait = 2 ** attempt
                logger.warning(f"{source_id}: attempt {attempt} failed ({e}), retry in {wait}s...")
                _time.sleep(wait)

    logger.error(f"{source_id}: all {max_retries} attempts failed: {last_error}")
    return None


def _fetch_open_chiayi_api(source: dict, max_retries: int = 3) -> str | None:
    """Fetch data from Open Chiayi API using oid + rid with retry."""
    oid = source.get("oid", "")
    rid = source.get("rid", "")

    if not oid:
        logger.warning(f"No OID for source {source['id']}")
        return None

    params = {"oid": oid, "rid": rid}
    return _request_with_retry(
        source["id"], max_retries,
        "GET", OPEN_CHIAYI_API, params=params,
    )


def _fetch_download(source: dict) -> str | None:
    """Direct file download (CSV/XML/XLS) with retry."""
    url = source.get("url", "")
    if not url:
        logger.warning(f"No URL for source {source['id']}")
        return None
    return _request_with_retry(source["id"], 3, "GET", url, timeout=60)


def _fetch_and_parse_html(source: dict) -> str | None:
    """Fetch and parse HTML table data with retry."""
    url = source.get("url", "")
    if not url:
        logger.warning(f"No URL for source {source['id']}")
        return None

    text = _request_with_retry(source["id"], 3, "GET", url, timeout=60)
    if not text:
        return None

    tree = html.fromstring(text)
    tables = tree.xpath("//table")
    if not tables:
        logger.warning(f"No tables found at {url}")
        return None

    table = tables[0]
    rows = table.xpath(".//tr")
    if not rows:
        return None

    headers = [th.text_content().strip() for th in rows[0].xpath(".//th|.//td")]
    data_rows = []
    for row in rows[1:]:
        cells = [td.text_content().strip() for td in row.xpath(".//td")]
        if cells:
            data_rows.append(cells)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data_rows)
    return output.getvalue()


def _run_scraper_module(source: dict) -> str | None:
    """Invoke a Python scraper module function and return CSV text."""
    import csv
    import io

    mod_name = source.get("scraper_module", "")
    func_name = source.get("scraper_func", "")
    if not mod_name or not func_name:
        logger.warning(f"Scraper source {source['id']} missing module/func")
        return None

    try:
        mod = importlib.import_module(mod_name)
        fn = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import {mod_name}.{func_name}: {e}")
        return None

    result = fn()
    if result is None:
        return None

    # Convert list[dict] to CSV
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=result[0].keys())
    writer.writeheader()
    writer.writerows(result)
    return buf.getvalue()


def _save_raw(source_id: str, data: str, output_path: Path) -> None:
    """Save raw data to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(data)


def fetch_all(sources: list[dict] | None = None, force: bool = False) -> dict[str, Path | None]:
    """Fetch all configured sources."""
    sources = sources or load_datasources()
    results = {}
    for source in sources:
        path = fetch_source(source, force=force)
        results[source["id"]] = path
        time.sleep(1)
    return results
