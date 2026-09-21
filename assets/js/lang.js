/*
  Idioma do site. Duas versões: português em / e inglês em /en/.
  - Preferência explícita (clique em EN/PT no menu) fica em localStorage ("estudatta.lang").
  - Sem preferência, na primeira visita a uma página em português, quem tem o navegador em outro
    idioma que não o português é levado à mesma página em inglês. Robôs de busca nunca são
    redirecionados (as duas versões têm hreflang), e quem chegou por um link interno também não.
  Carregado antes do conteúdo para redirecionar sem piscar a página.
*/
(function () {
  var KEY = "estudatta.lang";
  var MAP = { "": "", idiomas: "languages", concursos: "civil-service-exams", "vestibular-enem": "college-entrance-exams", planos: "pricing", faq: "faq", contato: "contact", privacidade: "privacy", termos: "terms" };
  var path = location.pathname;
  var isEn = path === "/en" || path.indexOf("/en/") === 0;

  function pref() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setPref(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  // clique em EN/PT no menu: guarda a escolha (o link já leva à página certa)
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-lang-switch]");
    if (a) setPref(a.getAttribute("data-lang-switch"));
  });

  // 404 em /en/…: mostra o texto em inglês (a página é uma só no GitHub Pages)
  if (isEn && document.documentElement.getAttribute("data-page") === "404") {
    document.documentElement.lang = "en";
    document.addEventListener("DOMContentLoaded", function () {
      var pt = document.querySelector("[data-404-pt]"), en = document.querySelector("[data-404-en]");
      if (pt && en) { pt.hidden = true; en.hidden = false; }
    });
  }

  if (isEn || pref()) return;
  var bot = /bot|crawl|spider|slurp|facebookexternalhit|preview|lighthouse/i.test(navigator.userAgent);
  if (bot) return;
  var langs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
  var wantsPt = false;
  for (var i = 0; i < langs.length; i++) {
    var l = String(langs[i]).toLowerCase();
    if (l.indexOf("pt") === 0) { wantsPt = true; break; }
    if (l.indexOf("en") === 0) break; // inglês aparece antes do português: prefere inglês
  }
  if (wantsPt) return;
  // veio de um link interno (ex.: clicou em PT sem JS ter salvo): não força
  if (document.referrer && document.referrer.indexOf(location.origin + "/") === 0) return;
  var slug = path.replace(/^\/|\/$/g, "").replace(/\/index\.html$/, "");
  if (!(slug in MAP)) return;
  setPref("en");
  location.replace("/en/" + (MAP[slug] ? MAP[slug] + "/" : "") + location.search + location.hash);
})();
