/*
  Estudatta — comportamento do site (sem framework).
  - Ajusta os links do app ao ambiente (config.js).
  - Planos: carrega o catálogo público da API; sem resposta, mantém o conteúdo estático
    ("Valor a definir"). Nunca inventa preço.
  - Formulários de novidades e de contato: enviam para a API pública.
*/
(function () {
  "use strict";
  var cfg = window.ESTUDATTA || { appUrl: "https://app.estudatta.com.br", apiUrl: "https://app.estudatta.com.br", productionAppUrl: "https://app.estudatta.com.br" };
  // Idioma da página: em /en/ as mensagens dos formulários vêm em inglês e os planos ficam com o
  // HTML estático traduzido (o catálogo da API é em português).
  var EN = (document.documentElement.lang || "").slice(0, 2) === "en";
  var L = EN
    ? { sending: "Sending…", sendFail: "Couldn’t send right now.", sendFailRetry: "Couldn’t send right now. Try again in a moment.", waitlistOk: "Done. We’ll email you when there’s news.", contactFail: "Couldn’t send the message.", contactOk: "Message received. We’ll reply to the email you gave.", offline: "No connection to the server. Your message is still in the form; try again in a moment." }
    : { sending: "Enviando…", sendFail: "Não foi possível enviar agora.", sendFailRetry: "Não foi possível enviar agora. Tente de novo em instantes.", waitlistOk: "Pronto. Avisamos você por e-mail quando houver novidades.", contactFail: "Não foi possível enviar a mensagem.", contactOk: "Mensagem recebida. Respondemos pelo e-mail informado.", offline: "Sem conexão com o servidor. Sua mensagem continua no formulário; tente de novo em instantes." };

  // ---- Links do app -------------------------------------------------------
  if (cfg.appUrl !== cfg.productionAppUrl) {
    document.querySelectorAll('a[href^="' + cfg.productionAppUrl + '"]').forEach(function (a) {
      a.href = cfg.appUrl + a.getAttribute("href").slice(cfg.productionAppUrl.length);
    });
  }

  function api(path, options) {
    options = options || {};
    var headers = { Accept: "application/json" };
    if (options.body) headers["Content-Type"] = "application/json";
    return fetch(cfg.apiUrl + "/api/v1" + path, {
      method: options.method || "GET",
      headers: headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
      credentials: "omit",
    }).then(function (res) {
      return res
        .json()
        .catch(function () {
          return {};
        })
        .then(function (data) {
          if (!res.ok) {
            var msg = (data && data.error && data.error.message) || L.sendFail;
            throw new Error(msg);
          }
          return data;
        });
    });
  }

  function setBusy(button, busy, label) {
    if (!button) return;
    if (busy) {
      button.dataset.label = button.textContent;
      button.disabled = true;
      button.innerHTML = '<span class="spinner" aria-hidden="true"></span>' + (label || L.sending);
    } else {
      button.disabled = false;
      button.textContent = button.dataset.label || button.textContent;
    }
  }

  // ---- Planos ---------------------------------------------------------------
  var catalog = null;
  var interval = "month";

  function brl(cents) {
    if (cents === null || cents === undefined) return "Valor a definir";
    return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(cents / 100);
  }

  function priceLabel(plan, iv) {
    if (plan.code === "free") return "R$ 0";
    var list = plan.prices || [];
    var p = list.filter(function (x) { return x.interval === iv; })[0] || list[0];
    return p ? brl(p.amount_cents) : "Valor a definir";
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function priceCents(plan, iv) {
    var p = (plan.prices || []).filter(function (x) { return x.interval === iv; })[0];
    return p ? p.amount_cents : null;
  }

  function planNote(plan) {
    if (plan.code === "free") return "Para sempre, sem cartão";
    var month = priceCents(plan, "month");
    var year = priceCents(plan, "year");
    if (interval === "year" && year != null) return "equivale a " + brl(Math.round(year / 12)) + " por mês";
    if (interval === "month" && year != null) return "ou " + brl(year) + " por ano (" + brl(Math.round(year / 12)) + " por mês)";
    return month == null ? "" : "";
  }

  function renderPlans() {
    if (!catalog) return;
    document.querySelectorAll("[data-plans]").forEach(function (box) {
      box.innerHTML = catalog.plans
        .map(function (p) {
          var price = priceLabel(p, interval);
          var unset = price === "Valor a definir";
          var cta = p.code === "free" ? "Começar grátis" : unset ? "Avisar quando abrir" : "Começar com o " + p.name;
          var per = p.code === "free" ? "" : ' <small>/ ' + (interval === "year" ? "ano" : "mês") + "</small>";
          return (
            '<article class="card plan' + (p.recommended ? " card-accent plan-accent" : "") + '">' +
            '<div class="plan-head"><span class="plan-name">' + esc(p.name) + "</span>" +
            (p.recommended ? '<span class="tag tag-accent">Recomendado</span>' : "") + "</div>" +
            '<span class="plan-price tnum">' + esc(price) + per + "</span>" +
            '<span class="plan-note tnum">' + esc(planNote(p)) + "</span>" +
            "<ul>" + (p.features || []).map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("") + "</ul>" +
            '<a class="btn ' + (p.recommended ? "btn-primary" : "btn-secondary") + '" href="' + cfg.appUrl + '/cadastro">' + esc(cta) + "</a>" +
            "</article>"
          );
        })
        .join("");
    });
    renderCompare();
  }

  var limitRows = [
    ["max_active_activities", "Objetivos ativos", function (v) { return v == null ? "Sem limite" : String(v); }],
    ["max_materials", "Materiais cadastrados", function (v) { return v == null ? "Sem limite" : "Até " + v; }],
    ["materials_storage_mb", "Espaço para arquivos", function (v) { return v == null ? "Sem limite" : v >= 1024 ? String(Math.round((v / 1024) * 10) / 10).replace(".", ",") + " GB" : v + " MB"; }],
    ["recovery_distribution", "Saldo e recuperação da pendência", function (v) { return v ? "Sim" : "Não"; }],
    ["reports", "Relatórios", function (v) { return v === "full" ? "Semana, mês e trimestre" : v === "basic" ? "Semana" : String(v); }],
    ["reminders", "Lembretes", function (v) { return v === "full" ? "Completos + resumo por e-mail" : v === "basic" ? "Horário planejado" : String(v); }],
    ["ai_monthly_actions", "IA (organizar, planejar e conversar com o Tatá), por mês", function (v) { return v == null ? "Sem limite mensal" : Number(v) > 0 ? v + " ações" : "Não incluída"; }],
    ["tata_voice_monthly", "Tatá com voz natural, por mês", function (v) { return v == null ? "Sem limite" : Number(v) > 0 ? v + " falas" : "Só a voz do aparelho"; }],
    ["ai_daily_actions", "IA: máximo por dia", function (v) { return Number(v) > 0 ? "Até " + v + " ações" : "Não incluída"; }],
    ["auto_planning", "Distribuição automática das tarefas", function (v) { return v ? "Sim" : "Não"; }],
  ];

  function renderCompare() {
    var table = document.querySelector("[data-compare]");
    if (!table || !catalog) return;
    var plans = catalog.plans;
    var head = '<tr><th scope="col">Recurso</th>' + plans.map(function (p) { return '<th scope="col"' + (p.recommended ? ' class="rec"' : "") + ">" + esc(p.name) + "</th>"; }).join("") + "</tr>";
    function row(label, values) {
      return '<tr><th scope="row">' + esc(label) + "</th>" + values.map(function (v) { return "<td>" + esc(v) + "</td>"; }).join("") + "</tr>";
    }
    var rows = [row("Valor mensal", plans.map(function (p) { return priceLabel(p, "month"); })), row("Valor anual", plans.map(function (p) { return priceLabel(p, "year"); }))];
    limitRows.forEach(function (r) {
      var has = plans.some(function (p) { return p.limits && r[0] in p.limits; });
      if (has) rows.push(row(r[1], plans.map(function (p) { return p.limits && r[0] in p.limits ? r[2](p.limits[r[0]]) : "—"; })));
    });
    // Recursos presentes em todos os planos, inclusive no Gratuito
    ["Revisões automáticas", "Simulados e taxa de acerto", "Conquistas, níveis e desafios", "Companheiro Tatá"].forEach(function (label) {
      rows.push(row(label, plans.map(function () { return "Sim"; })));
    });
    rows.push(row("Histórico completo das sessões", plans.map(function () { return "Sim"; })));
    rows.push(row("Exportação dos seus dados", plans.map(function () { return "Sim"; })));
    table.querySelector("thead").innerHTML = head;
    table.querySelector("tbody").innerHTML = rows.join("");
    var title = document.querySelector("[data-compare-title]");
    if (title) title.textContent = plans.map(function (p) { return p.name; }).join(" × ");
  }

  document.querySelectorAll("[data-interval]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      interval = btn.getAttribute("data-interval");
      document.querySelectorAll("[data-interval]").forEach(function (b) {
        b.setAttribute("aria-checked", String(b === btn));
      });
      if (catalog) renderPlans();
      else {
        // catálogo indisponível: alterna os valores estáticos da página
        document.querySelectorAll("[data-price]").forEach(function (el) {
          el.innerHTML = esc(el.getAttribute(interval === "year" ? "data-year" : "data-month")) + ' <small data-per>/ ' + (interval === "year" ? "ano" : "mês") + "</small>";
        });
        document.querySelectorAll("[data-note]").forEach(function (el) {
          el.textContent = el.getAttribute(interval === "year" ? "data-year" : "data-month");
        });
      }
    });
  });

  if (!EN && document.querySelector("[data-plans], [data-compare]")) {
    api("/public/plans")
      .then(function (data) {
        if (data && Array.isArray(data.plans) && data.plans.length) {
          catalog = data;
          renderPlans();
        }
      })
      .catch(function () {
        /* mantém o conteúdo estático */
      });
  }

  // ---- Lista de novidades -----------------------------------------------------
  document.querySelectorAll("form[data-waitlist]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type="email"]');
      var button = form.querySelector('button[type="submit"]');
      var msg = form.querySelector(".form-msg");
      setBusy(button, true, L.sending);
      api("/public/waitlist", { method: "POST", body: { email: input.value.trim(), source: form.getAttribute("data-waitlist") || "site" } })
        .then(function () {
          form.innerHTML = '<p class="form-msg ok">' + L.waitlistOk + "</p>";
        })
        .catch(function (err) {
          setBusy(button, false);
          msg.className = "form-msg error";
          msg.textContent = err.message || L.sendFailRetry;
        });
    });
  });

  // ---- Contato ----------------------------------------------------------------
  var contact = document.querySelector("form[data-contact]");
  if (contact) {
    var message = contact.querySelector("#ct-message");
    var counter = contact.querySelector("[data-count]");
    if (message && counter) {
      var update = function () { counter.textContent = String(message.value.length); };
      message.addEventListener("input", update);
      update();
    }
    contact.addEventListener("submit", function (e) {
      e.preventDefault();
      var button = contact.querySelector('button[type="submit"]');
      var status = contact.querySelector("[data-status]");
      var data = new FormData(contact);
      setBusy(button, true, L.sending);
      status.hidden = true;
      api("/public/contact", {
        method: "POST",
        body: {
          name: String(data.get("name") || "").trim() || null,
          email: String(data.get("email") || "").trim(),
          subject: String(data.get("subject") || ""),
          message: String(data.get("message") || "").trim(),
        },
      })
        .then(function (res) {
          if (res && res.ok === false) throw new Error(res.message || L.contactFail);
          var done = document.querySelector("[data-contact-done]");
          done.querySelector("[data-confirmation]").textContent = (res && res.message) || L.contactOk;
          contact.hidden = true;
          done.hidden = false;
        })
        .catch(function (err) {
          setBusy(button, false);
          status.hidden = false;
          status.querySelector("[data-error]").textContent = err.message === "Failed to fetch" ? L.offline : err.message;
        });
    });
    var again = document.querySelector("[data-contact-again]");
    if (again) {
      again.addEventListener("click", function () {
        contact.reset();
        contact.hidden = false;
        document.querySelector("[data-contact-done]").hidden = true;
        setBusy(contact.querySelector('button[type="submit"]'), false);
      });
    }
  }
})();
