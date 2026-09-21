"""Aplica a otimização de SEO no site estático (títulos, descrições, canônicas com barra final,
Open Graph/Twitter completos, JSON-LD, H1 com palavra-chave, links internos e sitemap)."""
import html
import json
import pathlib
import re

ROOT = pathlib.Path("/run/media/luiz-ricardo/DATA1/projects/estudatta/estudatta-site")
BASE = "https://estudatta.com.br"
OG_IMG = f"{BASE}/assets/divulgacao/compartilhamento-1200x630.png"
TODAY = "2026-09-21"

PAGES = {
    "index.html": {
        "path": "/",
        "title": "Estudatta | App de estudos: plano diário, cronômetro e revisões",
        "description": "App de estudos grátis: plano diário com meta de minutos, cronômetro, revisões espaçadas, questões e simulados. Atrasou? O tempo pendente vira recuperação.",
        "keywords": "app de estudos, app para organizar estudos, planner de estudos, plano de estudos, cronograma de estudos, cronômetro de estudos, controle de horas de estudo, revisão espaçada, aplicativo de estudos gratuito",
        "og_title": "Estudatta: o app de estudos que diz o que fazer hoje",
        "h1": ('<h1 class="display"><span>Saiba o que fazer hoje.</span><span>Retome quando atrasar.</span></h1>',
               '<h1 class="display"><span>O app de estudos que diz o que fazer hoje.</span><span>E como retomar quando atrasar.</span></h1>'),
        "breadcrumb": None,
    },
    "idiomas/index.html": {
        "path": "/idiomas/",
        "title": "App para estudar inglês e outros idiomas todo dia | Estudatta",
        "description": "Organize o estudo de inglês, espanhol, japonês ou mais de 90 idiomas: meta diária, aulas, podcasts e leitura no mesmo plano, com revisões e conquistas.",
        "keywords": "app para estudar inglês, app para estudar idiomas, plano de estudos de inglês, estudar inglês todo dia, rotina de estudo de inglês, app de estudo de espanhol, app de estudo de japonês, controle de tempo de estudo de idiomas",
        "og_title": "App para estudar inglês e outros idiomas todo dia",
        "h1": ('<h1 class="display"><span>60 minutos por dia.</span><span>Mesmo depois de ontem.</span></h1>',
               '<h1 class="display"><span>Estude idiomas 60 minutos por dia.</span><span>Mesmo depois de ontem.</span></h1>'),
        "breadcrumb": "Idiomas",
    },
    "concursos/index.html": {
        "path": "/concursos/",
        "title": "Plano de estudos para concurso: edital e revisões | Estudatta",
        "description": "Monte seu plano de estudos para concurso: importe o edital, organize matérias e tópicos, revise no prazo certo e registre questões e simulados. Comece grátis.",
        "keywords": "plano de estudos para concurso, app de estudos para concurso, cronograma de estudos para concurso, organizar edital, ciclo de estudos concurso, revisão espaçada concurso, controle de questões e simulados, edital verticalizado",
        "og_title": "Plano de estudos para concurso: edital longo, plano do dia curto",
        "h1": ('<h1 class="display"><span>Edital longo.</span><span>Plano do dia curto.</span></h1>',
               '<h1 class="display"><span>Plano de estudos para concurso:</span><span>edital longo, plano do dia curto.</span></h1>'),
        "breadcrumb": "Concursos",
    },
    "vestibular-enem/index.html": {
        "path": "/vestibular-enem/",
        "title": "Cronograma de estudos para ENEM e vestibular | Estudatta",
        "description": "Cronograma de estudos para ENEM e vestibular: áreas e matérias como tópicos, meta diária, revisões automáticas, questões e simulados por área. Comece grátis.",
        "keywords": "cronograma de estudos enem, app de estudos para vestibular, plano de estudos enem, app para estudar para o enem, organizar estudos vestibular, simulado enem acompanhamento, rotina de estudos vestibular, planner de estudos enem",
        "og_title": "Cronograma de estudos para ENEM e vestibular",
        "h1": None,
        "breadcrumb": "Vestibular e ENEM",
    },
    "planos/index.html": {
        "path": "/planos/",
        "title": "Planos e preços: app de estudos grátis e planos pagos | Estudatta",
        "description": "Compare os planos do Estudatta: Gratuito para sempre, Essencial por R$ 9,90/mês e Completo por R$ 19,90/mês. Sem cartão para começar e cancelamento livre.",
        "keywords": "estudatta preço, app de estudos grátis, planner de estudos gratuito, assinatura app de estudos, plano essencial estudatta, plano completo estudatta",
        "og_title": "Planos e preços do Estudatta: comece grátis",
        "h1": ('<h1 class="display">Comece grátis. Amplie quando precisar.</h1>',
               '<h1 class="display">Planos e preços: comece grátis, amplie quando precisar.</h1>'),
        "breadcrumb": "Planos",
    },
    "faq/index.html": {
        "path": "/faq/",
        "title": "Perguntas frequentes sobre o app de estudos | Estudatta",
        "description": "Tire dúvidas sobre o Estudatta: como funciona o plano diário, o que acontece quando você não estuda, offline, revisões, simulados, IA, dados e assinatura.",
        "keywords": "estudatta perguntas frequentes, como funciona o estudatta, app de estudos offline, app de estudos dúvidas, cancelar assinatura estudatta",
        "og_title": "Perguntas frequentes sobre o Estudatta",
        "h1": ('<h1 class="display">O que o app faz — e o que não faz.</h1>',
               '<h1 class="display">Perguntas frequentes: o que o app de estudos faz — e o que não faz.</h1>'),
        "breadcrumb": "Perguntas frequentes",
    },
    "contato/index.html": {
        "path": "/contato/",
        "title": "Contato: fale com a equipe do Estudatta",
        "description": "Fale com a equipe do Estudatta: dúvidas sobre o app de estudos, planos, pagamento ou seus dados. Respondemos por e-mail.",
        "keywords": "contato estudatta, suporte estudatta, falar com estudatta",
        "og_title": "Contato — Estudatta",
        "h1": None,
        "breadcrumb": "Contato",
    },
    "privacidade/index.html": {
        "path": "/privacidade/",
        "title": "Política de privacidade | Estudatta",
        "description": "Política de privacidade do Estudatta: quais dados o app de estudos coleta, como usa, com quem compartilha, cookies, IA, retenção e seus direitos pela LGPD.",
        "keywords": "política de privacidade estudatta, lgpd estudatta, dados app de estudos",
        "og_title": "Política de privacidade — Estudatta",
        "h1": None,
        "breadcrumb": "Privacidade",
    },
    "termos/index.html": {
        "path": "/termos/",
        "title": "Termos de uso | Estudatta",
        "description": "Termos de uso do Estudatta: conta, planos e cobrança, conteúdo enviado, uso da IA, notificações, disponibilidade e cancelamento.",
        "keywords": "termos de uso estudatta, assinatura estudatta, cancelamento estudatta",
        "og_title": "Termos de uso — Estudatta",
        "h1": None,
        "breadcrumb": "Termos de uso",
    },
}

