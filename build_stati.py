# -*- coding: utf-8 -*-
"""Сборка раздела статей /stati/ из Markdown-черновиков (17.10.2026).
Источник: ~/core/projects/aiseller-stati/chernoviki/NN-slug.md (front matter + Markdown).
Выход: stati/<slug>/index.html + stati/index.html. Служебные комментарии <!-- … --> не публикуются.
Разметка: canonical, Open Graph, JSON-LD Article + BreadcrumbList + FAQPage (если есть «Частые вопросы»).
Запуск: python3 build_stati.py [папка_с_черновиками]"""
import os, re, sys, json, html, glob, datetime as dt
import markdown

SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/redline/core/projects/aiseller-stati/chernoviki'
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://www.aiseller.space'
SEGODNYA = dt.date.today().isoformat()

def razobrat(path):
    s = open(path, encoding='utf-8').read()
    _, fm, body = s.split('---', 2)
    meta = {}
    for line in fm.strip().splitlines():
        m = re.match(r'^([a-z_]+):\s*"?(.*?)"?\s*$', line)
        if m and m.group(2): meta[m.group(1)] = m.group(2)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S).strip()
    istochniki = re.findall(r'^\s*-\s*"?(https?://\S+?)"?\s*$', fm, re.M)
    return meta, body, istochniki

def faq(body):
    m = re.search(r'^## Частые вопросы\s*$(.*?)(?=^## |\Z)', body, re.M | re.S)
    if not m: return []
    pary = re.findall(r'\*\*(.+?\?)\*\*\s*\n(.+?)(?=\n\s*\n|\Z)', m.group(1), re.S)
    return [(q.strip(), re.sub(r'\s+', ' ', re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', a)).strip()) for q, a in pary]

HEAD = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{descr}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{descr}">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="ИИ для селлеров маркетплейсов">
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/stati/stati.css">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<div class="grid-bg"></div>
<div class="layer">
<header class="hdr">
  <div class="hdr-in">
    <a href="/" class="logo"><span class="dot"></span><span><span class="hl">ai</span>seller</span></a>
    <nav class="nav">
      <div class="only-wide"><div class="nav-links">
        <a href="/stati/">Статьи</a><a href="/kurs/">Курс</a><a href="/siistema/">Сообщество</a>
      </div></div>
      <a href="/#napisat" class="btn btn-sm">Написать</a>
    </nav>
  </div>
</header>
'''
FOOT = '''<footer class="ftr">
  <div class="ftr-in">
    <div class="ftr-links">
      <a href="/stati/">Статьи</a>
      <a href="/kurs/">Курс «ИИ для селлеров»</a>
      <a href="/siistema/">Сообщество «СИИстема»</a>
      <a href="https://t.me/FirstonOzon" target="_blank" rel="noopener">Канал «Системный гуманИИст»</a>
      <a href="https://t.me/sellersmafia" target="_blank" rel="noopener">Мафклуб предпринимателей</a>
    </div>
    <small>Роман Воробьёв · ИИ для селлеров маркетплейсов</small>
  </div>
</footer>
</div>
</body>
</html>
'''
PERSON = {"@type": "Person", "@id": f"{SITE}/#roman", "name": "Роман Воробьёв", "url": f"{SITE}/",
          "jobTitle": "Селлер Ozon и Wildberries, внедряет ИИ для селлеров",
          "sameAs": ["https://t.me/FirstonOzon", "https://t.me/sellersmafia"]}

def stranica(meta, body, istochniki):
    slug = meta['slug']; url = f'{SITE}/stati/{slug}/'
    title = meta['title']; descr = meta.get('description', '')
    md = markdown.Markdown(extensions=['tables', 'sane_lists'])
    tel = md.convert(body)
    tel = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', tel)
    data = meta.get('data_proverki', SEGODNYA)
    graf = [
        {"@type": "Article", "@id": url + "#article", "headline": title, "description": descr,
         "inLanguage": "ru", "url": url, "mainEntityOfPage": url, "datePublished": SEGODNYA, "dateModified": data,
         "author": {"@id": f"{SITE}/#roman"}, "publisher": {"@id": f"{SITE}/#roman"},
         "keywords": meta.get('glavnyj_zapros', ''), **({"citation": istochniki[:20]} if istochniki else {})},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Статьи", "item": f"{SITE}/stati/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]},
        PERSON]
    f = faq(body)
    if f:
        graf.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in f]})
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graf}, ensure_ascii=False, indent=1)
    shapka = HEAD.format(title=html.escape(title), descr=html.escape(descr), url=url, ogtype='article', jsonld=jsonld)
    krohi = f'<nav class="kroshki"><a href="/">Главная</a> / <a href="/stati/">Статьи</a></nav>'
    podpis = (f'<p class="st-meta">Роман Воробьёв · проверено {dt.date.fromisoformat(data):%d.%m.%Y}</p>')
    return shapka + f'<main class="st"><article class="st-in">{krohi}{podpis}{tel}</article></main>\n' + FOOT

def spisok(statyi):
    url = f'{SITE}/stati/'
    title = 'Статьи для селлеров WB и Ozon: ИИ, автоматизация, правила'
    descr = 'Разборы для продавцов Wildberries и Ozon: нейросети для карточек и инфографики, аналитика, API, штрафы, выплаты, ТН ВЭД. С источниками и данными из чатов селлеров.'
    graf = [{"@type": "CollectionPage", "@id": url, "url": url, "name": title, "inLanguage": "ru",
             "hasPart": [{"@type": "Article", "headline": m['title'], "url": f"{SITE}/stati/{m['slug']}/"} for m in statyi]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Статьи", "item": url}]}, PERSON]
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graf}, ensure_ascii=False, indent=1)
    kartochki = '\n'.join(
        f'<a class="st-card" href="/stati/{m["slug"]}/"><h2>{html.escape(m["title"])}</h2><p>{html.escape(m.get("description",""))}</p></a>'
        for m in statyi)
    return (HEAD.format(title=html.escape(title), descr=html.escape(descr), url=url, ogtype='website', jsonld=jsonld)
            + f'<main class="st"><div class="st-in"><h1>Статьи для селлеров</h1>'
              f'<p class="lead">Нейросети, автоматизация и правила площадок — простыми словами, с источниками '
              f'и тем, что реально спрашивают в чатах селлеров.</p><div class="st-list">{kartochki}</div></div></main>\n' + FOOT)

def main():
    statyi = []
    for p in sorted(glob.glob(os.path.join(SRC, '[0-9][0-9]-*.md'))):
        meta, body, ist = razobrat(p)
        d = os.path.join(ROOT, 'stati', meta['slug']); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(stranica(meta, body, ist))
        statyi.append(meta); print('  ', meta['slug'], '| FAQ:', len(faq(body)))
    open(os.path.join(ROOT, 'stati', 'index.html'), 'w', encoding='utf-8').write(spisok(statyi))
    print('собрано статей:', len(statyi))

if __name__ == '__main__':
    main()
