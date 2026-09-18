# Verificação visual do site

Capturas feitas com Chrome em 1440×900 (desktop, página inteira) e 390×844 (celular), com o site servido localmente e a API do app rodando.

- **Referência:** `referencia/06-landing.png`, renderização do documento `06 Landing.dc.html` da pasta de design.
- **Implementação:** `implementado/desktop-site-*.png` e `implementado/mobile-site-*.png`.

## Resultado

**Página inicial:** mesma estrutura, textos e hierarquia da referência.
- Navegação com a marca e o botão "Criar conta" em contorno.
- Hero de 80 px com o telefone e o cartão "Hoje" (60/40/60/20).
- Faixa índigo com a citação.
- "Como funciona" em três linhas.
- "Para quem" com três cartões.
- Planos com "Valor a definir" e contorno acento no recomendado.
- FAQ, bloco de cadastro e rodapé.

**Diferenças em relação à referência, intencionais:**
- **Chamada principal:** passou a ser "Começar grátis" e "Criar conta". A referência previa "Quero acesso inicial", de pré-lançamento.
- **Novidades:** o cadastro por e-mail virou opção secundária, "Receber novidades".
- **Navegação:** ganhou o link "Entrar".

**Páginas de inglês e concursos:** variações da mesma linguagem visual, com a demonstração do saldo na faixa índigo e a árvore de matérias no visual de `03 Componentes`.

## Verificações de comportamento

Executadas em 18/09/2026, com o site em `http://localhost:5190` e a API em `:8020`:

- **Catálogo de planos:** carregado da API, com a tabela comparativa montada a partir dos limites reais (12 linhas).
- **Alternância mensal/anual:** funciona.
- **Links do app:** "Criar conta" e "Entrar" apontam para o app.
- **Receber novidades:** gravou o e-mail na API.
- **Contato:** a mensagem foi gravada e a confirmação apareceu.
- **Sem JavaScript:** as páginas mostram o conteúdo, os preços como "Valor a definir" e os links para o app em produção.
- **Console:** nenhum erro de JavaScript em nenhuma página.
- **HTML:** tags equilibradas em todas as 9 páginas.
- **Privacidade e termos:** o texto é idêntico ao da versão anterior, com a mesma contagem de palavras (2.405 e 1.515).
