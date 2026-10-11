#!/usr/bin/env python3
"""由 news_db.json 產生 data.js（只輸出已有合格摘要、近 60 天的新聞），並由補助王資料庫取「開放中／14 天內截止」補助。"""
import json, csv, datetime as dt
db = json.load(open('news_db.json')); st = json.load(open('source_status.json'))
cut = (dt.date.today() - dt.timedelta(days=60)).isoformat()
ok = [v for v in db.values() if v.get('summary_ok') and 50 <= len(v.get('summary', '')) <= 200 and v['date'] >= cut]
items = sorted(ok, key=lambda v: (v['date'], v.get('added', '')), reverse=True)
K = ('title', 'url', 'date', 'category', 'topic', 'unit', 'summary', 'also')
items = [{k: v[k] for k in K if v.get(k)} for v in items]
t = dt.date.today().isoformat(); e = (dt.date.today() + dt.timedelta(days=14)).isoformat(); op = []
try:
    for r in csv.DictReader(open('/workspace/subsidy/補助資料庫_full.csv', encoding='utf-8-sig')):
        d = r['截止日期'][:10]
        if (r['狀態'] == '開放中' and (not d or d >= t)) or (d and t <= d <= e and r['狀態'] != '歷史(已結束)'):
            op.append(dict(name=r['補助名稱'], org=r['主辦單位'], end=d, url=r['原始連結'], soon=bool(d and d <= e)))
except FileNotFoundError: pass
op.sort(key=lambda x: (not x['soon'], x['end'] or '9999'))
open('data.js', 'w').write('window.NEWS=' + json.dumps(items, ensure_ascii=False) + ';\nwindow.OPEN=' + json.dumps(op, ensure_ascii=False) + ';\nwindow.UPDATED=' + json.dumps(st['updated']) + ';\n')
print('網站資料', len(items), '則；補助區塊', len(op), '筆（14 天內截止', sum(x['soon'] for x in op), '）；未上線（待摘要）', sum(1 for v in db.values() if not v.get('summary_ok')), '則')
