#!/usr/bin/env python3
"""Calcula e grava o tempo de leitura dos guias (`N min de leitura`), a 200 palavras por minuto.

    python3 scripts/tempo_leitura.py

Roda depois de editar o texto de um guia. É idempotente: reescreve a linha existente.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
LINHA = '      <p class="updated">{} min de leitura</p>\n'


def palavras(html: str) -> int:
    corpo = html[html.index('<main id="conteudo">'):]
    corpo = re.sub(r"<script.*?</script>|<style.*?</style>|<nav\b.*?</nav>|<footer\b.*?</footer>", " ", corpo, flags=re.S)
    texto = re.sub(r"<[^>]+>", " ", corpo)
    return len([p for p in texto.split() if any(c.isalpha() for c in p)])


def main() -> None:
    for p in sorted(ROOT.glob("guias/*/index.html")):
        s = p.read_text(encoding="utf-8")
        minutos = max(1, round(palavras(s) / 200))
        s = re.sub(r'^      <p class="updated">\d+ min de leitura</p>\n', "", s, flags=re.M)
        m = re.search(r'^      <p class="lead u-mw48">.*?</p>\n', s, flags=re.M | re.S)
        if not m:
            print("sem parágrafo de abertura:", p.relative_to(ROOT))
            continue
        s = s[: m.end()] + LINHA.format(minutos) + s[m.end():]
        p.write_text(s, encoding="utf-8")
        print(f"{p.relative_to(ROOT)}: {minutos} min")


if __name__ == "__main__":
    main()
