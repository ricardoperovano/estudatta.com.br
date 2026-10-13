# Auditoria de SEO — Estudatta

Auditoria técnica e editorial do site institucional (`https://estudatta.com.br`) e da sua ligação
com o app (`https://app.estudatta.com.br`). Executada em **13/10/2026** sobre o site publicado e
sobre o repositório, com correções aplicadas no código existente.

O site **não foi redesenhado**: nenhuma mudança de layout, de identidade visual ou de
funcionalidade. A auditoria em si só alterou metadados, geradores, configuração e três trechos de
conteúdo com defeito comprovado. Numa segunda etapa, já com autorização, entraram o tipo de
sessão Devocional e a seção de guias (seção 6) — reaproveitando o layout existente, sem CSS novo
e sem tocar no menu.

---

## 1. Diagnóstico

### 1.1 Como a auditoria foi feita

| Verificação | Método |
|---|---|
| Disponibilidade e metadados | Rastreamento das 23 URLs públicas em produção (HTTP, título, descrição, H1, canônica, hreflang, JSON-LD) |
| Links e recursos | Resolução de todos os `href`/`src` de todas as páginas (32 alvos distintos) |
| Redirecionamentos | `http→https`, `www`, com e sem barra final, `/index.html`, `/ingles`, URL com UTM |
| Dados estruturados | Leitura e validação de cada bloco JSON-LD das 18 páginas indexáveis |
| Planos | Comparação do HTML estático com `GET /api/v1/public/plans` em produção |
| Desempenho | Medição em navegador real (Chromium, emulação Pixel 5) de TTFB, FCP, LCP e CLS |
| Acessibilidade | IDs repetidos, `alt`, rótulos de formulário, hierarquia de títulos, `prefers-reduced-motion` |
| Consentimento | Carregamento do GA4 antes e depois de aceitar e de recusar, em navegador real |
| Geradores | Execução de `scripts/seo.py` e `scripts/build_en.py` sobre a árvore limpa, comparando o resultado com o publicado |

### 1.2 Estado encontrado

O essencial já estava correto, e **não foi mexido**:

- As 18 URLs do sitemap respondem 200 em produção, com HTTPS, canônica própria e correta.
- `hreflang` pt-BR / en / x-default recíproco em todas as páginas e também dentro do sitemap.
- Títulos e descrições únicos por página, dentro do tamanho útil, com as palavras-chave da
  intenção de busca de cada página.
- Um `<h1>` por página e hierarquia `h2`/`h3` coerente.
- `robots.txt` liberando o rastreamento e apontando o sitemap.
- Redirecionamentos de infraestrutura corretos: `http→https`, `www→apex`, `/rota→/rota/`.
- URL inexistente responde **404 de verdade** (não 200 com página de erro).
- `/ingles/` é `noindex` e canônica para `/idiomas/`.
- Preços e limites do HTML **batem exatamente** com `GET /api/v1/public/plans`
  (R$ 0 / R$ 9,90 / R$ 19,90 ao mês; R$ 94,80 / R$ 190,80 ao ano; mesmos limites de objetivos,
  IA, voz, materiais e relatórios). Nenhuma correção comercial foi necessária.
- Todos os links e recursos internos resolvem (0 quebrados). Os 104 CTAs levam a
  `/cadastro`, `/entrar` ou à raiz do app, todos respondendo 200.
- Nenhuma imagem sem `alt`, nenhum campo de formulário sem rótulo, `prefers-reduced-motion`
  respeitado.
- O GA4 só carrega depois do aceite; recusar não dispara nenhuma requisição ao Google.