CLEAN_PATHS = ["idiomas", "concursos", "vestibular-enem", "planos", "faq", "contato", "privacidade", "termos"]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def faq_items(body: str) -> list[dict]:
    out = []
    for q, a in re.findall(r"<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>", body, flags=re.S):
        strip = lambda t: html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
        out.append({"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}})
    return out


def jsonld(obj) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


ORG = {
    "@type": "Organization",
    "@id": f"{BASE}/#org",
    "name": "Estudatta",
    "url": f"{BASE}/",
    "logo": {"@type": "ImageObject", "url": f"{BASE}/assets/marca/logo-escuro-512.png", "width": 512, "height": 512},
    "email": "contato@estudatta.com.br",
    "contactPoint": {"@type": "ContactPoint", "email": "contato@estudatta.com.br", "contactType": "customer support", "availableLanguage": "Portuguese"},
}
WEBSITE = {"@type": "WebSite", "@id": f"{BASE}/#site", "url": f"{BASE}/", "name": "Estudatta", "inLanguage": "pt-BR", "publisher": {"@id": f"{BASE}/#org"}}
APP = {
    "@type": "SoftwareApplication",
    "@id": f"{BASE}/#app",
    "name": "Estudatta",
    "url": "https://app.estudatta.com.br/",
    "applicationCategory": "EducationalApplication",
    "operatingSystem": "Web, Android, iOS (PWA)",
    "inLanguage": "pt-BR",
    "description": "App para organizar os estudos: plano diário com meta de minutos, cronômetro, registro de questões e simulados, revisões espaçadas e recuperação do tempo pendente.",
    "featureList": [
        "Plano diário com meta de minutos e dias da semana",
        "Cronômetro e registro manual, com funcionamento offline",
        "Saldo e recuperação do tempo pendente",
        "Revisões espaçadas automáticas (1, 7 e 30 dias)",
        "Questões, taxa de acerto por matéria e simulados",
        "Importação do edital em texto, CSV ou PDF",
        "Conquistas, níveis e desafios semanais",
    ],
    "screenshot": OG_IMG,
    "publisher": {"@id": f"{BASE}/#org"},
    "offers": [
        {"@type": "Offer", "name": "Gratuito", "price": "0", "priceCurrency": "BRL", "url": "https://app.estudatta.com.br/cadastro"},
        {"@type": "Offer", "name": "Essencial", "price": "9.90", "priceCurrency": "BRL", "url": f"{BASE}/planos/", "priceSpecification": {"@type": "UnitPriceSpecification", "price": "9.90", "priceCurrency": "BRL", "billingIncrement": 1, "unitCode": "MON"}},
        {"@type": "Offer", "name": "Completo", "price": "19.90", "priceCurrency": "BRL", "url": f"{BASE}/planos/", "priceSpecification": {"@type": "UnitPriceSpecification", "price": "19.90", "priceCurrency": "BRL", "billingIncrement": 1, "unitCode": "MON"}},
    ],
}


def build_head(rel: str, cfg: dict, body: str) -> str:
    url = BASE + cfg["path"]
    lines = [
        f"  <title>{esc(cfg['title'])}</title>",
        f'  <meta name="description" content="{esc(cfg["description"])}">',
        f'  <meta name="keywords" content="{esc(cfg["keywords"])}">',
        f'  <link rel="canonical" href="{url}">',
        '  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">',
        '  <meta name="theme-color" content="#f3f5fe">',
        '  <meta name="author" content="Estudatta">',
        '  <meta property="og:type" content="website">',
        '  <meta property="og:locale" content="pt_BR">',
        '  <meta property="og:site_name" content="Estudatta">',
        f'  <meta property="og:title" content="{esc(cfg["og_title"])}">',
        f'  <meta property="og:description" content="{esc(cfg["description"])}">',
        f'  <meta property="og:url" content="{url}">',
        f'  <meta property="og:image" content="{OG_IMG}">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        '  <meta property="og:image:alt" content="Estudatta: app de estudos com plano diário, cronômetro e o mascote Tatá">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{esc(cfg["og_title"])}">',
        f'  <meta name="twitter:description" content="{esc(cfg["description"])}">',
        f'  <meta name="twitter:image" content="{OG_IMG}">',
    ]
    graph = []
    if rel == "index.html":
        graph += [ORG, WEBSITE, APP]
    else:
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{BASE}/"},
                {"@type": "ListItem", "position": 2, "name": cfg["breadcrumb"], "item": url},
            ],
        })
        graph.append({"@type": "WebPage", "@id": url, "url": url, "name": cfg["title"], "description": cfg["description"], "inLanguage": "pt-BR", "isPartOf": {"@id": f"{BASE}/#site"}, "about": {"@id": f"{BASE}/#app"}})
    items = faq_items(body)
    if items:
        graph.append({"@type": "FAQPage", "mainEntity": items})
    lines.append("  " + jsonld({"@context": "https://schema.org", "@graph": graph}))
    return "\n".join(lines)


