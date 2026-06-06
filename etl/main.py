#!/usr/bin/env python3
"""Chiayi City Policy — ETL & Content Pipeline CLI.

Usage:
    python -m etl.main fetch          # Fetch all raw data
    python -m etl.main normalize      # Normalize raw → processed
    python -m etl.main generate       # Generate Markdown from processed
    python -m etl.main run            # Full pipeline: fetch → normalize → generate
    python -m etl.main fetch --force  # Force re-fetch (ignore cache)
"""
import logging
import sys
from pathlib import Path

import click

from etl.config_loader import load_datasources
from etl.fetcher import fetch_all
from etl.normalizer import run_normalization
from etl.fund_normalizer import run_fund_normalization
from etl.md_generator import run_markdown_generation
from etl.validator import validate_all
from etl.cross_county import run_cross_county_pipeline
from etl.change_detector import detect_changes, format_report
from etl.domain_classifier import run_classify_pipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("chiayi_etl")


@click.group()
def cli():
    """嘉義市人口與財政資料 — ETL & Content Pipeline"""
    pass


@cli.command()
@click.option("--force", is_flag=True, help="Force re-fetch even if cached")
@click.option("--source", default=None, help="Fetch only this source id")
def fetch(force: bool, source: str | None):
    """Fetch raw data from configured sources."""
    sources = load_datasources()
    if source:
        sources = [s for s in sources if s["id"] == source]
        if not sources:
            logger.error(f"Source '{source}' not found in config")
            sys.exit(1)

    logger.info(f"Fetching {len(sources)} source(s)...")
    results = fetch_all(sources, force=force)

    success = sum(1 for v in results.values() if v is not None)
    failed = len(results) - success
    logger.info(f"Fetch complete: {success} succeeded, {failed} failed")

    if failed > 0:
        for sid, path in results.items():
            if path is None:
                logger.warning(f"  FAILED: {sid}")


@cli.command()
@click.option("--all-tables", is_flag=True, help="Run all normalizers even without raw data")
def normalize(all_tables: bool):
    """Normalize raw data into processed tables."""
    logger.info("Running normalization...")
    results = run_normalization()

    success = sum(1 for v in results.values() if v is not None)
    skipped = len(results) - success
    logger.info(f"Normalization complete: {success} tables produced, {skipped} skipped")


@cli.command()
def generate():
    """Generate Markdown reports from processed data."""
    logger.info("Generating Markdown...")
    results = run_markdown_generation()

    if results:
        logger.info(f"Generated {len(results)} Markdown file(s):")
        for key, path in results.items():
            logger.info(f"  {key}: {path}")
    else:
        logger.warning("No Markdown files generated (no processed data found)")


@cli.command()
@click.option("--force", is_flag=True, help="Force re-fetch")
@click.option("--skip-fetch", is_flag=True, help="Skip fetch step (use existing raw data)")
@click.option("--skip-normalize", is_flag=True, help="Skip normalization step")
@click.option("--skip-generate", is_flag=True, help="Skip Markdown generation step")
def run_pipeline(force: bool, skip_fetch: bool, skip_normalize: bool, skip_generate: bool):
    """Run full pipeline: fetch → normalize → generate."""
    raw_paths = None
    processed_paths = None

    if not skip_fetch:
        logger.info("=== Phase 1: Fetch ===")
        raw_results = fetch_all(force=force)
        # Build mapping from output_filename (no ext) → Path for normalizer lookup
        sources = load_datasources()
        raw_paths = {}
        for src in sources:
            sid = src["id"]
            path = raw_results.get(sid)
            if path:
                output_rel = src.get("output", f"data/raw/{sid}.csv")
                raw_name = Path(output_rel).stem  # e.g. "population_historical"
                raw_paths[raw_name] = path
        success = sum(1 for v in raw_results.values() if v is not None)
        logger.info(f"Fetch: {success}/{len(raw_results)} succeeded")

    if not skip_normalize:
        logger.info("=== Phase 2: Normalize ===")
        processed_paths = run_normalization(raw_paths)
        fund_paths = run_fund_normalization(raw_paths)
        all_processed = {**processed_paths, **fund_paths}
        success = sum(1 for v in all_processed.values() if v is not None)
        logger.info(f"Normalize: {success} tables produced")

    if not skip_generate:
        logger.info("=== Phase 3: Generate ===")
        md_paths = run_markdown_generation(all_processed)
        logger.info(f"Generate: {len(md_paths)} Markdown files created")

    # Validate
    logger.info("=== Phase 4: Validate ===")
    val_results = validate_all()
    val_failed = sum(1 for r in val_results if not r.passed)
    if val_failed:
        logger.warning(f"Validation: {val_failed} table(s) have issues")
    else:
        logger.info("Validation: all tables passed ✅")


