#!/usr/bin/env python3
"""Машиночитаемая поверхность музея: API, Atom-фид, sitemap, robots.

Сайт — для людей, но архив должен читаться и программами: агрегаторы, фиды, поисковики,
другие агенты. Всё генерируется из тех же data/*.json, что и HTML, — второго источника
правды не появляется.

    python scripts/machine.py          # собрать api/, feed.xml, sitemap.xml, robots.txt
    (обычно вызывается из build.py в конце сборки)

Публикуется:
    api/index.json      каталог: дайджесты, документы, стеки + счётчики
    api/entries.json    все находки всех дайджестов, с источниками и признаком цитаты
    feed.xml            Atom: дайджесты и документы, по дате сборки
    sitemap.xml         все страницы сайта
    robots.txt          разрешено всё + ссылка на sitemap
"""
import glob
import html
import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("SITE_URL", "https://kostyk348.github.io/lost-tech-museum")
REPO_PATH = os.environ.get("REPO_PATH", "kostyk348/lost-tech-museum")
SKIP = {"link-audit", "quote-audit", "provenance"}


def _read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def _write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path, len(text)


def digest_files():
    return [p for p in sorted(glob.glob(os.path.join(ROOT, "data", "*.json")))
            if os.path.splitext(os.path.basename(p))[0] not in SKIP]


def load_digests():
    out = []
    for path in digest_files():
        with open(path, encoding="utf-8") as fh:
            out.append(json.load(fh))
    return out


def audit():
    """Аудиты (цитаты, ссылки) — если есть; отсутствие аудита не ошибка, а статус."""
    res = {}
    for key in ("quote-audit", "link-audit"):
        p = os.path.join(ROOT, "data", key + ".json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                res[key] = json.load(fh)
    return res


def entries_payload(digests):
    aud = audit()
    links = (aud.get("link-audit") or {}).get("links", {})
    rows = []
    for d in digests:
        for e in d.get("entries", []):
            src = []
            for s in e.get("src", []):
                item = {"url": s.get("u"), "title": s.get("t"), "read": bool(s.get("r")),
                        "quote": s.get("q") or None}
                if s.get("u") in links:
                    item["link_state"] = links[s["u"]].get("state")
                    item["link_code"] = links[s["u"]].get("code")
                src.append(item)
            rows.append({
                "digest": d.get("slug"),
                "digest_title": d.get("title"),
                "id": e.get("id"),
                "name": e.get("name"),
                "reg": e.get("reg"),
                "dom": e.get("dom"),
                "eras": e.get("eras"),
                "years": e.get("years"),
                "gap": e.get("gap"),
                "what": e.get("what"),
                "why": e.get("why"),
                "death": e.get("death"),
                "now": e.get("now"),
                "pitch": e.get("pitch"),
                "quotes": sum(1 for s in e.get("src", []) if s.get("q")),
                "sources": len(e.get("src", [])),
                "url": "%s/digests/%s/#c-%s" % (SITE, d.get("slug"), e.get("id")),
                "src": src,
            })
    return rows


def build_catalog(digests, docs=None, stacks=None):
    docs = docs or []
    stacks = stacks or []
    aud = audit()
    qa = aud.get("quote-audit") or {}
    la = aud.get("link-audit") or {}
    dig = []
    for d in digests:
        entries = d.get("entries", [])
        dig.append({
            "slug": d.get("slug"),
            "title": d.get("title"),
            "subtitle": d.get("subtitle"),
            "generated": d.get("generated"),
            "url": "%s/digests/%s/" % (SITE, d.get("slug")),
            "data_url": "%s/digests/%s/data.json" % (SITE, d.get("slug")),
            "entries": len(entries),
            "pitches": len(d.get("pitches", [])),
            "sources": sum(len(e.get("src", [])) for e in entries),
            "sources_read": sum(1 for e in entries for s in e.get("src", []) if s.get("r")),
            "quotes": sum(1 for e in entries for s in e.get("src", []) if s.get("q")),
            "entries_with_quote": sum(1 for e in entries if any(s.get("q") for s in e.get("src", []))),
        })
    return {
        "generated": time.strftime("%Y-%m-%d"),
        "museum": "Музей потерянных идей",
        "repo": "https://github.com/%s" % REPO_PATH,
        "site": SITE,
        "licence_note": "Факты — из первоисточников (ссылки в записях); «зазор» и «что внедрить» — "
                        "суждение агента, а не факт из источника.",
        "provenance": {
            "r1_read_in_full": "источник прочитан целиком",
            "r0_index_level": "источник уровня поискового индекса",
            "quote": "дословная цитата из источника (src[].q), сверяется scripts/quotes.py",
            "quote_audit": {k: qa.get(k) for k in ("generated", "checked", "confirmed", "failed", "missing")},
            "link_audit": {k: la.get(k) for k in ("generated", "total", "alive", "dead", "blocked")},
        },
        "digests": dig,
        "docs": [{"slug": m["slug"], "title": m["title"], "url": "%s/docs/%s/" % (SITE, m["slug"])} for m in docs],
        "stacks": [{"slug": m["slug"], "title": m["title"], "url": "%s/stacks/%s/" % (SITE, m["slug"])} for m in stacks],
    }


def atom(digests, docs=None):
    docs = docs or []
    items = []
    for d in digests:
        items.append({
            "title": d.get("title"),
            "link": "%s/digests/%s/" % (SITE, d.get("slug")),
            "updated": (d.get("generated") or time.strftime("%Y-%m-%d")) + "T00:00:00Z",
            "id": "%s/digests/%s/" % (SITE, d.get("slug")),
            "summary": d.get("subtitle") or "",
        })
    for m in docs:
        items.append({
            "title": m["title"], "link": "%s/docs/%s/" % (SITE, m["slug"]),
            "updated": time.strftime("%Y-%m-%dT00:00:00Z"), "id": "%s/docs/%s/" % (SITE, m["slug"]),
            "summary": m.get("blurb", ""),
        })
    items.sort(key=lambda x: x["updated"], reverse=True)
    updated = items[0]["updated"] if items else time.strftime("%Y-%m-%dT00:00:00Z")
    body = []
    for it in items:
        body.append(
            "  <entry>\n"
            "    <title>%s</title>\n"
            "    <link href=\"%s\"/>\n"
            "    <id>%s</id>\n"
            "    <updated>%s</updated>\n"
            "    <summary>%s</summary>\n"
            "  </entry>" % (html.escape(it["title"]), it["link"], it["id"], it["updated"],
                            html.escape(it["summary"])))
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<feed xmlns="http://www.w3.org/2005/Atom">\n'
            '  <title>Музей потерянных идей</title>\n'
            '  <subtitle>Проверенные находки: технологии и протоколы, которые стоит вернуть</subtitle>\n'
            '  <link href="%s/feed.xml" rel="self"/>\n'
            '  <link href="%s/"/>\n'
            '  <id>%s/</id>\n'
            '  <updated>%s</updated>\n'
            '  <author><name>Archivessa (музей)</name></author>\n'
            '%s\n</feed>\n' % (SITE, SITE, SITE, updated, "\n".join(body)))


