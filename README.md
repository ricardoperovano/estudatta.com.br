# Estudatta — site público

Site de aquisição do Estudatta (`https://estudatta.com.br`), em **HTML, CSS e JavaScript puros**, sem framework e sem etapa de build. O app (cadastro, login, PWA) fica em outro repositório e em outro domínio (`https://app.estudatta.com.br`).

## Páginas

| Rota | Arquivo |
|---|---|
| `/` | `index.html` |
| `/ingles` | `ingles/index.html` |
| `/concursos` | `concursos/index.html` |
| `/planos` | `planos/index.html` |
| `/faq` | `faq/index.html` |
| `/contato` | `contato/index.html` |
| `/privacidade` | `privacidade/index.html` |
| `/termos` | `termos/index.html` |
| 404 | `404.html` |

Também: `sitemap.xml`, `robots.txt`, `assets/` (CSS, JS, fonte Inter com licença OFL, marca, imagem de compartilhamento).

Cabeçalho e rodapé se repetem em cada página. Para mudar um item do menu ou do rodapé, altere todos os arquivos `.html`; eles são poucos e idênticos nesse trecho.

## Como o site conversa com o app

Tudo o que é essencial funciona sem JavaScript: os botões "Criar conta" e "Entrar" são links comuns para o app, e a página de planos já traz o texto "Valor a definir".

O JavaScript (`assets/js/site.js`) acrescenta três coisas, usando só endpoints públicos da API, sem cookie:

- **Planos:** `GET /api/v1/public/plans` substitui os cartões e a tabela pelo catálogo real. Se a API não responder, fica o conteúdo estático. Nenhum preço é escrito no HTML.
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

O servidor do Python não aplica as URLs limpas do Nginx: use `/ingles/` (com barra) em vez de `/ingles`.

## Publicar

Com Docker (Nginx já configurado com URLs limpas, 404 e cabeçalhos de segurança):

```
docker build -t estudatta-site .
docker run -d --name estudatta-site -p 8091:80 estudatta-site
```

Na frente, o Nginx do servidor com TLS encaminha `estudatta.com.br` e `www.estudatta.com.br` para a porta 8091 (exemplo em `docs/deploy.md` do repositório do app). Também funciona em qualquer hospedagem estática (Netlify, Cloudflare Pages, GitHub Pages, S3 + CDN), desde que ela sirva `pasta/index.html` para `/pasta` e use `404.html`.

A `Content-Security-Policy` do `nginx.conf` libera `connect-src` só para `https://app.estudatta.com.br`. Se a API mudar de endereço, atualize o `nginx.conf` e o `config.js`.

## Design

Segue a identidade e o design system do Estudatta (pasta "Identidade visual e design system PWA Estudatta", referência `06 Landing.dc.html`). As cores, a tipografia, os espaçamentos e os componentes estão em `assets/css/site.css`, com os mesmos valores dos tokens do app. A comparação visual está em `docs/verificacao-visual/`.

## Pendências do responsável

- **Termos e privacidade:** razão social, CNPJ, endereço, encarregado (DPO) e foro aparecem destacados em damasco para preencher, junto com a revisão jurídica.
- **Preço do plano Completo:** vem do catálogo do app. Enquanto não houver preço, o site mostra "Valor a definir".
- **Imagem de compartilhamento:** reexportar `assets/divulgacao/capa-compartilhamento-1200x630.png` com a fonte Inter instalada (limitação registrada no material de marca).
