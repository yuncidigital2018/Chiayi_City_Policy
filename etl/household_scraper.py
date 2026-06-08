"""Scrape household.chiayi.gov.tw population data (ASP.NET site)."""
from __future__ import annotations

import logging
import re
from pathlib import Path

import requests
from lxml import html

logger = logging.getLogger(__name__)

BASE = "https://household.chiayi.gov.tw"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}


def _session():
    s = requests.Session()
    s.verify = False
    s.headers.update(HEADERS)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return s


def scrape_historical() -> list[dict] | None:
    """Scrape 歷年人口數 (Parser=99,7,43).
    
    Returns: [{year, households, male, female, total, growth_pct}, ...]
    """
    s = _session()
    try:
        r = s.get(f"{BASE}/popul05/index.aspx?Parser=99,7,43", timeout=15)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Failed: {e}")
        return None

    tree = html.fromstring(r.text)
    texts = tree.xpath('//*/text()')
    raw = ' '.join(' '.join(texts).split())

    rows = []
    pattern = r'(\d{2,3})\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\-+]?[\d.]+%)'
    for m in re.finditer(pattern, raw):
        yr = int(m.group(1).lstrip('0') or '0')
        rows.append({
            'year': yr,
            'households': int(m.group(2).replace(',', '')),
            'male': int(m.group(3).replace(',', '')),
            'female': int(m.group(4).replace(',', '')),
            'total': int(m.group(5).replace(',', '')),
            'growth_pct': m.group(6),
        })
    logger.info(f"Scraped {len(rows)} years of historical population")
    return rows if rows else None


def scrape_age_gender() -> list[dict] | None:
    """Scrape 性別年齡人口數 (Parser=99,7,39) — population pyramid.
    
    Returns: [{age_group, male, female, total}, ...] (non-summary rows only)
    """
    s = _session()
    try:
        r = s.get(f"{BASE}/popul01/index.aspx?Parser=99,7,39", timeout=15)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Failed: {e}")
        return None

    tree = html.fromstring(r.text)
    rows = []
    
    for li in tree.xpath('//li[div[@class="pop_add"]]'):
        divs = li.xpath('div/text()')
        if len(divs) >= 4:
            age_group = divs[0].strip()
            try:
                male = int(divs[1].strip().replace(',', ''))
                female = int(divs[2].strip().replace(',', ''))
                total = int(divs[3].strip().replace(',', ''))
            except ValueError:
                continue
            is_summary = any(k in age_group for k in ['總', '以上'])
            if not is_summary:
                rows.append({
                    'age_group': age_group,
                    'male': male,
                    'female': female,
                    'total': total,
                })
    
    logger.info(f"Scraped {len(rows)} age/gender pyramid rows")
    return rows if rows else None


def scrape_village_list(year=115, month=4) -> list[dict] | None:
    """Scrape 區里戶數及人口數 — village-level data for both districts.
    
    District-specific URLs:
    - East: Parser=99,7,38,,,,,,,,,,,,,,,,,1,,,,1,{year},{month}
    - West: Parser=99,7,38,,,,,,,,,,,,,,,,,1,,,,2,{year},{month}
    
    Returns: [{year, month, district, village, neighborhoods, households, male, female, population}, ...]
    """
    s = _session()
    all_rows = []
    
    districts = [
        ('東區', f"99,7,38,,,,,,,,,,,,,,,,,1,,,,1,{year},{month}"),
        ('西區', f"99,7,38,,,,,,,,,,,,,,,,,1,,,,2,{year},{month}"),
    ]
    
    for district_name, parser in districts:
        try:
            r = s.get(f"{BASE}/popul01/List.aspx?Parser={parser}", timeout=15)
            r.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch {district_name}: {e}")
            continue
        
        tree = html.fromstring(r.text)
        
        for li in tree.xpath('//li[div[@class="pop_add"]]'):
            divs = li.xpath('div/text()')
            if len(divs) >= 5:
                village = divs[0].strip()
                try:
                    neighborhoods = int(divs[1].strip().replace(',', ''))
                    households = int(divs[2].strip().replace(',', ''))
                    male = int(divs[3].strip().replace(',', ''))
                    female = int(divs[4].strip().replace(',', ''))
                    total = int(divs[5].strip().replace(',', '')) if len(divs) > 5 else 0
                except (ValueError, IndexError):
                    continue
                if '總' in village:
                    continue
                all_rows.append({
                    'year': year,
                    'month': month,
                    'district': district_name,
                    'village': village,
                    'neighborhoods': neighborhoods,
                    'households': households,
                    'male': male,
                    'female': female,
                    'population': total,
                })
    
    logger.info(f"Scraped {len(all_rows)} village rows for {year}/{month}")
    return all_rows if all_rows else None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("=== 歷史人口資料 ===")
    hist = scrape_historical()
    if hist:
        print(f"  {hist[0]}")
        print(f"  ... ({len(hist)} rows total)")
        print(f"  Latest: {hist[-1]}")

    print("\n=== 性別年齡人口 ===")
    ag = scrape_age_gender()
    if ag:
        for row in ag[:3]:
            print(f"  {row}")
        print(f"  ... ({len(ag)} rows total)")
        
    print("\n=== 區里人口 ===")
    vl = scrape_village_list()
    if vl:
        for row in vl[:5]:
            print(f"  {row}")
        print(f"  ... ({len(vl)} rows total)")
        # Count by district
        east = sum(1 for r in vl if r['district'] == '東區')
        west = sum(1 for r in vl if r['district'] == '西區')
        print(f"  東區: {east} 里, 西區: {west} 里")
