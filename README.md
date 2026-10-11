# 台灣政府補助新聞網
每日彙整補助政策、補助成果發表、補助資訊。網址：https://tommyliu2009.github.io/subsidy-news/ （news.subsidyking.tw DNS 生效後改用該網域）
- 更新：`./deploy.sh 3` 抓新聞 → 依原文寫摘要存成 JSON → `python3 apply_summaries.py x.json` → `./deploy.sh publish`
- 電子報：`python3 newsletter.py 7` 產生 HTML（不自動寄送）
- 訂閱：網頁只填 Email，呼叫 Apps Script（apps_script/Code.gs）寫入試算表「台灣政府補助新聞網訂閱名單」；同一 Email 再送一次即取消。網址填在 config.js 的 SUB_URL。