### 1.3 Problemas confirmados

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| 1 | O site chamava a API no host errado | `apiUrl` era `https://app.estudatta.com.br`, que é o PWA estático e devolve o HTML do app em qualquer caminho. `GET …/api/v1/public/plans` lá retorna `text/html`; `POST …/public/contact` retorna **405** | **Alta** |
| 2 | Regenerar o SEO apagava o `hreflang` | `scripts/seo.py` reconstrói o `<head>` preservando só uma lista de linhas, que não incluía `<link rel="alternate">`. Rodar o gerador removia as 3 linhas de cada página em português | **Alta** |
| 3 | Regenerar o SEO reintroduzia o GA sem consentimento | `seo.py` injetava `gtag.js` direto no `<head>`, carregando o Google Analytics antes de qualquer escolha — o oposto do que `analytics.js` faz hoje, e um problema de LGPD | **Alta** |
| 4 | `seo.py` destruía o sitemap internacional | Ele reescrevia `sitemap.xml` com 9 URLs e sem `hreflang`; `build_en.py` escreve as 18 com alternates. Rodar só o primeiro derrubava metade do sitemap | **Média** |
| 5 | `lastmod` fixo em todas as URLs | `TODAY = "2026-09-21"` carimbado nas 18 URLs, inclusive nas de `/en/`. A data não correspondia à alteração real de cada página | **Média** |
| 6 | `id="conteudo"` repetido em Termos | `<main id="conteudo">` e a seção 05 usavam o mesmo id: o "Pular para o conteúdo" ficava ambíguo e o HTML, inválido | **Média** |
| 7 | Dockerfile não copiava 3 diretórios publicados | Faltavam `en/`, `vestibular-enem/` e `ingles/`: a imagem serviria 404 em 11 das 18 URLs do sitemap | **Média** (latente) |
| 8 | `screenshot` do app era material de divulgação | O JSON-LD de `SoftwareApplication` apontava `screenshot` para a imagem de compartilhamento, não para uma captura do app | **Baixa** |
| 9 | Título em inglês acima do limite útil | `/en/languages/` tinha 75 caracteres; o Google corta por volta de 70 | **Baixa** |

Os problemas 2, 3, 4 e 5 não afetavam o site publicado **naquele momento** — afetavam a próxima
regeneração. Como a regeneração é o caminho normal para qualquer mudança de SEO, eles iam
destruir silenciosamente o SEO internacional e a conformidade de cookies na primeira vez que
alguém rodasse os scripts.

---

## 2. Correções aplicadas

| Arquivo | O que mudou | Por quê |
|---|---|---|
| `assets/js/config.js` | `apiUrl` de produção passa a ser `https://api.estudatta.com.br` | Problema 1: era a causa do formulário de contato falhar e dos planos não sincronizarem |
| `nginx.conf` | `connect-src` da CSP passa a incluir `https://api.estudatta.com.br` | Acompanha a correção acima para quem servir pelo Docker |
| `scripts/seo.py` | Preserva as linhas `<link rel="alternate" hreflang=…>` ao reconstruir o `<head>` | Problema 2 |
| `scripts/seo.py` | Deixa de injetar `gtag.js`; o GA fica só em `analytics.js`, atrás do consentimento | Problema 3 |
| `scripts/seo.py` | Não escreve mais `sitemap.xml` (quem escreve é `build_en.py`, que conhece `/en/`) | Problema 4 |
| `scripts/seo.py` / `build_en.py` | `lastmod` passa a vir da data real do arquivo no git (ou de hoje, se houver alteração não commitada) | Problema 5 |
| `scripts/seo.py` | Remove `screenshot` do `SoftwareApplication` | Problema 8 |
| `scripts/seo.py` | Página `/ingles/` gerada sem indentação sobrando e com quebra de linha final | Higiene: o arquivo mudava a cada execução |
| `termos/index.html` | Seção 05 passa de `id="conteudo"` para `id="seu-conteudo"` (e o índice acompanha) | Problema 6 |
| `Dockerfile` | Copia `en/`, `vestibular-enem/` e `ingles/` | Problema 7 |
| `scripts/en_map1.py` | Título de `/en/languages/` encurtado para 61 caracteres | Problema 9 |
| `assets/js/analytics.js` | Evento `click_app` nos cliques que levam ao app (`destino`, `texto`, `pagina`) | Medição de conversão orgânica, só depois do consentimento |
| `scripts/test_seo.py` | **Novo**: bateria de verificações de SEO, com e sem rede | Impede a volta de qualquer um dos problemas acima |

Nada foi alterado no app, no backend, nos preços, nos planos, no layout, nas animações ou no
mascote.

### 2.1 Medição de conversão

