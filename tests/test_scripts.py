#!/usr/bin/env python3
"""Tests for the skills' scripts, run against the built copies in ai-plugins/public/skills (what users get).

    python3 tests/test_scripts.py                    in the published repository
    python3 ai-plugins/src/tests/test_scripts.py     in Visibian's sources, after python3 ai-plugins/build.py

No outside network: every test feeds the scripts local text, or a small web server on this machine.
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True   # keep the published tree free of __pycache__
HERE = pathlib.Path(__file__).resolve().parent
# in the published repository: tests/ beside skills/; in Visibian's sources: ai-plugins/src/tests, tested on the build
PUBLIC = HERE.parent / "skills" if HERE.parent.name != "src" else HERE.parents[1] / "public" / "skills"


def load(skill, script):
    path = PUBLIC / skill / "scripts" / script
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"{skill}_{path.stem}".replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        mod.main(list(args))
    return out.getvalue()


class Robots(unittest.TestCase):
    """RFC 9309 and Google's parser, as HQ's crawler study reads them."""

    @classmethod
    def setUpClass(cls):
        cls.m = load("ai-crawler-access", "aicrawlers.py")

    def access(self, text, token, path):
        rules, _ = self.m.group_for(self.m.parse(text), token)
        return self.m.allowed(rules, path)

    def test_own_group_ignores_star(self):
        text = "User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nDisallow: /private/\n"
        self.assertTrue(self.access(text, "GPTBot", "/blog"))
        self.assertFalse(self.access(text, "GPTBot", "/private/x"))
        self.assertFalse(self.access(text, "OAI-SearchBot", "/blog"))

    def test_longest_match_and_allow_wins_tie(self):
        text = "User-agent: *\nDisallow: /shop\nAllow: /shop/public\nDisallow: /a\nAllow: /a\n"
        self.assertFalse(self.access(text, "ClaudeBot", "/shop/cart"))
        self.assertTrue(self.access(text, "ClaudeBot", "/shop/public/item"))
        self.assertTrue(self.access(text, "ClaudeBot", "/a"))

    def test_wildcard_and_end_anchor(self):
        text = "User-agent: *\nDisallow: /*.pdf$\nDisallow: /search*q=\n"
        self.assertFalse(self.access(text, "PerplexityBot", "/files/a.pdf"))
        self.assertTrue(self.access(text, "PerplexityBot", "/files/a.pdf.html"))
        self.assertFalse(self.access(text, "PerplexityBot", "/search?q=x"))

    def test_case_and_grouped_agents(self):
        text = "user-agent: gptbot\nuser-agent: ClaudeBot\ndisallow: /\n"
        self.assertFalse(self.access(text, "GPTBot", "/"))
        self.assertFalse(self.access(text, "ClaudeBot", "/"))
        self.assertTrue(self.access(text, "Claude-SearchBot", "/"))

    def test_crawl_delay_does_not_end_group(self):
        text = "User-agent: Bingbot\nCrawl-delay: 5\nUser-agent: GPTBot\nDisallow: /\n"
        self.assertFalse(self.access(text, "Bingbot", "/"))

    def test_applebot_follows_googlebot(self):
        text = "User-agent: Googlebot\nDisallow: /nope/\n"
        self.assertFalse(self.access(text, "Applebot", "/nope/x"))

    def test_empty_disallow_and_robots_file(self):
        text = "User-agent: *\nDisallow:\n"
        self.assertTrue(self.access(text, "GPTBot", "/anything"))
        self.assertTrue(self.m.allowed([(False, "/")], "/robots.txt"))

    def test_unreachable_closes_everything(self):
        data = self.m.load_crawlers()
        _, rows = self.m.evaluate("", "unreachable", ["/"], data["crawlers"])
        self.assertTrue(all(r["access"].startswith("closed") for r in rows))

    def test_report_warns_on_search_crawler(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("User-agent: OAI-SearchBot\nDisallow: /\n")
        out = run(self.m, "--file", f.name)
        self.assertIn("OAI-SearchBot is shut out", out)
        self.assertIn("read 2026-", out)

    def test_crawler_data_matches_directory(self):
        data = self.m.load_crawlers()
        self.assertEqual(len(data["crawlers"]), 24)
        tokens = {c["token"] for c in data["crawlers"]}
        for t in ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Google-Extended",
                  "Googlebot", "Bingbot", "PerplexityBot", "CCBot"):
            self.assertIn(t, tokens)
        for c in data["crawlers"]:
            self.assertTrue(c["doc"].startswith("https://"), c["token"])


class JsonLd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("structured-data", "check_jsonld.py")

    def levels(self, blocks, page=""):
        return [(l, msg) for l, _, msg in self.m.check(blocks, page)[1]]

    def test_product_needs_one_of(self):
        f = self.levels(['{"@context":"https://schema.org","@type":"Product","name":"Shoe"}'])
        self.assertIn(("error", "Product needs one of: review, aggregateRating, offers"), f)

    def test_valid_product(self):
        f = self.levels(['{"@context":"https://schema.org","@type":"Product","name":"Shoe",'
                         '"offers":{"@type":"Offer","price":"10","priceCurrency":"EUR"}}'])
        self.assertFalse([x for x in f if x[0] == "error"])

    def test_bad_json_context_and_date(self):
        f = self.levels(['{nope', '{"@context":"https://example.org","@type":"Article","datePublished":"5 Nov"}'])
        msgs = [m for _, m in f]
        self.assertTrue(any(m.startswith("not valid JSON") for m in msgs))
        self.assertIn("@context does not name schema.org", msgs)
        self.assertTrue(any("not an ISO 8601 date" in m for m in msgs))

    def test_graph_and_alias(self):
        f = self.levels(['{"@context":"https://schema.org","@graph":[{"@type":"Dentist","name":"Smile"}]}'])
        self.assertIn(("error", "Dentist is missing required property address"), f)

    def test_faq_note_and_visibility(self):
        page = self.m.visible_text("<h1>Acme</h1><p>Hello</p>")
        f = self.levels(['{"@context":"https://schema.org","@type":"FAQPage","name":"Questions about Zeta"}'], page)
        self.assertTrue(any(l == "note" and "7 May 2026" in m for l, m in f))
        self.assertTrue(any("does not appear in the page text" in m for _, m in f))


class LlmsTxt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("llms-txt", "check_llms_txt.py")

    def test_valid(self):
        e, w, n, links = self.m.check("# Acme\n\n> Tools.\n\n## Docs\n\n- [Start](https://acme.com/start): setup\n")
        self.assertEqual(e, [])
        self.assertEqual(len(links), 1)

    def test_errors(self):
        e, w, n, links = self.m.check("Acme\n## Docs\n- Start page\n### Deep\n")
        self.assertTrue(any("H1" in x for x in e))
        self.assertTrue(any("markdown link" in x for x in e))
        self.assertTrue(any("only H1 and H2" in x for x in e))

    def test_relative_link_warns(self):
        e, w, n, links = self.m.check("# Acme\n## Docs\n- [Start](/start)\n")
        self.assertTrue(any("relative" in x for x in w))


class Claims(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("answer-first-content", "claims_check.py")

    def test_flags_and_passes(self):
        text = ("Acme is the best tool for clinics.\n\nIt saves 5 hours a week.\n\n"
                "In a 2024 study, statistics raised visibility by 40% ([GEO](https://arxiv.org/abs/2311.09735)).\n")
        found = self.m.check(text, False)
        reasons = [tuple(f["why"]) for f in found]
        self.assertIn(("superlative",), reasons)
        self.assertIn(("figure",), reasons)
        self.assertEqual(len(found), 2)


class Page(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("ai-search-audit", "page_check.py")   # shared; the same file in every skill that uses it

    def test_client_rendered_page(self):
        doc = ('<html><head><title>Acme</title><meta name="robots" content="noindex"></head>'
               '<body><div id="root"></div><script src="a.js"></script></body></html>')
        f = self.m.page_facts(doc)
        notes = self.m.findings(f, 200)
        msgs = " ".join(m for _, m in notes)
        self.assertTrue(f["empty_app_root"])
        self.assertIn("asks not to be indexed", msgs)
        self.assertIn("words of text in the HTML before scripts run", msgs)
        self.assertNotIn("score", msgs.lower())

    def test_good_page(self):
        words = " ".join(["word"] * 400)
        doc = ('<html lang="en"><head><title>Acme pricing</title><meta name="description" content="Plans.">'
               '<link rel="canonical" href="https://acme.com/pricing">'
               '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product",'
               '"name":"Acme","dateModified":"2026-11-01"}</script></head>'
               f'<body><h1>Acme pricing</h1><p>{words}</p></body></html>')
        f = self.m.page_facts(doc)
        levels = {l for l, _ in self.m.findings(f, 200)}
        self.assertNotIn("blocker", levels)
        self.assertEqual(f["jsonld_types"], ["Product"])


class FactsAcrossPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("brand-fact-sheet", "facts_across_pages.py")

    def test_reads_organization(self):
        doc = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization",'
               '"name":"Acme","sameAs":["https://b","https://a"],"address":{"@type":"PostalAddress",'
               '"streetAddress":"1 Main St","addressLocality":"Oslo"}}</script>'
               '<a href="tel:+47 123">call</a><a href="mailto:Hi@Acme.com">mail</a>')
        f = self.m.facts(doc)
        self.assertEqual(f["name"], "Acme")
        self.assertEqual(f["sameAs"], "https://a | https://b")
        self.assertEqual(f["address"], "1 Main St, Oslo")
        self.assertEqual(f["telephone links"], "+47123")
        self.assertEqual(f["email links"], "hi@acme.com")


# ------------------------------------------------------------------ the SEO skills

SITE = {
    "/robots.txt": ("text/plain", "User-agent: *\nDisallow: /private/\n\nSitemap: {root}/sitemap.xml\n"),
    "/sitemap.xml": ("application/xml", '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                     '<url><loc>{root}/</loc></url><url><loc>{root}/a</loc></url><url><loc>{root}/orphan</loc></url>'
                     '<url><loc>{root}/old</loc></url></urlset>'),
    "/": ("text/html", '<html lang="en"><head><title>Home of Acme widgets</title><meta name="description" content="Acme">'
          '<meta name="viewport" content="width=device-width"><link rel="canonical" href="{root}/"></head><body><main>'
          '<h1>Acme widgets</h1><p>' + "Widgets for teams that build things. " * 20 + '</p>'
          '<a href="/a">Widget guide</a> <a href="/b">click here</a> <a href="/old">Old page</a> <a href="/missing">Gone</a>'
          '</main></body></html>'),
    "/a": ("text/html", '<html lang="en"><head><title>Widget guide</title><meta name="viewport" content="x"></head><body>'
           '<main><h1>Widget guide</h1><p>' + "How to choose a widget for a team. " * 20 + '</p><img src="x.png">'
           '<a href="/">Home</a></main></body></html>'),
    "/b": ("text/html", '<html><head><title>Widget guide</title></head><body><div id="root"></div></body></html>'),
    "/orphan": ("text/html", '<html lang="en"><head><title>Widget pricing</title><meta name="viewport" content="x"></head>'
                '<body><main><h1>Widget pricing</h1><p>' + "Prices for widgets and their parts. " * 20 + '</p></main></body></html>'),
    # pages on another site, for the backlink checker
    "/links-out": ("text/html", '<html><body><p>See <a href="https://www.example.com/pricing" rel="nofollow ugc">Example '
                   'pricing</a> and <a href="https://example.com/"><img src="l.png" alt="Example logo"></a>.</p></body></html>'),
    "/no-link": ("text/html", '<html><body><p>Nothing here links out.</p></body></html>'),
}


class _Handler(__import__("http.server").server.BaseHTTPRequestHandler):
    def do_GET(self):
        root = f"http://{self.headers['Host']}"
        if self.path == "/old":
            self.send_response(301)
            self.send_header("Location", "/a")
            self.end_headers()
            return
        if self.path not in SITE:
            self.send_response(404)
            self.end_headers()
            return
        ctype, body = SITE[self.path]
        body = body.replace("{root}", root).encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class SiteAudit(unittest.TestCase):
    """The crawler, on a small site served from this machine."""

    @classmethod
    def setUpClass(cls):
        import http.server
        import threading
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.root = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.m = load("seo-audit", "site_audit.py")
        cls.audit = cls.m.crawl(cls.root + "/", max_pages=20, delay=0)
        cls.audit["findings"] = [{"level": l, "category": c, "message": msg, "urls": u}
                                 for l, c, msg, u in cls.m.findings(cls.audit)]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def msgs(self):
        return " | ".join(f["message"] for f in self.audit["findings"])

    def test_finds_what_is_wrong(self):
        m = self.msgs()
        self.assertIn("answers an error", m)                 # /missing
        self.assertIn("that redirect", m)                    # /old
        self.assertIn("fewer than 80 words", m)             # /b, an empty app root
        self.assertIn("share its title", m.replace("shares its title", "share its title"))   # /a and /b
        self.assertIn("orphans", m)                          # /orphan, in the sitemap only
        self.assertIn("click here", m)

    def test_respects_robots_and_records_redirects(self):
        self.assertTrue(all(not u.endswith("/private/") for u in self.audit["pages"]))
        old = self.audit["pages"][self.root + "/old"]
        self.assertEqual(old["chain"][0][0], 301)

    def test_report_and_link_graph(self):
        text = self.m.report(self.audit, [(f["level"], f["category"], f["message"], f["urls"])
                                          for f in self.audit["findings"]])
        self.assertIn("Pages checked:", text)
        lg = load("internal-linking", "link_graph.py")
        r = lg.analyse(json.loads(json.dumps(self.audit, default=str)))
        self.assertIn(self.root + "/orphan", r["orphans"])

    def test_client_report(self):
        rep = load("seo-report", "make_report.py")
        out = rep.build(json.loads(json.dumps(self.audit, default=str)), "Acme", "Agency", None, "**Note**", [], True)
        self.assertIn("SEO and AI search report", out)
        self.assertIn("<b>Note</b>", out)
        self.assertIn("github.com/visibian/seo-geo-skills", out)
        self.assertNotIn("github.com/visibian/seo-geo-skills",
                         rep.build(json.loads(json.dumps(self.audit, default=str)), "", "", None, "", [], False))


class Keywords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("keyword-research", "gsc_queries.py")

    def write(self, rows):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        f.write("\n".join(rows))
        f.close()
        return f.name

    def test_export_with_percent_ctr(self):
        rows = ["Top queries,Clicks,Impressions,CTR,Position", "how to pick a widget,10,1000,1%,7.5",
                "acme widgets,300,900,33.3%,1.2", "best widgets for teams,5,800,0.62%,12"]
        r = self.m.analyse(self.m.read(self.write(rows)), brand=["acme"])
        self.assertEqual(r["summary"]["queries"], 3)
        self.assertEqual([q["query"] for q in r["quick_wins"]], ["how to pick a widget", "best widgets for teams"])
        self.assertIn("how to pick a widget", [q["query"] for q in r["questions"]])
        self.assertAlmostEqual(r["all"][0]["ctr"], 0.01)
        self.assertEqual(next(q for q in r["all"] if q["query"] == "acme widgets")["intent"], "navigational")

    def test_pairs_and_declines(self):
        pairs = ["query,page,clicks,impressions,ctr,position", "widget price,/a,5,500,0.01,6", "widget price,/b,2,300,0.006,9"]
        r = self.m.analyse(self.m.read(self.write(pairs)))
        self.assertEqual(r["competing_pages"][0]["query"], "widget price")
        before = self.m.read(self.write(["query,clicks,impressions,ctr,position", "widget price,40,900,0.04,3"]))
        r = self.m.analyse(self.m.read(self.write(pairs)), before)
        self.assertEqual(r["declines"][0]["query"], "widget price")


class OnPage(unittest.TestCase):
    def test_terms_and_outline(self):
        m = load("on-page-seo", "onpage_check.py")
        doc = ('<html><head><title>Widget pricing for teams</title><meta name="description" content="What widgets cost">'
               '</head><body><main><h1>Widget pricing</h1><p>Widgets for teams cost from 10 to 40 euros a month, as of '
               'May 2026.</p><h2>What affects the price?</h2><p>Seats and support change the price of a widget.</p>'
               '<a href="https://example.org/study">a study</a></main></body></html>')
        r = m.analyse(doc, "https://acme.test/pricing", "widget pricing")
        self.assertEqual(r["title_has"], ["widget", "pricing"])
        self.assertEqual(r["question_headings"], ["What affects the price?"])
        self.assertEqual(r["external_links"], 1)


class Outline(unittest.TestCase):
    def test_shared_headings(self):
        m = load("content-brief", "page_outline.py")
        a = m.outline("<main><h2>What a widget costs</h2><h2>How to choose</h2></main>", "https://a.test/")
        b = m.outline("<main><h2>How to choose a widget</h2><h2>What widgets cost</h2></main>", "https://b.test/")
        self.assertTrue(any(c["pages"] == 2 for c in m.shared([a, b])) or m.shared([a, b]) == [])
        self.assertEqual(len(a["outline"]), 2)


class Hreflang(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("international-seo", "hreflang_check.py")

    def test_codes(self):
        ok = ["en", "en-GB", "zh-Hant", "zh-Hant-TW", "pt-br", "x-default", "de-DE"]
        self.assertEqual([c for c in ok if self.m.check_code(c)], [])
        for bad in ("en-UK", "en_GB", "jp", "es-419", "xx"):
            self.assertIsNotNone(self.m.check_code(bad), bad)

    def test_head_and_header(self):
        doc = '<head><link rel="alternate" hreflang="de" href="/de/"><link rel="alternate" hreflang="en" href="/"></head>'
        got = self.m.hreflangs(doc, {"Link": '<https://acme.test/fr/>; rel="alternate"; hreflang="fr"'}, "https://acme.test/")
        self.assertEqual(sorted(c for c, _ in got), ["de", "en", "fr"])


class Passages(unittest.TestCase):
    def test_sections(self):
        m = load("geo-optimization", "passage_check.py")
        doc = ('<main><h2>How much does a widget cost?</h2><p>A widget for a small team costs 25 euros a month on average, according to '
               '<a href="https://example.org/survey">a 2026 survey</a>.</p><h2>Why teams buy them</h2><p>Many teams say '
               'widgets help, and studies show they save time across several departments every week.</p></main>')
        s = m.sections(m.main_html(doc), "acme.test")
        self.assertTrue(s[0]["question"])
        self.assertEqual(s[0]["figures_with_source_link"], s[0]["figures"])
        self.assertIn("studies show", s[1]["vague_phrases"])


class Speed(unittest.TestCase):
    def test_psi_shape(self):
        m = load("page-speed", "page_speed.py")
        data = {"id": "https://acme.test/",
                "loadingExperience": {"id": "https://acme.test/", "metrics": {
                    "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 3100, "category": "AVERAGE"},
                    "INTERACTION_TO_NEXT_PAINT": {"percentile": 150, "category": "FAST"},
                    "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 30, "category": "SLOW"}}},
                "lighthouseResult": {"finalDisplayedUrl": "https://acme.test/", "lighthouseVersion": "12.6.1",
                                     "categories": {"performance": {"score": 0.72}},
                                     "audits": {"largest-contentful-paint": {"numericValue": 3600, "displayValue": "3.6 s"},
                                                "render-blocking-resources": {"title": "Eliminate render-blocking resources",
                                                                              "score": 0.3, "details": {"type": "opportunity", "overallSavingsMs": 820}},
                                                "largest-contentful-paint-element": {"details": {"items": [{"items": [{"node": {"snippet": "<img class=hero>"}}]}]}}}}}
        r = m.parse(data)
        self.assertEqual({x["metric"]: x["category"] for x in r["field_page"]},
                         {"LCP": "needs improvement", "INP": "good", "CLS": "poor"})
        self.assertEqual(r["performance_score"], 72)
        self.assertEqual(r["opportunities"][0]["saving_ms"], 820)
        self.assertEqual(r["lcp_element"], "<img class=hero>")


class SearchConsole(unittest.TestCase):
    """gsc_api.py against a small stand-in for the Search Console API on this machine."""

    @classmethod
    def setUpClass(cls):
        import http.server
        import threading

        class Api(http.server.BaseHTTPRequestHandler):
            calls = []

            def reply(self, code, data):
                body = json.dumps(data).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.headers.get("Authorization") != "Bearer good":
                    return self.reply(401, {"error": {"message": "Request had invalid authentication credentials."}})
                if self.path == "/webmasters/v3/sites":
                    return self.reply(200, {"siteEntry": [{"siteUrl": "sc-domain:acme.test",
                                                           "permissionLevel": "siteOwner"}]})
                if self.path.endswith("/sitemaps"):
                    return self.reply(200, {"sitemap": [{"path": "https://acme.test/sitemap.xml", "errors": "2",
                                                         "warnings": "0", "lastDownloaded": "2026-11-10T08:00:00Z",
                                                         "contents": [{"type": "web", "submitted": "40"}]}]})
                self.reply(404, {"error": {"message": "not found"}})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                Api.calls.append((self.path, body))
                if self.path.endswith("/searchAnalytics/query"):
                    rows = [{"keys": [f"widget {i}", f"https://acme.test/{i % 2}"], "clicks": 10 - i,
                             "impressions": 100 + i, "ctr": (10 - i) / (100 + i), "position": 3.5 + i}
                            for i in range(5)]
                    start = body["startRow"]
                    return self.reply(200, {"rows": rows[start:start + body["rowLimit"]]})
                if self.path == "/v1/urlInspection/index:inspect":
                    ok = body["inspectionUrl"].endswith("/a")
                    return self.reply(200, {"inspectionResult": {"indexStatusResult": {
                        "verdict": "PASS" if ok else "NEUTRAL",
                        "coverageState": "Submitted and indexed" if ok else "Crawled - currently not indexed",
                        "robotsTxtState": "ALLOWED", "indexingState": "INDEXING_ALLOWED",
                        "pageFetchState": "SUCCESSFUL", "lastCrawlTime": "2026-11-01T10:00:00Z",
                        "crawledAs": "MOBILE", "userCanonical": body["inspectionUrl"],
                        "googleCanonical": body["inspectionUrl"] if ok else "https://acme.test/a"}}})
                self.reply(404, {"error": {"message": "not found"}})

            def log_message(self, *a):
                pass

        cls.Api = Api
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Api)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.m = load("search-console", "gsc_api.py")
        cls.m.API = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        import os
        self.env = dict(os.environ)
        os.environ["SEARCH_CONSOLE_TOKEN"] = "good"

    def tearDown(self):
        import os
        os.environ.clear()
        os.environ.update(self.env)

    def test_performance_pages_through_rows_and_feeds_keyword_research(self):
        self.m.PAGE_ROWS = 2   # five rows come back in three requests
        with tempfile.TemporaryDirectory() as d:
            out = pathlib.Path(d) / "rows.csv"
            text = run(self.m, "performance", "sc-domain:acme.test", "--start", "2026-10-01", "--end", "2026-10-28",
                       "--out", str(out))
            self.assertIn("5 rows by query and page", text)
            kw = load("keyword-research", "gsc_queries.py")
            rows = kw.read(str(out))
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["query"], "widget 0")
        self.assertEqual(rows[0]["page"], "https://acme.test/0")
        self.assertAlmostEqual(rows[0]["ctr"], 0.1, places=3)
        queries = [b for p, b in self.Api.calls if p.endswith("/searchAnalytics/query")]
        self.assertEqual([q["startRow"] for q in queries[-3:]], [0, 2, 4])
        self.assertIn("/sites/sc-domain%3Aacme.test/", [p for p, _ in self.Api.calls][-1])

    def test_inspect_flags_pages_to_look_at(self):
        text = run(self.m, "inspect", "sc-domain:acme.test", "https://acme.test/a", "https://acme.test/b")
        self.assertIn("2 pages inspected; 1 with something to look at", text)
        self.assertIn("Google chose another canonical: https://acme.test/a", text)
        self.assertIn("not indexed: Crawled - currently not indexed", text)

    def test_sites_sitemaps_and_bad_token(self):
        import os
        self.assertIn("sc-domain:acme.test", run(self.m, "sites"))
        self.assertIn("| https://acme.test/sitemap.xml | 40 | 2 |", run(self.m, "sitemaps", "sc-domain:acme.test"))
        os.environ["SEARCH_CONSOLE_TOKEN"] = "tok-zz9-secret"
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(self.m.main(["sites"]), 1)
        self.assertIn("401", err.getvalue())
        self.assertNotIn("tok-zz9-secret", err.getvalue())   # the token is never printed

    def test_dates_trail_by_three_days(self):
        import datetime as dt
        self.assertEqual(self.m.dates(28, None, None, today=dt.date(2026, 11, 17)), ("2026-10-18", "2026-11-14"))


class CruxHistory(unittest.TestCase):
    """crux_history.py on an answer in the shape the CrUX History API documents, gaps included."""

    def test_trend_and_gaps(self):
        m = load("page-speed", "crux_history.py")
        periods = [{"firstDate": {"year": 2026, "month": 8, "day": d}, "lastDate": {"year": 2026, "month": 9, "day": d}}
                   for d in (1, 8, 15, 22)]
        data = {"record": {"key": {"origin": "https://acme.test"}, "collectionPeriods": periods, "metrics": {
            "largest_contentful_paint": {
                "histogramTimeseries": [{"start": 0, "end": 2500, "densities": ["NaN", 0.6, 0.7, 0.82]},
                                        {"start": 2500, "end": 4000, "densities": ["NaN", 0.3, 0.2, 0.1]},
                                        {"start": 4000, "densities": ["NaN", 0.1, 0.1, 0.08]}],
                "percentilesTimeseries": {"p75s": [None, 3100, 2700, 2300]}},
            "interaction_to_next_paint": {"percentilesTimeseries": {"p75s": [180, 190, 210, 150]}},
            "cumulative_layout_shift": {"percentilesTimeseries": {"p75s": ["0.31", "0.12", "0.05", "0.04"]}},
            "round_trip_time": {"percentilesTimeseries": {"p75s": [90, 95, 92, 91]}}}}}
        r = m.parse(data)
        lcp = r["metrics"][0]
        self.assertEqual((lcp["metric"], lcp["first_p75"], lcp["p75"], lcp["rating"]), ("LCP", 3100, 2300, "good"))
        self.assertEqual(lcp["periods_with_data"], 3)
        self.assertAlmostEqual(lcp["good_share"], 0.82)
        cls_ = [x for x in r["metrics"] if x["metric"] == "CLS"][0]
        self.assertEqual((cls_["first_rating"], cls_["rating"]), ("poor", "good"))
        self.assertNotIn("round_trip_time", [x["metric"] for x in r["metrics"]])
        text = m.render(r)
        self.assertIn("All three Core Web Vitals are good", text)
        self.assertIn("LCP from needs improvement to good", text)
        self.assertIn("2.30 s", text)


class AuditDiff(unittest.TestCase):
    """audit_diff.py on two audits that differ in known ways."""

    @staticmethod
    def page(url, **kw):
        p = {"url": url, "final_url": url, "status": 200, "chain": [], "title": "T " + url, "description": "D",
             "canonical_abs": url, "robots_meta": None, "x_robots_tag": None, "h1": ["H"], "words": 400,
             "jsonld_types": ["Organization"], "inlinks": 2, "depth": 1}
        p.update(kw)
        return p

    def audits(self):
        root = "https://acme.test"
        crawler = lambda access: [{"token": "OAI-SearchBot", "product": "ChatGPT search", "kind": "search",
                                   "access": access}]
        before = {"site": root, "start": root + "/", "checked": "2026-10-01", "max_pages": 100,
                  "robots": {"state": "rules", "detail": "read"}, "crawlers": crawler("open"),
                  "sitemap": {"count": 40}, "llms_txt": True,
                  "pages": {u: self.page(u) for u in (root + "/", root + "/a", root + "/b", root + "/c", root + "/d")},
                  "findings": [{"level": "fix", "category": "titles", "message": "2 pages share a title", "urls": []}]}
        after = json.loads(json.dumps(before))
        after["checked"] = "2026-11-01"
        after["crawlers"] = crawler("closed")
        after["sitemap"] = {"count": 30}
        after["llms_txt"] = False
        del after["pages"][root + "/d"]
        after["pages"][root + "/a"]["robots_meta"] = "noindex"
        after["pages"][root + "/b"]["title"] = "A new title"
        after["pages"][root + "/b"]["jsonld_types"] = []
        after["pages"][root + "/c"]["words"] = 120
        after["pages"][root + "/c"]["inlinks"] = 0
        after["findings"] = [{"level": "blocker", "category": "indexing", "message": "1 page has noindex", "urls": []}]
        return before, after

    def test_reports_each_change_at_its_level(self):
        m = load("seo-monitoring", "audit_diff.py")
        before, after = self.audits()
        r = m.compare(before, after)
        levels = {(c["level"], c["category"]) for c in r["changes"]}
        for expected in [("blocker", "indexability"), ("blocker", "AI crawlers"), ("fix", "sitemap"),
                         ("fix", "llms.txt"), ("fix", "pages"), ("fix", "structured data"), ("fix", "content"),
                         ("fix", "internal links"), ("note", "titles")]:
            self.assertIn(expected, levels)
        self.assertEqual(r["changes"][0]["level"], "blocker")
        text = m.render(r)
        self.assertIn("https://acme.test/a has noindex", text)
        self.assertIn("OAI-SearchBot (ChatGPT search) went from open to closed", text)
        self.assertIn("| https://acme.test/b | T https://acme.test/b | A new title |", text)
        self.assertIn("New, blocker: 1 page has noindex", text)
        self.assertIn("Gone, fix: 2 pages share a title", text)

    def test_same_crawl_has_no_changes(self):
        m = load("seo-monitoring", "audit_diff.py")
        before, _ = self.audits()
        self.assertIn("Nothing changed", m.render(m.compare(before, json.loads(json.dumps(before)))))


class Backlinks(unittest.TestCase):
    """backlinks.py on exports in the three tools' layouts, and on pages served from this machine."""

    @classmethod
    def setUpClass(cls):
        import http.server
        import threading
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.root = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.m = load("backlink-audit", "backlinks.py")
        cls.dir = tempfile.TemporaryDirectory()
        d = pathlib.Path(cls.dir.name)
        (d / "gsc.csv").write_text("Linking page,Last crawled\nhttps://news.site.co.uk/story,2026-11-02\n"
                                   "https://www.blog.test/post,2026-10-20\nhttps://example.com/about,2026-10-01\n")
        (d / "bing.csv").write_text("Source Url,Anchor Text,Target Url\n"
                                    "https://blog.test/post,Example,https://example.com/\n"
                                    "https://lists.test/best-tools,https://example.com,https://example.com/\n"
                                    "https://lists.test/top,click here,https://example.com/pricing\n"
                                    "https://forum.test/t/1,widget software for teams,https://example.com/old\n")
        awt = "Referring page URL\tReferring page title\tTarget URL\tAnchor\tNofollow\tUGC\tSponsored\n" \
              "https://dir.test/listing\tListing\thttps://example.com/\t\ttrue\tfalse\tfalse\n"
        (d / "awt.csv").write_bytes(awt.encode("utf-16"))
        (d / "rival-a.csv").write_text("Source Url,Target Url\nhttps://lists.test/best-tools,https://rival-a.test/\n"
                                       "https://review.test/x,https://rival-a.test/\nhttps://mag.test/y,https://rival-a.test/\n")
        (d / "rival-b.csv").write_text("Linking page\nhttps://review.test/z\nhttps://only-b.test/q\n")
        (d / "ranks.csv").write_text("1,site.co.uk\n5000,blog.test\n250000,lists.test\n")
        cls.d = d

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.dir.cleanup()

    def test_profile_from_three_layouts(self):
        rows = []
        for f in ("gsc.csv", "bing.csv", "awt.csv"):
            got, cols = self.m.read_file(self.d / f)
            rows += got
        self.assertEqual(cols["source"], "Referring page URL")
        p = self.m.profile(rows, "example.com", ["example"], self.m.load_ranks(self.d / "ranks.csv"))
        self.assertEqual(p["referring_domains"], 5)   # site.co.uk, blog.test, lists.test, forum.test, dir.test
        self.assertEqual({d["domain"] for d in p["top_domains"]},
                         {"site.co.uk", "blog.test", "lists.test", "forum.test", "dir.test"})
        self.assertEqual(p["anchors"], {"brand": 1, "address": 1, "generic": 1, "words": 1, "empty or image": 1})
        self.assertEqual(p["rel"], {"nofollow": 1})
        self.assertEqual(p["rank_tiers"]["top 10,000"], 2)

    def test_gap_orders_by_competitors(self):
        rows, _ = self.m.read_file(self.d / "bing.csv")
        comp = {"rival-a": self.m.read_file(self.d / "rival-a.csv")[0],
                "rival-b": self.m.read_file(self.d / "rival-b.csv")[0]}
        g = self.m.gap(rows, comp, "example.com")
        self.assertEqual(g[0], ["review.test", ["rival-a", "rival-b"]])
        self.assertNotIn("lists.test", [d for d, _ in g])   # it already links to the site

    def test_verify_and_targets_live(self):
        rows = [{"source": self.root + "/links-out", "domain": "x", "target": "", "anchor": "", "rel": ""},
                {"source": self.root + "/no-link", "domain": "x", "target": "", "anchor": "", "rel": ""},
                {"source": self.root + "/private/p", "domain": "x", "target": "", "anchor": "", "rel": ""}]
        v = {x["page"].rsplit("/", 1)[1]: x for x in self.m.verify(rows, "example.com", 10, 0)}
        self.assertEqual(v["links-out"]["state"], "live")
        self.assertEqual([(l["anchor"], l["rel"]) for l in v["links-out"]["links"]],
                         [("Example pricing", "nofollow ugc"), ("(image: Example logo)", "followed")])
        self.assertEqual(v["no-link"]["state"], "no link found")
        self.assertEqual(v["p"]["state"], "not checked (robots.txt)")
        t = self.m.check_targets([{"target": self.root + "/a", "domain": "d1"},
                                  {"target": self.root + "/missing", "domain": "d1"},
                                  {"target": self.root + "/missing", "domain": "d2"}], self.root, 0)
        status = {x["page"].rsplit("/", 1)[1]: x for x in t}
        self.assertEqual(status["a"]["status"], 200)
        self.assertEqual((status["missing"]["status"], status["missing"]["domains"]), (404, 2))

    def test_report_runs_end_to_end(self):
        text = run(self.m, str(self.d / "bing.csv"), "--site", "example.com", "--competitor",
                   str(self.d / "rival-a.csv"), "--quiet")
        self.assertIn("# Backlink audit: example.com", text)
        self.assertIn("Sites that link to competitors and not to example.com", text)
        self.assertIn("| review.test | rival-a |", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
