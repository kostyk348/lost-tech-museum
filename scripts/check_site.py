#!/usr/bin/env python3
"""Проверка собранных страниц: плейсхолдеры, форма данных, наличие контента.

Запускать после build.py (build.py делает это сам). Ловит класс ошибок, который уже
случался: шаблон читает DATA.entries, а в страницу вписан голый массив — синтаксически
валидный JS, который падает в рантайме и оставляет пустую страницу.

Список страниц здесь НЕ хардкодится, иначе новая страница молча остаётся непроверенной
и «все страницы в порядке» перестаёт что-либо значить: страницы находятся сканированием
каталогов (digests/*, stacks/*, docs/*), а регистрации из build.py сверяются со сборкой.

    python scripts/check_site.py            # проверить все страницы
    python scripts/check_site.py --fix-hint # + подсказка, где искать
"""
import glob
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACEHOLDER = re.compile(r"__[A-Z][A-Z0-9_]*__")

# Контракты страниц, которые нельзя вывести из имени файла.
BASE = [
    ("index.html", None, ["<h2>", "card"]),
]

# Каталог -> (глоб, ожидаемая форма DATA, обязательные маркеры)
KINDS = [
    ("digest", "digests/*/index.html", "{", ["const DATA", "DATA.entries"]),
    ("digest", "digests/*/widget.html", "{", ["const DATA", "DATA.entries"]),
    ("stack", "stacks/*/index.html", None, ["<script"]),
    ("doc", "docs/*/index.html", None, ["<h2>"]),
    ("provenance", "provenance/index.html", None, ["Провенанс архива", "<table>"]),
]


def discover():
    """Все собранные страницы по глобам — чтобы новую страницу нельзя было забыть."""
    found = {}
    for _, pattern, shape, markers in KINDS:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            found[rel] = (shape, markers)
    for rel, shape, markers in BASE:
        found[rel] = (shape, markers)
    return found


