"""Williams Electrical — multi-page site generator.

Reads content from _data.py, renders templates, writes:
 - 8 service pages   (services/<slug>.html)
 - 11 area pages   (areas/<slug>.html)
 - services hub   (services/index.html)
 - areas hub    (areas/index.html)
 - about page    (about.html)
 - contact page   (contact.html)
 - sitemap.xml, robots.txt, CNAME
"""
import json, re, sys
from pathlib import Path
from _data import (
 DOMAIN, BIZ_NAME, OWNER_NAME, BIZ_PHONE, BIZ_PHONE_DISPLAY, BIZ_EMAIL,
 BIZ_ADDR_STREET, BIZ_ADDR_LOCALITY, BIZ_ADDR_REGION, BIZ_ADDR_POSTCODE, BIZ_ADDR_COUNTRY, BIZ_ADDR_FULL,
 BIZ_LAT, BIZ_LON, GOOGLE_REVIEWS, GOOGLE_RATING, GOOGLE_REVIEWS_URL,
 SOCIAL_FACEBOOK, SOCIAL_INSTAGRAM, PUBLIC_LIABILITY, WEB3FORMS_KEY,
 YEARS, WA_BASE,
 SERVICES, AREAS,
)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).parent

# Google Analytics 4 measurement ID (kept here so a rebuild never drops the tag)
GA4_ID = "G-Z7KN2ZK7LP"

# ──────────────────────────────────────────
# Shared SVGs / icons
# ──────────────────────────────────────────

ICON_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 10.8 19.79 19.79 0 01.01 2.18 2 2 0 012 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92z"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" fill="none"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" stroke-width="2"/><circle cx="12" cy="10" r="3" stroke-width="2"/></svg>'
ICON_FB = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>'
ICON_IG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>'
ICON_WA = '<svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0.16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413"/></svg>'

# ──────────────────────────────────────────
# Path helpers — generate prefix to root from any page depth
# ──────────────────────────────────────────

def root_prefix(depth):
 """Return './' for root pages, '../' for /services/*.html etc."""
 return "../" if depth == 1 else "./"

# ──────────────────────────────────────────
# Head — shared between all pages
# ──────────────────────────────────────────

def head(title, desc, canonical_path, og_image_path="/assets/img/hero-2.jpg", schema_extra=None, depth=0):
 """Generate <head> + opening <body> with full SEO meta."""
 prefix = root_prefix(depth)
 abs_canonical = f"{DOMAIN}{canonical_path}"
 abs_og_image = f"{DOMAIN}{og_image_path}"

 # Default LocalBusiness schema (every page gets this)
 schemas = [{
  "@context": "https://schema.org",
  "@type": "Electrician",
  "@id": f"{DOMAIN}#electrician",
  "name": BIZ_NAME,
  "image": abs_og_image,
  "url": DOMAIN,
  "telephone": BIZ_PHONE,
  "email": BIZ_EMAIL,
  "address": {
   "@type": "PostalAddress",
   "streetAddress": BIZ_ADDR_STREET,
   "addressLocality": BIZ_ADDR_LOCALITY,
   "addressRegion": BIZ_ADDR_REGION,
   "postalCode": BIZ_ADDR_POSTCODE,
   "addressCountry": BIZ_ADDR_COUNTRY,
  },
  "geo": {
   "@type": "GeoCoordinates",
   "latitude": BIZ_LAT,
   "longitude": BIZ_LON,
  },
  "openingHoursSpecification": [
   {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "08:00", "closes": "18:00"},
   {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday"], "opens": "09:00", "closes": "16:00"},
  ],
  "areaServed": [{"@type": "City", "name": a["name"]} for a in AREAS],
  "priceRange": "££",
  "aggregateRating": {
   "@type": "AggregateRating",
   "ratingValue": GOOGLE_RATING,
   "reviewCount": GOOGLE_REVIEWS,
  },
  "sameAs": [
   GOOGLE_REVIEWS_URL,
  ],
 }]
 if schema_extra:
  schemas.append(schema_extra)

 schema_block = "\n".join(f'<script type="application/ld+json">{json.dumps(s, indent=0)}</script>' for s in schemas)

 return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA4_ID}');
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="{BIZ_NAME}">
<meta name="theme-color" content="#5C7762">
<link rel="canonical" href="{abs_canonical}">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:locale" content="en_GB">
<meta property="og:site_name" content="{BIZ_NAME}">
<meta property="og:url" content="{abs_canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{abs_og_image}">
<meta property="og:image:width" content="1600">
<meta property="og:image:height" content="900">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{abs_og_image}">

<!-- Geo -->
<meta name="geo.region" content="GB-WAR">
<meta name="geo.placename" content="Warwick">
<meta name="geo.position" content="{BIZ_LAT};{BIZ_LON}">
<meta name="ICBM" content="{BIZ_LAT}, {BIZ_LON}">

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/css/pages.css">

<!-- Favicons -->
<link rel="icon" type="image/svg+xml" href="{prefix}assets/img/favicons/favicon.svg">
<link rel="icon" type="image/x-icon" href="{prefix}favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="{prefix}assets/img/favicons/favicon-16.png">
<link rel="icon" type="image/png" sizes="32x32" href="{prefix}assets/img/favicons/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="{prefix}assets/img/favicons/favicon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="{prefix}assets/img/favicons/favicon-180.png">
<link rel="manifest" href="{prefix}site.webmanifest">

{schema_block}
</head>
<body>"""

# ──────────────────────────────────────────
# Navigation — consistent across all pages
# ──────────────────────────────────────────

def nav(current_section="", depth=0):
 """Render the top navbar.

 current_section ∈ {"home","services","areas","about","contact",""}
 """
 prefix = root_prefix(depth)
 act = lambda s: ' class="active"' if s == current_section else ""
 return f"""
<nav id="navbar">
 <div class="nav-inner">
 <div class="nav-left">
  <a href="tel:{BIZ_PHONE}" class="nav-call">
  {ICON_PHONE} {BIZ_PHONE_DISPLAY}
  </a>
 </div>
 <div class="nav-logo-wrap">
  <a href="{prefix}index.html" aria-label="{BIZ_NAME} home">
  <img src="{prefix}assets/img/logo.webp" alt="{BIZ_NAME} logo" class="nav-logo" width="120" height="54">
  </a>
 </div>
 <div class="nav-links">
  <a href="{prefix}services/"{act('services')}>Services</a>
  <a href="{prefix}areas/"{act('areas')}>Areas</a>
  <a href="{prefix}work.html"{act('work')}>Our Work</a>
  <a href="{prefix}about.html"{act('about')}>About</a>
  <a href="{prefix}contact.html"{act('contact')}>Contact</a>
 </div>
 <button class="hamburger" onclick="toggleMenu()" aria-label="Menu">
  <span></span><span></span><span></span>
 </button>
 </div>
 <div class="mobile-menu" id="mobileMenu">
 <a href="{prefix}services/">Services</a>
 <a href="{prefix}areas/">Areas Covered</a>
 <a href="{prefix}work.html">Our Work</a>
 <a href="{prefix}about.html">About Alfie</a>
 <a href="{prefix}contact.html">Contact</a>
 <a href="tel:{BIZ_PHONE}">📞 {BIZ_PHONE_DISPLAY}</a>
 </div>
</nav>"""

# ──────────────────────────────────────────
# Footer
# ──────────────────────────────────────────

def footer(depth=0):
 prefix = root_prefix(depth)
 return f"""
