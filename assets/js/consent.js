(function () {
  "use strict";
  var GA4_ID = "G-Z7KN2ZK7LP";
  var KEY = "we-consent";
  var banner = null;

  function getChoice() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setChoice(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function loadGa() {
    if (window.__weGaLoaded) return;
    window.__weGaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", GA4_ID);
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_ID;
    document.head.appendChild(s);
  }

  function clearGaCookies() {
    var host = location.hostname.replace(/^www\./, "");
    var domains = ["", location.hostname, "." + host];
    document.cookie.split(";").forEach(function (c) {
      var name = c.split("=")[0].trim();
      if (!/^_ga/.test(name)) return;
      domains.forEach(function (d) {
        document.cookie = name + "=; Max-Age=0; path=/" + (d ? "; domain=" + d : "");
      });
    });
  }

  function choose(v) {
    setChoice(v);
    if (banner) banner.hidden = true;
    if (v === "granted") { loadGa(); return; }
    window["ga-disable-" + GA4_ID] = true;
    clearGaCookies();
    if (window.__weGaLoaded) location.reload();
  }

  function showBanner() {
    if (!banner) {
      var css = document.createElement("style");
      css.textContent =
        ".cookie-actions{display:flex;gap:10px;flex-shrink:0}" +
        ".cookie-actions .cookie-btn{min-width:110px}" +
        "@media (max-width:540px){.cookie-actions{width:100%}.cookie-actions .cookie-btn{flex:1;width:auto;min-width:0}}";
      document.head.appendChild(css);
      banner = document.createElement("div");
      banner.id = "cookie-banner";
      banner.className = "cookie-banner";
      banner.setAttribute("role", "region");
      banner.setAttribute("aria-label", "Cookie choice");
      banner.innerHTML =
        "<p>We'd like to use Google Analytics cookies to see how people find and use this site. " +
        "They are only set if you accept. <a href=\"/cookies.html\">Cookie policy</a></p>" +
        "<div class=\"cookie-actions\">" +
        "<button type=\"button\" class=\"cookie-btn\" data-choice=\"denied\">Decline</button>" +
        "<button type=\"button\" class=\"cookie-btn\" data-choice=\"granted\">Accept</button>" +
        "</div>";
      banner.addEventListener("click", function (e) {
        var b = e.target.closest("[data-choice]");
        if (b) choose(b.getAttribute("data-choice"));
      });
      document.body.appendChild(banner);
    }
    banner.hidden = false;
  }

  if (getChoice() === "granted") loadGa();
  else if (getChoice() === "denied") clearGaCookies();

  function init() {
    if (!getChoice()) showBanner();
    document.addEventListener("click", function (e) {
      var t = e.target.closest("[data-cookie-settings]");
      if (!t) return;
      e.preventDefault();
      showBanner();
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
