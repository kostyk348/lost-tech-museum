#!/usr/bin/env python3
"""Проверка целостности стеков карточек (Chartessa).

    python scripts/lint_stacks.py          # проверить данные стеков + уже собранные страницы

Что проверяется:
  * обязательные поля карточки и уникальность id;
  * фон карточки объявлен в stack.backgrounds (фон — это шаблон, а не украшение);
  * связи: цель существует, связь не ведёт на саму себя, у связи написано «зачем»;
  * записи архива, на которые опирается карточка, реально есть в data/<archive>.json;
  * источники: http(s), метка r строго 0 или 1 (1 = прочитан целиком, 0 = индекс поиска);
  * действия: непустой текст, белый список инструментов из известного набора, никакого кода;
  * собранная страница stacks/<slug>/index.html: карточки на месте, плейсхолдеров не осталось;
  * обратные ссылки: дайджест-архив действительно ведёт в стеки, а стек — в записи архива.

Код возврата 1 — есть ошибки (стек публиковать нельзя).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402  (ROOT, STACKS, stack_data, _read)

ERRORS = []
WARNINGS = []

# Инструменты, которые агент реально может вызвать из действия карточки.
ALLOWED_TOOLS = {
    "web_search", "web_extract", "browser_exec", "read_file", "write_file",
    "terminal", "message_agent", "skill_view", "vision_analyze", "skill_manage",
}


def err(slug, msg):
    ERRORS.append("[%s] ошибка: %s" % (slug, msg))


def warn(slug, msg):
    WARNINGS.append("[%s] внимание: %s" % (slug, msg))


def lint_stack(meta):
    slug = meta["slug"]
    path = "stacks/%s/stack.json" % slug
    if not os.path.exists(os.path.join(build.ROOT, path)):
        err(slug, "нет файла данных %s" % path)
        return None
    try:
        st = build.stack_data(slug)
    except Exception as exc:                                  # noqa: BLE001
        err(slug, "stack.json не читается: %s" % exc)
        return None

    for key in ("slug", "title", "subtitle", "generated", "backgrounds", "cards"):
        if not st.get(key):
            err(slug, "пустое обязательное поле стека: %s" % key)
    if st.get("slug") != slug:
        err(slug, "slug в данных (%s) не совпадает с реестром сборки" % st.get("slug"))

    backgrounds = st.get("backgrounds") or {}
    for bid, bg in backgrounds.items():
        for key in ("name", "layout", "note"):
            if not bg.get(key):
                err(slug, "фон %s: пустое поле %s" % (bid, key))
        if bg.get("layout") not in ("list", "cols", "table"):
            err(slug, "фон %s: неизвестный layout %r" % (bid, bg.get("layout")))

    # Архив-источник стека
    arch = st.get("archive") or {}
    entries = set()
    if not arch.get("slug"):
        err(slug, "не указан архив-источник стека (archive.slug)")
    else:
        try:
            data = json.loads(build._read("data/%s.json" % arch["slug"]))
            entries = {e["id"] for e in data["entries"]}
        except Exception as exc:                             # noqa: BLE001
            err(slug, "архив %s не читается: %s" % (arch["slug"], exc))

    cards = st.get("cards") or []
    ids = [c.get("id") for c in cards]
    for cid in set(ids):
        if ids.count(cid) > 1:
            err(slug, "id карточки повторяется: %s" % cid)
    known = set(ids)

    linked_from = {cid: set() for cid in ids}
    for card in cards:
        cid = card.get("id") or "<без id>"
        for key in ("id", "title", "bg", "fields"):
            if not card.get(key):
                err(slug, "карточка %s: пустое поле %s" % (cid, key))
        if card.get("bg") not in backgrounds:
            err(slug, "карточка %s: фон %r не объявлен в backgrounds" % (cid, card.get("bg")))
        for f in card.get("fields") or []:
            if not (f.get("lbl") and f.get("val")):
                err(slug, "карточка %s: поле без lbl/val" % cid)
            if f.get("to") and f["to"] not in known:
                err(slug, "карточка %s: поле ссылается на несуществующую карточку %s" % (cid, f["to"]))
            elif f.get("to") and f["to"] != cid:
                linked_from.setdefault(f["to"], set()).add(cid)   # ссылка поля — тоже связь
        for eid in card.get("archive") or []:
            if entries and eid not in entries:
                err(slug, "карточка %s: записи %s нет в архиве %s" % (cid, eid, arch.get("slug")))
        for lk in card.get("links") or []:
            if lk.get("to") not in known:
                err(slug, "карточка %s: связь ведёт в никуда: %r" % (cid, lk.get("to")))
            elif lk["to"] == cid:
                err(slug, "карточка %s: связь на саму себя" % cid)
            elif not lk.get("why"):
                err(slug, "карточка %s -> %s: не написано, зачем связь" % (cid, lk["to"]))
            else:
                linked_from.setdefault(lk["to"], set()).add(cid)
        for src in card.get("sources") or []:
            if not str(src.get("u", "")).startswith("http"):
                err(slug, "карточка %s: источник без http(s)-ссылки: %r" % (cid, src.get("u")))
            if src.get("r") not in (0, 1):
                err(slug, "карточка %s: метка r должна быть 0 или 1, а не %r" % (cid, src.get("r")))
            if not src.get("t"):
                err(slug, "карточка %s: у источника нет названия" % cid)
        for i, act in enumerate(card.get("actions") or []):
            tag = "карточка %s, действие %d" % (cid, i + 1)
            if not act.get("t"):
                err(slug, "%s: нет подписи кнопки" % tag)
            if not (act.get("p") or "").strip():
                err(slug, "%s: пустой промпт — кнопка без действия" % tag)
            if "tools" not in act:
                err(slug, "%s: нет белого списка инструментов (пустой список — тоже ответ)" % tag)
            tools = act.get("tools") or []
            if len(set(tools)) != len(tools):
                err(slug, "%s: инструменты повторяются" % tag)
            for t in tools:
                if t not in ALLOWED_TOOLS:
                    err(slug, "%s: неизвестный инструмент %r" % (tag, t))
            if any(tok in (act.get("p") or "") for tok in ("{", "}", "$(", "<script", "=>", "def ", "import ")):
                err(slug, "%s: похоже на код, а действие должно быть промптом" % tag)

    # Достижимость: домашняя карточка — первая в файле
    home = ids[0] if ids else None
    seen, stack = set(), [home] if home else []
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        card = next((c for c in cards if c.get("id") == cur), None)
        if not card:
            continue
        targets = [l["to"] for l in card.get("links") or [] if l.get("to") in known]
        targets += [f["to"] for f in card.get("fields") or [] if f.get("to") in known]
        targets += list(linked_from.get(cur, ()))
        stack.extend(targets)
    for cid in ids:
        if cid not in seen:
            warn(slug, "карточка %s недостижима из витрины по связям" % cid)
    for cid in ids:
        if cid != home and not linked_from.get(cid):
            warn(slug, "на карточку %s никто не ссылается (односторонняя связь)" % cid)

    return st


def lint_built(slug, st):
    """Проверка уже собранной страницы: она обязана быть из этих данных."""
    page = os.path.join(build.ROOT, "stacks", slug, "index.html")
    if not os.path.exists(page):
        warn(slug, "страница stacks/%s/index.html ещё не собрана (python scripts/build.py)" % slug)
        return
    with open(page, encoding="utf-8") as fh:
        html = fh.read()
    for marker in ("__STACK__", "__TITLE__", "__THEME__", "__CLAMPCSS__"):
        if marker in html:
            err(slug, "в собранной странице остался плейсхолдер %s" % marker)
    for card in st.get("cards", []):
        if ('"id": "%s"' % card["id"]) not in html:
            err(slug, "в собранной странице нет данных карточки %s" % card["id"])
    arch = (st.get("archive") or {}).get("slug")
    if arch:
        digest = os.path.join(build.ROOT, "digests", arch, "index.html")
        if os.path.exists(digest):
            with open(digest, encoding="utf-8") as fh:
                dhtml = fh.read()
            if slug not in dhtml:
                err(slug, "обратной ссылки нет: дайджест %s не знает про стек %s" % (arch, slug))
            for eid in {e for c in st["cards"] for e in c.get("archive", [])}:
                if '"%s"' % eid not in dhtml:
                    err(slug, "в дайджесте %s нет записи %s, на которую ссылается стек" % (arch, eid))


def main():
    for meta in build.STACKS:
        st = lint_stack(meta)
        if st:
            lint_built(meta["slug"], st)
    for line in WARNINGS:
        print(line)
    for line in ERRORS:
        print(line)
    print("—" * 60)
    print("стеков: %d · ошибок: %d · предупреждений: %d" % (len(build.STACKS), len(ERRORS), len(WARNINGS)))
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
