#!/usr/bin/env python3
"""Verificações de SEO do site estático. Roda sem dependências e sem rede:

    python3 scripts/test_seo.py            # confere os arquivos do repositório
    python3 scripts/test_seo.py --prod     # confere também o site publicado (precisa de rede)

Cada falha aparece como uma linha "FALHA:". O processo sai com código 1 se houver alguma.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://estudatta.com.br"
APP = "https://app.estudatta.com.br"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}

falhas: list[str] = []


def checa(cond: bool, msg: str) -> bool:
    if not cond:
        falhas.append(msg)
    return cond


def rel_de_url(url: str) -> str:
    """URL pública -> caminho do arquivo no repositório."""
    return (url[len(BASE):].strip("/") + "/index.html").lstrip("/") if url != BASE + "/" else "index.html"


def um(pat: str, s: str) -> str | None:
    m = re.search(pat, s, re.I | re.S)
    return m.group(1).strip() if m else None


# ---------------------------------------------------------------- sitemap e robots
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
raiz = ET.fromstring(sitemap)
urls = raiz.findall("s:url", NS)
checa(bool(urls), "sitemap.xml sem URLs")
locs = [u.find("s:loc", NS).text for u in urls]
checa(len(locs) == len(set(locs)), "sitemap.xml com URLs repetidas")
for u in urls:
    loc = u.find("s:loc", NS).text
    checa(loc.startswith(BASE + "/"), f"sitemap: URL não absoluta em https: {loc}")
    checa(loc.endswith("/"), f"sitemap: URL sem barra final: {loc}")
    checa((ROOT / rel_de_url(loc)).exists(), f"sitemap: {loc} não tem arquivo no repositório")
    lm = u.find("s:lastmod", NS)
    checa(lm is not None and re.fullmatch(r"\d{4}-\d{2}-\d{2}", lm.text or ""), f"sitemap: lastmod inválido em {loc}")
    alts = {a.get("hreflang"): a.get("href") for a in u.findall("x:link", NS)}
    checa(set(alts) == {"pt-BR", "en", "x-default"}, f"sitemap: alternates incompletos em {loc}")
    checa(loc in alts.values(), f"sitemap: {loc} não aparece nos próprios alternates")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
checa("User-agent: *" in robots, "robots.txt sem User-agent")
checa(f"Sitemap: {BASE}/sitemap.xml" in robots, "robots.txt sem a linha Sitemap")
checa("Disallow: /\n" not in robots, "robots.txt bloqueia o site inteiro")

# ---------------------------------------------------------------- páginas
paginas = sorted({rel_de_url(loc) for loc in locs})
pares: dict[str, str] = {}
for rel in paginas:
    s = (ROOT / rel).read_text(encoding="utf-8")
    url = BASE + ("/" if rel == "index.html" else "/" + rel[: -len("index.html")])
    ident = f"[{rel}]"

    checa(bool(um(r"<title>(.*?)</title>", s)), f"{ident} sem <title>")
    titulo = um(r"<title>(.*?)</title>", s) or ""
    checa(len(titulo) <= 70, f"{ident} title com {len(titulo)} caracteres (acima de 70, o Google corta)")
    desc = um(r'<meta[^>]+name="description"[^>]+content="(.*?)"', s)
    checa(bool(desc), f"{ident} sem meta description")
    if desc:
        checa(60 <= len(desc) <= 170, f"{ident} description com {len(desc)} caracteres (fora de 60–170)")
    checa(len(re.findall(r"<h1[\s>]", s)) == 1, f"{ident} precisa de exatamente um <h1>")

    canon = um(r'<link rel="canonical" href="(.*?)"', s)
    checa(canon == url, f"{ident} canonical {canon!r} deveria ser {url!r}")

    alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', s))
    checa(set(alts) == {"pt-BR", "en", "x-default"}, f"{ident} hreflang incompleto: {sorted(alts)}")
    if alts:
        checa(url in alts.values(), f"{ident} não se referencia no próprio hreflang")
        outro = alts["en"] if not rel.startswith("en/") else alts["pt-BR"]
        pares[url] = outro

    for bloco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            dados = json.loads(bloco)
        except json.JSONDecodeError as e:
            falhas.append(f"{ident} JSON-LD inválido: {e}")
            continue
        for item in dados.get("@graph", []):
            if item.get("@type") == "SoftwareApplication":
                checa("aggregateRating" not in item and "review" not in item,
                      f"{ident} SoftwareApplication não pode declarar nota/avaliação inventada")
                tiro = item.get("screenshot")
                checa(not tiro or "divulgacao" not in tiro,
                      f"{ident} screenshot aponta para material de divulgação, não para uma captura do app")

    ids = re.findall(r'\sid="([^"]+)"', s)
    dups = {i for i in ids if ids.count(i) > 1}
    checa(not dups, f"{ident} ids repetidos: {sorted(dups)}")

    # links internos e recursos existem no repositório
    for alvo in re.findall(r'(?:href|src)="(/[^"#?]*)"', s):
        p = ROOT / alvo.lstrip("/")
        ok = p.exists() or (p / "index.html").exists()
        checa(ok, f"{ident} link/recurso quebrado: {alvo}")

    checa(f'{APP}/cadastro' in s, f"{ident} sem link de cadastro para o app")

# hreflang recíproco de verdade: A aponta para B e B aponta de volta para A
for a, b in pares.items():
    checa(pares.get(b) == a, f"hreflang não recíproco: {a} -> {b} -> {pares.get(b)}")

# ---------------------------------------------------------------- 404 e redirecionamento antigo
p404 = (ROOT / "404.html").read_text(encoding="utf-8")
checa("noindex" in (um(r'<meta name="robots" content="(.*?)"', p404) or ""), "404.html deveria ser noindex")
ingles = (ROOT / "ingles/index.html").read_text(encoding="utf-8")
checa("noindex" in ingles and f'canonical" href="{BASE}/idiomas/"' in ingles,
      "/ingles/ deveria ser noindex e canônica para /idiomas/")

# ---------------------------------------------------------------- imagem Open Graph
og = um(r'<meta property="og:image" content="(.*?)"', (ROOT / "index.html").read_text(encoding="utf-8")) or ""
checa((ROOT / og[len(BASE) + 1:]).exists(), f"imagem Open Graph ausente no repositório: {og}")

# ---------------------------------------------------------------- Dockerfile cobre tudo o que é publicado
docker = (ROOT / "Dockerfile").read_text(encoding="utf-8")
for d in sorted({p.parts[0] for p in (pathlib.Path(r) for r in paginas) if len(p.parts) > 1}):
    checa(f"COPY {d} " in docker, f"Dockerfile não copia o diretório publicado {d}/")

# ---------------------------------------------------------------- API usada pelo site
cfg = (ROOT / "assets/js/config.js").read_text(encoding="utf-8")
api = um(r'apiUrl: local \? "[^"]*" : "([^"]+)"', cfg)
checa(api == "https://api.estudatta.com.br",
      f"config.js aponta a API para {api!r}; o app em app.estudatta.com.br devolve HTML em qualquer caminho")

# ---------------------------------------------------------------- produção (opcional)
if "--prod" in sys.argv:
    import urllib.error
    import urllib.request

    def busca(u: str):
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (EstudattaSEO)"})
        try:
            r = urllib.request.urlopen(req, timeout=30)
            return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, ""

    for loc in locs:
        st, corpo = busca(loc)
        checa(st == 200, f"produção: {loc} respondeu {st}")
        if st == 200:
            checa(f'<link rel="canonical" href="{loc}"' in corpo, f"produção: canonical errada em {loc}")
    st, _ = busca(f"{BASE}/esta-url-nao-existe-{id(object())}/")
    checa(st == 404, f"produção: URL inexistente deveria responder 404, respondeu {st}")
    st, corpo = busca("https://api.estudatta.com.br/api/v1/public/plans")
    checa(st == 200 and corpo.lstrip().startswith("{"), "produção: a API pública de planos não respondeu JSON")

# ---------------------------------------------------------------- resultado
for f in falhas:
    print("FALHA:", f)
print(f"\n{len(paginas)} páginas conferidas, {len(falhas)} falha(s).")
sys.exit(1 if falhas else 0)
