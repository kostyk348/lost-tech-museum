#!/usr/bin/env python3
"""Сборка сайта «Музей потерянных идей» (GitHub Pages).

Использование:
    python scripts/build.py                # собрать сайт: index.html + digests/*/index.html
    python scripts/build.py --widget OUT   # собрать компактный виджет для чата (одна страница)

Данные дайджеста: data/<slug>.json  (список находок + заголовок, подзаголовок, питчи)
Шаблоны: templates/dashboard.html, templates/index.html
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> метаданные для карточки на главной
DIGESTS = [
    {
        "slug": "lost-ideas-1980s-2000s",
        "title": "Идеи, которые не дожили: японский и мировой софт 1980–2006",
        "blurb": "35 находок: TRON и BTRON, Fifth Generation, i-mode, FeliCa, FIPA-ACL, Minitel, Xanadu, Plan 9, BeOS, "
                 "Transputer, Linda/Jini, iAPX 432, Setun, OGAS, HyperCard, Weiser и другие.",
        "tags": ["Япония", "ОС", "протоколы", "агенты", "железо", "сообщества"],
    },
]


def load_digest(slug):
    with open(os.path.join(ROOT, "data", slug + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def render_dashboard(d, mode="page"):
    tpl = open(os.path.join(ROOT, "templates", "dashboard.html"), encoding="utf-8").read()
    footer = ('Часть архива «Музей потерянных идей» · '
              '<a href="https://github.com/{repo}">исходники и данные на GitHub</a>')
    out = (tpl
           .replace(".gridbox__CLAMPCSS__", ".gridbox{max-height:64vh;overflow:auto;padding-right:6px}" if mode == "widget" else ".gridbox")
           .replace("__OPEN__", "false" if mode == "widget" else "true")
           .replace("__TITLE__", d["title"])
           .replace("__SUBTITLE__", d["subtitle"])
           .replace("__DATE__", d.get("generated", ""))
           .replace("__SLUG__", d["slug"])
           .replace("__FOOTERREPO__", footer.format(repo=REPO_PATH))
           .replace("__DATA__", json.dumps({"entries": d["entries"]}, ensure_ascii=False))
           .replace("__PITCHES__", json.dumps(d["pitches"], ensure_ascii=False)))
    return out


def render_hub(date):
    tpl = open(os.path.join(ROOT, "templates", "index.html"), encoding="utf-8").read()
    cards = []
    for dg in DIGESTS:
        d = load_digest(dg["slug"])
        jp = sum(1 for e in d["entries"] if e["reg"] == "jp")
        src = sum(len(e["src"]) for e in d["entries"])
        cards.append(
            '<a class="card" href="digests/{slug}/">'
            '<h3>{title}</h3><p>{blurb}</p>'
            '<div class="st"><span>{n} находок</span><span>японских: {jp}</span><span>{src} источников</span>'
            '<span>{tags}</span></div>'
            '<div class="go">Открыть дайджест →</div></a>'.format(
                slug=dg["slug"], title=dg["title"], blurb=dg["blurb"], n=len(d["entries"]),
                jp=jp, src=src, tags=" · ".join(dg["tags"])))
    return (tpl.replace("__DIGESTS__", "\n  ".join(cards))
               .replace("__DATE__", date)
               .replace("__REPO__", REPO_PATH))


REPO_PATH = os.environ.get("REPO_PATH", "kostyk348/lost-tech-museum")


def main():
    args = sys.argv[1:]
    # widget mode: single self-contained file for the chat preview
    if args and args[0] == "--widget":
        out = args[1] if len(args) > 1 else os.path.join(ROOT, "widget.html")
        d = load_digest(DIGESTS[0]["slug"])
        open(out, "w", encoding="utf-8").write(render_dashboard(d, mode="widget"))
        print("widget:", out, os.path.getsize(out))
        return

    date = max(load_digest(dg["slug"]).get("generated", "") for dg in DIGESTS)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(render_hub(date))
    for dg in DIGESTS:
        slug = dg["slug"]
        outdir = os.path.join(ROOT, "digests", slug)
        os.makedirs(outdir, exist_ok=True)
        d = load_digest(slug)
        open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(render_dashboard(d))
        shutil.copy(os.path.join(ROOT, "data", slug + ".json"), os.path.join(outdir, "data.json"))
        print("digest:", "digests/" + slug + "/index.html", len(d["entries"]), "entries")
    # GitHub Pages: не запускать Jekyll на статике
    open(os.path.join(ROOT, ".nojekyll"), "w").write("")
    print("hub: index.html + .nojekyll")


if __name__ == "__main__":
    main()
