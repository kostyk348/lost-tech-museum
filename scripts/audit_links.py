#!/usr/bin/env python3
"""Аудит ссылок архива: каждая src[].u получает живой HTTP-статус.

Открытый пункт из docs/triage-log.md: «мёртвые ссылки из записей надо ловить аудитом,
иначе они живут годами». Этот скрипт и есть аудит.

    python scripts/audit_links.py            # проверить все ссылки, обновить кэш статусов
    python scripts/audit_links.py --only-dead  # перепроверить только те, что были битыми
    python scripts/audit_links.py --limit 20   # первые N (для быстрой проверки)

Результат: data/link-audit.json — по каждому URL статус, код, дата проверки.
Код возврата 1, если есть мёртвые ссылки: публиковать можно, но статус обязан быть
виден на странице провенанса (архив не удаляет — он помечает).

Требования к вежливости: не больше одного запроса в секунду на хост, честный User-Agent,
таймаут 20 с, редиректы разрешены.
"""
import collections
import glob
import json
import os
import subprocess
import sys
import time
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "link-audit.json")
UA = "Mozilla/5.0 (compatible; museum-link-audit/1.0; +https://kostyk348.github.io/lost-tech-museum/)"
PER_HOST_DELAY = 1.0           # секунда между запросами к одному хосту
DEAD = {404, 410, 451, 500, 502, 503}
TIMEOUT = "20"


def collect_urls():
    """Все уникальные URL из data/*.json с привязкой к записям."""
    urls = collections.OrderedDict()
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        slug = os.path.splitext(os.path.basename(path))[0]
        if slug in ("link-audit", "quote-audit", "provenance"):
            continue
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for entry in data.get("entries", []):
            for src in entry.get("src", []):
                u = (src.get("u") or "").strip()
                if not u.startswith("http"):
                    continue
                urls.setdefault(u, []).append({"digest": slug, "entry": entry.get("id"),
                                               "r": src.get("r", 0), "t": src.get("t", "")})
    return urls


def probe(url):
    """HEAD, при отказе — GET с диапазоном. Возвращает (код, ошибка)."""
    cmds = [
        ["curl", "-sS", "-o", os.devnull, "-A", UA, "--max-time", TIMEOUT,
         "-L", "--head", "-w", "%{http_code}", url],
        ["curl", "-sS", "-o", os.devnull, "-A", UA, "--max-time", TIMEOUT,
         "-L", "-r", "0-2048", "-w", "%{http_code}", url],
    ]
    for cmd in cmds:
        last = 0
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=45)
        except subprocess.TimeoutExpired:
            continue
        code = (res.stdout or b"").decode("ascii", "replace").strip()
        if code.isdigit() and int(code) not in (403, 405, 501, 000):
            return int(code), ""
        last = code or (res.stderr or b"").decode("utf-8", "replace").strip()[:120]
    return (int(last) if str(last).isdigit() else 0), ("" if str(last).isdigit() else str(last))


def main():
    args = sys.argv[1:]
    old = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8")).get("links", {})
        except Exception:                      # noqa: BLE001 — битый кэш не повод не проверять
            old = {}
    urls = collect_urls()
    if "--only-dead" in args:
        urls = collections.OrderedDict((u, v) for u, v in urls.items()
                                       if old.get(u, {}).get("state") == "dead")
    if "--limit" in args:
        urls = collections.OrderedDict(list(urls.items())[:int(args[args.index("--limit") + 1])])

    print("ссылок к проверке: %d" % len(urls))
    last_hit = {}
    links = dict(old)
    dead = alive = unknown = 0
    for i, (url, refs) in enumerate(urls.items(), 1):
        host = urlparse(url).netloc
        wait = PER_HOST_DELAY - (time.time() - last_hit.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        code, err = probe(url)
        last_hit[host] = time.time()
        if code and code < 400:
            state = "alive"
            alive += 1
        elif code in DEAD or code == 0 or code >= 500:
            state = "dead"
            dead += 1
        else:
            state = "blocked"          # 401/403/429/999 — живой, но бот-стена
            unknown += 1
        links[url] = {"state": state, "code": code, "error": err,
                      "checked": time.strftime("%Y-%m-%d"), "refs": refs}
        if state != "alive" or i % 10 == 0:
            print("  %-7s %-5s %s" % (state, code, url[:96]))

    report = {"generated": time.strftime("%Y-%m-%d"), "total": len(links),
              "alive": sum(1 for v in links.values() if v.get("state") == "alive"),
              "dead": sum(1 for v in links.values() if v.get("state") == "dead"),
              "blocked": sum(1 for v in links.values() if v.get("state") == "blocked"),
              "links": dict(sorted(links.items()))}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    # История аудитов: снимок за дату, чтобы видеть тренд «сколько ссылок умерло», а не только текущее число.
    hist = os.path.join(ROOT, "data", "audit-history")
    os.makedirs(hist, exist_ok=True)
    snapshot = {"generated": report["generated"], "total": report["total"], "alive": report["alive"],
                "dead": report["dead"], "blocked": report["blocked"],
                "dead_urls": sorted(u for u, v in links.items() if v.get("state") == "dead")}
    with open(os.path.join(hist, report["generated"] + ".json"), "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, ensure_ascii=False, indent=1)
    print("\nитого: %d ссылок · живых %d · мёртвых %d · закрыто бот-стеной %d\nотчёт: data/link-audit.json"
          % (report["total"], report["alive"], report["dead"], report["blocked"]))
    return 1 if report["dead"] else 0


if __name__ == "__main__":
    sys.exit(main())
