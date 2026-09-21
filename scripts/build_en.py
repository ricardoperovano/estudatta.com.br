"""Gera a versão em inglês do site em /en/ a partir das páginas em português + mapa de tradução,
acrescenta hreflang nas duas versões, seletor de idioma no menu e sitemap com alternates."""
import html
import json
import re
import sys
import pathlib

SCRATCH = pathlib.Path(__file__).parent
sys.path.insert(0, str(SCRATCH))
import en_map1, en_map2, en_map3  # noqa: E402
import seo  # noqa: E402  (reaproveita ORG/WEBSITE/APP/faq_items/jsonld)

T = {}
for m in (en_map1, en_map2, en_map3):
    T.update(m.T)

ROOT = seo.ROOT
BASE = seo.BASE
# slug pt -> slug en
SLUG = {"": "", "idiomas": "languages", "concursos": "civil-service-exams", "vestibular-enem": "college-entrance-exams",
        "planos": "pricing", "faq": "faq", "contato": "contact", "privacidade": "privacy", "termos": "terms"}
CRUMB = {"idiomas": "Languages", "concursos": "Civil service exams", "vestibular-enem": "College entrance exams", "planos": "Plans",
         "faq": "FAQ", "contato": "Contact", "privacidade": "Privacy", "termos": "Terms of use"}

ATTRS = ("aria-label", "placeholder", "alt", "title", "content", "data-month", "data-year", "data-per")
missing = set()


def tr(t: str) -> str:
    s = t.strip()
    if not s or s in ("Estudatta", "Estudatta — início"):
        return t
    if s in T:
        return t.replace(s, T[s])
    if not re.fullmatch(r"[\d\W]+", s):
        missing.add(s)
    return t


def translate_html(s: str) -> str:
    # protege JSON-LD e SVGs (o JSON-LD é regenerado depois)
    keep = []

    def stash(m):
        keep.append(m.group(0))
        return f"\x00{len(keep) - 1}\x00"

    s = re.sub(r'<script type="application/ld\+json">.*?</script>', stash, s, flags=re.S)
    s = re.sub(r"<svg.*?</svg>", stash, s, flags=re.S)
    s = re.sub(r">([^<>]+)<", lambda m: ">" + tr(m.group(1)) + "<", s)
    s = re.sub(r'\b(' + "|".join(ATTRS) + r')="([^"]*)"', lambda m: f'{m.group(1)}="{tr(m.group(2))}"', s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)
    return s


def en_path(pt_slug: str) -> str:
    return "/en/" + (SLUG[pt_slug] + "/" if pt_slug else "")


def relink(s: str) -> str:
    # links internos: /x/ -> /en/<slug>/ ; raiz -> /en/
    for pt, en in SLUG.items():
        if pt:
            s = s.replace(f'href="/{pt}/"', f'href="/en/{en}/"').replace(f'href="/{pt}/#', f'href="/en/{en}/#')
    s = s.replace('href="/" aria-label=', 'href="/en/" aria-label=')
    return s


def hreflang(pt_slug: str) -> str:
    pt_url = BASE + ("/" + pt_slug + "/" if pt_slug else "/")
    en_url = BASE + en_path(pt_slug)
    return (f'  <link rel="alternate" hreflang="pt-BR" href="{pt_url}">\n'
            f'  <link rel="alternate" hreflang="en" href="{en_url}">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{pt_url}">')


def switcher(pt_slug: str, current: str) -> str:
    pt_url = "/" + pt_slug + "/" if pt_slug else "/"
    en_url = en_path(pt_slug)
    if current == "pt":
        return f'  <a class="lang" href="{en_url}" hreflang="en" lang="en" data-lang-switch="en" aria-label="Read in English">EN</a>\n'
    return f'  <a class="lang" href="{pt_url}" hreflang="pt-BR" lang="pt-BR" data-lang-switch="pt" aria-label="Ler em português">PT</a>\n'


APP_EN = dict(seo.APP)
APP_EN["description"] = "A study planner app: a daily plan with a minutes goal, timer, question and mock exam logging, spaced reviews and catch-up of owed time."
APP_EN["featureList"] = [
    "Daily plan with a minutes goal and days of the week",
    "Timer and manual logging, works offline",
    "Balance and catch-up of owed time",
    "Automatic spaced reviews (1, 7 and 30 days)",
    "Questions, accuracy per subject and mock exams",
    "Syllabus import from text, CSV or PDF",
    "Achievements, levels and weekly challenges",
]
APP_EN["offers"] = json.loads(json.dumps(seo.APP["offers"]).replace("/planos/", "/en/pricing/"))
APP_EN["offers"][0]["name"] = "Free"; APP_EN["offers"][1]["name"] = "Essential"; APP_EN["offers"][2]["name"] = "Complete"


def build_jsonld(pt_slug: str, title: str, desc: str, body: str) -> str:
    url = BASE + en_path(pt_slug)
    graph = []
    if not pt_slug:
        graph += [seo.ORG, dict(seo.WEBSITE, inLanguage="en"), APP_EN]
    else:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/en/"},
            {"@type": "ListItem", "position": 2, "name": CRUMB[pt_slug], "item": url}]})
        graph.append({"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "en",
                      "isPartOf": {"@id": f"{BASE}/#site"}, "about": {"@id": f"{BASE}/#app"}})
    items = seo.faq_items(body)
    if items:
        graph.append({"@type": "FAQPage", "mainEntity": items})
    return seo.jsonld({"@context": "https://schema.org", "@graph": graph})