O novo evento mede **intenção**, não cadastro: dispara no clique de um link que leva ao app,
com `destino` = `cadastro`, `entrar` ou `app`. O cadastro efetivado só o app conhece — o site
não tem como afirmar que ele aconteceu, e por isso não afirma.

---

## 3. Resultados dos testes

### 3.1 Bateria de SEO (`scripts/test_seo.py`)

```
python3 scripts/test_seo.py            # 18 páginas conferidas, 0 falha(s).
python3 scripts/test_seo.py --prod     # 18 páginas conferidas, 0 falha(s).
```

Ela confere: sitemap bem formado, sem URLs repetidas, todas absolutas em HTTPS com barra final,
cada uma com arquivo correspondente e `lastmod` válido; `robots.txt`; por página — título (≤ 70
caracteres), descrição (60–170), exatamente um `h1`, canônica igual à própria URL, `hreflang`
completo e recíproco, JSON-LD que compila, ausência de nota/avaliação inventada, `screenshot` que
não seja material de divulgação, ids não repetidos, links e recursos existentes e link de
cadastro presente; `404.html` `noindex`; `/ingles/` `noindex` + canônica; imagem Open Graph
existente; Dockerfile cobrindo todo diretório publicado; `config.js` apontando para a API certa.
Com `--prod` ainda confere que cada URL do sitemap responde 200 com a canônica certa, que uma URL
inexistente responde 404 e que a API pública devolve JSON.

### 3.2 Geração da versão em inglês

`python3 scripts/seo.py && python3 scripts/build_en.py` roda sem erro e agora é **idempotente**:
numa árvore limpa, não altera nenhum arquivo. Antes desta auditoria, a mesma sequência modificava
20 arquivos, apagando `hreflang` e duplicando o Analytics.

As 24 pendências de tradução relatadas por `build_en.py` são valores técnicos (`#f3f5fe`,
`20 min`, nomes de classe), não texto visível.

### 3.3 Navegador real (Chromium, emulação Pixel 5)

| Verificação | Resultado |
|---|---|
| Formulário de contato | Envia para `api.estudatta.com.br` e exibe a confirmação |
| Aviso de cookies | Aparece na primeira visita |
| GA antes de aceitar | **Não carrega** (`gtag` indefinido, nenhuma requisição ao Google) |
| GA depois de aceitar | Carrega |
| Depois de recusar | 0 requisições ao Google; o evento de CTA **não** é enviado |
| Evento de CTA após aceitar | `click_app {destino: "cadastro", …}` |
| Detecção de idioma | Navegador em inglês cai em `/en/` |

### 3.4 Desempenho (laboratório)

| Página | TTFB | FCP | LCP | CLS | Requisições | Peso |
|---|---|---|---|---|---|---|
| `/` | 187 ms | 300 ms | 300 ms | 0,000 | 17 | ~185 KB |
| `/planos/` | 175 ms | 252 ms | 252 ms | 0,000 | 19 | ~198 KB |
| `/concursos/` | 192 ms | 260 ms | 260 ms | 0,000 | 19 | ~202 KB |

Confortavelmente dentro das metas (LCP ≤ 2,5 s, CLS ≤ 0,1). **Nenhuma otimização de performance
foi aplicada**: não havia defeito a corrigir, e mexer traria risco sem ganho. Duas observações
registradas e não aplicadas:

- `assets/js/config.js` (782 bytes) bloqueia o parser. `defer` funcionaria, mas o ganho é de
  poucos milissegundos e qualquer script inline futuro que dependa de `window.ESTUDATTA` quebraria.
- `assets/marca/logo-estudada-escuro.png` e `logo-estudata-claro.png` somam ~1,8 MB e **não são
  referenciados por nenhuma página**. Não pesam no carregamento; só ocupam o repositório.

Estes são números de **laboratório**, com rede local e sem limitação de banda. Não são dados de
campo: o domínio é novo e ainda não tem tráfego suficiente para aparecer no relatório de
experiência do Chrome.

---

## 4. Infraestrutura de publicação

