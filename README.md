# 台灣政府補助新聞網
每日彙整補助政策、補助成果發表、補助資訊。網址：https://tommyliu2009.github.io/subsidy-news/ （news.subsidyking.tw DNS 生效後改用該網域）
- 更新：`./deploy.sh 3` 抓新聞 → 依原文寫摘要存成 JSON → `python3 apply_summaries.py x.json` → `./deploy.sh publish`
- 電子報：`python3 newsletter.py 7` 產生 HTML（不自動寄送）
- 訂閱：網頁表單以 mailto 寄訂閱信到 tommyliu2009@gmail.com，主旨「訂閱台灣政府補助新聞網 <email>」，再整理到雲端硬碟 Grok 資料夾的「台灣政府補助新聞網訂閱名單」試算表。
