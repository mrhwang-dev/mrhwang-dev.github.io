# -*- coding: utf-8 -*-
"""한국어 페이지(hwangchiwoong/*.html)를 원본으로 en/, ja/ 페이지를 만든다.
한국어 페이지에는 언어 전환 링크와 hreflang만 채워 넣는다."""
import html, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from i18n import EN, JA

ROOT = os.path.join(HERE, '..', 'hwangchiwoong')
BASE = 'https://mrhwang-dev.github.io/hwangchiwoong/'
PAGES = ['index.html', 'hub.html', 'network.html', 'column.html']
LANGS = {'ko': ('한국어', ''), 'en': ('English', 'en/'), 'ja': ('日本語', 'ja/')}
HANGUL = re.compile('[가-힣]')

JA_FONTS = """@font-face{font-family:'PretendardJP';src:url(../fonts/PretendardJP-subset.woff2) format('woff2');font-weight:45 920;font-style:normal;font-display:swap}
@font-face{font-family:'ShipporiB1';src:url(../fonts/ShipporiMinchoB1-subset.woff2) format('woff2');font-weight:400;font-style:normal;font-display:swap}
"""

def rel(cur, target, page):
    """cur 언어의 페이지에서 target 언어의 같은 페이지로 가는 상대 경로"""
    up = '' if cur == 'ko' else '../'
    return up + LANGS[target][1] + page

def lang_links(cur, page):
    out = []
    for code, (label, _) in LANGS.items():
        cur_attr = ' aria-current="page"' if code == cur else ''
        out.append(f'<a href="{rel(cur, code, page)}" lang="{code}" hreflang="{code}"{cur_attr}>{label}</a>')
    return ' · '.join(out)

def alternates(page):
    tail = '' if page == 'index.html' else page
    links = [f'<link rel="alternate" hreflang="{c}" href="{BASE}{p}{tail}">' for c, (_, p) in LANGS.items()]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}{tail}">')
    return '\n'.join(links)

def prepare_source(s, page):
    """한국어 원본에 언어 전환 자리({{LANG}})와 hreflang 자리({{ALT}})를 한 번만 넣는다."""
    if '{{LANG}}' not in s and 'hreflang="en"' not in s:
        if '<span>한국어 · English · 日本語</span>' in s:
            s = s.replace('<span>한국어 · English · 日本語</span>', '<span class="langs">{{LANG}}</span>')
        else:
            s = re.sub(r'(<nav class="nav" aria-label="주요 메뉴"[^>]*>.*?)(</nav>)',
                       r'\1<span class="langs" style="font-weight: 500">{{LANG}}</span>\n\2', s, count=1, flags=re.S)
        s = s.replace('<meta name="robots" content="noindex">', '<meta name="robots" content="noindex">\n{{ALT}}', 1)
    return s


LOCALE = {'ko': 'ko_KR', 'en': 'en_US', 'ja': 'ja_JP'}
PERSON = {'ko': ('황치웅', '웹 서비스·콘텐츠 기획·운영'), 'en': ('Chiwoong Hwang', 'Web service and content planning and operations'), 'ja': ('ファン・チウン', 'ウェブサービス・コンテンツの企画・運営')}

def share_tags(s, code, page):
    tail = '' if page == 'index.html' else page
    url = BASE + LANGS[code][1] + tail
    title = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
    e = lambda x: html.escape(x, quote=True)
    tags = [f'<link rel="canonical" href="{url}">',
            '<link rel="icon" type="image/png" href="img/favicon.png">',
            '<link rel="apple-touch-icon" href="img/apple-touch-icon.png">',
            '<meta name="theme-color" content="#ffffff">',
            f'<meta property="og:type" content="{"website" if page == "index.html" else "article"}">',
            f'<meta property="og:site_name" content="{e(PERSON[code][0])}">',
            f'<meta property="og:title" content="{e(title)}">',
            f'<meta property="og:description" content="{e(desc)}">',
            f'<meta property="og:url" content="{url}">',
            f'<meta property="og:image" content="{BASE}img/og-{code}.png">',
            '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
            f'<meta property="og:locale" content="{LOCALE[code]}">',
            '<meta name="twitter:card" content="summary_large_image">']
    if page == 'index.html':
        import json
        ld = {"@context": "https://schema.org", "@type": "Person", "@id": BASE + "#person", "name": PERSON[code][0], "alternateName": [PERSON[c][0] for c in PERSON if c != code], "url": url,
              "jobTitle": PERSON[code][1], "email": "mailto:facti301@gmail.com",
              "alumniOf": {"@type": "CollegeOrUniversity", "name": "Chosun University"},
              "sameAs": ["https://www.linkedin.com/in/chiwoong-h-a4b833171/"]}
        tags.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')
    return s.replace('{{ALT}}', '{{ALT}}\n' + '\n'.join(tags), 1)

