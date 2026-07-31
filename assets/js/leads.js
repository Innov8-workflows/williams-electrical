/*
 * Williams Electrical — lead capture
 * Built by Innov8 Workflows.
 *
 * Sends three kinds of lead to the Google Apps Script endpoint, which logs
 * them to the "Williams Electrical Leads" sheet and emails a notification:
 *
 *   1. Contact form submissions  (type: "Contact form")
 *   2. WhatsApp widget / link clicks (type: "WhatsApp")
 *   3. Click-to-call taps        (type: "Phone call")
 *
 * The contact form still POSTs to Web3Forms as before, so Alfie keeps
 * receiving his own email — this runs alongside it, it does not replace it.
 */
(function () {
  "use strict";

  // Apps Script Web App URL (Deploy > New deployment > Web app).
  // Project: "Williams Electrical - Lead Capture", bound to the
  // "Williams Electrical Leads" sheet.
  var ENDPOINT = "https://script.google.com/macros/s/AKfycbymjkeYx25wV7Wu-HfBfLkhCfSRkKP6F4BpzRoy-44_8vHiqWVJ4auXm20VhrG5BhqK/exec";

  // Not deployed yet? Do nothing rather than throwing on every page.
  if (!ENDPOINT || ENDPOINT.indexOf("script.google.com") === -1) return;

  /* Session-scoped visitor id, used server-side to collapse duplicate
     call/WhatsApp taps from the same person within 10 minutes. */
  function clientId() {
    try {
      var k = "we-cid";
      var v = sessionStorage.getItem(k);
      if (!v) {
        v = Math.random().toString(36).slice(2) + Date.now().toString(36);
        sessionStorage.setItem(k, v);
      }
      return v;
    } catch (err) {
      return "";
    }
  }

  function send(payload) {
    try {
      payload.page = location.pathname + location.search;
      payload.referrer = document.referrer || "";
      payload.device = navigator.userAgent || "";
      payload.cid = clientId();

      var body = JSON.stringify(payload);

      /* sendBeacon survives the page navigating away, which matters because
         tel:, wa.me and the form POST all leave the page immediately.
         text/plain keeps it a "simple" request, so no CORS preflight. */
      if (navigator.sendBeacon) {
        var blob = new Blob([body], { type: "text/plain;charset=UTF-8" });
        if (navigator.sendBeacon(ENDPOINT, blob)) return;
      }

      fetch(ENDPOINT, {
        method: "POST",
        mode: "no-cors",
        keepalive: true,
        headers: { "Content-Type": "text/plain;charset=UTF-8" },
        body: body
      })["catch"](function () { /* never break the page */ });
    } catch (err) { /* never break the page */ }
  }

  /* 1) Call + WhatsApp clicks — one delegated listener covers every link,
        including the floating widgets and anything added later. */
  document.addEventListener("click", function (e) {
    var el = e.target;
    if (!el || typeof el.closest !== "function") return;

    var a = el.closest("a");
    if (!a) return;

    var href = a.getAttribute("href") || "";

    if (href.indexOf("tel:") === 0) {
      send({ type: "Phone call", phone: href.replace("tel:", "") });
    } else if (/(^|\/\/)(wa\.me|api\.whatsapp\.com)/.test(href)) {
      send({ type: "WhatsApp" });
    }
  }, true);

  /* 2) Contact form — fires on submit, just before the native POST to
        Web3Forms carries the visitor off to /thanks.html. */
  function wireForms() {
    var forms = document.querySelectorAll("form.contact-form");
    for (var i = 0; i < forms.length; i++) {
      (function (form) {
        if (form.getAttribute("data-leads-wired")) return;
        form.setAttribute("data-leads-wired", "1");

        form.addEventListener("submit", function () {
          var data = { type: "Contact form" };
          try {
            var fd = new FormData(form);
            fd.forEach(function (value, key) {
              // Skip Web3Forms plumbing — it is not lead data.
              if (key === "access_key" || key === "redirect" ||
                  key === "subject" || key === "from_name") return;
              data[key] = value;
            });
          } catch (err) { /* still send what we have */ }
          send(data);
        });
      })(forms[i]);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wireForms);
  } else {
    wireForms();
  }
})();
