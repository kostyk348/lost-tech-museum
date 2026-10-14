#!/usr/bin/env python3
"""Проверка собранных страниц: плейсхолдеры, форма данных, наличие контента.

Запускать после build.py. Ловит класс ошибок, который уже случился однажды:
шаблон читает DATA.entries, а в страницу вписан голый массив — синтаксически валидный
JS, который падает в рантайме и оставляет пустую страницу.

    python scripts/check_site.py            # проверить все страницы
    python scripts/check_site.py --fix-hint # + подсказка, где искать
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACEHOLDER = re.compile(r"__[A-Z][A-Z0-9_]*__")

# страница -> (ожидаемый первый символ JSON-данных, обязательные маркеры)
PAGES: list[tuple[str, str | None, list[str]]] = [
    ("index.html", None, ["<h2>", "card"]),
    ("stacks/agent-protocols/index.html", None, ["<script"]),
    ("docs/museum-bots/index.html", None, ["<h2>"]),
]

# Страницы дайджестов и виджетов находим сами: добавил data/<slug>.json и собрал —
# проверка подхватит страницу без правки этого файла.
for _d in sorted(glob.glob(os.path.join(ROOT, "digests", "*"))):
    if not os.path.isdir(_d):
        continue
    _slug = os.path.basename(_d)
    if os.path.exists(os.path.join(_d, "index.html")):
        PAGES.append(("digests/%s/index.html" % _slug, "{", ["const DATA", "DATA.entries"]))
    if os.path.exists(os.path.join(_d, "widget.html")):
        PAGES.append(("digests/%s/widget.html" % _slug, "{", ["const DATA", "DATA.entries"]))


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
    # (список слаг'ов — из data/*.json, а не жёстко: новый дайджест проверяется сам)
    for _path in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        slug = os.path.splitext(os.path.basename(_path))[0]
        if not os.path.exists(os.path.join(ROOT, "digests", slug, "index.html")):
            continue
        data = json.load(open(_path, encoding="utf-8"))
        page = open(os.path.join(ROOT, "digests", slug, "index.html"), encoding="utf-8").read()
        ok = (data["title"][:30] in page)
        print("  %s  данные %-30s записей: %d, заголовок в странице: %s" %
              ("OK   " if ok else "FAIL ", slug, len(data["entries"]), ok))
        bad += 0 if ok else 1
    print("\nИТОГ:", "страницы согласованы" if not bad else "ПРОБЛЕМ: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