def translate(s, table):
    for ko in sorted(table, key=len, reverse=True):
        s = s.replace(ko, html.escape(table[ko], quote=True))
    return s

def build(page, src):
    out = {}
    for code in LANGS:
        s = src
        if code != 'ko':
            s = translate(s, EN if code == 'en' else JA)
        s = share_tags(s, code, page)
        if code != 'ko':
            s = s.replace('<html lang="ko">', f'<html lang="{code}">')
            s = re.sub(r'(src|href|srcset)="(img|fonts)/', r'\1="../\2/', s)
            s = s.replace('href="style.css"', 'href="../style.css"')
            s = s.replace('url(fonts/', 'url(../fonts/')
        if code == 'ja':
            s = s.replace('href="../style.css"', 'href="../style-ja.css"')
            s = s.replace('href="../fonts/PretendardVariable.woff2"', 'href="../fonts/PretendardJP-subset.woff2"').replace('href="../fonts/ChosunilboNM.woff2"', 'href="../fonts/ShipporiMinchoB1-subset.woff2"')
            s = s.replace("'Pretendard', sans-serif", "'PretendardJP', 'Pretendard', sans-serif")
            s = s.replace("'ChosunilboNM', serif", "'ShipporiB1', 'ChosunilboNM', serif")
            s = s.replace('第2回</a> · <a', '第2回</a>・<a')
            s = s.replace('word-break:keep-all;overflow-wrap:break-word', 'word-break:auto-phrase;line-break:strict;overflow-wrap:anywhere')

        s = re.sub(r'(<h[12][^>]*>[^<]*?)85만 건,', r'\1<span style="white-space:nowrap">85만 건,</span>', s)
        for credit in ('갈무리 = 황치웅', '사진 = 대학언론인 네트워크', 'Screenshot: Chiwoong Hwang', 'Photo: University Journalists Network', '画面キャプチャ＝ファン・チウン', '写真＝大学ジャーナリスト・ネットワーク'):
            s = s.replace(credit + '</figcaption>', f'<span style="white-space:nowrap">{credit}</span></figcaption>')
        s = s.replace('{{LANG}}', lang_links(code, page)).replace('{{ALT}}', alternates(page))
        if code != 'ko':
            left = [m for m in HANGUL.findall(re.sub(r'<script type="application/ld\+json">.*?</script>', '', re.sub(r'<a [^>]*lang="ko"[^>]*>한국어</a>', '', s), flags=re.S))]
            assert not left, (code, page, ''.join(left)[:80])
        assert not re.search(r'\[[^\]<]*(한 줄|문장|One line|sentence)[^\]<]*\]|［[^］<]*(一行|一文|二文)[^］<]*］', s), (code, page, '빈칸이 남아 있음')
        out[code] = s
    return out

SRC = os.path.join(HERE, 'ko')
os.makedirs(SRC, exist_ok=True)
for page in PAGES:
    sp = os.path.join(SRC, page)
    if not os.path.exists(sp):  # 처음 한 번: 공개 중인 한국어 페이지를 원본으로 옮긴다
        open(sp, 'w', encoding='utf-8').write(prepare_source(open(os.path.join(ROOT, page), encoding='utf-8').read(), page))
    src = open(sp, encoding='utf-8').read()
    for code, s in build(page, src).items():
        d = os.path.join(ROOT, LANGS[code][1])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, page), 'w', encoding='utf-8').write(s)
    print('built', page)

# 일본어용 스타일시트: 공통 스타일에 일본어 글꼴과 줄바꿈 규칙을 덧씌운다
css = open(os.path.join(ROOT, 'style.css'), encoding='utf-8').read()
ja = JA_FONTS.replace('url(../fonts/', 'url(fonts/') + css
ja = ja.replace(":root{--sans:'Pretendard',sans-serif;--serif:'ChosunilboNM',serif}", ":root{--sans:'PretendardJP','Pretendard',sans-serif;--serif:'ShipporiB1','ChosunilboNM',serif}")
ja = ja.replace("'Pretendard',sans-serif", "'PretendardJP','Pretendard',sans-serif").replace("'PretendardJP','PretendardJP'", "'PretendardJP'")
ja = ja.replace('word-break:keep-all;overflow-wrap:break-word', 'word-break:auto-phrase;line-break:strict;overflow-wrap:anywhere')
ja += '@media (min-width:821px){.hlead{font-size:2.6rem!important}}\n@media (max-width:820px){.mast{white-space:nowrap;font-size:clamp(2.25rem,11vw,3.4rem)!important}}\n'
open(os.path.join(ROOT, 'style-ja.css'), 'w', encoding='utf-8').write(ja)
print('built style-ja.css')