<footer id="footer">
 <div class="footer-inner">
 <div class="footer-top">
  <div class="footer-brand">
  <img src="{prefix}assets/img/logo.webp" alt="{BIZ_NAME}" width="120" height="56">
  <p>Expert electrical services across Warwick and Warwickshire. Fully qualified and insured (£4m public liability), trusted by homeowners and businesses for over {YEARS} years.</p>
  <div class="footer-socials">
   <a href="https://wa.me/447360528992" aria-label="WhatsApp" target="_blank" rel="noopener">{ICON_WA}</a>
   <a href="{SOCIAL_FACEBOOK}" aria-label="Facebook" target="_blank" rel="noopener">{ICON_FB}</a>
   <a href="{SOCIAL_INSTAGRAM}" aria-label="Instagram" target="_blank" rel="noopener">{ICON_IG}</a>
  </div>
  </div>
  <div class="footer-col">
  <h5>Services</h5>
  <ul>
   {"".join(f'<li><a href="{prefix}services/{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES[:5])}
   <li><a href="{prefix}services/">All Services →</a></li>
  </ul>
  </div>
  <div class="footer-col">
  <h5>Areas Covered</h5>
  <ul>
   {"".join(f'<li><a href="{prefix}areas/{a["slug"]}.html">{a["name"]}</a></li>' for a in AREAS[:5])}
   <li><a href="{prefix}areas/">All Areas →</a></li>
  </ul>
  </div>
  <div class="footer-col">
  <h5>Contact</h5>
  <ul>
   <li><a href="tel:{BIZ_PHONE}">{BIZ_PHONE_DISPLAY}</a></li>
   <li><a href="mailto:{BIZ_EMAIL}">{BIZ_EMAIL}</a></li>
   <li>Warwick {BIZ_ADDR_POSTCODE}</li>
   <li><a href="{prefix}about.html">About Alfie</a></li>
  </ul>
  </div>
 </div>
 <div class="footer-bottom">
  <p>© 2026 {BIZ_NAME}. All rights reserved. · BS 7671 Compliant</p>
  <p class="footer-policies">
  <a href="{prefix}privacy.html">Privacy Policy</a>
  <span>·</span>
  <a href="{prefix}cookies.html">Cookie Policy</a>
  <span>·</span>
  <a href="{prefix}sitemap.xml">Sitemap</a>
  </p>
 </div>
 <p class="footer-credit">Made by <a href="https://innov8workflows.co.uk/index.html" target="_blank" rel="noopener">innov8workflows.co.uk</a></p>
 </div>
</footer>

<!-- Floating CTAs -->
<div class="float-actions">
 <a href="https://wa.me/447360528992?text=Hi%20Alfie%2C%20I%27d%20like%20to%20get%20a%20quote%20please." target="_blank" rel="noopener" class="float-btn float-wa" aria-label="WhatsApp">{ICON_WA}</a>
 <a href="tel:{BIZ_PHONE}" class="float-btn float-call" aria-label="Call {BIZ_NAME}">{ICON_PHONE}</a>
</div>

<!-- Cookie banner (essential cookies only, dismissed via localStorage) -->
<div id="cookie-banner" class="cookie-banner" hidden>
 <p>This site uses essential cookies only — no tracking, no third-party analytics. <a href="{prefix}cookies.html">Read more</a>.</p>
 <button type="button" onclick="acceptCookies()" class="cookie-btn">Got it</button>
</div>

<script>
const nav = document.getElementById('navbar');
window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 16), {{ passive: true }});
function toggleMenu() {{ document.getElementById('mobileMenu').classList.toggle('open'); }}
function toggleFaq(btn) {{ btn.parentElement.classList.toggle('open'); }}
function acceptCookies() {{
 try {{ localStorage.setItem('we-cookies-ok', '1'); }} catch(e) {{}}
 var b = document.getElementById('cookie-banner');
 if (b) {{ b.hidden = true; b.style.display = 'none'; }}
}}
(function () {{
 try {{
 if (!localStorage.getItem('we-cookies-ok')) {{
  document.addEventListener('DOMContentLoaded', function () {{
  var b = document.getElementById('cookie-banner');
  if (b) b.hidden = false;
  }});
 }}
 }} catch(e) {{}}
}})();
</script>

<!-- GA4 conversion tracking + lead capture to Google Sheet -->
<script defer src="{prefix}assets/js/tracking.js"></script>
<script defer src="{prefix}assets/js/leads.js"></script>
</body>
</html>"""

# ──────────────────────────────────────────
# Final CTA section
# ──────────────────────────────────────────

def cta_final(headline_main="Let's get your", headline_em="electrics sorted"):
 return f"""
<section class="cta-final">
 <div class="cta-final-inner">
 <div class="cta-final-eyebrow">Ready when you are</div>
 <h2>{headline_main} <em>{headline_em}</em>.</h2>
 <p>Free quote, no call-out fee, fast response. Call Alfie directly — you'll speak to a fully qualified electrician, not a call centre.</p>
 <div class="cta-final-actions">
  <a href="tel:{BIZ_PHONE}" class="btn btn-primary">{ICON_PHONE} Call Alfie · {BIZ_PHONE_DISPLAY}</a>
  <a href="{WA_BASE}?text=Hi%20Alfie%2C%20I%27d%20like%20to%20get%20a%20quote%20please." target="_blank" rel="noopener" class="btn btn-outline">Message on WhatsApp</a>
 </div>
 </div>
</section>"""

# ──────────────────────────────────────────
# Breadcrumbs
# ──────────────────────────────────────────

def breadcrumbs(trail, depth=0):
 """trail = [(label, href),...]; last item is current page (no link)."""
 prefix = root_prefix(depth)
 parts = []
 for i, (label, href) in enumerate(trail):
  if i == len(trail) - 1:
   parts.append(f"<span aria-current=\"page\">{label}</span>")
  else:
   full_href = href if href.startswith("http") else f"{prefix}{href}"
   parts.append(f'<a href="{full_href}">{label}</a>')
 return f'<nav class="breadcrumbs" aria-label="Breadcrumb">{"<span class=\"sep\">/</span>".join(parts)}</nav>'

def breadcrumb_schema(trail):
 """JSON-LD breadcrumb schema."""
 items = []
 for i, (label, href) in enumerate(trail):
  item = {"@type": "ListItem", "position": i + 1, "name": label}
  if href and not href.startswith("#"):
   item["item"] = f"{DOMAIN}/{href}" if not href.startswith("http") else href
  items.append(item)
 return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}

# ──────────────────────────────────────────
# Sidebar (used on service + area pages)
# ──────────────────────────────────────────

def sidebar_quote_card():
 return f"""
<aside class="sidebar-card">
 <h4>Quick quote</h4>
 <p>Call or message Alfie directly — fully qualified, no call-centre, free quotes always.</p>
 <a href="tel:{BIZ_PHONE}" class="btn btn-primary" style="margin-bottom:10px;">{ICON_PHONE} Call {BIZ_PHONE_DISPLAY}</a>
 <a href="{WA_BASE}?text=Hi%20Alfie%2C%20I%27d%20like%20to%20get%20a%20quote%20please." target="_blank" rel="noopener" class="btn btn-outline">Message on WhatsApp</a>
</aside>"""

def sidebar_services_list(current_slug=None, depth=1):
 prefix = root_prefix(depth)
 items = []
 for s in SERVICES:
  active = ' class="active"' if s["slug"] == current_slug else ""
  items.append(f'<a href="{prefix}services/{s["slug"]}.html"{active}>{s["name"]}</a>')
 return f"""
<aside class="sidebar-card">
 <h4>All services</h4>
 <div class="sidebar-list">{"".join(items)}</div>
</aside>"""

def sidebar_areas_list(current_slug=None, depth=1):
 prefix = root_prefix(depth)
 items = []
 for a in AREAS:
  active = ' class="active"' if a["slug"] == current_slug else ""
  items.append(f'<a href="{prefix}areas/{a["slug"]}.html"{active}>{a["name"]}</a>')
 return f"""
<aside class="sidebar-card">
 <h4>Areas covered</h4>
 <div class="sidebar-list">{"".join(items)}</div>
