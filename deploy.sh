#!/usr/bin/env bash
# 台灣政府補助新聞網：抓新聞 → 產生網站資料 → 推送 GitHub Pages（news.subsidyking.tw（DNS 生效前用 tommyliu2009.github.io/subsidy-news））
# 用法：./deploy.sh [天數，預設3]   抓新聞＋部署（沒摘要的新聞不會上線，列在 pending_summary.json）
#       ./deploy.sh publish        只重建網站並部署（依原文補寫摘要、跑完 apply_summaries.py 之後用）
set -euo pipefail
cd "$(dirname "$0")"
exec 9>/tmp/subsidy-news.lock
flock -n 9 || { echo "上一次更新還在執行，略過本次"; exit 0; }
export PATH="$HOME/.local/bin:$PATH"
if [ "${1:-}" != "publish" ]; then timeout 2400 python3 fetch_news.py "${1:-3}" || echo "抓取逾時或失敗，沿用既有資料"; fi
python3 build_site.py
[ -f CNAME ] || echo news.subsidyking.tw > CNAME
python3 /workspace/shared-data/ga_inject.py . || echo "⚠️ GA 程式碼補入或檢查有問題，請看上面訊息"   # GA4：所有頁面 <head> 補 gtag（2026-10-18）
git add -A
if git diff --cached --quiet; then echo "資料無變動，不需部署"; exit 0; fi
git -c user.name="tommyliu2009" -c user.email="tommyliu2009@users.noreply.github.com" commit -qm "新聞更新 $(TZ=Asia/Taipei date '+%Y-%m-%d %H:%M')"
git push -q origin main
echo "已部署：$(git log -1 --format=%s)"
