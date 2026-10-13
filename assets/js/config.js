/*
  Endereços usados pelo site. Em produção:
    - app (cadastro, login, PWA): https://app.estudatta.com.br
    - API pública (planos, contato, novidades): https://api.estudatta.com.br/api/v1
      (o app em app.estudatta.com.br é estático e devolve o HTML do PWA em qualquer caminho:
       apontar a API para lá fazia o formulário de contato falhar e os planos não carregarem)
  Os links do HTML já apontam para produção e funcionam sem JavaScript.
  Em desenvolvimento local (localhost), este arquivo troca para o app e a API locais.
  Para outro ambiente, edite os valores abaixo.
*/
(function () {
  var local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  window.ESTUDATTA = {
    appUrl: local ? "http://localhost:5180" : "https://app.estudatta.com.br",
    apiUrl: local ? "http://localhost:8020" : "https://api.estudatta.com.br",
    productionAppUrl: "https://app.estudatta.com.br",
    supportEmail: "contato@estudatta.com.br",
  };
})();
