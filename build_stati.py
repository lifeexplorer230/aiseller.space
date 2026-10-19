# -*- coding: utf-8 -*-
"""Сборка раздела статей /stati/ из Markdown-черновиков (17.10.2026).
Источник: ~/core/projects/aiseller-stati/chernoviki/NN-slug.md (front matter + Markdown).
Выход: stati/<slug>/index.html + stati/index.html + avtor/index.html + llms.txt;
блок «Статьи» на главной и /kurs/ (между метками <!-- stati:start/end -->). Служебные комментарии <!-- … --> не публикуются.
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
      <a href="/avtor/">Об авторе</a>
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
PERSON = {"@type": "Person", "@id": f"{SITE}/#roman", "name": "Роман Воробьёв", "url": f"{SITE}/avtor/",
          "jobTitle": "Селлер Ozon и Wildberries, внедряет ИИ для селлеров",
          "knowsAbout": ["Wildberries", "Ozon", "Яндекс Маркет", "нейросети для селлеров", "Seller API", "ИИ-агенты", "Telegram-боты"],
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
         "inLanguage": "ru", "url": url, "mainEntityOfPage": url, "datePublished": meta.get('data_publikacii', data), "dateModified": data,
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
    podpis = (f'<p class="st-meta"><a href="/avtor/">Роман Воробьёв</a> · проверено {dt.date.fromisoformat(data):%d.%m.%Y}</p>')
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

def avtor(statyi):
    url = f'{SITE}/avtor/'
    title = 'Роман Воробьёв — селлер WB и Ozon, ИИ для маркетплейсов'
    descr = 'Об авторе статей aiseller.space: восемь лет продаю на Wildberries и Ozon, собираю ИИ-агентов на Claude, подключаю ИИ к кабинету Ozon по API. Как проверяю факты.'
    graf = [{"@type": "ProfilePage", "@id": url, "url": url, "name": title, "inLanguage": "ru", "mainEntity": {"@id": f"{SITE}/#roman"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Об авторе", "item": url}]}, PERSON]
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graf}, ensure_ascii=False, indent=1)
    spisok_st = '\n'.join(f'<li><a href="/stati/{m["slug"]}/">{html.escape(m["title"])}</a></li>' for m in statyi)
    return (HEAD.format(title=html.escape(title), descr=html.escape(descr), url=url, ogtype='profile', jsonld=jsonld)
            + f'''<main class="st"><article class="st-in"><nav class="kroshki"><a href="/">Главная</a> / Об авторе</nav>
<h1>Роман Воробьёв</h1>
<p class="lead">Восемь лет продаю на Wildberries и Ozon, сейчас торгую ещё и на Яндекс Маркете. Собираю ИИ-агентов на Claude,
подключаю ИИ к кабинету Ozon через API и делаю Telegram-ботов для селлеров. Первым кабинетом, куда я поставил ИИ, был мой.</p>
<h2>Чем занимаюсь</h2>
<ul>
<li>Настраиваю ИИ, который работает с цифрами конкретного магазина: отчёты, цены, ответы на отзывы, споры с площадкой.</li>
<li>С февраля 2026 веду клуб селлеров <a href="/siistema/">«СИИстема»</a>: участники разбирают, как внедряют ИИ у себя, встречи каждую пятницу.</li>
<li>Веду вводный курс <a href="/kurs/">«ИИ для селлеров»</a>. Первый поток в сентябре 2026 прошли 9 человек.</li>
<li>Пишу в Telegram-канал <a href="https://t.me/FirstonOzon">«Системный гуманИИст»</a> про ИИ в работе селлера.</li>
</ul>
<h2>Как я пишу статьи</h2>
<ul>
<li><strong>Правила площадок — только из первоисточника.</strong> Справочный центр продавца Wildberries, документация Ozon и Яндекс Маркета. В каждой статье есть ссылки и дата проверки.</li>
<li><strong>Что болит у селлеров — из чатов.</strong> Я слежу примерно за двумя сотнями Telegram-чатов продавцов WB и Ozon и считаю, о чём спрашивают чаще всего. Данные обезличены.</li>
<li><strong>Не подтвердил — так и пишу.</strong> Без выдуманных кейсов и цифр. Советы из чатов подаю как опыт селлеров, а не как правило.</li>
<li><strong>Обновляю.</strong> Площадки меняют правила; когда меняется первоисточник, правлю статью и дату проверки.</li>
</ul>
<h2>Статьи</h2>
<ul>
{spisok_st}
</ul>
<h2>Связаться</h2>
<p>Проще всего — написать в Telegram: <a href="https://t.me/ozonsel">@ozonsel</a>. Отвечаю сам.</p>
</article></main>
''' + FOOT)

def llms(statyi):
    stroki = [f'- [{m["title"]}]({SITE}/stati/{m["slug"]}/): {m.get("description", "")}' for m in statyi]
    return (f'''# aiseller.space — ИИ для селлеров маркетплейсов

> Сайт Романа Воробьёва: восемь лет продаёт на Wildberries и Ozon, собирает ИИ-агентов на Claude, подключает ИИ к кабинету Ozon через API. Статьи для продавцов WB и Ozon — нейросети для карточек и инфографики, аналитика, API, штрафы, выплаты, ТН ВЭД.

Правила площадок в статьях даны по первоисточникам (справочный центр Wildberries, документация Ozon и Яндекс Маркета) со ссылками и датой проверки. Данные о частых вопросах — из ~200 Telegram-чатов селлеров, обезличенно. При цитировании указывайте ссылку на статью.

## Статьи

''' + '\n'.join(stroki) + f'''

## О сайте

- [Об авторе]({SITE}/avtor/): кто пишет и как проверяются факты
- [Все статьи]({SITE}/stati/): список разборов для селлеров
- [Курс «ИИ для селлеров»]({SITE}/kurs/): вводный курс для владельцев магазинов на маркетплейсах
- [Клуб «СИИстема»]({SITE}/siistema/): сообщество селлеров, которые внедряют ИИ
''')

def blok_na_stranice(path, statyi, n=6):
    """Блок «Статьи» между метками <!-- stati:start --> и <!-- stati:end --> на главной и странице курса."""
    s = open(path, encoding='utf-8').read()
    kartochki = '\n'.join(f'      <a class="card" href="/stati/{m["slug"]}/"><h3>{html.escape(m["title"])}</h3></a>' for m in statyi[:n])
    blok = (f'''<!-- stati:start -->
<section class="sec sec--line" id="stati">
  <div class="in">
    <div class="eyebrow">Статьи</div>
    <h2>Разборы для селлеров</h2>
    <p class="sub">Нейросети, автоматизация и правила площадок — простыми словами, с источниками.</p>
    <div class="cards">
{kartochki}
    </div>
    <p class="more"><a href="/stati/">Все статьи &rarr;</a></p>
  </div>
</section>
<!-- stati:end -->''')
    s2 = re.sub(r'<!-- stati:start -->.*?<!-- stati:end -->', lambda _: blok, s, flags=re.S)
    if s2 != s: open(path, 'w', encoding='utf-8').write(s2)

def main():
    statyi = []
    for p in sorted(glob.glob(os.path.join(SRC, '[0-9][0-9]-*.md'))):
        meta, body, ist = razobrat(p)
        d = os.path.join(ROOT, 'stati', meta['slug']); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(stranica(meta, body, ist))
        statyi.append(meta); print('  ', meta['slug'], '| FAQ:', len(faq(body)))
    open(os.path.join(ROOT, 'stati', 'index.html'), 'w', encoding='utf-8').write(spisok(statyi))
    os.makedirs(os.path.join(ROOT, 'avtor'), exist_ok=True)
    open(os.path.join(ROOT, 'avtor', 'index.html'), 'w', encoding='utf-8').write(avtor(statyi))
    open(os.path.join(ROOT, 'llms.txt'), 'w', encoding='utf-8').write(llms(statyi))
    for p in ('index.html', 'kurs/index.html'): blok_na_stranice(os.path.join(ROOT, p), statyi)
    print('собрано статей:', len(statyi))

if __name__ == '__main__':
    main()
