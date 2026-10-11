#!/usr/bin/env python3
"""台灣政府補助新聞網：抓取中央社、各部會與縣市政府新聞稿，分類後寫入 news_db.json
程式只放暫時摘要（summary_ok=False，不上線）；每則須依原文寫 50～200 字繁中摘要後以 apply_summaries.py 寫回。
用法: python3 fetch_news.py [天數，預設3]"""
import sys, json, re, time, html, datetime as dt, urllib.parse, concurrent.futures as cf, ssl
import feedparser, requests, trafilatura
from requests.adapters import HTTPAdapter
class _SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *a, **k):
        ctx = ssl.create_default_context(); ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        k['ssl_context'] = ctx; return super().init_poolmanager(*a, **k)
_S = requests.Session(); _S.mount('https://', _SSLAdapter())
from googlenewsdecoder import gnewsdecoder
from pubdate import extract as extract_pubdate, text_of
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
MAX_NEW = int(sys.argv[2]) if len(sys.argv) > 2 else 60   # 每次最多新增候選（摘要要逐則寫）
DB = 'news_db.json'; STATUS = 'source_status.json'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36', 'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'}
CATS = ['補助政策', '補助成果發表', '補助資訊']
RSS = {
 '國科會': ('https://www.nstc.gov.tw/rss?language=ch', None, '國科會'),
}
ZH = ('hl=zh-TW&gl=TW&ceid=TW:zh-Hant'); EN = ZH
GQ = [
 ('補助 site:cna.com.tw', ZH, None),
 ('(補助 OR 獎勵 OR 徵件) 計畫 site:cna.com.tw', ZH, None),
 ('(補助 OR 補貼) (預算 OR 條例 OR 修正 OR 新制) site:cna.com.tw', ZH, '補助政策'),
 ('(成果發表 OR 成果展 OR 獲補助 OR 頒獎) 計畫 site:cna.com.tw', ZH, '補助成果發表'),
 ('(補助 OR 補貼) (企業 OR 產業 OR 中小企業 OR 新創) site:cna.com.tw', ZH, None),
 ('(補助 OR 補貼) (農民 OR 農業 OR 漁民) site:cna.com.tw', ZH, None),
 ('(補助 OR 獎勵) (就業 OR 勞工 OR 青年 OR 育兒 OR 托育) site:cna.com.tw', ZH, None),
 ('(補助 OR 補貼) (節能 OR 電動車 OR 太陽光電 OR 汰舊換新) site:cna.com.tw', ZH, None),
 ('(補助 OR 獎勵) (文化 OR 藝文 OR 影視 OR 觀光) site:cna.com.tw', ZH, None),
 ('(補助 OR 津貼) (長照 OR 身障 OR 弱勢 OR 租金 OR 社宅) site:cna.com.tw', ZH, None),
 ('(補助 OR 補貼) (縣府 OR 市府 OR 縣長 OR 市長) site:cna.com.tw', ZH, None),
 ('(客委會 OR 原民會 OR 移民署) 補助 site:cna.com.tw', ZH, None),
 ('(補助 OR 補貼) 預算 (行政院 OR 立法院) site:cna.com.tw', ZH, '補助政策'),
 ('(AI OR 數位轉型 OR 研發) 補助 site:cna.com.tw', ZH, None),
 ('說明會 補助 site:cna.com.tw', ZH, '補助資訊'),
 ('補助 site:moea.gov.tw', ZH, None), ('site:sme.gov.tw', ZH, None), ('補助 site:moeaidb.gov.tw', ZH, None),
 ('補助 site:nstc.gov.tw', ZH, None), ('補助 site:mol.gov.tw', ZH, None), ('補助 site:wda.gov.tw', ZH, None),
 ('補助 site:moa.gov.tw', ZH, None), ('補助 site:moc.gov.tw', ZH, None), ('補助 site:hakka.gov.tw', ZH, None),
 ('補助 site:cip.gov.tw', ZH, None), ('補助 site:moda.gov.tw', ZH, None), ('補助 site:ndc.gov.tw', ZH, None),
 ('補助 site:ey.gov.tw', ZH, '補助政策'), ('補助 site:moenv.gov.tw', ZH, None), ('補助 site:moeaea.gov.tw', ZH, None),
 ('補助 site:mohw.gov.tw', ZH, None), ('補助 site:taichung.gov.tw', ZH, None), ('補助 site:gov.taipei', ZH, None),
 ('補助 site:ntpc.gov.tw', ZH, None), ('補助 site:kcg.gov.tw', ZH, None), ('補助 site:tainan.gov.tw', ZH, None),
 ('補助 site:tycg.gov.tw', ZH, None), ('補助 site:chcg.gov.tw', ZH, None), ('補助 site:yunlin.gov.tw', ZH, None),
 ('(SBIR OR 地方型SBIR OR SIIR OR CITD) 補助', ZH, None),
]
RES = re.compile(r'成果|發表會|成果展|獲補助|獲獎|頒獎|表揚|名單|入選|核定|通過.{0,6}(件|家|案)|案例|亮點|帶動|成效|圓夢|績優')
INFO = re.compile(r'受理|開放申請|申請|徵件|說明會|截止|報名|起跑|即日起|公告|上路|開跑')
POL = re.compile(r'政策|預算|條例|修正|法規|新制|擴大|加碼|放寬|調高|調整|草案|立法|行政院|會議通過|編列|方案')
NOISE = re.compile(r'今彩|大樂透|統一發票|車禍|命案|火警|詐騙|酒駕|圖輯|台股|收盤|加權指數|匯率|美股|ETF|樂透|天氣|颱風|地震|標售|徵才|招考')
REL = re.compile(r'補助|補貼|獎勵|獎補助|徵件|計畫|津貼|輔導|SBIR|貸款|紓困')
BAD_URL = re.compile(r'(\.pdf|\.docx?|\.xlsx?|\.odt|\.ods|/login|/download|Download\.ashx|/File/|/Attachment/|/tag/|/tags/|/category/|/search|/video|faq|/privacy)', re.I)
BAD_TITLE = re.compile(r'(^\s*-|首頁$|專區$|常見問答|問答集|錄取|徵才|招募|甄選|約用|採購|招標|會議紀錄|下載|影音|影片)', re.I)
def is_news(title, url): return not BAD_URL.search(url or '') and not BAD_TITLE.search(title or '')
SUBT = [('創新研發', r'SBIR|研發|創新|科專|科技'), ('中小企業與新創', r'中小|新創|創業|青創|微型'), ('就業與人才', r'就業|勞動|職訓|人才|薪|僱用|工作'),
 ('農業', r'農|漁|畜|林'), ('文化', r'文化|藝文|影視|出版|文創'), ('客家', r'客家|客委'), ('原住民', r'原住民|原民|部落|族'),
 ('節能減碳', r'節能|淨零|減碳|綠能|電動|太陽光電|汰換|儲能'), ('數位轉型與AI', r'數位|AI|人工智慧|資安'), ('社福與生活', r'長照|育兒|托育|住宅|租金|身障|弱勢|老人')]
