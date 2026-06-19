/*
 * Williams Electrical — GA4 conversion tracking
 * Fires Key Events for phone taps, email taps and successful form leads.
 * Requires the gtag.js snippet (G-Z7KN2ZK7LP) already loaded in <head>.
 */
(function () {
  "use strict";

  // Safe wrapper: never break the page if gtag isn't ready.
  function track(name, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, params || {});
    }
  }

  // 1) Click-to-call — one delegated listener covers every tel: link.
  document.addEventListener("click", function (e) {
    var link = e.target.closest("a");
    if (!link) return;
    var href = link.getAttribute("href") || "";

    if (href.indexOf("tel:") === 0) {
      track("contact_phone_call", {
        method: "phone",
        phone_number: href.replace("tel:", ""),
        link_location: link.textContent.trim().slice(0, 80) || "tel link"
      });
    } else if (href.indexOf("mailto:") === 0) {
      track("contact_email", {
        method: "email",
        email_address: href.replace("mailto:", "")
      });
    }
  });

  // 2) Form lead — Web3Forms redirects to /thanks.html only on a genuine
  //    successful submission, so this page view IS a confirmed lead.
  if (/\/thanks(\.html)?$/i.test(window.location.pathname)) {
    track("generate_lead", {
      method: "contact_form",
      currency: "GBP",
      value: 0
    });
  }
})();
