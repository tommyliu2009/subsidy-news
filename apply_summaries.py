#!/usr/bin/env python3
"""把依原文寫好的摘要寫回 news_db.json。
用法: python3 apply_summaries.py summaries.json
格式: {"<網址>": "50～200字繁中摘要"} 或 {"<網址>": {"summary": "...", "title_zh": "英文新聞的中文標題"}}；
值寫 "REMOVE" 代表不是新聞或資訊不足，刪除並列入 rejected_urls.json；{"merge": "<另一則網址>"} 代表與該則重複，合併（保留該則，本則列為其他來源）。"""
import json, sys
db = json.load(open('news_db.json')); new = json.load(open(sys.argv[1]))
try: rej = set(json.load(open('rejected_urls.json')))
except Exception: rej = set()
bad = []
for u, s in new.items():
    if u not in db: bad.append((u, '不在資料庫')); continue
    if s == 'REMOVE': db.pop(u); rej.add(u); continue
    if isinstance(s, dict) and s.get('merge'):
        m = s['merge']
        if m in db: db[m].setdefault('also', []).append(dict(unit=db[u]['unit'], url=u))
        db.pop(u); rej.add(u); continue
    if isinstance(s, str): s = {'summary': s}
    t = ' '.join(s['summary'].split())
    if not 50 <= len(t) <= 200: bad.append((u, f'字數 {len(t)}')); continue
    if db[u].get('lang') == 'en' and not s.get('title_zh') and not db[u].get('title_zh'): bad.append((u, '英文新聞缺中文標題')); continue
    db[u]['summary'] = t; db[u]['summary_ok'] = True; db[u].pop('hint', None)
    if s.get('title_zh'): db[u]['title_zh'] = s['title_zh']
    for k in ('category', 'topic'):
        if s.get(k): db[u][k] = s[k]
json.dump(db, open('news_db.json', 'w'), ensure_ascii=False, indent=0)
json.dump(sorted(rej), open('rejected_urls.json', 'w'), ensure_ascii=False)
pend = [dict(url=u, title=v['title'], date=v['date'], unit=v['unit'], category=v['category'], topic=v.get('topic'), lang=v.get('lang'), hint=v.get('hint', '')) for u, v in db.items() if not v.get('summary_ok')]
json.dump(pend, open('pending_summary.json', 'w'), ensure_ascii=False, indent=1)
for b in bad: print('未寫入:', *b)
print('剩待寫摘要', len(pend), '則')