def classify(title, desc, default):
    t = title
    if not REL.search(t + ' ' + (desc or '')[:200]): return None, None
    if default: cat = default
    elif RES.search(t): cat = '補助成果發表'
    elif POL.search(t) and not INFO.search(t): cat = '補助政策'
    else: cat = '補助資訊'
    for s, k in SUBT:
        if re.search(k, t + ' ' + (desc or '')[:200], re.I): return cat, s
    return cat, '綜合'

UNIT = {'mol.gov.tw':'勞動部','wda.gov.tw':'勞動部勞動力發展署','moc.gov.tw':'文化部','hakka.gov.tw':'客家委員會','cip.gov.tw':'原住民族委員會','moenv.gov.tw':'環境部','moeaea.gov.tw':'經濟部能源署','mohw.gov.tw':'衛生福利部','taichung.gov.tw':'臺中市政府','gov.taipei':'臺北市政府','ntpc.gov.tw':'新北市政府','kcg.gov.tw':'高雄市政府','tainan.gov.tw':'臺南市政府','tycg.gov.tw':'桃園市政府','chcg.gov.tw':'彰化縣政府','yunlin.gov.tw':'雲林縣政府','ithome.com.tw':'iThome','udn.com':'聯合新聞網','ltn.com.tw':'自由時報','cna.com.tw':'中央社','moea.gov.tw':'經濟部','sme.gov.tw':'經濟部中小及新創企業署','moeaidb.gov.tw':'經濟部產業發展署','ida.gov.tw':'經濟部產業發展署',
 'nstc.gov.tw':'國科會','moda.gov.tw':'數位發展部','ndc.gov.tw':'國家發展委員會','ey.gov.tw':'行政院','itri.org.tw':'工研院','iii.org.tw':'資策會',
 'tier.org.tw':'台灣經濟研究院','reuters.com':'Reuters','apnews.com':'AP','techcrunch.com':'TechCrunch','theverge.com':'The Verge',
 'technologyreview.com':'MIT Technology Review','openai.com':'OpenAI','blog.google':'Google','deepmind.google':'Google DeepMind',
 'blogs.nvidia.com':'NVIDIA','nvidia.com':'NVIDIA','anthropic.com':'Anthropic','about.fb.com':'Meta','ai.meta.com':'Meta','moa.gov.tw':'農業部','mof.gov.tw':'財政部'}