@cli.command()
@click.option("--year", default=114, help="ROC year to fetch (default: 114)")
def compare(year: int):
    """Fetch cross-county population comparison data."""
    logger.info(f"Fetching county comparison for year {year}...")
    df = run_cross_county_pipeline([year])
    if df is not None:
        chiayi = df[df["county"] == "嘉義市"]
        if not chiayi.empty:
            r = chiayi.iloc[0]
            logger.info(f"嘉義市: 第 {int(r['rank'])}/{len(df)} 名, 人口 {int(r['population']):,}")
    else:
        logger.error("Failed to fetch county comparison data")


@cli.command()
def validate():
    """Validate processed data quality."""
    logger.info("Running data validation...")
    results = validate_all()
    failed = sum(1 for r in results if not r.passed)
    if failed:
        logger.error(f"Validation failed for {failed} table(s)")
        sys.exit(1)
    else:
        logger.info("All validations passed ✅")


@cli.command()
def changes():
    """Detect data changes since last run."""
    result = detect_changes()
    report = format_report(result)
    logger.info(report)


@cli.command()
def status():
    """Show current data status."""
    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    content_dir = Path(__file__).resolve().parent.parent / "content"

    logger.info("=== Data Status ===")

    # Raw files
    if raw_dir.exists():
        raw_files = list(raw_dir.glob("*.csv"))
        logger.info(f"Raw files: {len(raw_files)}")
        for f in raw_files:
            logger.info(f"  {f.name} ({f.stat().st_size:,} bytes)")

    # Processed files
    if processed_dir.exists():
        processed_files = list(processed_dir.glob("*.csv"))
        logger.info(f"Processed tables: {len(processed_files)}")
        for f in processed_files:
            logger.info(f"  {f.name} ({f.stat().st_size:,} bytes)")

    # Content files
    if content_dir.exists():
        content_files = list(content_dir.rglob("*.md"))
        logger.info(f"Markdown files: {len(content_files)}")
        for f in content_files:
            logger.info(f"  {f.relative_to(content_dir)}")


@cli.command()
def classify():
    """Classify budget by policy domain (function + agency)."""
    logger.info("Running policy domain classification...")
    result = run_classify_pipeline()

    logger.info("=== Function Classification ===")
    if result["classified_path"]:
        logger.info(f"Classified: {result['classified_path']}")
        logger.info(f"Summary:    {result['summary_path']}")
        logger.info(f"Domains:    {result['domain_count']}")
        if result["unmapped_functions"] > 0:
            logger.warning(f"Unmapped function categories: {result['unmapped_functions']}")
        else:
            logger.info("All function categories mapped ✅")
    else:
        logger.error("Function classification failed")

    logger.info("=== Agency Classification ===")
    if result["agency_classified_path"]:
        logger.info(f"Classified: {result['agency_classified_path']}")
        logger.info(f"Summary:    {result['agency_summary_path']}")
        if result["unmapped_agencies"] > 0:
            logger.warning(f"Unmapped agencies: {result['unmapped_agencies']}")
        else:
            logger.info("All agencies mapped ✅")
    else:
        logger.warning("Agency classification skipped (no data)")

    if not result["classified_path"]:
        sys.exit(1)


if __name__ == "__main__":
    cli()

