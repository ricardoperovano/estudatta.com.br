# Estudatta — site público

Site de aquisição do Estudatta (`https://estudatta.com.br`), em **HTML, CSS e JavaScript puros**, sem framework e sem etapa de build. O app (cadastro, login, PWA) fica em outro repositório e em outro domínio (`https://app.estudatta.com.br`).

O site usa o **tema claro** do design system (fundo `#f3f5fe`, superfícies `#fafbff`, acento `#5d5294`), com as rampas invertidas como no app. A faixa índigo "Seu saldo" é o único bloco escuro. Os tokens ficam no início de `assets/css/site.css`.

## Páginas

| Rota | Arquivo |
|---|---|
| `/` | `index.html` |
| `/idiomas` | `idiomas/index.html` (`/ingles/index.html` redireciona para cá com meta refresh; o Nginx faz 301) |
| `/concursos` | `concursos/index.html` |
| `/vestibular-enem` | `vestibular-enem/index.html` |
| `/planos` | `planos/index.html` |
| `/en/…` | `en/**/index.html` (gerado; ver abaixo) |
| `/faq` | `faq/index.html` |
| `/contato` | `contato/index.html` |
| `/privacidade` | `privacidade/index.html` |
| `/termos` | `termos/index.html` |
| 404 | `404.html` |

Também: `sitemap.xml`, `robots.txt`, `assets/` (CSS, JS, fonte Inter com licença OFL, marca, mascote, imagem de compartilhamento).

Cabeçalho e rodapé se repetem em cada página. Para mudar um item do menu ou do rodapé, altere todos os arquivos `.html`; eles são poucos e idênticos nesse trecho.

## Como o site conversa com o app

Tudo o que é essencial funciona sem JavaScript: os botões "Criar conta" e "Entrar" são links comuns para o app, e os cartões e a tabela de planos já trazem os preços no HTML.

O JavaScript (`assets/js/site.js`) acrescenta três coisas, usando só endpoints públicos da API, sem cookie:

- **Planos:** `GET /api/v1/public/plans` substitui os cartões e a tabela pelo catálogo real (a fonte de verdade é o painel admin do app). Se a API não responder, fica o conteúdo estático, e a alternância mensal/anual usa os valores dos atributos `data-month` e `data-year`. **Ao mudar um preço no painel, atualize também os cartões e a tabela no HTML** (`index.html`, `ingles/`, `concursos/` e `planos/`).
- **Receber novidades:** `POST /api/v1/public/waitlist`.
- **Contato:** `POST /api/v1/public/contact`.

Os endereços estão em `assets/js/config.js`. Em `localhost`, o site usa o app em `http://localhost:5180` e a API em `http://localhost:8020`; fora disso, `https://app.estudatta.com.br`.

**A API precisa liberar a origem do site por CORS.** No `.env` do app: `CORS_ORIGINS=https://estudatta.com.br` (em desenvolvimento, `http://localhost:5190`).

## Rodar localmente

Qualquer servidor estático serve. Com Python:

```
python3 -m http.server 5190 --bind 127.0.0.1
```

Abra http://localhost:5190. Para planos, novidades e contato funcionarem, a API do app precisa estar rodando em `:8020` com `CORS_ORIGINS=http://localhost:5190`.

O servidor do Python não aplica as URLs limpas do Nginx: use `/idiomas/` (com barra) em vez de `/idiomas`.

## Publicar

Com Docker (Nginx já configurado com URLs limpas, 404 e cabeçalhos de segurança):

```
docker build -t estudatta-site .
docker run -d --name estudatta-site -p 8091:80 estudatta-site
```

Na frente, o Nginx do servidor com TLS encaminha `estudatta.com.br` e `www.estudatta.com.br` para a porta 8091 (exemplo em `docs/deploy.md` do repositório do app). Também funciona em qualquer hospedagem estática (Netlify, Cloudflare Pages, GitHub Pages, S3 + CDN), desde que ela sirva `pasta/index.html` para `/pasta` e use `404.html`.

A `Content-Security-Policy` do `nginx.conf` libera `connect-src` só para `https://app.estudatta.com.br`. Se a API mudar de endereço, atualize o `nginx.conf` e o `config.js`.

## Design

Segue o design system do Estudatta (pasta "Identidade visual e design system PWA Estudatta", referência `06 Landing.dc.html`), com a logo nova no lugar do símbolo original. As cores, a tipografia, os espaçamentos e os componentes estão em `assets/css/site.css`, com os mesmos valores dos tokens do app. A comparação visual está em `docs/verificacao-visual/`.

## Planos exibidos

Gratuito (R$ 0), Essencial (R$ 9,90/mês ou R$ 94,80/ano, recomendado) e Completo (R$ 19,90/mês ou R$ 190,80/ano). A IA para organizar está nos dois planos pagos. Racional e limites: `docs/planos-e-precos.md` no repositório do app.

## Mascote Tatá

O Tatá é o mascote do app: um cronômetro roxo com marcador de livro no lugar da cauda. A geometria é a mesma do componente do app (`apps/web/src/components/mascot/TataSvg.tsx`).

