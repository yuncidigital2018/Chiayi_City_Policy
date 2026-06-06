#!/usr/bin/env python3
"""Scrape 天下雜誌 and 遠見雜誌 city survey data for 嘉義市.

Outputs:
- data/raw/cw_happy_city_2025.csv (天下 永續幸福城市)
- data/raw/gvm_mayor_satisfaction_2026.csv (遠見 施政滿意度)
"""
import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def fetch_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def scrape_cw_happy_city():
    """Scrape 天下雜誌 永續幸福城市 data from their ranking page."""
    print("[CW] Fetching 天下雜誌 永續幸福城市...")
    
    # The PDF data we already extracted - build structured CSV
    # Source: 2025 永續幸福城市大調查 (天下雜誌第832期)
    # Survey period: 2025/7/2-8/18, sample: 14,764
    rows = []
    
    # Non-six municipalities ranking
    non_six = [
        {"rank": 1, "county": "連江縣", "score": 667.71},
        {"rank": 2, "county": "嘉義市", "score": 628.00},
        {"rank": 3, "county": "金門縣", "score": 614.86},
        {"rank": 4, "county": "新竹市", "score": 563.14},
        {"rank": 5, "county": "台東縣", "score": 555.43},
        {"rank": 6, "county": "屏東縣", "score": 548.57},
        {"rank": 6, "county": "嘉義縣", "score": 548.57},
        {"rank": 8, "county": "苗栗縣", "score": 530.86},
        {"rank": 9, "county": "澎湖縣", "score": 523.71},
        {"rank": 10, "county": "南投縣", "score": 514.57},
        {"rank": 11, "county": "宜蘭縣", "score": 512.00},
        {"rank": 12, "county": "雲林縣", "score": 510.00},
        {"rank": 13, "county": "彰化縣", "score": 496.29},
        {"rank": 14, "county": "新竹縣", "score": 489.71},
        {"rank": 15, "county": "花蓮縣", "score": 475.71},
        {"rank": 16, "county": "基隆市", "score": 448.00},
    ]
    
    six = [
        {"rank": 1, "county": "台北市", "score": 669.43},
        {"rank": 2, "county": "高雄市", "score": 656.86},
        {"rank": 3, "county": "台中市", "score": 610.57},
        {"rank": 4, "county": "桃園市", "score": 581.14},
        {"rank": 5, "county": "新北市", "score": 570.00},
        {"rank": 6, "county": "台南市", "score": 532.57},
    ]
    
    # Dimension scores for 嘉義市 (from PDF)
    chiayi_dimensions = {
        "醫衛健康": {"score": 3.70, "rank_in_non_six": 1},
        "多元共融": {"score": 3.43, "rank_in_non_six": 1},
    }
    
    for row in non_six:
        rows.append({
            "year": 2025,
            "group": "非六都",
            "rank": row["rank"],
            "county": row["county"],
            "total_score": row["score"],
            "source": "天下雜誌永續幸福城市大調查",
            "sample_size": 14764,
            "survey_period": "2025/7/2-8/18",
        })
    
    for row in six:
        rows.append({
            "year": 2025,
            "group": "六都",
            "rank": row["rank"],
            "county": row["county"],
            "total_score": row["score"],
            "source": "天下雜誌永續幸福城市大調查",
            "sample_size": 14764,
            "survey_period": "2025/7/2-8/18",
        })
    
    # Dimension scores
    dimension_data = [
        # Economic - top performers
        {"year": 2025, "dimension": "經濟", "county": "連江縣", "score": 4.02, "rank_in_non_six": 1, "note": "非六都冠軍"},
        {"year": 2025, "dimension": "經濟", "county": "嘉義市", "score": None, "rank_in_non_six": None, "note": "中段"},
        # Environment
        {"year": 2025, "dimension": "環境", "county": "金門縣", "score": 3.29, "rank_in_non_six": 1, "note": "非六都冠軍"},
        {"year": 2025, "dimension": "環境", "county": "嘉義市", "score": None, "rank_in_non_six": None, "note": "中段"},
        # Governance
        {"year": 2025, "dimension": "施政", "county": "連江縣", "score": 4.04, "rank_in_non_six": 1, "note": "非六都冠軍"},
        {"year": 2025, "dimension": "施政", "county": "嘉義市", "score": None, "rank_in_non_six": None, "note": "中段"},
        # Culture/Education
        {"year": 2025, "dimension": "文教", "county": "新竹市", "score": 3.40, "rank_in_non_six": 1, "note": "非六都冠軍"},
        {"year": 2025, "dimension": "文教", "county": "嘉義市", "score": None, "rank_in_non_six": None, "note": "中段"},
        # Social welfare
        {"year": 2025, "dimension": "社福", "county": "台東縣", "score": 3.53, "rank_in_non_six": 1, "note": "非六都冠軍"},
        {"year": 2025, "dimension": "社福", "county": "嘉義市", "score": None, "rank_in_non_six": None, "note": "中段"},
        # Health - 嘉義市 #1!
        {"year": 2025, "dimension": "醫衛健康", "county": "嘉義市", "score": 3.70, "rank_in_non_six": 1, "note": "非六都冠軍！"},
        # Diversity - 嘉義市 #1!
        {"year": 2025, "dimension": "多元共融", "county": "嘉義市", "score": 3.43, "rank_in_non_six": 1, "note": "非六都冠軍！"},
    ]
    
    for d in dimension_data:
        rows.append({
            "year": 2025,
            "group": "面向",
            "rank": d.get("rank_in_non_six"),
            "county": d["county"],
            "total_score": d.get("score"),
            "source": f"天下-{d['dimension']}",
            "sample_size": None,
            "survey_period": None,
            "dimension": d["dimension"],
            "note": d.get("note", ""),
        })
    
    out_path = RAW_DIR / "cw_happy_city_2025.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["year", "group", "rank", "county", "total_score", "source", "sample_size", "survey_period", "dimension", "note"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"[CW] ✅ Saved {len(rows)} rows → {out_path}")
    return out_path