def sitemap(digests, docs=None, stacks=None):
    docs, stacks = docs or [], stacks or []
    today = time.strftime("%Y-%m-%d")
    urls = [(SITE + "/", today, "1.0")]
    for d in digests:
        urls.append(("%s/digests/%s/" % (SITE, d.get("slug")), d.get("generated") or today, "0.9"))
    for m in docs:
        urls.append(("%s/docs/%s/" % (SITE, m["slug"]), today, "0.6"))
    for m in stacks:
        urls.append(("%s/stacks/%s/" % (SITE, m["slug"]), today, "0.8"))
    urls.append((SITE + "/provenance/", today, "0.9"))
    rows = "\n".join("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>"
                     % (u, d, p) for u, d, p in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % rows)


def robots():
    return ("User-agent: *\nAllow: /\n\n"
            "# Правило музея: короткие цитаты и ссылки, никакой перепубликации чужих текстов.\n"
            "Sitemap: %s/sitemap.xml\n" % SITE)


def bibtex(rows):
    """BibTeX для исследователя: каждая находка — запись с адресом первоисточника."""
    def esc(s):
        return re.sub(r"[{}]", "", str(s or "")).replace("&", r"\&")
    out = ["% Музей потерянных идей — экспорт для библиографии. Сгенерировано " + time.strftime("%Y-%m-%d") + ".",
           "% «gap» и «pitch» — суждение агента; факты — со ссылкой на источник.", ""]
    for r in rows:
        year = re.search(r"\b(19|20)\d\d\b", r.get("years") or "")
        primary = (r.get("src") or [{}])[0].get("url", "")
        key = "%s-%s" % (r.get("digest", "museum"), r.get("id", "entry"))
        out.append("@misc{%s," % re.sub(r"[^A-Za-z0-9:_-]", "", key))
        out.append("  title       = {%s}," % esc(r.get("name")))
        if year:
            out.append("  year        = {%s}," % year.group(0))
        out.append("  howpublished= {Музей потерянных идей (%s)}," % esc(r.get("digest_title")))
        if primary:
            out.append("  url         = {%s}," % primary)
        out.append("  note        = {id: %s; источников: %s; цитат: %s}" %
                   (esc(r.get("id")), r.get("sources"), r.get("quotes")))
        out.append("}\n")
    return "\n".join(out)


def csv_rows(rows):
    """CSV для таблиц: одна строка — одна находка, источники перечислены через ;."""
    import csv as _csv
    import io
    buf = io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow(["digest", "id", "name", "reg", "dom", "eras", "years", "gap", "sources", "quotes",
                "page_url", "source_urls"])
    for r in rows:
        w.writerow([r.get("digest"), r.get("id"), r.get("name"), r.get("reg"), r.get("dom"),
                    "|".join(r.get("eras") or []), r.get("years"), r.get("gap"),
                    r.get("sources"), r.get("quotes"), r.get("url"),
                    ";".join(s.get("url") or "" for s in (r.get("src") or []))])
    return buf.getvalue()


def write_all(digests, docs=None, stacks=None):
    docs, stacks = docs or [], stacks or []
    rows = entries_payload(digests)
    written = []
    written.append(_write("api/index.json",
                          json.dumps(build_catalog(digests, docs, stacks), ensure_ascii=False, indent=1) + "\n"))
    written.append(_write("api/entries.json",
                          json.dumps({"generated": time.strftime("%Y-%m-%d"), "count": len(rows),
                                      "entries": rows}, ensure_ascii=False, indent=1) + "\n"))
    written.append(_write("api/museum.bib", bibtex(rows)))
    written.append(_write("api/entries.csv", csv_rows(rows)))
    written.append(_write("feed.xml", atom(digests, docs)))
    written.append(_write("sitemap.xml", sitemap(digests, docs, stacks)))
    written.append(_write("robots.txt", robots()))
    return written


if __name__ == "__main__":
    dig = load_digests()
    for path, size in write_all(dig):
        print("%-18s %6d байт" % (path, size))
