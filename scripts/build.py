#!/usr/bin/env python3
"""Сборка сайта «Музей потерянных идей» (GitHub Pages).

    python scripts/build.py                # index.html + digests/*/index.html + docs/*/index.html
    python scripts/build.py --widget OUT   # компактный виджет дайджеста для чата

Источники правды:
    data/<slug>.json   — находки дайджеста (title, subtitle, pitches, entries)
    docs/<slug>.md     — документы (концепты, заметки) в безопасном подмножестве Markdown
Шаблоны: templates/dashboard.html, templates/doc.html, templates/index.html
HTML всегда генерируется из данных; руками не правится.
"""
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_PATH = os.environ.get("REPO_PATH", "kostyk348/lost-tech-museum")

DIGESTS = [
    {
        "slug": "lost-ideas-1980s-2000s",
        "title": "Идеи, которые не дожили: японский и мировой софт 1980–2006",
        "blurb": "35 находок: TRON и BTRON, Fifth Generation, i-mode, FeliCa, FIPA-ACL, Minitel, Xanadu, Plan 9, BeOS, "
                 "Transputer, Linda/Jini, iAPX 432, Setun, OGAS, HyperCard, Weiser и другие.",
        "tags": ["Япония", "ОС", "протоколы", "агенты", "железо", "сообщества"],
    },
]

DOCS = [
    {
        "slug": "museum-bots",
        "title": "Два бота, которые делают музей: «Куратор» и «HyperCard»",
        "blurb": "Концепт: автономный конвейер проверенных находок + бот личных стеков-карточек поверх архива",
        "tags": ["архитектура", "агенты", "автоматизация"],
    },
]


def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\s][^*]*)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


_BREAK = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|>|#{1,6}\s|\||```|---)")


def md_to_html(text):
    """Безопасное подмножество Markdown: заголовки, списки, таблицы, код, цитаты, hr, inline."""
    lines = text.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue

        if re.match(r"^\s*\|", line) and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and re.match(r"^\s*\|", lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = "<table><thead><tr>" + "".join("<th>%s</th>" % _inline(h) for h in head) + "</tr></thead><tbody>"
            for r in rows:
                t += "<tr>" + "".join("<td>%s</td>" % _inline(c) for c in r) + "</tr>"
            out.append(t + "</tbody></table>")
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = min(len(m.group(1)), 6)      # "#" = заголовок страницы, в тело не дублируется
            if lvl >= 2:
                out.append("<h%d>%s</h%d>" % (lvl, _inline(m.group(2)), lvl))
            i += 1
            continue

        if re.match(r"^\s*---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        if re.match(r"^\s*>", line):
            buf = []
            while i < len(lines) and re.match(r"^\s*>", lines[i]):
                buf.append(_inline(re.sub(r"^\s*>\s?", "", lines[i])))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(buf))
            continue

        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            items = []
            while i < len(lines) and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i])):
                items.append(_inline(re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[i])))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % it for it in items), tag))
            continue

        if not line.strip():
            i += 1
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not _BREAK.match(lines[i]):
            para.append(lines[i].strip())
            i += 1
        if not para:                      # страховка: цикл обязан двигаться
            para.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % _inline(" ".join(para)))
    return "\n".join(out)


def _read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def render_dashboard(d, mode="page"):
    tpl = _read("templates/dashboard.html")
    footer = ('Часть архива «Музей потерянных идей» · '
              '<a href="https://github.com/{repo}">исходники и данные на GitHub</a>')
    return (tpl
            .replace(".gridbox__CLAMPCSS__",
                     ".gridbox{max-height:64vh;overflow:auto;padding-right:6px}" if mode == "widget" else ".gridbox")
            .replace("__OPEN__", "false" if mode == "widget" else "true")
            .replace("__TITLE__", d["title"])
            .replace("__SUBTITLE__", d["subtitle"])
            .replace("__DATE__", d.get("generated", ""))
            .replace("__SLUG__", d["slug"])
            .replace("__FOOTERREPO__", footer.format(repo=REPO_PATH))
            .replace("__DATA__", json.dumps({"entries": d["entries"]}, ensure_ascii=False))
            .replace("__PITCHES__", json.dumps(d["pitches"], ensure_ascii=False)))


def render_doc(meta, date):
    tpl = _read("templates/doc.html")
    body = md_to_html(_read("docs/%s.md" % meta["slug"]))
    return (tpl.replace("__TITLE__", meta["title"])
               .replace("__BLURB__", html.escape(meta["blurb"], quote=False))
               .replace("__DATE__", date)
               .replace("__SLUG__", meta["slug"])
               .replace("__REPO__", REPO_PATH)
               .replace("__BODY__", body))


def _card(href, title, blurb, stats, go):
    return ('<a class="card" href="%s"><h3>%s</h3><p>%s</p>'
            '<div class="st">%s</div><div class="go">%s</div></a>'
            % (href, title, blurb, "".join("<span>%s</span>" % s for s in stats), go))


def render_hub(date):
    tpl = _read("templates/index.html")
    dcards = []
    for dg in DIGESTS:
        d = json.loads(_read("data/%s.json" % dg["slug"]))
        jp = sum(1 for e in d["entries"] if e["reg"] == "jp")
        src = sum(len(e["src"]) for e in d["entries"])
        dcards.append(_card("digests/%s/" % dg["slug"], dg["title"], dg["blurb"],
                            ["%d находок" % len(d["entries"]), "японских: %d" % jp,
                             "%d источников" % src, " · ".join(dg["tags"])],
                            "Открыть дайджест →"))
    mcards = [_card("docs/%s/" % m["slug"], m["title"], m["blurb"], list(m["tags"]), "Читать концепт →")
              for m in DOCS]
    sections = ("  <h2>Дайджесты</h2>\n  " + "\n  ".join(dcards)
                + "\n\n  <h2>Концепты и архитектура</h2>\n  " + "\n  ".join(mcards))
    return (tpl.replace("__SECTIONS__", sections)
               .replace("__DATE__", date)
               .replace("__REPO__", REPO_PATH))


def main():
    args = sys.argv[1:]
    if args and args[0] == "--widget":
        out = args[1] if len(args) > 1 else os.path.join(ROOT, "widget.html")
        d = json.loads(_read("data/%s.json" % DIGESTS[0]["slug"]))
        open(out, "w", encoding="utf-8").write(render_dashboard(d, mode="widget"))
        print("widget:", out, os.path.getsize(out))
        return

    date = max([json.loads(_read("data/%s.json" % dg["slug"])).get("generated", "") for dg in DIGESTS] + ["2026-01-01"])
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(render_hub(date))
    print("hub: index.html")
    for dg in DIGESTS:
        outdir = os.path.join(ROOT, "digests", dg["slug"])
        os.makedirs(outdir, exist_ok=True)
        d = json.loads(_read("data/%s.json" % dg["slug"]))
        open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(render_dashboard(d))
        shutil.copy(os.path.join(ROOT, "data", dg["slug"] + ".json"), os.path.join(outdir, "data.json"))
        print("digest: digests/%s/index.html %d entries" % (dg["slug"], len(d["entries"])))
    for meta in DOCS:
        outdir = os.path.join(ROOT, "docs", meta["slug"])
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(render_doc(meta, date))
        shutil.copy(os.path.join(ROOT, "docs", meta["slug"] + ".md"), os.path.join(outdir, "source.md"))
        print("doc: docs/%s/index.html" % meta["slug"])
    open(os.path.join(ROOT, ".nojekyll"), "w").write("")
    print("done")


if __name__ == "__main__":
    main()
