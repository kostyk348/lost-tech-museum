#!/usr/bin/env python3
"""Предложения цитат: показывает кандидатов из уже скачанных первоисточников.

Долг архива: у части записей в `src[].q` нет дословной цитаты, а правило музея —
«нет цитаты — нет записи». Этот скрипт не выбирает цитату сам (выбор — суждение,
и оно должно быть человеческим/агентским), он готовит материал: скачивает источники
и ранжирует предложения по пересечению с фактами записи.

    python scripts/suggest_quotes.py --digest lost-ideas-1980s-2000s --fetch
    python scripts/suggest_quotes.py --digest rfc-graveyard --only-missing

Ничего не пишет в data/ — только печатает кандидатов с адресом источника.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quotes as qlib                                    # noqa: E402 — переиспользуем скачивание и нормализацию

ROOT = qlib.ROOT
JUNK = re.compile(r"(jump to|retrieved \d|isbn|edit links|privacy policy|cookie|sign in|log in|"
                  r"subscribe|all rights reserved|wikipedia®|navigation|содержание|навигаци)", re.I)
SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZА-ЯЁ«\"(])")


def tokens(text):
    return {w.lower() for w in re.findall(r"[A-Za-zА-Яа-яЁё0-9][A-Za-zА-Яа-яЁё0-9\-]{3,}", text or "")}


def suggestions(entry, text, limit=3):
    """Кандидаты: предложения, пересекающиеся по словам с фактами записи."""
    want = tokens(" ".join(str(entry.get(k, "")) for k in ("what", "why", "death", "now")))
    scored = []
    for sent in SPLIT.split(text):
        s = sent.strip()
        if not 45 <= len(s) <= 320 or JUNK.search(s):
            continue
        st = tokens(s)
        if not st:
            continue
        overlap = len(st & want)
        if overlap < 2:
            continue
        scored.append((overlap / (len(st) ** 0.5), overlap, s))
    scored.sort(reverse=True)
    out, seen = [], set()
    for _, overlap, s in scored:
        key = s[:60]
        if key in seen:
            continue
        seen.add(key)
        out.append((overlap, s))
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--digest", required=True)
    ap.add_argument("--fetch", action="store_true", help="скачать отсутствующие источники")
    ap.add_argument("--only-missing", action="store_true", help="только записи без цитаты")
    ap.add_argument("--entry", help="конкретная запись")
    ap.add_argument("--limit", type=int, default=4)
    ap.add_argument("--compact", action="store_true", help="по одному кандидату на источник")
    args = ap.parse_args()

    data = json.load(open(os.path.join(ROOT, "data", args.digest + ".json"), encoding="utf-8"))
    todo = []
    for e in data["entries"]:
        if args.entry and e.get("id") != args.entry:
            continue
        if args.only_missing and any(s.get("q") for s in e.get("src", [])):
            continue
        todo.append(e)
    print("записей к работе: %d" % len(todo))
    for e in todo:
        print("\n### %s — %s" % (e["id"], e.get("name")))
        for src in e.get("src", []):
            if src.get("q"):
                print("   (уже есть цитата: %s)" % src["q"][:70])
                continue
            local = qlib.cache_path(src["u"])
            if not os.path.exists(local) and args.fetch:
                local = qlib.fetch(src["u"]) or ""
            if not os.path.exists(local):
                print("   [%s] %s — не скачан" % ("✓" if src.get("r") else "↗", src["u"][:100]))
                continue
            text = qlib.flatten(open(local, encoding="utf-8", errors="replace").read())
            cands = suggestions(e, text, args.limit)
            print("   [%s] %s" % ("✓" if src.get("r") else "↗", src["u"]))
            if not cands:
                print("      — кандидатов нет (текст не про эту запись)")
            for overlap, s in (cands[:1] if args.compact else cands):
                print("      · (%d) %s" % (overlap, s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
