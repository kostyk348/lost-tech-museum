#!/usr/bin/env python3
"""Проверка провенанса: каждая дословная цитата (src[].q) должна найтись в своём первоисточнике.

Правило музея: «нет цитаты — нет записи». Этот скрипт не даёт правилу размякнуть:
он скачивает первоисточники в cache/quotes/ и ищет в них каждую цитату из data/*.json,
игнорируя переносы строк (сравнение по словам, не по пробелам).

    python scripts/quotes.py            # проверить то, что уже скачано
    python scripts/quotes.py --fetch     # сначала скачать отсутствующие источники

Код возврата 1, если хоть одна цитата не подтвердилась — публиковать нельзя.
"""
import glob
import hashlib
import html as htmlmod
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "quotes")


def flatten(text):
    """Строки источника -> непрерывный текст (дефисный перенос не разрывается)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    if "<html" in text[:2000].lower() or "</p>" in text[:4000].lower():
        text = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", text)
        text = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|dd|dt|blockquote)>", "\n", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = htmlmod.unescape(text)
    lines = [l.strip() for l in text.split("\n")]
    out = []
    for line in lines:
        if not line:
            continue
        if out and out[-1].endswith("-"):
            out[-1] = out[-1] + line
        else:
            out.append(line)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def cache_path(url):
    return os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest()[:16] + ".txt")


def fetch(url):
    path = cache_path(url)
    if os.path.exists(path):
        return path
    os.makedirs(CACHE, exist_ok=True)
    tmp = path + ".part"
    code = subprocess.run(
        ["curl", "-sSL", "--max-time", "45", "-A", "Mozilla/5.0 (museum-quotes)", "-o", tmp, "-w", "%{http_code}", url],
        capture_output=True, text=True).stdout.strip()
    if code != "200":
        if os.path.exists(tmp):
            os.remove(tmp)
        return None
    if url.lower().endswith(".pdf"):          # PDF: пробуем вытащить текстовый слой
        txt = subprocess.run(["pdftotext", "-q", tmp, "-"], capture_output=True, text=True).stdout
        if txt.strip():
            open(path, "w", encoding="utf-8").write(txt)
            os.remove(tmp)
            return path
        os.remove(tmp)
        return None
    os.rename(tmp, path)
    return path


def quoted_regex(quote):
    """Регулярка по цитате: пробелы и переносы источника не важны, слова — важны."""
    words = [re.escape(w) for w in re.sub(r"\s*…\s*$", "", quote).split()]
    return re.compile(r"\s+".join(words))


def main():
    do_fetch = "--fetch" in sys.argv
    checks, missing_src, failed = [], [], []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        digest = os.path.splitext(os.path.basename(path))[0]
        for entry in json.load(open(path, encoding="utf-8")).get("entries", []):
            for src in entry.get("src", []):
                if not src.get("q"):
                    continue
                checks.append((digest, entry["id"], src))

    print("цитат к проверке: %d" % len(checks))
    for digest, entry_id, src in checks:
        local = cache_path(src["u"])
        if not os.path.exists(local) and do_fetch:
            local = fetch(src["u"]) or ""
        if not os.path.exists(local):
            missing_src.append((entry_id, src["u"]))
            continue
        text = flatten(open(local, encoding="utf-8", errors="replace").read())
        if quoted_regex(src["q"]).search(text):
            print("  OK    %-13s %s" % (entry_id, src["u"][:90]))
        else:
            failed.append((entry_id, src["u"], src["q"][:80]))
            print("  FAIL  %-13s %s" % (entry_id, src["u"][:90]))

    for entry_id, url in missing_src:
        print("  НЕТ   %-13s %s (источник не скачан: нужен --fetch)" % (entry_id, url[:80]))
    print("\nподтверждено: %d · не подтверждено: %d · без источника: %d" %
          (len(checks) - len(failed) - len(missing_src), len(failed), len(missing_src)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
