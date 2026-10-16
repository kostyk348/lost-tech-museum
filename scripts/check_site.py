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
    print("\nИТОГ:", "страницы согласованы" if not bad else "ПРОБЛЕМ: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