ALLOWED = tuple(UNIT)
def unit_of(url, fallback=''):
    h = urllib.parse.urlparse(url).netloc.lower()
    for k, v in UNIT.items():
        if h == k or h.endswith('.' + k): return v
    return fallback or h

def fetch_page(url, title=''):
    """回傳 (原文開頭文字, 狀態, 原文發布日)"""
    try:
        r = _S.get(url, headers=UA, timeout=20)
        if r.status_code != 200: return None, f'HTTP {r.status_code}', None
        if not r.encoding or r.encoding.lower() == 'iso-8859-1': r.encoding = r.apparent_encoding
        h = r.text; pd = extract_pubdate(url, h, title)
        body = trafilatura.extract(h, include_comments=False, include_tables=False, favor_precision=True) or ''
        if len(body) < 80:
            m = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:)?description["\'][^>]+content=["\']([^"\']+)', h, re.I)
            body = (html.unescape(m.group(1)) if m else '') + ' ' + body
        return re.sub(r'\s+', ' ', body).strip()[:1500], 'ok', pd
    except Exception as e:
        return None, type(e).__name__, None

def tkey(t): return re.sub(r'[\W_]', '', re.sub(r'\|.*$|｜.*$', '', t)).lower()[:30]

def main():
    try: db = json.load(open(DB))
    except Exception: db = {}
    try: rejected = set(json.load(open('rejected.json')))
    except Exception: rejected = set()
    try: rej_urls = set(json.load(open('rejected_urls.json')))
    except Exception: rej_urls = set()
    status = {}; cand = []; cutoff = time.time() - DAYS * 86400
    for name, (u, cat, unit) in RSS.items():
        try:
            r = _S.get(u, headers=UA, timeout=25); f = feedparser.parse(r.content)
            if r.status_code != 200 or not f.entries: raise Exception(f'HTTP {r.status_code}, {len(f.entries)} 則')
            n = 0
            for e in f.entries:
                pub = e.get('published_parsed') or e.get('updated_parsed')
                if not pub or time.mktime(pub) < cutoff: continue
                if cat is None and not REL.search(e.title): continue
                cand.append(dict(title=html.unescape(e.title).strip(), url=e.link, cat=cat, unit=unit, src=name, desc=re.sub('<[^>]+>', '', e.get('summary', ''))[:300])); n += 1
            status[name] = {'ok': True, 'note': f'RSS {len(f.entries)} 則，期間內 {n} 則'}
        except Exception as ex:
            status[name] = {'ok': False, 'note': str(ex)[:120]}
    for q, lang, cat in GQ:
        n = 0
        try:
            url = f'https://news.google.com/rss/search?q={urllib.parse.quote(q + f" when:{DAYS}d")}&{lang}'
            f = feedparser.parse(_S.get(url, headers=UA, timeout=25).content)
            for e in f.entries[:(60 if 'cna.com.tw' in q else 25)]:
                pub = e.get('published_parsed')
                if not pub or time.mktime(pub) < cutoff: continue
                t = re.sub(r'\s+[-|]\s+[^-|]+$', '', html.unescape(e.title)).strip()
                cand.append(dict(title=t, url=None, glink=e.link, cat=cat, unit='', src='Google新聞', desc='')); n += 1
            status[f'Google新聞：{q}'] = {'ok': True, 'note': f'候選 {n} 則'}
        except Exception as ex:
            status[f'Google新聞：{q}'] = {'ok': False, 'note': str(ex)[:100]}
        time.sleep(1)
    known = {tkey(v['title']) for v in db.values()} | {tkey(v.get('title_zh', '')) for v in db.values() if v.get('title_zh')} | {tkey(t) for t in rejected}
    seen = set(); todo = []
    for c in cand:
        if NOISE.search(c['title']): continue
        k = tkey(c['title'])
        if not k or k in seen or k in known or c.get('url') in db: continue
        seen.add(k); todo.append(c)
    # 各分類平均取，避免單一分類塞滿
    by = {}
    for c in todo: by.setdefault(c['cat'] or '_', []).append(c)
    todo = []
    while len(todo) < MAX_NEW * 2 and any(by.values()):
        for k in list(by):
            if by[k]: todo.append(by[k].pop(0))
    for c in todo:
        if c['url'] is None:
            try:
                d = gnewsdecoder(c['glink'], interval=1); c['url'] = d.get('decoded_url') if d.get('success') else None
            except Exception: c['url'] = None
    todo = [c for c in todo if c['url'] and c['url'] not in rej_urls and c['url'] not in db and unit_of(c['url']) in UNIT.values()]
    for c in todo:
        if not is_news(c['title'], c['url']): rejected.add(c['title'])
    todo = [c for c in todo if is_news(c['title'], c['url'])]
    fail_hosts = {}; no_date = 0; added = 0
    cutoff_date = (dt.date.today() - dt.timedelta(days=DAYS)).isoformat()
    with cf.ThreadPoolExecutor(8) as ex:
        for c, (body, st, pd) in zip(todo, ex.map(lambda c: fetch_page(c['url'], c['title']), todo)):
            host = urllib.parse.urlparse(c['url']).netloc
            if body is None: fail_hosts.setdefault(host, [0, st])[0] += 1; continue
            if not pd: no_date += 1; rejected.add(c['title']); continue          # 發布日一律以原文為準，取不到不收
            if pd < cutoff_date: rejected.add(c['title']); continue
            if added >= MAX_NEW: break
            cat, sub = classify(c['title'], body[:300], c['cat'])
            if not cat: rejected.add(c['title']); continue
            en = not re.search(r'[\u4e00-\u9fff]', c['title'])
            db[c['url']] = dict(title=re.sub(r'\s*\|\s*\S{2,4}\s*$', '', c['title']), url=c['url'], date=pd, category=cat, topic=sub, unit=unit_of(c['url'], c['unit']),
                                lang='en' if en else 'zh', summary='', hint=body[:1200], summary_ok=False, added=dt.date.today().isoformat())
            added += 1
    json.dump(sorted(rejected), open('rejected.json', 'w'), ensure_ascii=False)
    json.dump(db, open(DB, 'w'), ensure_ascii=False, indent=0)
    status['_原文取不到發布日（未收錄）'] = {'ok': True, 'note': f'{no_date} 則'}
    status['_原文無法讀取的網站（未收錄）'] = {'ok': not fail_hosts, 'note': '; '.join(f'{h} {n}則({e})' for h, (n, e) in fail_hosts.items())}
    json.dump(dict(updated=dt.datetime.now().strftime('%Y-%m-%d %H:%M'), sources=status), open(STATUS, 'w'), ensure_ascii=False, indent=1)
    pend = [dict(url=u, title=v['title'], date=v['date'], unit=v['unit'], category=v['category'], topic=v['topic'], lang=v.get('lang'), hint=v.get('hint', '')) for u, v in db.items() if not v.get('summary_ok')]
    json.dump(pend, open('pending_summary.json', 'w'), ensure_ascii=False, indent=1)
    print('本次新增', added, '則；資料庫共', len(db), '則；待寫摘要（未上線）', len(pend), '則 → pending_summary.json')
if __name__ == '__main__':
    main()