- **Arquivo estático:** `assets/mascote/tata.svg`, na pose ociosa, sem `<style>` interno.
- **Nas páginas:** SVG inline com as classes do componente (`tata tata--wave`, `tata--focus`, `tata--paused`, `tata--cheer`, `tata--sleep`, `tata--think`). Cada instância tem um `id` próprio no gradiente do rosto.
- **Animações:** ficam em `site.css`, na seção "Tatá", com o prefixo `.tata`. Com `prefers-reduced-motion: reduce` nada se mexe, e a pose se mantém.
- **Onde aparece:** no hero da página inicial, sentado no telefone; na seção "Seu companheiro de estudo", com foco, pausa, comemorando e dormindo; e na 404, pensativo.

## Recursos descritos no site

Página inicial:
- **Como funciona:** em 4 passos.
- **Recursos:** tipos de sessão, revisões automáticas (1, 7 e 30 dias), simulados, edital coberto, próxima matéria sugerida e metas semanais.
- **Tatá:** a seção "Seu companheiro de estudo".
- **Gamificação:** "Conquistas, níveis e desafios", com 8 exemplos das mais de 40 conquistas. Não há ranking, e quebrar a sequência não tira nada.
- **Para quem:** concursos, vestibular e ENEM, faculdade e residência, idiomas e rotina pessoal.

Outras páginas:
- **Concursos:** revisões, questões, simulados, edital coberto e próxima matéria.
- **Idiomas:** mais de 90 idiomas (inglês como padrão), tipos de sessão, metas semanais de páginas e gamificação.
- **Planos:** 4 linhas novas, "Sim" em todos os planos. Estão também fixas em `site.js`, depois das linhas de limites.
- **FAQ:** seção "Revisões, simulados e conquistas".

Tudo isso vale para todos os planos, inclusive o Gratuito. Ao mudar esses recursos no app, revise esses textos.

## Logo

Os originais estão em `assets/marca/logo-estudada-escuro.png` e `assets/marca/logo-estudata-claro.png`, em PNG de 1254 px com fundo sólido. Os tamanhos web (cabeçalho, favicons, ícone da tela inicial) são gerados por:

```
bash scripts/gerar-logos.sh ../estudatta.com.br/apps/web/public/marca
```

O argumento é opcional: ele gera também os ícones do app (PWA) na pasta indicada. O script requer ImageMagick. A imagem de compartilhamento `assets/divulgacao/compartilhamento-1200x630.png` foi gerada a partir da logo escura, com a fonte Inter.

## Pendências do responsável

- **Termos e privacidade:** razão social, CNPJ, endereço, encarregado (DPO) e foro aparecem destacados em damasco para preencher, junto com a revisão jurídica.
- **Logo em SVG:** se existir uma versão vetorial da logo nova, ela deixa o cabeçalho e os ícones nítidos em qualquer tamanho.

## Inglês (`/en/`) e detecção de idioma

- A versão em inglês é **gerada** a partir das páginas em português: `python3 scripts/build_en.py` (usa `scripts/en_map*.py`, um dicionário frase → tradução, e `scripts/seo.py`). Ao mudar um texto em português, acrescente a tradução no mapa e rode o script; ele avisa as frases sem tradução. Nunca edite `en/` à mão.
- Rotas: `/en/`, `/en/languages/`, `/en/civil-service-exams/`, `/en/college-entrance-exams/`, `/en/pricing/`, `/en/faq/`, `/en/contact/`, `/en/privacy/`, `/en/terms/`. Todas com `hreflang` (pt-BR, en, x-default → português) nas duas versões e no `sitemap.xml`.
- `assets/js/lang.js` (carregado no `<head>`): na primeira visita a uma página em português, quem tem o navegador sem português vai para a página equivalente em inglês. Robôs de busca e quem já escolheu (EN/PT no menu, `localStorage estudatta.lang`) nunca são redirecionados. A 404 é uma só (`404.html`) e mostra o texto em inglês quando o caminho começa com `/en/`.
- Em `/en/`, o `site.js` não substitui os planos pelo catálogo da API (que é em português): fica o HTML traduzido, com a alternância mensal/anual pelos atributos `data-*`. O app em si continua em português; a versão em inglês avisa isso no topo.

## SEO e analytics

- Cada página tem título com palavra-chave (≤ 65 caracteres), descrição (≤ 160), `keywords`, canônica **com barra final** (`/concursos/`: é como o GitHub Pages serve), Open Graph e Twitter completos e JSON-LD (`Organization`, `WebSite` e `SoftwareApplication` na home; `BreadcrumbList`, `WebPage` e `FAQPage` nas demais). O `FAQPage` é gerado a partir dos `<details><summary>` da própria página: manter as perguntas no HTML mantém o dado estruturado.
- `sitemap.xml` com `lastmod`/`priority`; `robots.txt` libera tudo. Links internos sempre com barra final.
- Google Analytics 4 (`G-8XFNHTHEX7`) **só depois do consentimento** (LGPD): `assets/js/analytics.js` mostra o aviso de cookies, guarda a escolha em `localStorage` (`estudatta.consent`, 12 meses) e só então injeta o `gtag.js`. Recusou ou não respondeu: nada do Google é carregado. O link “Cookies” do rodapé (`data-cookie-prefs`) reabre o aviso. A CSP do `nginx.conf` libera `googletagmanager.com` e `google-analytics.com`.
- Ao criar uma página nova: copiar o `<head>` de uma existente, ajustar título/descrição/canônica/JSON-LD, adicionar ao `sitemap.xml` e ao menu de todas as páginas.