def build_registries():
    """Читает DIGESTS/DOCS/STACKS из build.py, не выполняя сборку."""
    path = os.path.join(ROOT, "scripts", "build.py")
    spec = importlib.util.spec_from_file_location("_museum_build", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    return mod


def check_machine():
    """Машиночитаемая поверхность и целостность данных.

    Страница может быть красивой, а API — врать: тогда агрегатор тихо разнесёт ошибку.
    Поэтому api/feed/sitemap проверяются разбором, а не наличием файла.
    """
    import xml.etree.ElementTree as ET
    bad = 0
    print("\nмашиночитаемое и данные:")

    def note(ok, msg):
        print("  %s  %s" % ("OK  " if ok else "FAIL", msg))
        return 0 if ok else 1

    digests = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        slug = os.path.splitext(os.path.basename(path))[0]
        if slug in ("link-audit", "quote-audit"):
            continue
        digests.append((slug, json.load(open(path, encoding="utf-8"))))
    # kind (например «portfolio») зарегистрирован в build.py, а не в данных — берём оттуда
    portfolio = set()
    try:
        for dg in getattr(build_registries(), "DIGESTS", []):
            if dg.get("kind") == "portfolio":
                portfolio.add(dg["slug"])
    except Exception:                          # noqa: BLE001
        pass

    # api/index.json — каталог согласован с числом дайджестов
    api_index = os.path.join(ROOT, "api", "index.json")
    if not os.path.exists(api_index):
        bad += note(False, "api/index.json отсутствует — запустить python scripts/machine.py")
    else:
        cat = json.load(open(api_index, encoding="utf-8"))
        bad += note(len(cat.get("digests", [])) == len(digests),
                    "api/index.json: дайджестов %d, в данных %d"
                    % (len(cat.get("digests", [])), len(digests)))
        bad += note(bool(cat.get("provenance")), "api/index.json: блок provenance заполнен")

    # api/entries.json — ни одна находка не потерялась
    api_entries = os.path.join(ROOT, "api", "entries.json")
    expected = sum(len(d.get("entries", [])) for _, d in digests)
    if not os.path.exists(api_entries):
        bad += note(False, "api/entries.json отсутствует")
    else:
        rows = json.load(open(api_entries, encoding="utf-8"))
        bad += note(rows.get("count") == expected == len(rows.get("entries", [])),
                    "api/entries.json: записей %s, в данных %d" % (rows.get("count"), expected))

    # feed.xml / sitemap.xml — обязаны разбираться как XML
    for rel, min_items, tag in (("feed.xml", 1, "entry"), ("sitemap.xml", 6, "url")):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            bad += note(False, "%s отсутствует" % rel)
            continue
        try:
            root = ET.parse(path).getroot()
            n = len([el for el in root.iter() if el.tag.endswith(tag)])
            bad += note(n >= min_items, "%s: разбирается, элементов %s = %d" % (rel, tag, n))
        except Exception as exc:              # noqa: BLE001 — битый XML и есть провал проверки
            bad += note(False, "%s: не разбирается (%s)" % (rel, exc))

    robots = os.path.join(ROOT, "robots.txt")
    bad += note(os.path.exists(robots) and "Sitemap:" in open(robots, encoding="utf-8").read(),
                "robots.txt ссылается на sitemap")

    # Экспорт для исследователя: BibTeX и CSV
    for rel, marker, min_lines in (("api/museum.bib", "@misc{", 80), ("api/entries.csv", "digest,id,name", 80)):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            bad += note(False, "%s отсутствует" % rel)
            continue
        body = open(path, encoding="utf-8").read()
        n = body.count("\n")
        bad += note(marker in body and n >= min_lines,
                    "%s: %d строк, маркер на месте" % (rel, n))

    bad += note(os.path.exists(os.path.join(ROOT, "provenance", "index.html")),
                "страница провенанса собрана")

    # Целостность данных: id уникальны между дайджестами, источники размечены, gap в диапазоне
    seen, dupes, bad_src, bad_gap = {}, [], [], []
    for slug, d in digests:
        for e in d.get("entries", []):
            seen.setdefault(e.get("id"), []).append(slug)
            g = e.get("gap")
            if g is not None and not (isinstance(g, int) and 1 <= g <= 5):
                bad_gap.append("%s/%s=%r" % (slug, e.get("id"), g))
            for s in e.get("src", []):
                if not str(s.get("u", "")).startswith("http") or not s.get("t"):
                    bad_src.append("%s/%s" % (slug, e.get("id")))
                if s.get("r") is not None and s.get("r") not in (0, 1):
                    bad_src.append("%s/%s (r не 0/1)" % (slug, e.get("id")))
                if slug not in portfolio and s.get("r") not in (0, 1):
                    bad_src.append("%s/%s (нет разметки r)" % (slug, e.get("id")))
                if "q" in s and not str(s.get("q") or "").strip():
                    bad_src.append("%s/%s (пустая цитата)" % (slug, e.get("id")))
    dupes = [i for i, v in seen.items() if len(v) > 1]
    bad += note(not dupes, "id находок уникальны между дайджестами" if not dupes
                else "дубли id: %s" % ", ".join(dupes[:8]))
    bad += note(not bad_src, "источники размечены (url, название, r:0|1, непустая цитата)" if not bad_src
                else "битые источники: %s" % ", ".join(sorted(set(bad_src))[:6]))
    bad += note(not bad_gap, "gap в диапазоне 1..5" if not bad_gap else "gap вне диапазона: %s" % bad_gap[:6])
    return bad


def main():
    bad = 0
    pages = discover()
    print("страниц найдено: %d" % len(pages))
    for rel in sorted(pages):
        shape, markers = pages[rel]
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("  SKIP  %-46s нет файла" % rel)
            continue
        html = open(path, encoding="utf-8").read()
        problems = []
        left = sorted(set(PLACEHOLDER.findall(html)))
        if left:
            problems.append("остались плейсхолдеры: %s" % ", ".join(left[:5]))
        m = re.search(r"const DATA = (.)", html)
        if m and shape and m.group(1) != shape:
            problems.append("форма DATA: начинается с %r, шаблон ждёт %r" % (m.group(1), shape))
        if "DATA.entries" in html and m and m.group(1) != "{":
            problems.append("JS читает DATA.entries, а в DATA не объект — страница отрисуется пустой")
        for mk in markers:
            if mk not in html:
                problems.append("нет маркера %r" % mk)
        if len(html) < 800:
            problems.append("подозрительно мало ( %d байт)" % len(html))
        if problems:
            bad += 1
            print("  FAIL  %-46s %s" % (rel, "; ".join(problems)))
        else:
            print("  OK    %-46s %d КБ" % (rel, len(html) // 1024))

    # Регистрации в build.py обязаны совпадать с собранным («забыли собрать» / «собрали не то»).
    try:
        b = build_registries()
        registered = ([("digests/%s/index.html" % d["slug"], "дайджест") for d in getattr(b, "DIGESTS", [])]
                      + [("docs/%s/index.html" % d["slug"], "документ") for d in getattr(b, "DOCS", [])]
                      + [("stacks/%s/index.html" % d["slug"], "сборник") for d in getattr(b, "STACKS", [])])
        missing = [rel for rel, _ in registered if rel not in pages]
        for rel in missing:
            print("  FAIL  %-46s зарегистрирован в build.py, но не собран" % rel)
        bad += len(missing)
        if not missing:
            print("  OK    регистрации build.py совпадают со сборкой (%d записей)" % len(registered))
    except Exception as e:  # noqa: BLE001 — сверка не должна ломать саму проверку
        print("  note  сверка с build.py пропущена: %s" % e)

    # данные дайджестов: количество записей и заголовок должны совпадать со страницей
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        slug = os.path.splitext(os.path.basename(path))[0]
        if not os.path.exists(os.path.join(ROOT, "digests", slug, "index.html")):
            continue
        data = json.load(open(path, encoding="utf-8"))
        page = open(os.path.join(ROOT, "digests", slug, "index.html"), encoding="utf-8").read()
        ok = (data["title"][:30] in page)
        print("  %s  данные %-30s записей: %d, заголовок в странице: %s" %
              ("OK   " if ok else "FAIL ", slug, len(data["entries"]), ok))
        bad += 0 if ok else 1
    bad += check_machine()
    print("\nИТОГ:", "страницы согласованы" if not bad else "ПРОБЛЕМ: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
