#!/usr/bin/env python3
"""產生每週電子報 HTML（newsletter_YYYYMMDD.html），只產生檔案、不寄信。
用法: python3 newsletter.py [天數，預設7]。寄送前須由劉靜渡確認名單與內容。"""
import json, sys, html, datetime as dt
D = int(sys.argv[1]) if len(sys.argv) > 1 else 7
db = json.load(open('news_db.json')); cut = (dt.date.today() - dt.timedelta(days=D)).isoformat()
U = 'https://tommyliu2009.github.io/subsidy-news/'
out = [f'<html><body style="font-family:sans-serif;max-width:680px;margin:auto"><h1>台灣政府補助新聞網｜每週電子報 {dt.date.today()}</h1>']
for c in ['補助政策', '補助成果發表', '補助資訊']:
    a = sorted([v for v in db.values() if v.get('summary_ok') and v['category'] == c and v['date'] >= cut], key=lambda v: v['date'], reverse=True)
    if not a: continue
    out.append(f'<h2>{c}</h2>')
    for v in a: out.append(f'<p><a href="{html.escape(v["url"])}"><b>{html.escape(v["title"])}</b></a><br><small>{v["unit"]}｜{v["date"]}</small><br>{html.escape(v["summary"])}</p>')
out.append(f'<p>查詢全台補助：<a href="https://www.subsidyking.tw/">補助王</a>｜網站：<a href="{U}">{U}</a></p><p>補助、標案、商業模式顧問｜仁禾管理顧問 劉靜渡 tommyliu2009@gmail.com</p><p style="color:#777;font-size:12px">取消訂閱：回信主旨寫「取消訂閱台灣政府補助新聞網」。</p></body></html>')
f = f'newsletter_{dt.date.today():%Y%m%d}.html'; open(f, 'w').write('\n'.join(out)); print('已產生', f)