**O site é servido pelo GitHub Pages**, não pelo Docker. Evidências: a resposta de produção traz
`server: GitHub.com` e `x-github-request-id`; existe `CNAME` com `estudatta.com.br`; não há
workflow em `.github/`; a publicação acontece no push para `main`.

Portanto o `Dockerfile` **não participa do deploy atual** — mas estava incompleto, e foi
corrigido para que a imagem sirva o site inteiro caso um dia seja usada. O teste automatizado
agora falha se um diretório publicado ficar de fora dele.

Consequências de estar no GitHub Pages, registradas porque limitam o que é possível:

- Não há redirecionamento 301 configurável. `/ingles/` usa `meta refresh` + canônica + `noindex`;
  o 301 do `nginx.conf` só vale para quem servir pelo Docker.
- `/rota/index.html` responde 200 além de `/rota/`. A canônica consolida as duas, e o sitemap só
  lista a forma com barra final.
- Os cabeçalhos de segurança e de cache do `nginx.conf` não se aplicam.

---

## 5. SEO internacional

| Item | Estado |
|---|---|
| `lang` do documento | `pt-BR` e `en`, corretos |
| `hreflang` | pt-BR / en / x-default em todas as páginas, recíproco, com URLs absolutas |
| Canônica | Independente por idioma, apontando para a própria URL |
| Sitemap | As 18 URLs com os três alternates cada |
| Geração | `scripts/build_en.py` + mapas `en_map1..3.py`; `/en/` nunca é editado à mão |
| Detecção automática | `assets/js/lang.js` |

Sobre `lang.js`, auditado e **mantido como está**: a preferência explícita (clique em EN/PT) é
gravada e respeitada; quem chega por link interno não é redirecionado; robôs são excluídos por
User-Agent, de modo que o Google indexa as duas versões pelo `hreflang`; sem JavaScript, nada
acontece e a página em português é servida normalmente; não há como entrar em laço, porque
páginas sob `/en/` saem no início. Redirecionar por idioma do navegador é prática aceita pelo
Google, e as duas versões continuam acessíveis e declaradas uma à outra.

---

## 6. Conteúdo e posicionamento

O conteúdo já descreve o produto com honestidade, e esse foi um critério de revisão, não só de
SEO. Em particular:

- A página de idiomas **não** promete ensinar idiomas: fala em organizar, acompanhar e manter
  constância. O FAQ da home responde explicitamente "o app ensina idiomas ou tem conteúdo de
  concurso? Não".
- A página de concursos não anuncia banco de questões próprio nem curso preparatório.
- A de vestibular não promete aulas, questões oficiais nem correção de prova.
- O FAQ afirma que o relatório mostra constância, tempo e taxa de acerto — e não diz se a pessoa
  está aprendendo.

Nenhuma reescrita foi necessária nas páginas comerciais.

Duas lacunas identificadas na auditoria foram cobertas em seguida, com autorização:

**Devocional.** O tipo de sessão já existia no app e não aparecia em lugar nenhum do site. Entrou
na home (texto e etiqueta dos tipos de sessão) e no FAQ, com resposta honesta: o app organiza e
acompanha a leitura, não traz o texto nem um plano de leitura pronto. Traduzido para `/en/`.

**Guias** (`/guias/`). Quatro textos para consultas informacionais com intenção clara que não
tinham página correspondente, mais um índice:

| URL | Consulta principal |
|---|---|
| `/guias/recuperar-estudos-atrasados/` | como recuperar estudos atrasados |
| `/guias/ciclo-de-estudos/` | ciclo de estudos, como montar |
| `/guias/quantas-horas-estudar-por-dia/` | quantas horas estudar por dia |
| `/guias/revisao-espacada/` | revisão espaçada, intervalos de revisão |
| `/guias/disciplina-para-estudar/` | como ter disciplina para estudar, criar hábito de estudo |

O último nasceu de uma lacuna que só apareceu quando procuramos por ela: o site descrevia o
produto na língua da **organização** ("rotina" 24 vezes, "constância" 22) e não tinha nada na
língua de quem busca — disciplina, hábito, motivação, procrastinação. "Constância" descreve bem o
produto e ninguém a digita no Google. "Disciplina" aparecia 6 vezes, quase sempre em sentido
contrário ao da busca ("o problema não é disciplina") e uma delas com outro significado (matéria
de faculdade). Nenhum título, descrição ou H1 trazia essa família de palavras.

