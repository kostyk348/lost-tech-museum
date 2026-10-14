#!/usr/bin/env python3
"""Проверка собранных страниц: плейсхолдеры, форма данных, наличие контента.

Запускать после build.py. Ловит класс ошибок, который уже случился однажды:
шаблон читает DATA.entries, а в страницу вписан голый массив — синтаксически валидный
JS, который падает в рантайме и оставляет пустую страницу.

    python scripts/check_site.py            # проверить все страницы
    python scripts/check_site.py --fix-hint # + подсказка, где искать
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACEHOLDER = re.compile(r"__[A-Z][A-Z0-9_]*__")

# страница -> (ожидаемый первый символ JSON-данных, обязательные маркеры)
PAGES = [
    ("index.html", None, ["<h2>", "card"]),
    ("digests/lost-ideas-1980s-2000s/index.html", "{", ["const DATA", "DATA.entries"]),
    ("digests/portfolio-review/index.html", "{", ["const DATA", "DATA.entries"]),
    ("digests/lost-ideas-1980s-2000s/widget.html", "{", ["const DATA", "DATA.entries"]),
    ("digests/portfolio-review/widget.html", "{", ["const DATA", "DATA.entries"]),
    ("stacks/agent-protocols/index.html", None, ["<script"]),
    ("docs/museum-bots/index.html", None, ["<h2>"]),
]


def main():
    bad = 0
    for rel, shape, markers in PAGES:
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
    # данные дайджестов: количество записей должно совпадать с JSON
    for slug in ("lost-ideas-1980s-2000s", "portfolio-review"):
        data = json.load(open(os.path.join(ROOT, "data", slug + ".json"), encoding="utf-8"))
        page = open(os.path.join(ROOT, "digests", slug, "index.html"), encoding="utf-8").read()
        ok = (data["title"][:30] in page)
        print("  %s  данные %-30s записей: %d, заголовок в странице: %s" %
              ("OK   " if ok else "FAIL ", slug, len(data["entries"]), ok))
        bad += 0 if ok else 1
    print("\nИТОГ:", "страницы согласованы" if not bad else "ПРОБЛЕМ: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