</aside>"""

def render_faqs(faqs):
 parts = ['<div class="faq-list">']
 for q, a in faqs:
  parts.append(f"""
  <div class="faq-item">
   <button class="faq-q" onclick="toggleFaq(this)">{q}<span class="faq-icon"></span></button>
   <div class="faq-a"><p>{a}</p></div>
  </div>""")
 parts.append("</div>")
 return "\n".join(parts)

def faq_schema(faqs):
 return {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
   {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
   for q, a in faqs
  ],
 }

# ──────────────────────────────────────────
# Page renderers
# ──────────────────────────────────────────

def render_service_page(service):
 trail = [("Home", "index.html"), ("Services", "services/"), (service["name"], "")]
 bc = breadcrumbs(trail, depth=1)
 bc_schema = breadcrumb_schema([("Home", "index.html"), ("Services", "services/"), (service["name"], f"services/{service['slug']}.html")])

 # Service schema
 service_schema = {
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": service["name"],
  "provider": {"@id": f"{DOMAIN}#electrician"},
  "areaServed": [{"@type": "City", "name": a["name"]} for a in AREAS],
  "description": service["meta"],
  "url": f"{DOMAIN}/services/{service['slug']}.html",
 }

 fq = faq_schema(service["faqs"])

 canon = f"/services/{service['slug']}.html"
 page_head = head(
  title=service["title"],
  desc=service["meta"],
  canonical_path=canon,
  schema_extra=service_schema,
  depth=1,
 )
 # Add breadcrumb + FAQ schema inline
 extra_schemas = f"""