Decisões tomadas, e os porquês:

- **Só em português.** A intenção de busca que os motivou é em português; inventar uma versão em
  inglês criaria páginas sem demanda comprovada. O gerador ganhou uma lista `PT_ONLY`: essas URLs
  entram no sitemap sem alternates e não declaram `hreflang`, porque não têm par.
- **Links marcados `data-pt-only`.** O que aponta para um guia é removido da versão em inglês,
  para que nenhuma página `/en/` mande o leitor para um texto em português. O teste automatizado
  falha se isso escapar.
- **Reaproveitam o layout `.doc`**, o mesmo de Termos e Privacidade. Nenhum CSS novo.
- **FAQ real no fim de cada guia**, o que gera `FAQPage` a partir dos `<details>` — o mesmo
  mecanismo das outras páginas.
- **Trilha de três níveis** (Início › Guias › guia) no `BreadcrumbList`.
- **Descoberta pelo rodapé** das páginas em português e por links contextuais onde a dúvida
  aparece de verdade (a resposta do FAQ sobre pendência leva ao guia de atraso). O menu principal
  **não** foi alterado.
- **Sem promessa de resultado.** Os guias dizem o que não dá para afirmar: que tempo não mede
  aprendizado, que não existe número de horas que garanta aprovação, que recuperar tempo não é o
  mesmo que recuperar conteúdo, que nenhum app cria disciplina e que "21 dias para criar um
  hábito" não tem base sólida. O guia de disciplina também diz quando o caso pede ajuda
  profissional em vez de aplicativo.
- **Tempo de leitura** no topo de cada guia, calculado por `scripts/tempo_leitura.py` a 200
  palavras por minuto — número derivado do texto, não estimado à mão.

Oportunidade ainda **não executada**: `/contato/` é a página mais fraca do conjunto — cumpre a
função, mas tem pouco texto rastreável.

---

## 7. Pendências (dependem de decisão ou acesso humano)

| Pendência | Observação |
|---|---|
| **Google Search Console** | Sem acesso nesta sessão. Impressões, cliques, consultas, cobertura e canônica escolhida pelo Google não foram analisados, e não foram inventados |
| **Dados jurídicos** | Termos e Privacidade trazem, em destaque e assumidamente, campos a preencher: razão social, CNPJ, endereço, idade mínima, política de reembolso e foro. Não foram preenchidos: inventar dado jurídico seria pior do que a lacuna |
| **Captura real do app** | `screenshot` foi removido do JSON-LD por apontar para material de divulgação. Uma captura verdadeira do app pode ser adicionada depois |
| **Dados de campo** | O domínio é novo; ainda não há Core Web Vitals de usuários reais |

---

## 8. Acompanhamento sugerido — 90 dias

Sem metas numéricas: o domínio tem poucas semanas e qualquer número seria chute. O que importa é
a direção de cada série.

**Quinzenal, no Search Console**

1. Impressões e cliques **sem marca** (excluindo "estudatta") — é o indicador principal. Consultas
   de marca medem divulgação, não SEO.
2. Quantas das 18 URLs estão indexadas, e por qual motivo as demais não estão.
3. CTR por página comercial (`/`, `/concursos/`, `/vestibular-enem/`, `/idiomas/`, `/planos/`):
   CTR baixa com impressões altas é sinal de título ou descrição a ajustar — não de conteúdo ruim.
4. Consultas que já trazem impressão sem ter página dedicada: é a lista de prioridades editoriais.

**Mensal, no GA4**

5. Sessões orgânicas por página de entrada.
6. Eventos `click_app` com `destino = cadastro`, por página de entrada — mede quais páginas
   convertem, não quantas contas nasceram.
7. Confronto com os cadastros reais no app, que só o backend conhece.

**Contínuo**

8. `python3 scripts/test_seo.py --prod` depois de cada publicação.
9. Reavaliar performance se alguma imagem pesada entrar em alguma página.
