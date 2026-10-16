

(function () {
  "use strict";

  var ENDPOINT = "https://script.google.com/macros/s/AKfycbymjkeYx25wV7Wu-HfBfLkhCfSRkKP6F4BpzRoy-44_8vHiqWVJ4auXm20VhrG5BhqK/exec";

  if (!ENDPOINT || ENDPOINT.indexOf("script.google.com") === -1) return;

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

      if (typeof fetch === "function") {
        fetch(ENDPOINT, {
          method: "POST",
          mode: "no-cors",
          keepalive: true,
          headers: { "Content-Type": "text/plain;charset=UTF-8" },
          body: body
        })["catch"](function () {   });
        return;
      }

      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "text/plain;charset=UTF-8" }));
      }
    } catch (err) {   }
  }

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

              if (key === "access_key" || key === "redirect" ||
                  key === "subject" || key === "from_name") return;
              data[key] = value;
            });
          } catch (err) {   }
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