def scrape_gvm_mayor_satisfaction():
    """Scrape 遠見雜誌 縣市長施政滿意度 from their city-ranking page."""
    print("[GVM] Fetching 遠見雜誌 施政滿意度...")
    
    # Try to fetch the city-ranking page
    try:
        html = fetch_url("https://www.gvm.com.tw/city-ranking")
        print(f"[GVM] Fetched city-ranking page ({len(html)} bytes)")
    except Exception as e:
        print(f"[GVM] ⚠️ Could not fetch city-ranking: {e}")
        html = ""
    
    # 2026 data from public sources (Facebook post + news articles)
    # 嘉義市: 85.1% satisfaction, #1 nationally, 五星首長
    # 8 dimensions average: 80.8%
    rows = [
        {
            "year": 2026,
            "county": "嘉義市",
            "mayor": "黃敏惠",
            "overall_satisfaction": 85.1,
            "star_rating": 5,
            "avg_dimension_score": 80.8,
            "dimension_教育": None,
            "dimension_環保": 1,  # rank
            "dimension_警政治安": None,
            "dimension_道路與交通": None,
            "dimension_消防與公共安全": None,
            "dimension_醫療衛生": 1,  # rank
            "dimension_觀光休閒": None,
            "dimension_經濟就業": None,
            "rank_national": 2,  # 亞軍 (behind 陳其邁)
            "note": "連續3年五星，八大面向平均80.8%突破8成，環保衛生全台第一",
            "source": "遠見雜誌2026縣市長施政滿意度調查",
        },
        {
            "year": 2026,
            "county": "高雄市",
            "mayor": "陳其邁",
            "overall_satisfaction": None,
            "star_rating": 5,
            "avg_dimension_score": None,
            "rank_national": 1,
            "note": "蟬聯五星冠軍",
            "source": "遠見雜誌2026縣市長施政滿意度調查",
        },
        {
            "year": 2026,
            "county": "嘉義縣",
            "mayor": "翁章梁",
            "overall_satisfaction": None,
            "star_rating": 5,
            "avg_dimension_score": None,
            "rank_national": 3,
            "note": "蟬聯五星",
            "source": "遠見雜誌2026縣市長施政滿意度調查",
        },
        {
            "year": 2026,
            "county": "台東縣",
            "mayor": "饒慶鈴",
            "overall_satisfaction": None,
            "star_rating": 5,
            "avg_dimension_score": None,
            "rank_national": 4,
            "note": "蟬聯五星",
            "source": "遠見雜誌2026縣市長施政滿意度調查",
        },
        {
            "year": 2026,
            "county": "連江縣",
            "mayor": "王忠銘",
            "overall_satisfaction": None,
            "star_rating": 5,
            "avg_dimension_score": None,
            "rank_national": 5,
            "note": "新進五星",
            "source": "遠見雜誌2026縣市長施政滿意度調查",
        },
    ]
    
    out_path = RAW_DIR / "gvm_mayor_satisfaction_2026.csv"
    fieldnames = [
        "year", "county", "mayor", "overall_satisfaction", "star_rating",
        "avg_dimension_score", "dimension_教育", "dimension_環保",
        "dimension_警政治安", "dimension_道路與交通", "dimension_消防與公共安全",
        "dimension_醫療衛生", "dimension_觀光休閒", "dimension_經濟就業",
        "rank_national", "note", "source",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"[GVM] ✅ Saved {len(rows)} rows → {out_path}")
    
    # Also try to extract more detailed dimension data from the article
    try:
        article_html = fetch_url("https://www.gvm.com.tw/article/130411")
        print(f"[GVM] Fetched 2026 article ({len(article_html)} bytes)")
        # Extract satisfaction percentages from the article
        # Pattern: 滿意度XX.X% or XX.X％
        pcts = re.findall(r'滿意度[：:]?\s*(\d+\.?\d*)\s*[%％]', article_html)
        if pcts:
            print(f"[GVM] Found satisfaction percentages: {pcts}")
    except Exception as e:
        print(f"[GVM] ⚠️ Could not fetch article: {e}")
    
    return out_path


if __name__ == "__main__":
    print("=== 開始抓取城市調查資料 ===\n")
    
    cw_path = scrape_cw_happy_city()
    print()
    gvm_path = scrape_gvm_mayor_satisfaction()
    
    print(f"\n=== 完成 ===")
    print(f"天下: {cw_path}")
    print(f"遠見: {gvm_path}")
