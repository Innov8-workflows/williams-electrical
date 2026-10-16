

(function () {
  "use strict";


  function track(name, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, params || {});
    }
  }


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



  if (/\/thanks(\.html)?$/i.test(window.location.pathname)) {
    track("generate_lead", {
      method: "contact_form",
      currency: "GBP",
      value: 0
    });
  }
})();