<script type="application/ld+json">{json.dumps(bc_schema)}</script>
<script type="application/ld+json">{json.dumps(fq)}</script>
"""
 page_head = page_head.replace("</head>", f"{extra_schemas}</head>")

 # Build areas list (linked, comma separated, used in copy)
 area_links = ", ".join(
  f'<a href="../areas/{a["slug"]}.html">{a["name"]}</a>'
  for a in AREAS[:8]
 )

 return f"""{page_head}
{nav("services", depth=1)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>{service["h1_html"]}</h1>
 <p class="lead">{service["lead"]}</p>
 <div class="page-hero-actions">
  <a href="tel:{BIZ_PHONE}" class="btn btn-primary">{ICON_PHONE} Call Alfie · {BIZ_PHONE_DISPLAY}</a>
  <a href="../contact.html" class="btn btn-outline">Get a free quote</a>
 </div>
 </div>
</section>

<section class="section-inner">
 <div class="body-layout">
 <article class="prose">
  {service["body"]}

  <h2>Frequently asked questions</h2>
  {render_faqs(service["faqs"])}

  <h2>Areas we cover for {service["short"]}</h2>
  <p>We provide {service["name"].lower()} across Warwickshire — most commonly in {area_links}, with all other areas listed on our <a href="../areas/">areas covered</a> page.</p>
 </article>
 <aside class="sidebar">
  {sidebar_quote_card()}
  {sidebar_services_list(current_slug=service["slug"], depth=1)}
 </aside>
 </div>
</section>

{cta_final()}
{footer(depth=1)}"""


def render_area_page(area):
 trail = [("Home", "index.html"), ("Areas", "areas/"), (area["name"], "")]
 bc = breadcrumbs(trail, depth=1)
 bc_schema = breadcrumb_schema([("Home", "index.html"), ("Areas", "areas/"), (area["name"], f"areas/{area['slug']}.html")])

 place_schema = {
  "@context": "https://schema.org",
  "@type": "Place",
  "name": area["name"],
  "address": {"@type": "PostalAddress", "addressLocality": area["name"], "postalCode": area["postcodes"], "addressCountry": "GB"},
 }

 page_head = head(
  title=area["title"],
  desc=area["meta"],
  canonical_path=f"/areas/{area['slug']}.html",
  schema_extra=place_schema,
  depth=1,
 )
 page_head = page_head.replace(
  "</head>",
  f'<script type="application/ld+json">{json.dumps(bc_schema)}</script>\n</head>'
 )

 service_links = ", ".join(
  f'<a href="../services/{s["slug"]}.html">{s["name"].lower()}</a>'
  for s in SERVICES
 )

 return f"""{page_head}
{nav("areas", depth=1)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>{area["h1_html"]}</h1>
 <p class="lead">{area["lead"]}</p>
 <p style="font-size:0.9rem;color:var(--muted);margin-bottom:24px;">
  <strong>Postcodes:</strong> {area["postcodes"]}<br>
  <strong>Neighbourhoods:</strong> {area["neighborhoods"]}
 </p>
 <div class="page-hero-actions">
  <a href="tel:{BIZ_PHONE}" class="btn btn-primary">{ICON_PHONE} Call Alfie · {BIZ_PHONE_DISPLAY}</a>
  <a href="../contact.html" class="btn btn-outline">Get a free quote</a>
 </div>
 </div>
</section>

<section class="section-inner">
 <div class="body-layout">
 <article class="prose">
  {area["body"]}

  <h2>Electrical services in {area["name"]}</h2>
  <p>We offer the full range of domestic and commercial electrical services in {area["name"]}: {service_links}. Click any service to read more, or call us on <a href="tel:{BIZ_PHONE}">{BIZ_PHONE_DISPLAY}</a> for a free quote.</p>

  <h2>Other areas we cover</h2>
  <p>If you're outside {area["name"]}, see our <a href="../areas/">full coverage map</a> — we work across Warwick, Leamington Spa, Kenilworth, Coventry, Stratford-upon-Avon and the wider Warwickshire area.</p>
 </article>
 <aside class="sidebar">
  {sidebar_quote_card()}
  {sidebar_areas_list(current_slug=area["slug"], depth=1)}
 </aside>
 </div>
</section>

{cta_final(headline_main=f"Need an electrician in", headline_em=area["name"] + "?")}
{footer(depth=1)}"""


def render_services_hub():
 trail = [("Home", "index.html"), ("Services", "")]
 bc = breadcrumbs(trail, depth=1)

 cards = []
 for s in SERVICES:
  icon_svg = f'<svg viewBox="0 0 24 24">{s["icon"]}</svg>'
  cards.append(f"""
 <a href="{s["slug"]}.html" class="card" style="text-decoration:none;color:inherit;">
  <div class="card-icon">{icon_svg}</div>
  <h3>{s["name"]}</h3>
  <p>{s["lead"]}</p>
  <span class="card-link">Read more</span>
 </a>""")

 page_head = head(
  title="Our Electrical Services in Warwickshire | Williams Electrical",
  desc="Domestic and commercial electrical services: consumer units, rewires, EV chargers, EICRs, fault finding, sockets & lighting, solar. Fully qualified.",
  canonical_path="/services/",
  depth=1,
 )

 return f"""{page_head}
{nav("services", depth=1)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Electrical services<br><em>across Warwickshire</em></h1>
 <p class="lead">From a single extra socket to a full house rewire, EV charger installs to commercial fit-outs — every service is delivered by a fully qualified electrician with 9 years' trade experience.</p>
 <div class="page-hero-actions">
  <a href="tel:{BIZ_PHONE}" class="btn btn-primary">{ICON_PHONE} Call Alfie · {BIZ_PHONE_DISPLAY}</a>
  <a href="../contact.html" class="btn btn-outline">Get a free quote</a>
 </div>
 </div>
</section>

<section class="section-inner">
 <div class="eyebrow">What we do</div>
 <h2 class="section-title">Choose a <em>service</em> to learn more.</h2>
 <p class="section-sub" style="margin-bottom:42px;">Each service page covers what's involved, typical costs, FAQs, and the areas across Warwickshire we cover for that work.</p>
 <div class="grid-cards">
 {"".join(cards)}
 </div>
</section>

{cta_final()}
{footer(depth=1)}"""


def render_areas_hub():
 trail = [("Home", "index.html"), ("Areas", "")]
 bc = breadcrumbs(trail, depth=1)

 cards = []
 for a in AREAS:
  cards.append(f"""
 <a href="{a["slug"]}.html" class="card" style="text-decoration:none;color:inherit;">
  <div class="card-icon">{ICON_PIN}</div>
  <h3>{a["name"]}</h3>
  <p><strong>{a["postcodes"]}</strong><br>{a["neighborhoods"][:120]}{'...' if len(a["neighborhoods"]) > 120 else ''}</p>
  <span class="card-link">Visit area page</span>
 </a>""")

 page_head = head(
  title="Areas Covered — Electrician across Warwick & Warwickshire | Williams Electrical",
  desc="Williams Electrical covers Warwick, Leamington Spa, Kenilworth, Coventry, Stratford-upon-Avon, Solihull, Rugby and surrounding villages across Warwickshire.",
  canonical_path="/areas/",
  depth=1,
 )

 return f"""{page_head}
{nav("areas", depth=1)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Areas we cover<br><em>across Warwickshire</em></h1>
 <p class="lead">Based in Warwick CV34 4PJ. We cover a wide radius across Warwickshire and beyond — same-day call-outs available across our core area.</p>
 </div>
</section>

<section class="section-inner">
 <div class="eyebrow">Coverage map</div>
 <h2 class="section-title">Pick your <em>area</em> — see what we do locally.</h2>
 <p class="section-sub" style="margin-bottom:42px;">Each area page covers the postcodes we serve, the typical jobs we do there, and our travel time from base.</p>
 <div class="grid-cards">
 {"".join(cards)}
 </div>
</section>

{cta_final()}
{footer(depth=1)}"""


def render_about():
 bc = breadcrumbs([("Home", "index.html"), ("About", "")], depth=0)

 page_head = head(
  title=f"About {OWNER_NAME} — Qualified Electrician in Warwick | {BIZ_NAME}",
  desc=f"Meet {OWNER_NAME} — fully qualified electrician serving Warwick & Warwickshire for over {YEARS} years. {GOOGLE_REVIEWS} 5-star Google reviews.",
  canonical_path="/about.html",
  depth=0,
 )

 return f"""{page_head}
{nav("about", depth=0)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Expert work,<br><em>honest service.</em></h1>
 <p class="lead">{BIZ_NAME} is led by director {OWNER_NAME} — a fully qualified electrician trusted by homeowners and businesses across Warwick and Warwickshire for over {YEARS} years. With a focus on safety, professionalism and attention to detail, every job from a single light fixture to a full domestic rewire is treated with the same care.</p>
 <div class="page-hero-actions">
  <a href="tel:{BIZ_PHONE}" class="btn btn-primary">{ICON_PHONE} Call Alfie · {BIZ_PHONE_DISPLAY}</a>
  <a href="./contact.html" class="btn btn-outline">Get in touch</a>
 </div>
 </div>
</section>

<section class="section-inner">
 <div class="prose" style="margin:0 auto;">
 <h2>How we got here</h2>
 <p>{BIZ_NAME} started with a simple idea: that local trades work best when there's one person you actually deal with. Not a call centre, not a quote-by-text bot, not a different sub-contractor each time. Just a qualified electrician who answers the phone, comes when he says he will, and stands behind the work.</p>
 <p>{OWNER_NAME.split()[0]} has been in the trade for over {YEARS} years — first as an apprentice, then through his NVQs and AM2 assessment, then as a fully qualified domestic and commercial electrician fully certified. He works on jobs from a single socket to a full house rewire, and every one is treated the same way: properly planned, properly fitted, properly tested, properly certified.</p>

 <h2>What we believe</h2>
 <h3>Local matters</h3>
 <p>We live and work in Warwick. We know the local housing stock — the 1960s semis with the original Wylex boards, the Victorian terraces with surface wiring under decades of paint, the new-builds where adding a socket means cutting through plasterboard you'd really rather not damage. Being local isn't a marketing line; it means you get someone who's done your kind of job a hundred times before.</p>

 <h3>Honest pricing, fixed quotes</h3>
 <p>Every job over the basic call-out is quoted in writing before work starts. Materials at trade plus a fair margin — no inflated mark-ups. If we find concealed problems mid-job (rotten cabling behind plaster, a broken back-box you couldn't see), we'll stop and tell you the cost before continuing. The price you agree is the price you pay.</p>

 <h3>Tidy site, no surprises</h3>
 <p>Sheet up before chasing. Hoover up before leaving. Floorboards screwed back down. Cables clipped, not draped. Plastered chases flush, not bulging. If you wouldn't want it in your own house, we wouldn't leave it in yours.</p>

 <h2>Credentials &amp; cover</h2>
 <ul>
     <li><strong>18th Edition Wiring Regulations (BS 7671)</strong> — current to amendment 2.</li>
  <li><strong>City &amp; Guilds Level 3</strong> NVQ Electrotechnical Services.</li>
  <li><strong>AM2 assessment</strong> — full ECS Gold Card.</li>
  <li><strong>{PUBLIC_LIABILITY} Public Liability</strong> insurance — certificate available on request.</li>
  <li><strong>5.0★ on Google</strong> ({GOOGLE_REVIEWS} reviews).</li>
 </ul>

 <h2>How to get in touch</h2>
 <p>The fastest route is <strong>phone</strong>: <a href="tel:{BIZ_PHONE}">{BIZ_PHONE_DISPLAY}</a>. You'll get Alfie directly. If we don't pick up, we're either up a ladder or in someone's loft — leave a message and we'll be back to you within a few hours.</p>
 <p><strong>WhatsApp</strong> works well for sending photos of issues: <a href="{WA_BASE}" target="_blank" rel="noopener">message us here</a>.</p>
 <p>For non-urgent enquiries you can also use our <a href="./contact.html">contact form</a> — the message routes straight to WhatsApp.</p>
 </div>
</section>

{cta_final()}
{footer(depth=0)}"""


def render_contact():
 bc = breadcrumbs([("Home", "index.html"), ("Contact", "")], depth=0)
 page_head = head(
  title=f"Contact Williams Electrical — Warwick & Warwickshire Electrician",
  desc=f"Call, WhatsApp or email Williams Electrical. Free quotes, no call-out fee. Based in Warwick {BIZ_ADDR_POSTCODE} — covering all of Warwickshire.",
  canonical_path="/contact.html",
  depth=0,
 )

 contact_form = f"""
<form class="contact-form" action="https://api.web3forms.com/submit" method="POST">
 <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
 <input type="hidden" name="subject" value="New Williams Electrical enquiry">
 <input type="hidden" name="from_name" value="Williams Electrical Website">
 <input type="hidden" name="redirect" value="{DOMAIN}/thanks.html">
 <h3>Send a message</h3>
 <p>Goes straight to Alfie at <a href="mailto:{BIZ_EMAIL}">{BIZ_EMAIL}</a> — usually replies within a few hours.</p>
 <div class="form-row">
  <div class="form-field"><label for="cf-fname">First name</label><input type="text" id="cf-fname" name="first_name" required></div>
  <div class="form-field"><label for="cf-lname">Last name</label><input type="text" id="cf-lname" name="last_name"></div>
 </div>
 <div class="form-row">
  <div class="form-field"><label for="cf-phone">Phone</label><input type="tel" id="cf-phone" name="phone"></div>
  <div class="form-field"><label for="cf-email">Email</label><input type="email" id="cf-email" name="email" required></div>
 </div>
 <div class="form-single">
  <div class="form-field"><label for="cf-service">Service needed</label>
   <select id="cf-service" name="service">
    <option value="">Select a service…</option>
    {"".join(f'<option>{s["name"]}</option>' for s in SERVICES)}
    <option>Other</option>
   </select>
  </div>
 </div>
 <div class="form-single">
  <div class="form-field"><label for="cf-msg">Message</label><textarea id="cf-msg" name="message" placeholder="Tell Alfie about the job..." required></textarea></div>
 </div>
 <!-- Honeypot anti-spam: humans never see this, bots fill it in -->
 <input type="checkbox" name="botcheck" style="display:none !important;" tabindex="-1" autocomplete="off">
 <button type="submit" class="btn-submit">Send message →</button>
</form>"""

 return f"""{page_head}
{nav("contact", depth=0)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Get in touch<br><em>with Alfie directly.</em></h1>
 <p class="lead">Call, WhatsApp, email or fill in the form below. No call-out fee for quotes. Same-day responses during working hours.</p>
 </div>
</section>

<section class="section-inner">
 <div class="body-layout">
 <article class="prose">
  <h2>Direct contact</h2>
  <p><strong>Phone (fastest):</strong> <a href="tel:{BIZ_PHONE}">{BIZ_PHONE_DISPLAY}</a> — you'll speak to Alfie, not a call centre.</p>
  <p><strong>WhatsApp (best for photos):</strong> <a href="{WA_BASE}" target="_blank" rel="noopener">message us here</a> — send photos of the issue or the area you'd like worked on.</p>
  <p><strong>Email:</strong> <a href="mailto:{BIZ_EMAIL}">{BIZ_EMAIL}</a> — reply usually within a few hours during working days.</p>

  <h2>Where we're based</h2>
  <p><strong>{BIZ_ADDR_FULL}</strong></p>
  <p>From our Warwick base we cover all of CV34, CV35, and the surrounding postcodes across {BIZ_ADDR_REGION}. See our <a href="./areas/">full coverage list</a> if you're not sure whether we cover your area.</p>

  <h2>Hours</h2>
  <p><strong>Mon–Fri:</strong> 8am–6pm<br>
  <strong>Saturday:</strong> 9am–4pm<br>
  <strong>Sunday:</strong> Emergency call-outs only (surcharge applies)</p>

  <h2>What to expect</h2>
  <p>When you call we'll ask three or four questions about the job — what's happening, where it is, when you'd like us, and whether it's urgent. For quotes we usually pop round to the property in person rather than quote blind over the phone — call-outs for quotes are free.</p>
  <p>For emergencies (no power, smell of burning, sparking) we'll prioritise and aim to be with you the same day where possible.</p>
 </article>
 <aside class="sidebar">
  {contact_form}
 </aside>
 </div>
</section>

{cta_final()}
{footer(depth=0)}"""


def render_work():
 bc = breadcrumbs([("Home", "index.html"), ("Our Work", "")], depth=0)
 page_head = head(
  title=f"Our Work — Recent Projects Across Warwick & Warwickshire | {BIZ_NAME}",
  desc=f"Before/after photos and case studies from {BIZ_NAME} — consumer units, EV chargers, lighting, sockets across Warwick and Warwickshire.",
  canonical_path="/work.html",
  depth=0,
 )

 # Before/After pairs reused on this page
 ba_items = [
  ("1", "EV Charger Installation",  "Hampton Magna · 7kW wall-mounted unit on dedicated 32A circuit"),
  ("2", "Feature Lighting Install", "Leamington Spa · pendant, paired wall lights &amp; LED downlights"),
  ("3", "New Sockets &amp; USB Outlets", "Warwick · twin matt-black sockets with USB-A/USB-C"),
  ("4", "LED Ambient Coving",   "Kenilworth · perimeter LED strip in colour-changing channel"),
  ("5", "Consumer Unit Upgrade",  "Warwick · old board to Schneider Easy9 18-way RCBO unit"),
  ("6", "Exterior Facade Lighting", "New-build · soffit downlights, wall up/down lights & feature uplighting"),
 ]
 ba_slider_html = "".join(f"""
  <article class="ba-slider" data-pos="50">
   <img src="assets/img/ba/{num}-after.jpg" alt="After: {label.replace('&amp;', 'and')} in {sub.split(' · ')[0]}" class="ba-img ba-after" loading="lazy">
   <img src="assets/img/ba/{num}-before.jpg" alt="Before: existing setup prior to {label.replace('&amp;', 'and').lower()}" class="ba-img ba-before" loading="lazy">
   <span class="ba-tag ba-tag-before">Before</span>
   <span class="ba-tag ba-tag-after">After</span>
   <div class="ba-handle" tabindex="0" role="slider" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50" aria-label="Drag to reveal before and after: {label.replace('&amp;', 'and')}">
   <span class="ba-handle-line"></span>
   <span class="ba-handle-dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 6 3 12 9 18"/><polyline points="15 6 21 12 15 18"/></svg></span>
   </div>
   <div class="ba-caption"><h4>{label}</h4><p>{sub}</p></div>
  </article>""" for num, label, sub in ba_items)

 # Gallery photos reused
 gallery_items = [
  ("job-1.jpg", "Garden Lighting Design",   "Pergola feature lights, fence uplights &amp; low-glow ground markers"),
  ("job-2.jpg", "Driveway &amp; Exterior Lighting", "Wall up/down lights + uplit shrubs and pathway"),
  ("job-3.jpg", "Kitchen LED Downlights",   "Full recessed downlight scheme with under-cabinet strip"),
  ("job-4.jpg", "CCTV &amp; Security Cameras",  "IP-rated wired install with concealed cable run"),
  ("job-5.jpg", "Staircase Step Lighting",  "Recessed riser lights with warm-white LED strip"),
 ]
 gallery_html = "".join(f"""
  <a href="contact.html" class="gallery-tile" aria-label="{label}: {sub}">
   <img src="assets/img/gallery/{fn}" alt="{label} — {sub}" loading="lazy">
   <div class="gallery-tile-label"><h4>{label}</h4><span>{sub}</span></div>
  </a>""" for fn, label, sub in gallery_items)

 return f"""{page_head}
{nav("work", depth=0)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Our Work &mdash;<br><em>Recent projects across Warwickshire</em></h1>
 <p class="lead">A growing portfolio of real installations completed across Warwick, Leamington Spa, Kenilworth, Coventry and the wider Warwickshire area. Every project below was carried out by Alfie personally, certified to BS 7671, and signed off via our certifying body. Browse the featured case studies, slide through real before-and-after comparisons, and have a look at recent smaller jobs.</p>
 <div class="page-hero-actions">
  <a href="tel:{BIZ_PHONE}" class="btn btn-primary">{ICON_PHONE} Call Alfie · {BIZ_PHONE_DISPLAY}</a>
  <a href="contact.html" class="btn btn-outline">Get a free quote</a>
 </div>
 </div>
</section>

<!-- FEATURED CASE STUDIES -->
<section class="section-inner">
 <div class="work-header">
 <div class="eyebrow">Featured Case Studies</div>
 <h2 class="section-title">Three jobs in <em>detail</em>.</h2>
 <p class="section-sub">Picked because they cover the most-asked-about service categories — fuse-board replacement, external lighting design, and garden lighting.</p>
 </div>

 <article class="case-study">
 <div class="case-study-photos case-study-photos-double">
  <figure>
  <img src="assets/img/ba/5-before.jpg" alt="Before: original 1970s Wylex fuse board with burn marks and no RCD protection" loading="lazy">
  <figcaption>Before — original 1970s Wylex</figcaption>
  </figure>
  <figure>
  <img src="assets/img/ba/5-after.jpg" alt="After: modern Schneider Easy9 18-way RCBO consumer unit with labelled circuits" loading="lazy">
  <figcaption>After — Schneider Easy9 RCBO unit</figcaption>
  </figure>
 </div>
 <div class="case-study-body">
  <div class="case-study-meta">
  <span class="case-chip">Warwick CV34</span>
  <span class="case-chip case-chip-service">Consumer Unit Upgrade</span>
  </div>
  <h3>Consumer Unit Upgrade — 1970s board to Schneider Easy9</h3>
  <p>This Warwick semi-detached had its original <strong>1970s Wylex pull-out fuse board</strong> still in service — no RCD protection on any circuit, rewireable fuses long past their design life, and burn marks around two of the fuse-ways. The homeowner had noticed circuits tripping irregularly and called us in for an inspection.</p>
  <p>After a full EICR confirming the board needed replacement (we also flagged a few minor remedials on the lighting circuit), we scheduled the upgrade for the following week. The replacement is a <strong>Schneider Easy9 18-way RCBO</strong> consumer unit — every circuit has its own individual RCBO, so a fault on one circuit doesn't kill the rest of the house. Surge protection (SPD) fitted as standard, every circuit individually labelled, full insulation resistance and earth-loop testing, certificate issued same day.</p>
  <p><strong>Total time on site:</strong> 5 hours. Power off for 2.5 hours during the swap, planned around the homeowner's school run.</p>
 </div>
 </article>

 <article class="case-study case-study-reverse">
 <div class="case-study-photos case-study-photos-double">
  <figure>
  <img src="assets/img/ba/6-before.jpg" alt="Before: new-build facade with only a single porch light" loading="lazy">
  <figcaption>Before — single porch light only</figcaption>
  </figure>
  <figure>
  <img src="assets/img/ba/6-after.jpg" alt="After: full external lighting design with soffit downlights and wall up/down lights" loading="lazy">
  <figcaption>After — full external lighting scheme</figcaption>
  </figure>
 </div>
 <div class="case-study-body">
  <div class="case-study-meta">
  <span class="case-chip">New-build estate, Warwickshire</span>
  <span class="case-chip case-chip-service">External Lighting</span>
  </div>
  <h3>Facade Lighting Design — new-build presentation upgrade</h3>
  <p>A new-build customer wanted to add presentation lighting to their facade — the developer had only fitted a single porch light. We designed and installed a full external lighting scheme: <strong>soffit downlights on the entry side, paired up/down LED wall lights</strong> on each side of the garage and front door, and recessed driveway uplights to pick out the path and a young silver birch.</p>
  <p>All circuits run from a new external IP-rated junction in the porch, controlled via <strong>timed photocell</strong> so the lights come on at dusk and off at 11pm — homeowner can override from a switch by the front door. Every fitting is IP65 minimum, every cable run buried to BS 7671 depth, fully RCD protected on a dedicated 6A circuit.</p>
  <p><strong>Total job:</strong> 1.5 days on site, all certified. The transformation when the lights come on at dusk speaks for itself — drag the slider below to see the before and after.</p>
 </div>
 </article>

 <article class="case-study">
 <div class="case-study-photos case-study-photos-single">
  <figure>
  <img src="assets/img/gallery/job-1.jpg" alt="Garden lighting design with pergola feature lights, fence uplights and ground markers" loading="lazy">
  <figcaption>Warm-white pergola, tree uplights &amp; low-glow ground markers</figcaption>
  </figure>
 </div>
 <div class="case-study-body">
  <div class="case-study-meta">
  <span class="case-chip">Leamington Spa CV32</span>
  <span class="case-chip case-chip-service">Garden Lighting</span>
  </div>
  <h3>Garden Lighting Design — pergola, fence uplights and ground markers</h3>
  <p>A Leamington homeowner had recently completed a garden renovation — porcelain patio, raised beds, pergola, and three young silver birches — but the space was unusable after dark. We were brought in to design a lighting scheme that would let them entertain in the evening without it looking like a Christmas grotto.</p>
  <p>The result: <strong>warm-white fence-mounted uplights</strong> pulling the trees and pergola posts out of the dark, <strong>ground-recessed deck lights</strong> along the patio edges as low-glow markers, and a four-bulb festoon string above the pergola seating area on its own dimmer. Three separate circuits so they can switch the trees + pergola without lighting the path, or just have the festoon for a quiet drink outside.</p>
  <p>Cabling buried beneath the patio in armoured SWA to BS 7671 depth. All RCD-protected on a dedicated outdoor circuit. <strong>Smart-home integration</strong> via the existing Loxone system — homeowner can hit an "evening" scene from their phone and the whole garden warms up at sunset.</p>
 </div>
 </article>
</section>

<!-- BEFORE / AFTER GRID -->
<section class="section-inner" style="padding-top: 30px;">
 <div class="work-header">
 <div class="eyebrow">Before &amp; After</div>
 <h2 class="section-title">Real jobs, <em>drag to reveal</em>.</h2>
 <p class="section-sub">Every slider below is a real Williams Electrical project. Drag the handle (or click anywhere on the image) to wipe between before and after.</p>
 </div>
 <div class="ba-grid">{ba_slider_html}
 </div>
</section>

<!-- GALLERY -->
<section class="section-inner" style="padding-top: 30px;">
 <div class="work-header">
 <div class="eyebrow">Recent Installations</div>
 <h2 class="section-title">Highlights from <em>recent months</em>.</h2>
 <p class="section-sub">A snapshot of recent smaller jobs across Warwick and Warwickshire — outdoor lighting, kitchen schemes, security, staircase features.</p>
 </div>
 <div class="gallery-grid">{gallery_html}
 </div>
</section>

{cta_final()}

<!-- Slider JS — inline because this page uses the BA slider component -->
<script>
(function () {{
 const sliders = document.querySelectorAll('.ba-slider');
 sliders.forEach(slider => {{
 const handle = slider.querySelector('.ba-handle');
 let dragging = false;
 const setPos = (clientX) => {{
  const rect = slider.getBoundingClientRect();
  let pct = ((clientX - rect.left) / rect.width) * 100;
  pct = Math.max(0, Math.min(100, pct));
  slider.style.setProperty('--pos', pct + '%');
  handle.setAttribute('aria-valuenow', Math.round(pct));
  slider.dataset.pos = Math.round(pct);
 }};
 const start = (e) => {{ dragging = true; slider.style.cursor = 'grabbing'; const cx = e.touches ? e.touches[0].clientX : e.clientX; setPos(cx); e.preventDefault(); }};
 const move = (e) => {{ if (!dragging) return; const cx = e.touches ? e.touches[0].clientX : e.clientX; setPos(cx); }};
 const end = () => {{ dragging = false; slider.style.cursor = 'ew-resize'; }};
 slider.addEventListener('mousedown', start);
 slider.addEventListener('touchstart', start, {{ passive: false }});
 window.addEventListener('mousemove', move);
 window.addEventListener('touchmove', move, {{ passive: true }});
 window.addEventListener('mouseup', end);
 window.addEventListener('touchend', end);
 slider.addEventListener('click', (e) => {{ if (e.target.closest('.ba-handle')) return; setPos(e.clientX); }});
 handle.addEventListener('keydown', (e) => {{
  const cur = parseInt(slider.dataset.pos || '50', 10);
  let next = cur;
  if (e.key === 'ArrowLeft') next = Math.max(0, cur - 5);
  if (e.key === 'ArrowRight') next = Math.min(100, cur + 5);
  if (e.key === 'Home') next = 0;
  if (e.key === 'End') next = 100;
  if (next !== cur) {{ slider.style.setProperty('--pos', next + '%'); slider.dataset.pos = next; handle.setAttribute('aria-valuenow', next); e.preventDefault(); }}
 }});
 }});
}})();
</script>

{footer(depth=0)}"""


# ──────────────────────────────────────────
# FAQ page (lifted off the home page so home stays scannable)
# ──────────────────────────────────────────

HOME_FAQS = [
 ("Are you fully qualified and insured?",
  "Yes. All work is carried out by a fully qualified electrician and is compliant with BS 7671 (18th Edition Wiring Regulations). We are fully insured for domestic and commercial work."),
 ("Do you charge a call-out fee?",
  "No — there's no call-out fee for quotes. You only pay for the work carried out. Emergency out-of-hours visits may carry a small surcharge, which we'll always confirm before attending."),
 ("How long does a consumer unit upgrade take?",
  "A standard consumer unit upgrade typically takes 4–6 hours. We'll need to isolate power for part of the day. We plan around you and aim to have everything back on before we leave."),
 ("Do I need an EICR as a landlord?",
  "Yes — since 1 April 2021 it has been a legal requirement for all private landlords in England to have an EICR every 5 years. We can carry these out and provide the certificate promptly."),
 ("Can you install EV chargers at my home?",
  "Yes. We install 7kW and 22kW home EV charging points compatible with all major manufacturers. We'll assess your supply capacity and advise on the best solution for your property."),
 ("What areas do you cover?",
  f"We are based in Warwick {BIZ_ADDR_POSTCODE} and cover Warwick, Leamington Spa, Kenilworth, Coventry, Stratford-upon-Avon, Solihull, Rugby and surrounding areas across Warwickshire. Give us a call and we'll confirm."),
 ("Do you offer emergency electrical work?",
  f"Yes. Where possible we offer same-day and emergency call-outs for urgent faults. Call us directly on {BIZ_PHONE_DISPLAY} — you'll speak to {OWNER_NAME.split()[0]}, not a call centre."),
]

def render_faq():
 bc = breadcrumbs([("Home", "index.html"), ("FAQs", "")], depth=0)
 page_head = head(
  title=f"FAQs — Common Questions Answered | {BIZ_NAME}",
  desc=f"Common questions about {BIZ_NAME}: qualifications, call-out fees, consumer units, EICRs, EV chargers, areas covered, emergency work.",
  canonical_path="/faq.html",
  depth=0,
  schema_extra=[faq_schema(HOME_FAQS), breadcrumb_schema([("Home", "index.html"), ("FAQs", "faq.html")])],
 )
 return f"""{page_head}
{nav("", depth=0)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Frequently asked<br><em>questions</em>.</h1>
 <p class="lead">Common questions from our customers — answered honestly. If yours isn't here, give Alfie a call on <a href="tel:{BIZ_PHONE}" style="color: var(--sage-dark); font-weight: 600;">{BIZ_PHONE_DISPLAY}</a> and we'll talk it through.</p>
 </div>
</section>

<section class="section-inner" style="padding-top: 30px;">
 <div style="max-width: 860px; margin: 0 auto;">
 {render_faqs(HOME_FAQS)}
 </div>
</section>

{cta_final()}
{footer(depth=0)}"""


def render_thanks():
    """Confirmation page after a successful form submission (Web3Forms redirects here)."""
    page_head = head(
        title=f"Thanks — we've got your message | {BIZ_NAME}",
        desc=f"Thanks for your enquiry — {OWNER_NAME} will reply shortly.",
        canonical_path="/thanks.html",
        depth=0,
    )
    # We don't want search engines indexing the thanks page (only reachable post-submit)
    page_head = page_head.replace(
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="robots" content="noindex, nofollow">'
    )
    return f"""{page_head}
{nav("", depth=0)}

<section class="page-hero" style="min-height: 60vh; display: flex; align-items: center;">
  <div class="page-hero-inner" style="text-align: center; max-width: 620px; margin: 0 auto;">
    <div class="eyebrow" style="justify-content: center;">Message sent</div>
    <h1>Thanks &mdash;<br><em>we've got it.</em></h1>
    <p class="lead" style="margin: 18px auto 30px;">Your enquiry is in {OWNER_NAME.split()[0]}'s inbox. You'll usually hear back within a few working hours — sometimes sooner.</p>
    <p style="color: var(--muted); font-size: 0.95rem; margin-bottom: 36px;">If it's urgent, please call <a href="tel:{BIZ_PHONE}" style="color: var(--sage-dark); font-weight: 600;">{BIZ_PHONE_DISPLAY}</a> &mdash; you'll get {OWNER_NAME.split()[0]} directly.</p>
    <div class="page-hero-actions" style="justify-content: center;">
      <a href="tel:{BIZ_PHONE}" class="btn btn-primary">{ICON_PHONE} Call {BIZ_PHONE_DISPLAY}</a>
      <a href="/" class="btn btn-outline">Back to homepage</a>
    </div>
  </div>
</section>

{footer(depth=0)}"""


def render_privacy():
 bc = breadcrumbs([("Home", "index.html"), ("Privacy Policy", "")], depth=0)
 page_head = head(
  title=f"Privacy Policy | {BIZ_NAME}",
  desc=f"How {BIZ_NAME} collects, uses and protects your personal data. UK GDPR-compliant. Contact form data, no third-party tracking.",
  canonical_path="/privacy.html",
  depth=0,
 )
 return f"""{page_head}
{nav("", depth=0)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Privacy Policy</h1>
 <p class="lead">How we collect, use and protect any personal information you share with us. Last updated 1 May 2026.</p>
 </div>
</section>

<section class="section-inner">
 <div class="prose" style="margin:0 auto;">
 <h2>Who we are</h2>
 <p>This site is operated by <strong>{BIZ_NAME}</strong>, an electrical contractor directed by {OWNER_NAME} based at {BIZ_ADDR_FULL}, Warwick {BIZ_ADDR_POSTCODE}, United Kingdom. We are the data controller responsible for any personal data you provide via this website.</p>
 <p>If you have any questions about this policy or how we handle your data, contact us at <a href="mailto:{BIZ_EMAIL}">{BIZ_EMAIL}</a> or call <a href="tel:{BIZ_PHONE}">{BIZ_PHONE_DISPLAY}</a>.</p>

 <h2>What information we collect</h2>
 <p>We only collect information that you actively provide to us — we do not run any third-party analytics or tracking. When you complete our contact form or message us via WhatsApp, we collect:</p>
 <ul>
  <li>Your name (first name, optionally surname)</li>
  <li>Your phone number (if provided)</li>
  <li>Your email address (if provided)</li>
  <li>The service you're enquiring about</li>
  <li>The free-text message you write</li>
 </ul>

 <h2>How we use your information</h2>
 <p>We use the information you provide only for the purposes you provided it — responding to your enquiry, quoting for work, scheduling a visit, and where applicable invoicing you. We will never use your details for marketing without your explicit consent, and we will never share them with third parties for marketing.</p>

 <h2>Legal basis for processing</h2>
 <p>Under UK GDPR, our legal basis is:</p>
 <ul>
  <li><strong>Performance of a contract</strong> — when you're asking us to quote for or carry out work.</li>
  <li><strong>Legitimate interests</strong> — responding to enquiries before any contract is formed.</li>
  <li><strong>Legal obligation</strong> — keeping records required by HMRC and Building Regulations (s).</li>
 </ul>

 <h2>How long we keep it</h2>
 <p>Enquiry data (where no work was undertaken) is deleted within 12 months.</p>
 <p>Customer data (where work was carried out) is retained for 6 years to comply with HMRC record-keeping requirements and our insurance obligations. After that period, records are securely deleted or anonymised.</p>

 <h2>Who we share data with</h2>
 <p>We don't share your personal data with third parties, with three narrow exceptions:</p>
 <ul>
  <li><strong>Fully qualified</strong> — for certification of regulated electrical work (required by law).</li>
  <li><strong>HMRC</strong> — invoicing and tax records (required by law).</li>
  <li><strong>Our accountant</strong> — for bookkeeping, under a written confidentiality agreement.</li>
 </ul>
 <p>WhatsApp messages you send us are subject to <a href="https://www.whatsapp.com/legal/privacy-policy-eea" target="_blank" rel="noopener">WhatsApp's own privacy policy</a>. We do not use WhatsApp Business or any tools that scrape, store, or share your message data outside the WhatsApp app itself.</p>

 <h2>Your rights under UK GDPR</h2>
 <p>You have the right to:</p>
 <ul>
  <li><strong>Access</strong> — request a copy of the personal data we hold about you.</li>
  <li><strong>Rectification</strong> — ask us to correct inaccurate or incomplete data.</li>
  <li><strong>Erasure</strong> — ask us to delete your data (subject to legal record-keeping obligations).</li>
  <li><strong>Restriction</strong> — ask us to stop processing your data while a dispute is resolved.</li>
  <li><strong>Portability</strong> — request your data in a machine-readable format.</li>
  <li><strong>Objection</strong> — object to processing based on legitimate interests.</li>
 </ul>
 <p>To exercise any of these rights, email <a href="mailto:{BIZ_EMAIL}">{BIZ_EMAIL}</a>. We aim to respond within 14 days. If you're unhappy with how we've handled your data, you can complain to the Information Commissioner's Office at <a href="https://ico.org.uk/" target="_blank" rel="noopener">ico.org.uk</a>.</p>

 <h2>Cookies</h2>
 <p>We use essential cookies only. We do not run any third-party analytics (no Google Analytics, no Facebook Pixel, no advertising trackers). See our <a href="./cookies.html">Cookie Policy</a> for full detail.</p>

 <h2>Changes to this policy</h2>
 <p>We may update this policy from time to time. The "last updated" date at the top of this page will reflect any changes. Material changes will be highlighted on the homepage.</p>
 </div>
</section>

{cta_final()}
{footer(depth=0)}"""


def render_cookies():
 bc = breadcrumbs([("Home", "index.html"), ("Cookie Policy", "")], depth=0)
 page_head = head(
  title=f"Cookie Policy | {BIZ_NAME}",
  desc=f"{BIZ_NAME} uses essential cookies only. No Google Analytics, no advertising trackers, no third-party tracking. Read our full cookie policy.",
  canonical_path="/cookies.html",
  depth=0,
 )
 return f"""{page_head}
{nav("", depth=0)}

<section class="page-hero">
 <div class="page-hero-inner">
 {bc}
 <h1>Cookie Policy</h1>
 <p class="lead">What cookies we use, why, and how to control them. Last updated 1 May 2026.</p>
 </div>
</section>

<section class="section-inner">
 <div class="prose" style="margin:0 auto;">
 <h2>The short version</h2>
 <p><strong>We don't track you.</strong> This site uses no Google Analytics, no Facebook Pixel, no advertising cookies, no fingerprinting, no third-party tracking of any kind. The only cookies set are essential ones described below.</p>

 <h2>What is a cookie?</h2>
 <p>A cookie is a small text file that a website stores on your device. Some cookies are essential for a site to function; others are used for analytics, advertising, or personalisation. UK and EU law require websites to inform you about cookies and, where they're not strictly necessary, get your consent before setting them.</p>

 <h2>Cookies we use</h2>
 <h3>Essential cookies</h3>
 <ul>
  <li><strong><code>we-cookies-ok</code></strong> — set by us when you dismiss the cookie banner. Stored in your browser's localStorage (technically not a cookie, but covered here for transparency). It records that you've seen the banner so we don't show it on every page. Contains a single value: "1". No personal data.</li>
 </ul>
 <p>That's the only thing we set.</p>

 <h3>Third-party cookies</h3>
 <p>None. We don't embed Google Maps, YouTube, Facebook widgets, or any other third-party content that would set cookies on your visit.</p>

 <h3>What about WhatsApp / Google reviews?</h3>
 <p>When you click a WhatsApp link or our "Read all reviews on Google" link, you'll be taken to those services and they may set their own cookies. We don't control or share data with those services beyond the click itself. Their own privacy and cookie policies apply once you're on their sites.</p>

 <h2>How to control cookies</h2>
 <p>Because we only use essential cookies, you don't need to take any action to opt out. If you want to clear what's stored anyway, use your browser's privacy settings:</p>
 <ul>
  <li><strong>Chrome:</strong> Settings → Privacy &amp; security → Clear browsing data</li>
  <li><strong>Safari:</strong> Settings → Safari → Clear History and Website Data</li>
  <li><strong>Firefox:</strong> Settings → Privacy &amp; Security → Clear Data</li>
  <li><strong>Edge:</strong> Settings → Privacy, search and services → Clear browsing data</li>
 </ul>

 <h2>Will this ever change?</h2>
 <p>If we add anything in future — for example, a map embed, an analytics tool, or chat widget — we'll update this policy and the cookie banner will reappear so you can re-consent.</p>

 <h2>Contact</h2>
 <p>Questions? Email <a href="mailto:{BIZ_EMAIL}">{BIZ_EMAIL}</a> or call <a href="tel:{BIZ_PHONE}">{BIZ_PHONE_DISPLAY}</a>.</p>
 </div>
</section>

{cta_final()}
{footer(depth=0)}"""


def render_webmanifest():
 import json as _json
 return _json.dumps({
  "name": BIZ_NAME,
  "short_name": "Williams Electric",
  "description": f"fully qualified electrician serving Warwick and Warwickshire.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F7F4ED",
  "theme_color": "#5C7762",
  "icons": [
   {"src": "/assets/img/favicons/favicon-192.png", "sizes": "192x192", "type": "image/png"},
   {"src": "/assets/img/favicons/favicon-512.png", "sizes": "512x512", "type": "image/png"},
  ],
 }, indent=2)


def render_sitemap():
 pages = []
 pages.append((f"{DOMAIN}/", "1.0", "weekly"))
 pages.append((f"{DOMAIN}/about.html", "0.8", "monthly"))
 pages.append((f"{DOMAIN}/contact.html", "0.8", "monthly"))
 pages.append((f"{DOMAIN}/work.html", "0.9", "monthly"))
 pages.append((f"{DOMAIN}/faq.html", "0.7", "monthly"))
 pages.append((f"{DOMAIN}/services/", "0.9", "monthly"))
 pages.append((f"{DOMAIN}/areas/", "0.9", "monthly"))
 for s in SERVICES:
  pages.append((f"{DOMAIN}/services/{s['slug']}.html", "0.8", "monthly"))
 for a in AREAS:
  pages.append((f"{DOMAIN}/areas/{a['slug']}.html", "0.8", "monthly"))
 pages.append((f"{DOMAIN}/privacy.html", "0.3", "yearly"))
 pages.append((f"{DOMAIN}/cookies.html", "0.3", "yearly"))

 urls = "\n".join(
  f" <url><loc>{u}</loc><changefreq>{cf}</changefreq><priority>{p}</priority></url>"
  for u, p, cf in pages
 )
 return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""


def render_robots():
 return f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""


# ──────────────────────────────────────────
# Main — write all files
# ──────────────────────────────────────────

def main():
 written = 0

 # Service pages
 services_dir = ROOT / "services"
 services_dir.mkdir(exist_ok=True)
 for s in SERVICES:
  (services_dir / f"{s['slug']}.html").write_text(render_service_page(s), encoding="utf-8")
  print(f" wrote services/{s['slug']}.html")
  written += 1

 # Area pages
 areas_dir = ROOT / "areas"
 areas_dir.mkdir(exist_ok=True)
 for a in AREAS:
  (areas_dir / f"{a['slug']}.html").write_text(render_area_page(a), encoding="utf-8")
  print(f" wrote areas/{a['slug']}.html")
  written += 1

 # Hubs
 (services_dir / "index.html").write_text(render_services_hub(), encoding="utf-8")
 print(" wrote services/index.html")
 written += 1

 (areas_dir / "index.html").write_text(render_areas_hub(), encoding="utf-8")
 print(" wrote areas/index.html")
 written += 1

 # About + Contact + Legal
 (ROOT / "about.html").write_text(render_about(), encoding="utf-8")
 print(" wrote about.html")
 written += 1

 (ROOT / "contact.html").write_text(render_contact(), encoding="utf-8")
 print(" wrote contact.html")
 written += 1

 (ROOT / "work.html").write_text(render_work(), encoding="utf-8")
 print(" wrote work.html")
 written += 1

 (ROOT / "privacy.html").write_text(render_privacy(), encoding="utf-8")
 print(" wrote privacy.html")
 written += 1

 (ROOT / "cookies.html").write_text(render_cookies(), encoding="utf-8")
 print(" wrote cookies.html")
 written += 1

 (ROOT / "faq.html").write_text(render_faq(), encoding="utf-8")
 print(" wrote faq.html")

 (ROOT / "thanks.html").write_text(render_thanks(), encoding="utf-8")
 print(" wrote thanks.html")
 written += 1

 (ROOT / "site.webmanifest").write_text(render_webmanifest(), encoding="utf-8")
 print(" wrote site.webmanifest")
 written += 1

 # Sitemap + robots
 (ROOT / "sitemap.xml").write_text(render_sitemap(), encoding="utf-8")
 print(" wrote sitemap.xml")
 written += 1

 (ROOT / "robots.txt").write_text(render_robots(), encoding="utf-8")
 print(" wrote robots.txt")
 written += 1

 print(f"\n✓ {written} files written")


if __name__ == "__main__":
 main()