HEAD_KEEP = re.compile(r'^\s*(<meta charset|<meta name="viewport"|<link rel="icon"|<link rel="apple-touch-icon"|<link rel="preload"|<link rel="stylesheet"|<script src=)')


def rewrite(rel: str, cfg: dict) -> None:
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    head_m = re.search(r"<head>(.*?)</head>", s, flags=re.S)
    old_head = head_m.group(1)
    keep = [ln for ln in old_head.splitlines() if HEAD_KEEP.match(ln)]
    # ordem: charset, viewport, SEO, ícones/preload/css/js
    first = [ln for ln in keep if "charset" in ln or "viewport" in ln]
    rest = [ln for ln in keep if ln not in first]
    body = s[head_m.end():]
    ga = ['  <!-- Google tag (gtag.js) -->', '  <script async src="https://www.googletagmanager.com/gtag/js?id=G-8XFNHTHEX7"></script>', '  <script src="/assets/js/analytics.js"></script>']
    new_head = "\n" + "\n".join(first) + "\n" + build_head(rel, cfg, body) + "\n" + "\n".join(rest) + "\n" + "\n".join(ga) + "\n  <link rel=\"preconnect\" href=\"https://app.estudatta.com.br\" crossorigin>\n"
    s = s[: head_m.start()] + "<head>" + new_head + "</head>" + body
    if cfg["h1"]:
        old, new = cfg["h1"]
        if old in s:
            s = s.replace(old, new, 1)
    # links internos com barra final (GitHub Pages redireciona /x para /x/)
    for c in CLEAN_PATHS:
        s = re.sub(rf'href="/{c}"', f'href="/{c}/"', s)
    p.write_text(s, encoding="utf-8")