def build_page(rel: str):
    pt_slug = rel.replace("/index.html", "") if rel != "index.html" else ""
    src = (ROOT / rel).read_text(encoding="utf-8")
    # a fonte em português pode já ter hreflang e o seletor EN (rodadas anteriores): remove antes
    src = re.sub(r'  <link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', "", src)
    src = re.sub(r'  <a class="lang" [^\n]*data-lang-switch="en"[^\n]*\n', "", src)
    s = translate_html(src)
    s = relink(s)
    s = s.replace('<html lang="pt-BR">', '<html lang="en">')
    s = s.replace('<meta property="og:locale" content="pt_BR">', '<meta property="og:locale" content="en_US">')
    pt_url = BASE + ("/" + pt_slug + "/" if pt_slug else "/")
    en_url = BASE + en_path(pt_slug)
    s = s.replace(f'<link rel="canonical" href="{pt_url}">', f'<link rel="canonical" href="{en_url}">\n{hreflang(pt_slug)}')
    s = s.replace(f'<meta property="og:url" content="{pt_url}">', f'<meta property="og:url" content="{en_url}">')
    # JSON-LD em inglês
    title = re.search(r"<title>(.*?)</title>", s).group(1)
    desc = re.search(r'name="description" content="(.*?)"', s).group(1)
    body = s[s.index("</head>"):]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: build_jsonld(pt_slug, html.unescape(title), html.unescape(desc), body), s, count=1, flags=re.S)
    # seletor de idioma no menu (antes de "Criar conta")
    s = s.replace('  <a class="btn btn-primary" href="https://app.estudatta.com.br/cadastro">Create account</a>',
                  switcher(pt_slug, "en") + '  <a class="btn btn-primary" href="https://app.estudatta.com.br/cadastro">Create account</a>')
    s = s.replace('data-waitlist="site-', 'data-waitlist="site-en-')
    out = ROOT / "en" / (SLUG[pt_slug] + "/index.html" if pt_slug else "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding="utf-8")


def patch_pt_page(rel: str):
    pt_slug = rel.replace("/index.html", "") if rel != "index.html" else ""
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    pt_url = BASE + ("/" + pt_slug + "/" if pt_slug else "/")
    if 'hreflang="en"' not in s:
        s = s.replace(f'<link rel="canonical" href="{pt_url}">', f'<link rel="canonical" href="{pt_url}">\n{hreflang(pt_slug)}')
    if "data-lang-switch" not in s:
        s = s.replace('  <a class="btn btn-primary" href="https://app.estudatta.com.br/cadastro">Criar conta</a>',
                      switcher(pt_slug, "pt") + '  <a class="btn btn-primary" href="https://app.estudatta.com.br/cadastro">Criar conta</a>')
    if "/assets/js/lang.js" not in s:
        s = s.replace('  <script src="/assets/js/config.js"></script>', '  <script src="/assets/js/lang.js"></script>\n  <script src="/assets/js/config.js"></script>')
    p.write_text(s, encoding="utf-8")


PAGES = ["index.html", "idiomas/index.html", "concursos/index.html", "vestibular-enem/index.html", "planos/index.html",
         "faq/index.html", "contato/index.html", "privacidade/index.html", "termos/index.html"]
for rel in PAGES:
    build_page(rel)
    patch_pt_page(rel)

# 404: uma só página (GitHub Pages) — texto em inglês vem por JS quando o caminho começa com /en/
p = ROOT / "404.html"
s = p.read_text(encoding="utf-8")
if "/assets/js/lang.js" not in s:
    s = s.replace('  <script src="/assets/js/config.js"></script>', '  <script src="/assets/js/lang.js"></script>\n  <script src="/assets/js/config.js"></script>')
if "data-404-en" not in s:
    m = re.search(r'  <section class="notfound">.*?</section>\n', s, flags=re.S)
    pt_sec = m.group(0).replace('<section class="notfound">', '<section class="notfound" data-404-pt>')
    en_sec = relink(translate_html(m.group(0))).replace('<section class="notfound">', '<section class="notfound" lang="en" data-404-en hidden>')
    en_sec = en_sec.replace('href="/">', 'href="/en/">')
    s = s.replace(m.group(0), pt_sec + en_sec)
p.write_text(s, encoding="utf-8")

# sitemap com alternates
order = ["index.html", "concursos/index.html", "vestibular-enem/index.html", "idiomas/index.html", "planos/index.html", "faq/index.html", "contato/index.html", "privacidade/index.html", "termos/index.html"]
prio = {"": "1.0", "concursos": "0.9", "vestibular-enem": "0.9", "idiomas": "0.9", "planos": "0.8", "faq": "0.6", "contato": "0.3", "privacidade": "0.2", "termos": "0.2"}
rows = []
for rel in order:
    slug = rel.replace("/index.html", "") if rel != "index.html" else ""
    pt_url = BASE + ("/" + slug + "/" if slug else "/")
    en_url = BASE + en_path(slug)
    freq = "monthly" if prio[slug] >= "0.6" else "yearly"
    alts = (f'<xhtml:link rel="alternate" hreflang="pt-BR" href="{pt_url}"/><xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>'
            f'<xhtml:link rel="alternate" hreflang="x-default" href="{pt_url}"/>')
    for loc, pr in ((pt_url, prio[slug]), (en_url, str(round(float(prio[slug]) * 0.8, 1)))):
        rows.append(f"  <url><loc>{loc}</loc><lastmod>{seo.TODAY}</lastmod><changefreq>{freq}</changefreq><priority>{pr}</priority>{alts}</url>")
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")

print("missing:", len(missing))
for m in sorted(missing):
    print("  ", repr(m)[:140])
