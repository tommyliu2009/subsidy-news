"""從原文頁面取「發布日期」（民國年換算為西元），取不到回傳 None。
不採用 更新日期／修改時間／檢核日期／DC.Date 這類常為網站範本或更新時間的欄位。"""
import re, html, datetime as dt
LABEL = r'(?:發布日期|公佈日期|公布日期|發佈日期|發布時間|發佈時間|發稿日期|發文日期|公告日期|刊登日期|上版日期|上架日期|上稿日期|新聞日期|Publish(?:ed)? Date|(?<![新改修檢截止期])日期)'
DATE = r'((?:20\d\d|1[01]\d))\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})'
def _mk(y, m, d):
    y, m, d = int(y), int(m), int(d)
    if y < 1911: y += 1911
    try: x = dt.date(y, m, d)
    except ValueError: return None
    if y < 2000 or x > dt.date.today() + dt.timedelta(days=1): return None
    return x.isoformat()
def text_of(h):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S | re.I)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return re.sub(r'[\s\x00\ufeff]+', ' ', t)
def extract(url, h, title=''):
    t = text_of(h)
    m = re.search(LABEL + r'\s*[:：]?\s*' + DATE, t)
    if m: return _mk(*m.groups())
    m = re.search(r':::\s*(20\d\d)-(\d\d)-(\d\d)\s+\d\d:\d\d', t)
    if m: return _mk(*m.groups())
    m = re.search(r'(?:article:published_time|datePublished|og:published_time|pubdate|publish-date|parsely-pub-date)["\']?[^>]{0,80}?(?:content=|:)\s*["\']\s*(20\d\d)-(\d\d)-(\d\d)', h, re.I) \
        or re.search(r'content=["\'](20\d\d)-(\d\d)-(\d\d)[^"\']*["\'][^>]{0,80}(?:article:published_time|datePublished|og:published_time|pubdate|publish-date|parsely-pub-date)', h, re.I)
    if m: return _mk(*m.groups())
    m = re.search(r'cna\.com\.tw/news/\w+/(20\d{2})(\d{2})(\d{2})\d+', url) or re.search(r'/(20\d\d)[/-](\d\d)[/-](\d\d)/', url)
    if m: return _mk(*m.groups())
    # 標題後緊接日期（如移民署新聞網、南投觀光網）
    key = re.sub(r'\s+', ' ', title).strip()[:20]
    if len(key) >= 8:
        i = t.find(key)
        while i >= 0:
            m = re.match(r'.{0,%d}?\s(20\d\d)-(\d\d)-(\d\d)\s\d\d' % (len(title) + 30), t[i:i + len(title) + 60])
            if m: return _mk(*m.groups())
            i = t.find(key, i + 1)
    return None