if __name__ == "__main__":
    for rel, cfg in PAGES.items():
        if (ROOT / rel).exists():
            rewrite(rel, cfg)

    # --- 404: só links e canônica ausente (noindex já está) ---
    p = ROOT / "404.html"
    s = p.read_text(encoding="utf-8")
    for c in CLEAN_PATHS:
        s = re.sub(rf'href="/{c}"', f'href="/{c}/"', s)
    if "gtag/js" not in s:
        s = s.replace("</head>", '  <script async src="https://www.googletagmanager.com/gtag/js?id=G-8XFNHTHEX7"></script>\n  <script src="/assets/js/analytics.js"></script>\n</head>', 1)
    p.write_text(s, encoding="utf-8")

    # --- /ingles → /idiomas/ (GitHub Pages não aplica o redirect do nginx) ---
    (ROOT / "ingles").mkdir(exist_ok=True)
    (ROOT / "ingles/index.html").write_text(
        """<!doctype html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <title>Idiomas · Estudatta</title>
      <meta name="robots" content="noindex, follow">
      <link rel="canonical" href="https://estudatta.com.br/idiomas/">
      <meta http-equiv="refresh" content="0; url=/idiomas/">
      <script>location.replace("/idiomas/" + location.hash);</script>
    </head>
    <body>
      <p>A página de inglês agora é a de idiomas: <a href="/idiomas/">estudatta.com.br/idiomas</a>.</p>
    </body>
    </html>
    """,
        encoding="utf-8",
    )

    # --- sitemap com lastmod e prioridade ---
    order = ["index.html", "concursos/index.html", "vestibular-enem/index.html", "idiomas/index.html", "planos/index.html", "faq/index.html", "contato/index.html", "privacidade/index.html", "termos/index.html"]
    prio = {"/": "1.0", "/concursos/": "0.9", "/vestibular-enem/": "0.9", "/idiomas/": "0.9", "/planos/": "0.8", "/faq/": "0.6", "/contato/": "0.3", "/privacidade/": "0.2", "/termos/": "0.2"}
    rows = []
    for rel in order:
        if not (ROOT / rel).exists():
            continue
        path = PAGES[rel]["path"]
        freq = "monthly" if prio[path] >= "0.6" else "yearly"
        rows.append(f"  <url><loc>{BASE}{path}</loc><lastmod>{TODAY}</lastmod><changefreq>{freq}</changefreq><priority>{prio[path]}</priority></url>")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")
    print("ok")
