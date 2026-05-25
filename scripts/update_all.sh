#!/usr/bin/env bash
# update_all.sh — 完整更新流程：fetch → normalize → generate → (frontend build)
# 用法: bash scripts/update_all.sh [--force] [--skip-frontend]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

FORCE=""
SKIP_FRONTEND=""
for arg in "$@"; do
    case "$arg" in
        --force) FORCE="--force" ;;
        --skip-frontend) SKIP_FRONTEND="1" ;;
    esac
done

echo "=== 嘉義市人口與財政知識庫 — 完整更新流程 ==="
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "目錄: $PROJECT_ROOT"
echo ""

# Step 1: Fetch
echo ">>> Step 1: 抓取原始資料..."
python3 -m etl.main fetch $FORCE
echo ""

# Step 2: Normalize
echo ">>> Step 2: 清洗與標準化..."
python3 -m etl.main normalize
echo ""

# Step 3: Generate Markdown
echo ">>> Step 3: 產生 Markdown 報告..."
python3 -m etl.main generate
echo ""

# Step 4: Frontend build (optional)
if [ -z "$SKIP_FRONTEND" ]; then
    if [ -d "web" ] && [ -f "web/package.json" ]; then
        echo ">>> Step 4: 前端 build..."
        cd web
        npm ci --silent 2>/dev/null || npm install --silent
        npm run build 2>&1 || echo "⚠ 前端 build 失敗，但不影響已生成的 Markdown"
        cd "$PROJECT_ROOT"
    else
        echo ">>> Step 4: 跳過前端（web/ 尚未初始化）"
    fi
fi

echo ""
echo "=== 更新完成 ==="
echo "Processed 資料: data/processed/"
echo "Markdown 報告: content/"
echo ""

# Show summary
python3 -m etl.main status
