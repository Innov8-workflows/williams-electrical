#!/usr/bin/env python3
"""
SEO Audit Report generator — Williams Electrical
Branded for Innov8 Workflows. Pure-reportlab (no system deps).
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import math, datetime

# ── Brand palette (Innov8 Workflows) ───────────────────────────────
INK      = HexColor("#14123A")   # deep indigo
INK2     = HexColor("#1F1D55")   # indigo card
CYAN     = HexColor("#16D0E6")   # electric cyan accent
VIOLET   = HexColor("#6C5CE7")   # violet accent
SLATE    = HexColor("#5A5A72")   # body grey
MIST     = HexColor("#8A8AA3")   # muted
LIGHT    = HexColor("#F4F6FB")   # panel bg
LINE     = HexColor("#E4E7F2")   # hairline
GOOD     = HexColor("#1FB47A")   # green
WARN     = HexColor("#E8A13A")   # amber
BAD      = HexColor("#E5575B")   # red
WHITE    = white

PAGE_W, PAGE_H = A4
MX = 18*mm                       # left/right margin

c = canvas.Canvas("/home/user/williams-electrical/seo-audit/williams-electrical-seo-audit.pdf",
                  pagesize=A4)
c.setTitle("Williams Electrical — SEO Audit Report")
c.setAuthor("Innov8 Workflows")
c.setSubject("Search Engine Optimisation Audit")

REPORT_DATE = datetime.date(2026, 6, 13).strftime("%d %B %Y")

# ── helpers ────────────────────────────────────────────────────────
def score_colour(s):
    if s >= 8: return GOOD
    if s >= 5: return WARN
    return BAD

def wrap(text, font, size, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if stringWidth(t, font, size) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def para(x, y, text, font="Helvetica", size=9.5, leading=14,
         colour=SLATE, max_w=None):
    max_w = max_w or (PAGE_W - 2*MX)
    c.setFillColor(colour); c.setFont(font, size)
    for ln in wrap(text, font, size, max_w):
        c.drawString(x, y, ln); y -= leading
    return y

def logo(x, y, scale=1.0, light=False):
    """Innov8 Workflows wordmark + mark."""
    m = 9*scale
    # rounded mark
    c.setFillColor(CYAN)
    c.roundRect(x, y-m*0.15, m, m, 2.4*scale, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", m*0.62)
    c.drawCentredString(x+m/2, y+m*0.18, "8")
    # wordmark
    tx = x + m + 6*scale
    c.setFont("Helvetica-Bold", 13*scale)
    c.setFillColor(WHITE if light else INK)
    c.drawString(tx, y+m*0.30, "innov")
    w1 = stringWidth("innov", "Helvetica-Bold", 13*scale)
    c.setFillColor(CYAN)
    c.drawString(tx+w1, y+m*0.30, "8")
    w2 = stringWidth("8", "Helvetica-Bold", 13*scale)
    c.setFont("Helvetica", 7.2*scale)
    c.setFillColor(MIST if not light else HexColor("#B9B9D4"))
    c.drawString(tx, y-3.2*scale, "W O R K F L O W S")

def gauge(cx, cy, r, score, max_score=10):
    """Circular score gauge."""
    frac = score/max_score
    col = score_colour(score)
    # track
    c.setLineWidth(r*0.20); c.setStrokeColor(HexColor("#2A2860"))
    c.setLineCap(1)
    c.arc(cx-r, cy-r, cx+r, cy+r, 0, 360)
    # progress arc (start at top, clockwise)
    steps = max(2, int(frac*120))
    c.setStrokeColor(col)
    start = 90.0
    for i in range(steps):
        a0 = math.radians(start - (i/120.0)*360)
        a1 = math.radians(start - ((i+1)/120.0)*360)
        c.line(cx+r*math.cos(a0), cy+r*math.sin(a0),
               cx+r*math.cos(a1), cy+r*math.sin(a1))
    # centre text
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", r*0.72)
    c.drawCentredString(cx, cy-r*0.10, f"{score:g}")
    c.setFillColor(HexColor("#B9B9D4")); c.setFont("Helvetica", r*0.26)
    c.drawCentredString(cx, cy-r*0.46, "OUT OF 10")

def footer(page_no):
    c.setStrokeColor(LINE); c.setLineWidth(0.6)
    c.line(MX, 16*mm, PAGE_W-MX, 16*mm)
    c.setFont("Helvetica", 7.5); c.setFillColor(MIST)
    c.drawString(MX, 11.5*mm, "Prepared by Innov8 Workflows  ·  innov8workflows.co.uk")
    c.drawCentredString(PAGE_W/2, 11.5*mm, "Williams Electrical — SEO Audit")
    c.drawRightString(PAGE_W-MX, 11.5*mm, f"Page {page_no}")

def header_band(title, kicker):
    c.setFillColor(INK); c.rect(0, PAGE_H-30*mm, PAGE_W, 30*mm, fill=1, stroke=0)
    c.setFillColor(CYAN); c.rect(0, PAGE_H-30*mm, PAGE_W, 1.4*mm, fill=1, stroke=0)
    logo(MX, PAGE_H-15*mm, 0.78, light=True)
    c.setFont("Helvetica", 8); c.setFillColor(HexColor("#B9B9D4"))
    c.drawRightString(PAGE_W-MX, PAGE_H-12*mm, kicker)
    c.setFont("Helvetica-Bold", 17); c.setFillColor(WHITE)
    c.drawString(MX, PAGE_H-25*mm, title)

# ════════════════════════════════════════════════════════════════════
# PAGE 1 — COVER
# ════════════════════════════════════════════════════════════════════
c.setFillColor(INK); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
# decorative accent shapes
c.setFillColor(HexColor("#1C1A52"))
c.circle(PAGE_W*0.86, PAGE_H*0.84, 120*mm, fill=1, stroke=0)
c.setFillColor(INK); c.rect(0,0,PAGE_W,PAGE_H*0.62, fill=1, stroke=0)
c.setStrokeColor(CYAN); c.setLineWidth(1.2)
c.line(MX, PAGE_H-46*mm, MX+22*mm, PAGE_H-46*mm)

logo(MX, PAGE_H-34*mm, 1.15, light=True)

c.setFont("Helvetica", 11); c.setFillColor(CYAN)
c.drawString(MX, PAGE_H-58*mm, "SEARCH ENGINE OPTIMISATION  ·  AUDIT REPORT")
c.setFont("Helvetica-Bold", 38); c.setFillColor(WHITE)
c.drawString(MX, PAGE_H-78*mm, "Williams")
c.drawString(MX, PAGE_H-92*mm, "Electrical")
c.setFont("Helvetica", 12); c.setFillColor(HexColor("#B9B9D4"))
c.drawString(MX, PAGE_H-104*mm, "williams-electric.co.uk")

# overall score gauge
gauge(PAGE_W-58*mm, PAGE_H-86*mm, 26*mm, 7.6)

# verdict pill
c.setFillColor(HexColor("#1FB47A"))
c.roundRect(MX, PAGE_H-120*mm, 64*mm, 11*mm, 5.5*mm, fill=1, stroke=0)
c.setFont("Helvetica-Bold", 10); c.setFillColor(WHITE)
c.drawCentredString(MX+32*mm, PAGE_H-116.4*mm, "VERDICT:  STRONG FOUNDATION")

# meta block bottom
by = 40*mm
c.setStrokeColor(HexColor("#2A2860")); c.setLineWidth(0.8)
c.line(MX, by+14*mm, PAGE_W-MX, by+14*mm)
def meta(x, label, val):
    c.setFont("Helvetica", 7.5); c.setFillColor(MIST)
    c.drawString(x, by+8*mm, label.upper())
    c.setFont("Helvetica-Bold", 10.5); c.setFillColor(WHITE)
    c.drawString(x, by+2.5*mm, val)
meta(MX, "Prepared for", "Williams Electrical Ltd")
meta(MX+62*mm, "Prepared by", "Innov8 Workflows")
meta(MX+118*mm, "Date", REPORT_DATE)
c.setFont("Helvetica", 8); c.setFillColor(MIST)
c.drawString(MX, 22*mm, "Confidential — prepared for the named client only.")
c.setFillColor(CYAN); c.rect(0,0,PAGE_W,4*mm, fill=1, stroke=0)
c.showPage()

# ════════════════════════════════════════════════════════════════════
# PAGE 2 — EXECUTIVE SUMMARY + SCORECARD
# ════════════════════════════════════════════════════════════════════
header_band("Executive Summary", "01  ·  OVERVIEW")
y = PAGE_H-42*mm
y = para(MX, y,
    "Williams Electrical operates a genuinely well-engineered website. Across 28 crawled pages we found "
    "strong on-page fundamentals, comprehensive local-SEO architecture and rich structured data that already "
    "position the business to compete for electrician searches across Warwick and Warwickshire. The site earns "
    "a headline score of 7.6/10. The gap to a top-tier score is concentrated in three fixable areas: the "
    "complete absence of analytics/measurement, an over-weight homepage caused by image data embedded directly "
    "in the HTML, and a thin top-of-funnel content layer.",
    size=10, leading=15)
y -= 4*mm

# scorecard
c.setFont("Helvetica-Bold", 12); c.setFillColor(INK)
c.drawString(MX, y, "Category Scorecard"); y -= 7*mm

cats = [
    ("On-Page SEO",            9.0, "Titles, meta, headings, alt text"),
    ("Local SEO",              9.0, "NAP, geo signals, area pages"),
    ("Indexability & Crawl",   9.0, "Sitemap, robots, canonicals"),
    ("Technical SEO",          8.5, "Mobile, HTTPS, markup hygiene"),
    ("Structured Data",        8.5, "Schema.org coverage & richness"),
    ("Content & Topical Depth",7.0, "Breadth of service/area copy"),
    ("Performance",            6.0, "Page weight & Core Web Vitals"),
    ("Analytics & Measurement",2.0, "Tracking, GSC, conversions"),
]
row_h = 9.4*mm
bar_x = MX+74*mm
bar_w = 64*mm
for name, sc, desc in cats:
    c.setFillColor(LIGHT); c.roundRect(MX, y-row_h+2*mm, PAGE_W-2*MX, row_h-1.5*mm, 2*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9.3); c.setFillColor(INK)
    c.drawString(MX+4*mm, y-3.4*mm, name)
    c.setFont("Helvetica", 7.2); c.setFillColor(MIST)
    c.drawString(MX+4*mm, y-6.6*mm, desc)
    # bar track
    c.setFillColor(HexColor("#E0E4F0"))
    c.roundRect(bar_x, y-5.4*mm, bar_w, 3.4*mm, 1.7*mm, fill=1, stroke=0)
    c.setFillColor(score_colour(sc))
    c.roundRect(bar_x, y-5.4*mm, bar_w*(sc/10.0), 3.4*mm, 1.7*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10.5); c.setFillColor(score_colour(sc))
    c.drawRightString(PAGE_W-MX-4*mm, y-4.4*mm, f"{sc:g}")
    y -= row_h

y -= 3*mm
c.setFillColor(INK2); c.roundRect(MX, y-15*mm, PAGE_W-2*MX, 14*mm, 2.5*mm, fill=1, stroke=0)
c.setFont("Helvetica-Bold", 9); c.setFillColor(CYAN)
c.drawString(MX+5*mm, y-5.5*mm, "OVERALL SCORE  7.6 / 10")
c.setFont("Helvetica", 8.4); c.setFillColor(HexColor("#D7D9EC"))
c.drawString(MX+5*mm, y-10.5*mm,
    "Weighted across the eight categories above. A strong, well-built site held back by measurement and performance gaps.")
footer(2); c.showPage()

# ════════════════════════════════════════════════════════════════════
# PAGE 3 — WHAT'S WORKING WELL
# ════════════════════════════════════════════════════════════════════
header_band("What's Working Well", "02  ·  STRENGTHS")
y = PAGE_H-42*mm
strengths = [
 ("Tailored metadata on every page",
  "All 28 pages (home, 9 service pages, 12 location pages, plus about/contact/FAQ/work) carry unique, "
  "keyword-rich title tags and meta descriptions with location and unique-selling-point cues."),
 ("Comprehensive structured data",
  "Electrician / LocalBusiness schema includes full NAP, geo-coordinates, opening hours, an areaServed list "
  "of 11 towns and an aggregateRating (5.0★, 33 reviews). FAQPage and BreadcrumbList markup is present on "
  "every service page."),
 ("Excellent local-SEO architecture",
  "12 dedicated town landing pages (Warwick, Leamington Spa, Kenilworth, Coventry, Stratford-upon-Avon and more) "
  "combined with 9 service pages give strong geographic and topical coverage for “electrician in [town]” queries."),
 ("Clean on-page fundamentals",
  "Exactly one H1 per page, a logical H2/H3 hierarchy, and 100% image alt-text coverage (23/23 on the homepage). "
  "Every URL declares a correct canonical tag."),
 ("Crawl & social readiness",
  "Open Graph and Twitter Card tags, a 27-URL XML sitemap referenced from robots.txt, lang=“en-GB”, a web "
  "app manifest, a full favicon set and geo meta tags are all in place."),
 ("Mobile-first and secure",
  "Responsive viewport, custom HTTPS domain, lazy-loaded imagery (17 images) and inlined critical CSS for fast "
  "first paint."),
]
for i,(t,d) in enumerate(strengths,1):
    c.setFillColor(GOOD); c.circle(MX+3*mm, y-1*mm, 2.6*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8.5); c.setFillColor(WHITE)
    c.drawCentredString(MX+3*mm, y-2.1*mm, "✓")
    c.setFont("Helvetica-Bold", 10.5); c.setFillColor(INK)
    c.drawString(MX+9*mm, y-2*mm, t)
    yy = para(MX+9*mm, y-7*mm, d, size=9, leading=12.5, colour=SLATE,
              max_w=PAGE_W-2*MX-9*mm)
    y = yy - 6*mm
footer(3); c.showPage()

# ════════════════════════════════════════════════════════════════════
# PAGE 4 — PRIORITISED RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════
header_band("Issues & Recommendations", "03  ·  ACTION PLAN")
y = PAGE_H-40*mm
issues = [
 ("P1", BAD, "No analytics or conversion tracking",
  "No GA4, Google Tag Manager or call/form tracking was detected, and no Search Console verification is present. "
  "The business currently has no visibility into traffic, rankings or where leads come from.",
  "Install GA4 via GTM, verify Google Search Console, and configure click-to-call and contact-form conversion events."),
 ("P1", BAD, "Homepage HTML is 1.12 MB",
  "Roughly 1.0 MB of that is seven images base64-embedded directly in the HTML. This blocks parsing, inflates "
  "Largest Contentful Paint and prevents the browser from caching those images.",
  "Move embedded images to external, optimised WebP/AVIF files with explicit width/height; target sub-150 KB HTML."),
 ("P2", WARN, "Location pages lack FAQ schema",
  "Service pages carry FAQPage markup, but the 12 town landing pages do not — a missed local rich-result opportunity.",
  "Add a short localised FAQ block plus FAQPage schema to each area page."),
 ("P2", WARN, "Hero imagery heavier than needed",
  "Hero and CTA JPEGs weigh 148–208 KB each, the main drag on Core Web Vitals.",
  "Serve WebP/AVIF with responsive srcset; aim for sub-100 KB heroes to lift LCP."),
 ("P2", WARN, "No individual review or sameAs markup",
  "Schema declares an aggregateRating but no individual Review items and no sameAs links. Google increasingly wants "
  "reviewer context for star snippets, and sameAs strengthens entity trust.",
  "Add Review items and a sameAs array linking the Google Business Profile and social profiles."),
 ("P3", MIST, "No top-of-funnel content layer",
  "Every page is transactional; there is no advice/blog content to capture informational searches such as "
  "“how much does an EICR cost” or “signs you need a rewire”.",
  "Add a small advice hub to capture long-tail queries and strengthen internal linking."),
]
for tag,col,title,problem,fix in issues:
    box_h = 25*mm
    c.setFillColor(LIGHT); c.roundRect(MX, y-box_h, PAGE_W-2*MX, box_h, 2.5*mm, fill=1, stroke=0)
    c.setFillColor(col); c.roundRect(MX, y-box_h, 2*mm, box_h, 1*mm, fill=1, stroke=0)
    # priority chip
    c.setFillColor(col); c.roundRect(MX+5*mm, y-7*mm, 11*mm, 5*mm, 2.5*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8.5); c.setFillColor(WHITE)
    c.drawCentredString(MX+10.5*mm, y-5.6*mm, tag)
    c.setFont("Helvetica-Bold", 10.5); c.setFillColor(INK)
    c.drawString(MX+19*mm, y-5.8*mm, title)
    yy = para(MX+6*mm, y-12*mm, problem, size=8.6, leading=11.5, colour=SLATE,
              max_w=PAGE_W-2*MX-12*mm)
    c.setFont("Helvetica-Bold", 8.4); c.setFillColor(col)
    c.drawString(MX+6*mm, yy-1*mm, "Fix  →")
    para(MX+6*mm+stringWidth("Fix  → ", "Helvetica-Bold", 8.4), yy-1*mm, fix,
         size=8.6, leading=11.5, colour=INK, max_w=PAGE_W-2*MX-26*mm)
    y -= box_h + 4*mm
footer(4); c.showPage()

# ════════════════════════════════════════════════════════════════════
# PAGE 5 — ROADMAP + METHODOLOGY
# ════════════════════════════════════════════════════════════════════
header_band("Roadmap & Methodology", "04  ·  NEXT STEPS")
y = PAGE_H-42*mm
c.setFont("Helvetica-Bold", 12); c.setFillColor(INK)
c.drawString(MX, y, "Suggested 90-day roadmap"); y -= 8*mm
phases = [
 ("Weeks 1–2 · Measure", CYAN,
  "Stand up GA4 + GTM, verify Search Console, submit the sitemap and configure call/form conversions so every "
  "later change can be measured."),
 ("Weeks 3–5 · Performance", VIOLET,
  "Externalise the base64 images, convert heroes to WebP/AVIF with srcset and re-test Core Web Vitals. Biggest "
  "speed win for the least effort."),
 ("Weeks 6–9 · Expand rich results", HexColor("#2BA8C9"),
  "Add FAQ + FAQPage schema to all 12 area pages and Review/sameAs markup site-wide to chase more local "
  "rich snippets."),
 ("Weeks 10–12 · Content", GOOD,
  "Launch a small advice hub (3–4 cornerstone articles) targeting informational queries and interlink it with "
  "the service and area pages."),
]
for t,col,d in phases:
    c.setFillColor(col); c.circle(MX+2.5*mm, y-1.5*mm, 2.5*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10); c.setFillColor(INK)
    c.drawString(MX+8*mm, y-2*mm, t)
    yy = para(MX+8*mm, y-7*mm, d, size=9, leading=12.5, colour=SLATE,
              max_w=PAGE_W-2*MX-8*mm)
    y = yy - 5*mm

y -= 2*mm
c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(MX, y, PAGE_W-MX, y); y -= 8*mm
c.setFont("Helvetica-Bold", 11); c.setFillColor(INK)
c.drawString(MX, y, "Methodology"); y -= 6*mm
y = para(MX, y,
  "This audit was performed on 13 June 2026 against the production source of williams-electric.co.uk, covering "
  "28 pages: the homepage, 9 service pages, 12 town landing pages and the about, contact, FAQ, work and legal "
  "pages. The live URL returned HTTP 403 to automated crawlers (bot protection), so signals were assessed from "
  "the deployed source rather than a live browser render.",
  size=8.6, leading=12, colour=SLATE)
y = para(MX, y-1*mm,
  "Scores reflect crawlable on-page, technical, structured-data and local-SEO signals. Performance was estimated "
  "from HTML and asset weights; field Core Web Vitals were not measured in-browser and should be confirmed with "
  "PageSpeed Insights once analytics is in place. This document is an independent technical assessment, not a "
  "guarantee of specific rankings.",
  size=8.6, leading=12, colour=SLATE)

# closing brand card
cy = 40*mm
c.setFillColor(INK); c.roundRect(MX, cy-2*mm, PAGE_W-2*MX, 20*mm, 3*mm, fill=1, stroke=0)
logo(MX+6*mm, cy+9*mm, 0.85, light=True)
c.setFont("Helvetica", 8.4); c.setFillColor(HexColor("#B9B9D4"))
c.drawRightString(PAGE_W-MX-6*mm, cy+11*mm, "Let's turn 7.6 into a 9.")
c.setFont("Helvetica-Bold", 9); c.setFillColor(CYAN)
c.drawRightString(PAGE_W-MX-6*mm, cy+5*mm, "innov8workflows.co.uk")
footer(5); c.showPage()

c.save()
print("PDF written.")
