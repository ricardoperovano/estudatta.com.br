/*
  Google Analytics 4 com consentimento (LGPD).
  Nada é carregado antes de a pessoa aceitar: o gtag.js só entra na página depois do "Aceitar".
  A escolha fica em localStorage ("estudatta.consent" = "granted" | "denied") por 12 meses.
  O link com [data-cookie-prefs] (rodapé) reabre o aviso para mudar a escolha.
*/
(function () {
  var KEY = "estudatta.consent";
  var GA_ID = "G-8XFNHTHEX7";
  var MAX_AGE = 365 * 24 * 60 * 60 * 1000;
  var loaded = false;

  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return null;
      var v = JSON.parse(raw);
      if (!v || !v.at || Date.now() - v.at > MAX_AGE) return null;
      return v.choice;
    } catch (e) {
      return null;
    }
  }
  function write(choice) {
    try {
      localStorage.setItem(KEY, JSON.stringify({ choice: choice, at: Date.now() }));
    } catch (e) {}
  }

  function loadGa() {
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "granted" });
    gtag("js", new Date());
    gtag("config", GA_ID);
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
  }

  function removeBanner() {
    var el = document.getElementById("cookie-banner");
    if (el) el.remove();
  }

  function showBanner() {
    if (document.getElementById("cookie-banner")) return;
    var box = document.createElement("section");
    box.id = "cookie-banner";
    box.className = "cookie-banner";
    box.setAttribute("role", "region");
    box.setAttribute("aria-label", "Aviso de cookies");
    box.innerHTML =
      '<p>Usamos o Google Analytics para saber quais páginas do site são visitadas. Ele só é ativado se você aceitar; sem isso, nenhum cookie de métricas é gravado. <a href="/privacidade/#cookies-titulo">Saiba mais</a>.</p>' +
      '<div class="cookie-actions"><button type="button" class="btn btn-secondary" data-choice="denied">Recusar</button><button type="button" class="btn btn-primary" data-choice="granted">Aceitar</button></div>';
    box.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-choice]");
      if (!b) return;
      var choice = b.getAttribute("data-choice");
      write(choice);
      removeBanner();
      if (choice === "granted") loadGa();
    });
    document.body.appendChild(box);
  }

  function init() {
    var choice = read();
    if (choice === "granted") loadGa();
    else if (choice !== "denied") showBanner();
    document.addEventListener("click", function (e) {
      var a = e.target.closest("[data-cookie-prefs]");
      if (!a) return;
      e.preventDefault();
      showBanner();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
