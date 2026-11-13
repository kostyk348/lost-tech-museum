#!/usr/bin/env python3
"""Сборка сайта «Музей потерянных идей» (GitHub Pages).

    python scripts/build.py                # index.html + digests/*/index.html + docs/*/index.html + stacks/*/index.html
    python scripts/build.py --widget OUT   # компактный виджет дайджеста для чата
    python scripts/build.py --widget OUT <slug>   # slug — дайджест или стек

Источники правды:
    data/<slug>.json         — находки дайджеста (title, subtitle, pitches, entries)
    docs/<slug>.md           — документы (концепты, заметки) в безопасном подмножестве Markdown
    stacks/<slug>/stack.json — стек карточек: карточки, фоны, связи, действия, источники
Шаблоны: templates/dashboard.html, templates/doc.html, templates/stack.html, templates/index.html
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
SITE_URL = os.environ.get("SITE_URL", "https://kostyk348.github.io/lost-tech-museum")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DIGESTS = [
    {
        "slug": "lost-ideas-1980s-2000s",
        "title": "Идеи, которые не дожили: японский и мировой софт 1980–2006",
        "blurb": "35 находок: TRON и BTRON, Fifth Generation, i-mode, FeliCa, FIPA-ACL, Minitel, Xanadu, Plan 9, BeOS, "
                 "Transputer, Linda/Jini, iAPX 432, Setun, OGAS, HyperCard, Weiser и другие.",
        "tags": ["Япония", "ОС", "протоколы", "агенты", "железо", "сообщества"],
        "title_en": "Ideas that didn't survive: Japanese and world software, 1980–2006",
        "blurb_en": "35 findings: TRON and BTRON, Fifth Generation, i-mode, FeliCa, FIPA-ACL, Minitel, Xanadu, Plan 9, BeOS, "
                    "Transputer, Linda/Jini, iAPX 432, Setun, OGAS, HyperCard, Weiser and more. Archive content is Russian.",
        "kind": "dashboard",
    },
    {
        "slug": "portfolio-review",
        "kind": "portfolio",
        "title": "Портфель kostyk348: что почти готово и что стоит дореализовать",
        "blurb": "33 проекта из 83 публичных репозиториев: что уже работает у автора, чего не хватает до продукта "
                 "и что стоит выпустить первым.",
        "tags": ["портфель", "продукты", "GitHub"],
        "title_en": "Portfolio of kostyk348: what is nearly ready and what is worth finishing",
        "blurb_en": "33 projects out of 83 public repositories: what already works, what is missing before it becomes a "
                    "product, and what to ship first. Content is Russian.",
    },
    {
        "slug": "rfc-graveyard",
        "title": "RFC-кладбище: протоколы, описанные до последней запятой",
        "blurb": "15 находок: кандидаты в IPv6 (TUBA, CATNIP, SIPP, Nimrod), IP multicast и MBone, RSVP/IntServ, "
                 "WHOIS++ и CRISP, мосты X.400/MIXER, IP поверх ATM, POP2, Time Protocol, SET, публичный UDDI, "
                 "Web Intents, PubSubHubbub → WebSub. У каждой записи — дословная цитата из первоисточника.",
        "tags": ["RFC", "стандарты", "протоколы", "кладбище", "агенты"],
        "title_en": "The RFC graveyard: protocols specified down to the last comma",
        "blurb_en": "15 findings: IPv6 candidates (TUBA, CATNIP, SIPP, Nimrod), IP multicast and MBone, RSVP/IntServ, "
                    "WHOIS++ and CRISP, X.400/MIXER bridges, IP over ATM, POP2, Time Protocol, SET, public UDDI, "
                    "Web Intents, PubSubHubbub → WebSub. Every entry carries a verbatim quote. Content is Russian.",
        "kind": "dashboard",
    },
]

DOCS = [
    {
        "slug": "glossary",
        "title": "Глоссарий: capability, tuple space, performatives и другие термины архива",
        "blurb": "Короткие определения терминов, без которых записи читаются тяжело, со ссылками на записи, "
                 "где термин работает по делу. Определения — объяснение агента, факты — в первоисточниках",
        "tags": ["глоссарий", "термины", "навигация"],
    },
    {
        "slug": "roadmap",
        "title": "Куда развивать музей: состояние, долг по цитатам и что начать дальше",
        "blurb": "План, а не находка: где архив сейчас, какие записи ждут дословной цитаты, "
                 "патентный срез, рубрика «зазор», ночной смотритель, маршруты и экспорт",
        "tags": ["план", "провенанс", "аудит"],
        "title_en": "Where the museum should go: state, citation debt, and what to start next",
        "blurb_en": "A plan, not a finding: where the archive stands, which entries still lack a verbatim quote, "
                    "the patent slice, the “gap” rubric, the night watchman, routes and export. Content is Russian.",
    },
    {
        "slug": "museum-bots",
        "title": "Два бота, которые делают музей: Archivessa и Chartessa",
        "blurb": "Концепт: автономный конвейер проверенных находок + бот личных стеков-карточек поверх архива",
        "tags": ["архитектура", "агенты", "автоматизация"],
        "title_en": "Two bots that make the museum: Archivessa and Chartessa",
        "blurb_en": "Concept: an autonomous pipeline of verified findings plus a bot for personal card stacks on top of "
                    "the archive. Content is Russian.",
    },
    {
        "slug": "instrumentation-on-egui",
        "title": "Инженерный инструмент на egui и электротехнический слой в CAD",
        "blurb": "Практики egui для плотных инженерных интерфейсов, три варианта дизайна аналога Modbus Poll "
                 "и что делает EPLAN незаменимым — плюс чего в CAD делать не надо",
        "tags": ["архитектура", "egui", "CAD", "инструменты"],
        "title_en": "An engineering tool on egui and an electrical layer in CAD",
        "blurb_en": "egui practices for dense engineering interfaces, three designs for a Modbus Poll analogue, and what "
                    "makes EPLAN irreplaceable — plus what not to do in CAD. Content is Russian.",
    },
]

# Стеки карточек (Chartessa). Источник правды — stacks/<slug>/stack.json, здесь только витрина.
STACKS = [
    {
        "slug": "agent-protocols",
        "title": "Стек: агентные протоколы, которые уже были решены",
        "blurb": "8 карточек поверх архива музея: язык агентов FIPA-ACL/KQML, мобильный код Telescript, tuple space, "
                 "личный дата-хаб HailStorm, урок проигранного стандарта OSI, слой вывода Fifth Generation — "
                 "и чек-лист «чего не хватает вашему агентному протоколу».",
        "tags": ["стеки", "агенты", "протоколы"],
        "blurb_en": "8 cards on top of the museum archive: the FIPA-ACL/KQML agent language, Telescript mobile code, "
                    "tuple space, the HailStorm personal data hub, the OSI lesson, the Fifth Generation inference layer — "
                    "and a checklist of what your agent protocol is missing.",
    },
    {
        "slug": "legacy-os",
        "title": "Стек: операционные системы, которые всё придумали первыми",
        "blurb": "11 карточек: Plan 9 и Inferno, BeOS и BFS, Cairo→WinFS, Newton Soup, Workplace OS, TRON и μITRON, "
                 "FM Towns, Self — и сборка «ОС для локального агента» из десяти решений.",
        "tags": ["стеки", "ОС", "системы"],
        "blurb_en": "11 cards: Plan 9 and Inferno, BeOS and BFS, Cairo→WinFS, Newton Soup, Workplace OS, TRON and μITRON, "
                    "FM Towns, Self — plus a build card “an OS for a local agent” from ten decisions.",
    },
    {
        "slug": "pre-web",
        "title": "Стек: сеть и гипертекст до веба — что там было решено",
        "blurb": "10 карточек: Xanadu, HyperCard, Gopher/WAIS, Minitel, Usenet, NIFTY-Serve, i-mode, OGAS — "
                 "и сборка «сеть для агентов» из восьми решений.",
        "tags": ["стеки", "сеть", "гипертекст"],
        "blurb_en": "10 cards: Xanadu, HyperCard, Gopher/WAIS, Minitel, Usenet, NIFTY-Serve, i-mode, OGAS — plus a build "
                    "card “a network for agents” from eight decisions.",
    },
    {
        "slug": "hardware-and-context",
        "title": "Стек: железо, идентичность и внимание — что опередило время",
        "blurb": "13 карточек: FeliCa и QR, ucode, iAPX 432, Transputer, Setun, MSX и PC-98, TRON Code, NeWS, "
                 "calm technology Вейзера — и сборка «устройство и протокол, которые выживут».",
        "tags": ["стеки", "железо", "идентичность"],
        "blurb_en": "13 cards: FeliCa and QR, ucode, iAPX 432, Transputer, Setun, MSX and PC-98, TRON Code, NeWS, Weiser’s "
                    "calm technology — plus a build card “a device and protocol that survive”.",
    },
]

# Тема виджета: в чате страница живёт в теме приложения — берём её переменные, а не свои цвета.
STACK_THEME_WIDGET = (
    ":root{--bg:transparent;--card:var(--card,#141a24);--line:var(--border,#242d3d);"
    "--fg:var(--foreground,#e6edf7);--mut:var(--muted-foreground,#8b98ad);--soft:rgba(127,127,127,.10);"
    "--cy:var(--accent,#22d3ee);--lp:var(--muted-foreground,#a78bfa)}\n"
    "body{background:transparent}\n"
)

# ---------------------------------------------------------------------------
# Локали. Русский — корень сайта, английский — те же страницы под /en/.
# Интерфейс переводится здесь (SITE_UI), содержание стеков — в
# stacks/<slug>/i18n/en.json (сидекар), данные архива остаются русскими.
# ---------------------------------------------------------------------------
LOCALES = ("ru", "en")
LANG_LABEL = {"ru": "Русский", "en": "English"}
LANG_NAME = {"ru": "русском", "en": "English"}

# Замены интерфейсных строк в шаблонах. Порядок важен: длинные фразы раньше коротких.
SITE_UI = {
    "ru": [],
    "en": [
        # шапка стека
        ("Музей потерянных идей · стек карточек · автор", "Lost Tech Museum · card stack · by"),
        ("стек · Музей потерянных идей", "stack · Lost Tech Museum"),
        ("карточек:", "cards:"),
        ("связей:", "links:"),
        ("источников:", "sources:"),
        ("записей архива:", "archive entries:"),
        ("собрано:", "built:"),
        # панель навигации
        ("фильтр: fipa, tuple space…", "filter: fipa, tuple space…"),
        ("Весь архив находок →", "Full archive →"),
        ("← → листать · Esc — витрина стека", "← → browse · Esc — stack home"),
        ("Ничего не нашлось.", "Nothing matched."),
        # карточка
        ("фон:", "background:"),
        ("насколько идея недожата — оценка агента", "how unfinished the idea is — the agent's judgement"),
        ("зазор", "gap"),
        ("витрина", "stack home"),
        ("→ карточка:", "→ card:"),
        ("Связи", "Links"),
        ("ссылается сюда", "links here"),
        ("⌗ запись архива:", "⌗ archive entry:"),
        ("проверенная карточка музея с источниками", "verified museum card with sources"),
        ("Другие стеки", "Other stacks"),
        ("выход в другой стек", "link to another stack"),
        ("Действия — ограниченный промпт, не код", "Actions — a bounded prompt, not code"),
        ("без инструментов", "no tools"),
        ("инструменты:", "tools:"),
        ("Разрешённые инструменты:", "Allowed tools:"),
        ("Инструменты не требуются.", "No tools required."),
        ("Источники (✓ прочитан целиком · ↗ индекс поиска · ⌗ запись архива)",
         "Sources (✓ read in full · ↗ search index · ⌗ archive entry)"),
        ("[Стек «", "[Stack “"),
        ("» → карточка «", "” → card “"),
        ("»]", "”]"),
        ("Фоны карточек", "Card backgrounds"),
        ("Собрано автоматически: <code>scripts/build.py</code> из <code>stacks/__SLUG__/stack.json</code>",
         "Generated by <code>scripts/build.py</code> from <code>stacks/__SLUG__/stack.json</code>"),
        # хаб
        ("Музей потерянных идей", "Lost Tech Museum"),
        ("Музей потерянных идей — архив находок Information search", "Lost Tech Museum — the Information search archive"),
        ("архив находок", "finding archive"),
        ("Сгенерировано автоматически", "Generated automatically"),
        ("исходники и данные на GitHub", "sources and data on GitHub"),
        ("стек карточек", "card stack"),
    ],
}

STACK_FOOTER = {
    "ru": (
        '<p><b>Методология.</b> Факты в карточках взяты из проверенных записей архива музея — ссылка «архив» на карточке ведёт\n'
        '    на запись, метки <span class="leg">✓</span> (страница прочитана целиком) и <span class="leg">↗</span> (источник уровня\n'
        '    поискового индекса) унаследованы из архива. Оценка «зазор» и блоки «что внедрить» — суждение агента Chartessa, а не цитата.</p>\n'
        '    <p><b>Кнопки.</b> Действие на карточке — ограниченный промпт с белым списком инструментов, а не произвольный код:\n'
        '    в чате с агентом кнопка отправляет промпт, на сайте — копирует его в буфер обмена.</p>\n'
        '    <p><b>Фоны карточек</b> (шаблоны) — <span class="leg" id="bglist"></span>.</p>'
    ),
    "en": (
        '<p><b>Method.</b> Facts in the cards come from verified museum archive entries: the “archive” link on a card leads to\n'
        '    the entry, and the <span class="leg">✓</span> (page read in full) and <span class="leg">↗</span> (search-index level)\n'
        '    marks are inherited from the archive. The “gap” score and the “what to build” blocks are the judgement of the agent\n'
        '    Chartessa, not a quotation.</p>\n'
        '    <p><b>Buttons.</b> A card action is a bounded prompt with a whitelist of tools, not arbitrary code: in the chat the\n'
        '    button sends the prompt to the agent, on the site it copies it to the clipboard.</p>\n'
        '    <p><b>Card backgrounds</b> (templates) — <span class="leg" id="bglist"></span>.</p>\n'
        '    <p class="leg">Source titles and archive contents are published in Russian: they are the museum\'s primary record.</p>'
    ),
}

HUB_LEDE = {
    "ru": ('Здесь агент <b>Information search</b> собирает находки: патенты, RFC, стандарты, операционные системы,\n'
           '  протоколы и практики, которые были впереди своего времени — и которые стоит переизобрести сегодня.\n'
           '  Каждый дайджест — самостоятельная страница с источниками, оценкой «недожатости» и списком того, что внедрять.\n'
           '  Из этих находок агент <b>Chartessa</b> собирает <b>стеки карточек</b> — личные инструменты, которыми пользуются\n'
           '  руками, а не читают как отчёт.'),
    "en": ('Here the agent <b>Information search</b> collects findings: patents, RFCs, standards, operating systems, protocols\n'
           '  and practices that were ahead of their time — and are worth reinventing today. Each digest is a standalone page\n'
           '  with sources, an “unfinished” score and a list of what to build. From those findings the agent <b>Chartessa</b>\n'
           '  assembles <b>card stacks</b> — personal tools you use by hand, not reports you read.'),
}

HUB_NOTE = {
    "ru": (
        '<p><b>Источник данных</b> — <code>data/&lt;slug&gt;.json</code>: список находок с полями «что было / почему круто / почему умерло / где сейчас / что внедрить» и ссылками на источники.</p>\n'
        '    <p><b>Сборка</b> — <code>python scripts/build.py</code>: генерирует эту страницу и каждую страницу дайджеста из шаблонов в <code>templates/</code>. HTML не правится руками.</p>\n'
        '    <p><b>Провенанс</b> — под каждой находкой стоят ссылки на источники; знак <code>✓</code> означает, что страница прочитана целиком,\n'
        '    знак <code>↗</code> — источник взят из индекса поиска. Оценочные суждения (зазор, питчи) помечены как вывод агента, а не как факт из источника.</p>\n'
        '    <p><b>Обновление</b> — новый дайджест = новый JSON в <code>data/</code> + запись в <code>DIGESTS</code> в <code>scripts/build.py</code>, затем <code>git push</code>: GitHub Pages публикует сайт заново.</p>\n'
        '    <p><b>Стеки карточек</b> — поверх архива: <code>stacks/&lt;slug&gt;/stack.json</code> задаёт карточки, фоны (шаблоны\n'
        '    вида «до/после», «сравнение», «чек-лист»), двусторонние связи и кнопки — ограниченные промпты с белым списком\n'
        '    инструментов, а не код. Стеки собирает агент <b>Chartessa</b>; HTML так же генерируется из данных, а целостность\n'
        '    связей проверяет <code>python scripts/lint_stacks.py</code>.</p>'
    ),
    "en": (
        '<p><b>Data source</b> — <code>data/&lt;slug&gt;.json</code>: findings with “what it was / why it mattered / why it died / where it lives now / what to build”, plus source links.</p>\n'
        '    <p><b>Build</b> — <code>python scripts/build.py</code> generates this page and every digest page from <code>templates/</code>. The HTML is never edited by hand.</p>\n'
        '    <p><b>Provenance</b> — every finding carries its sources; <code>✓</code> means the page was read in full, <code>↗</code> means the source came from a search index.\n'
        '    Judgements (gap, pitches) are marked as the agent\'s conclusion, not as source facts.</p>\n'
        '    <p><b>Updates</b> — a new digest = a new JSON in <code>data/</code> + an entry in <code>DIGESTS</code> in <code>scripts/build.py</code>, then <code>git push</code>; GitHub Pages republishes the site.</p>\n'
        '    <p><b>Card stacks</b> — built on top of the archive: <code>stacks/&lt;slug&gt;/stack.json</code> defines cards, backgrounds (before/after, comparison, checklist),\n'
        '    two-way links and buttons — bounded prompts with a tool whitelist, not code. Stacks are assembled by the agent <b>Chartessa</b>;\n'
        '    <code>python scripts/lint_stacks.py</code> checks their integrity.</p>'
    ),
}

HUB_SECTIONS = {
    "ru": {"stacks": "Стеки карточек <small>— инструменты, собранные из архива</small>",
           "digests": "Дайджесты <small>— проверенные находки</small>",
           "docs": "Концепты и архитектура",
           "prov": "Проверяемость <small>— насколько архиву можно верить</small>",
           "how": "Как это работает"},
    "en": {"stacks": "Card stacks <small>— tools assembled from the archive</small>",
           "digests": "Digests <small>— verified findings</small>",
           "docs": "Concepts and architecture",
           "prov": "Verifiability <small>— how far the archive can be trusted</small>",
           "how": "How it works"},
}


TAG_EN = {
    "Япония": "Japan", "ОС": "OS", "протоколы": "protocols", "агенты": "agents", "железо": "hardware",
    "сообщества": "communities", "стеки": "stacks", "системы": "systems", "сеть": "network",
    "гипертекст": "hypertext", "идентичность": "identity", "портфель": "portfolio", "продукты": "products",
    "план": "plan", "провенанс": "provenance", "аудит": "audit", "архитектура": "architecture",
    "автоматизация": "automation", "инструменты": "tools", "стандарты": "standards", "кладбище": "graveyard",
    "термины": "terms", "RFC": "RFC", "CAD": "CAD", "egui": "egui", "GitHub": "GitHub",
}


def tags_for(meta, lang):
    """Ключевые слова карточек хаба: переводим по словарю, незнакомые оставляем как есть."""
    tags = list(meta.get("tags") or [])
    return [TAG_EN.get(t, t) for t in tags] if lang == "en" else tags


def tr_ui(tpl, lang):
    """Перевод интерфейсных строк шаблона. Порядок пар в SITE_UI уже «длинное раньше короткого»."""
    for ru, en in SITE_UI.get(lang, []):
        tpl = tpl.replace(ru, en)
    return tpl


def load_i18n(slug):
    """Сидекар перевода стека: stacks/<slug>/i18n/en.json (может отсутствовать)."""
    path = os.path.join(ROOT, "stacks", slug, "i18n", "en.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def localize_stack(st, tr, lang):
    """Накладывает английский сидекар на данные стека. Нет перевода — остаётся русский (и это видно в линтере)."""
    if lang == "ru" or not tr:
        return st
    out = json.loads(json.dumps(st, ensure_ascii=False))
    for key in ("title", "subtitle", "about"):
        if tr.get(key):
            out[key] = tr[key]
    if tr.get("archive_title") and out.get("archive"):
        out["archive"]["title"] = tr["archive_title"]
    for bid, name in (tr.get("backgrounds") or {}).items():
        if bid in (out.get("backgrounds") or {}):
            out["backgrounds"][bid]["name"] = name
    cards = {c["id"]: c for c in out.get("cards", [])}
    for cid, t in (tr.get("cards") or {}).items():
        card = cards.get(cid)
        if not card:
            continue
        for key in ("title", "subtitle"):
            if t.get(key):
                card[key] = t[key]
        fields = card.get("fields") or []
        if len(t.get("fields") or []) == len(fields):
            for f_ru, f_en in zip(fields, t["fields"]):
                f_ru["lbl"] = f_en.get("lbl", f_ru["lbl"])
                f_ru["val"] = f_en.get("val", f_ru["val"])
        for lk in card.get("links") or []:
            why = (t.get("links") or {}).get(lk["to"])
            if why:
                lk["why"] = why
        for ref in card.get("other") or []:
            why = (t.get("other") or {}).get("%s/%s" % (ref["stack"], ref["card"]))
            if why:
                ref["why"] = why
        acts = card.get("actions") or []
        if len(t.get("actions") or []) == len(acts):
            for a_ru, a_en in zip(acts, t["actions"]):
                a_ru["t"] = a_en.get("t", a_ru["t"])
                a_ru["p"] = a_en.get("p", a_ru["p"])
        for s_ru, s_en in zip(card.get("sources") or [], t.get("sources") or []):
            if s_en:
                s_ru["t"] = s_en
    return out


def _switch_html(lang, alt_href, alt_lang):
    """Переключатель языка: текущий язык выделен, альтернатива — ссылкой."""
    other = "en" if lang == "ru" else "ru"
    return ('<span class="cur">%s</span> · <a href="%s" hreflang="%s">%s</a>'
            % (LANG_LABEL[lang], alt_href, alt_lang, LANG_LABEL[other]))


def _rel_root(depth):
    return "../" * depth


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


def _js_json(obj):
    """JSON для вставки внутрь <script>: данные не должны уметь закрыть тег."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def stack_data(slug):
    return json.loads(_read("stacks/%s/stack.json" % slug))


def stack_refs(archive_slug):
    """Обратные ссылки: id записи архива -> карточки стеков, которые на неё опираются.

    Двусторонность: каждая карточка стека ссылается на запись архива, а та же запись
    в дайджесте показывает, в каких стеках она используется.
    """
    refs = {}
    for meta in STACKS:
        st = stack_data(meta["slug"])
        if (st.get("archive") or {}).get("slug") != archive_slug:
            continue
        for card in st.get("cards", []):
            for eid in card.get("archive", []):
                refs.setdefault(eid, []).append({
                    "slug": meta["slug"],
                    "title": meta["title"],
                    "card": card["id"],
                    "card_title": card["title"],
                })
    return refs


def cross_for(slug, st):
    """Связи между стеками. В JSON они односторонние (`other`), здесь считаются обе стороны.

    Возвращает {"out": {card_id: [...]}, "back": {card_id: [...]}} — «куда ведёт» и «кто ссылается сюда».
    """
    idx = {}
    for meta in STACKS:
        other = stack_data(meta["slug"])
        idx[meta["slug"]] = {"title": other["title"],
                             "cards": {c["id"]: c["title"] for c in other.get("cards", [])},
                             "data": other}
    out, back = {}, {}
    for sid, sentry in idx.items():
        if sid == slug:
            continue
        for card in sentry["data"].get("cards", []):
            for ref in card.get("other", []):
                if ref.get("stack") != slug or ref.get("card") not in idx[slug]["cards"]:
                    continue
                back.setdefault(ref["card"], []).append({
                    "stack": sid, "title": sentry["title"], "card": card["id"], "card_title": card["title"],
                    "why": ref.get("why", ""), "path": "stacks/%s/#c-%s" % (sid, card["id"]),
                })
    for card in st.get("cards", []):
        for ref in card.get("other", []):
            tgt = idx.get(ref.get("stack"))
            if not tgt or ref.get("card") not in tgt["cards"]:
                continue
            out.setdefault(card["id"], []).append({
                "stack": ref["stack"], "title": tgt["title"], "card": ref["card"],
                "card_title": tgt["cards"][ref["card"]], "why": ref.get("why", ""),
                "path": "stacks/%s/#c-%s" % (ref["stack"], ref["card"]),
            })
    return {"out": out, "back": back}


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
            .replace("__STACKREFS__", _js_json(stack_refs(d["slug"])))
            .replace("__DATA__", _js_json({"entries": d["entries"]}))
            .replace("__PITCHES__", _js_json(d["pitches"])))


def render_portfolio(d, mode="page"):
    tpl = _read("templates/portfolio.html")
    footer = ('Часть архива «Музей потерянных идей» · '
              '<a href="https://github.com/{repo}">данные и генератор на GitHub</a>')
    return (tpl
            .replace(".gridbox__CLAMPCSS__",
                     ".gridbox{max-height:64vh;overflow:auto;padding-right:6px}" if mode == "widget" else ".gridbox")
            .replace("__OPEN__", "false" if mode == "widget" else "true")
            .replace("__TITLE__", d["title"])
            .replace("__SUBTITLE__", d["subtitle"])
            .replace("__DATE__", d.get("generated", ""))
            .replace("__SLUG__", d["slug"])
            .replace("__FOOTERREPO__", footer.format(repo=REPO_PATH))
            # templates/portfolio.html читает DATA.entries — форма должна совпадать с рендерером дашборда
            .replace("__DATA__", _js_json({"entries": d["entries"]}))
            .replace("__PITCHES__", _js_json(d["pitches"])))


def renderer_for(kind):
    return render_portfolio if kind == "portfolio" else render_dashboard


def render_doc(meta, date):
    tpl = _read("templates/doc.html")
    body = md_to_html(_read("docs/%s.md" % meta["slug"]))
    return (tpl.replace("__TITLE__", meta["title"])
               .replace("__BLURB__", html.escape(meta["blurb"], quote=False))
               .replace("__DATE__", date)
               .replace("__SLUG__", meta["slug"])
               .replace("__REPO__", REPO_PATH)
               .replace("__BODY__", body))


def render_stack(meta, st, mode="page", lang="ru", depth=2):
    tr = load_i18n(st["slug"]) if lang == "en" else {}
    data = localize_stack(st, tr, lang)
    root = _rel_root(depth)
    alt_lang = "en" if lang == "ru" else "ru"
    alt_href = root + ("stacks/%s/" % data["slug"] if lang == "en" else "en/stacks/%s/" % data["slug"])
    tpl = tr_ui(_read("templates/stack.html"), lang)
    footer = ('Часть архива «Музей потерянных идей» · '
              '<a href="https://github.com/{repo}">данные и генератор на GitHub</a>') if lang == "ru" else (
              'Part of the “Lost Tech Museum” archive · '
              '<a href="https://github.com/{repo}">data and generator on GitHub</a>')
    blurb = meta.get("blurb_en") if lang == "en" and meta.get("blurb_en") else meta["blurb"]
    return (tpl
            .replace(".stackbox__CLAMPCSS__",
                     "#navlist{max-height:46vh;overflow:auto}" if mode == "widget" else "")
            .replace("__THEME__", STACK_THEME_WIDGET if mode == "widget" else "")
            .replace("__LANG__", lang)
            .replace("__ALT_LANG__", alt_lang)
            .replace("__ALT_HREF__", alt_href)
            .replace("__SWITCH__", _switch_html(lang, alt_href, alt_lang))
            .replace("__ROOT__", root)
            .replace("__TITLE__", data["title"])
            .replace("__SUBTITLE__", data.get("subtitle", ""))
            .replace("__BLURB__", html.escape(blurb, quote=True))
            .replace("__DATE__", data.get("generated", ""))
            .replace("__SLUG__", data["slug"])
            .replace("__FOOTERNOTE__", STACK_FOOTER[lang])
            .replace("__FOOTERREPO__", footer.format(repo=REPO_PATH))
            .replace("__CROSS__", _js_json(cross_for(data["slug"], data)))
            .replace("__STACK__", _js_json(data)))


def _card(href, title, blurb, stats, go):
    return ('<a class="card" href="%s"><h3>%s</h3><p>%s</p>'
            '<div class="st">%s</div><div class="go">%s</div></a>'
            % (href, title, blurb, "".join("<span>%s</span>" % s for s in stats), go))


def render_provenance(digests, audits, date):
    """Страница провенанса: что проверено, что в долгу, что уже мертво.

    Считается по самим данным и отчётам аудитов (data/quote-audit.json, data/link-audit.json).
    Никаких вписанных руками цифр: страница стареет вместе с архивом, а не врёт вместе с ним.
    """
    qa = audits.get("quote-audit") or {}
    la = audits.get("link-audit") or {}
    links = la.get("links", {})
    rows, debt = [], []
    total_entries = total_src = total_r1 = total_q = 0
    total_covered = 0
    for d in digests:
        entries = d.get("entries", [])
        src = [s for e in entries for s in e.get("src", [])]
        dead = sum(1 for s in src if links.get(s.get("u"), {}).get("state") == "dead")
        port = d.get("kind") == "portfolio"     # портфель — разбор репозиториев, а не находки с цитатами
        if port:
            rows.append(
                '<tr><td><a href="../digests/%s/">%s</a> <span class="tag">разбор репозиториев</span></td>'
                '<td class="num">%d</td><td class="num">%d</td><td class="num">—</td>'
                '<td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td>'
                '<td class="num">—</td><td class="num %s">%d</td></tr>'
                % (d.get("slug"), html.escape(d.get("title", "")), len(entries), len(src),
                   "bad" if dead else "ok", dead))
            continue
        r1 = sum(1 for s in src if s.get("r"))
        q = sum(1 for s in src if s.get("q"))
        refs = stack_refs(d.get("slug"))          # какие записи подхвачены стеками карточек
        covered = sum(1 for e in entries if e.get("id") in refs)
        total_covered += covered
        noq = [e for e in entries if not any(s.get("q") for s in e.get("src", []))]
        total_entries += len(entries)
        total_src += len(src)
        total_r1 += r1
        total_q += q
        rows.append(
            '<tr><td><a href="../digests/%s/">%s</a></td>'
            '<td class="num">%d</td><td class="num">%d</td><td class="num">%d</td>'
            '<td class="num">%d</td><td class="num">%d</td><td class="num">%d</td>'
            '<td class="num %s">%d</td><td class="num %s">%d</td><td class="num %s">%d</td></tr>'
            % (d.get("slug"), html.escape(d.get("title", "")),
               len(entries), len(src), r1, len(src) - r1, q, len(entries) - len(noq),
               "ok" if covered == len(entries) else "warn", covered,
               "warn" if noq else "ok", len(noq), "bad" if dead else "ok", dead))
        if noq:
            items = "".join(
                '<li><a href="../digests/%s/#c-%s">%s</a> <span class="dim">— источников: %d, цитаты нет</span></li>'
                % (d.get("slug"), e.get("id"), html.escape(e.get("name", "")), len(e.get("src", [])))
                for e in noq)
            debt.append('<p><b>%s</b> — %d из %d записей без дословной цитаты:</p><ul>%s</ul>'
                        % (html.escape(d.get("title", "")), len(noq), len(entries), items))

    confirmed = qa.get("confirmed")
    failed = qa.get("failed") or []
    missing = qa.get("missing") or []

    def card(value, label, cls=""):
        return '<div><b class="%s">%s</b><span>%s</span></div>' % (cls, value, label)

    stats = "".join([
        card(total_entries, "записей в архиве"),
        card(total_src, "источников"),
        card(total_r1, "прочитано целиком (r:1) ✓", "ok"),
        card(total_src - total_r1, "уровня индекса (r:0) ↗"),
        card(total_q, "дословных цитат"),
        card("—" if confirmed is None else confirmed, "цитат подтверждено аудитом",
             "ok" if confirmed else "dim"),
        card(len(failed), "цитат НЕ подтвердилось", "ok" if not failed else "bad"),
        card(total_covered, "записей подхвачено стеками карточек", "ok" if total_covered else "dim"),
        card(la.get("dead", 0), "мёртвых ссылок", "ok" if not la.get("dead") else "bad"),
    ])
    table = ('<table><thead><tr><th>Дайджест</th><th class="num">Записей</th><th class="num">Источников</th>'
             '<th class="num">r:1 ✓</th><th class="num">r:0 ↗</th><th class="num">Цитат</th>'
             '<th class="num">С цитатой</th><th class="num">В стеках</th><th class="num">Без цитаты</th><th class="num">Мёртвых</th>'
             '</tr></thead><tbody>%s</tbody></table>' % "".join(rows))
    debt_html = ("".join(debt) if debt else
                 '<div class="note"><b>Долга нет.</b> У каждой записи есть дословная цитата.</div>')
    if failed:
        debt_html += ('<div class="note warnbox"><b>Цитаты, не подтвердившиеся при скачивании источника</b>'
                      ' (публиковать нельзя, пока не исправлено):</div><ul>%s</ul>' % "".join(
                          '<li><code>%s</code> <a href="%s">%s</a> — «%s…»</li>'
                          % (html.escape(f.get("entry", "")), html.escape(f.get("url", "")),
                             html.escape((f.get("url") or "")[:80]),
                             html.escape((f.get("quote") or "")[:90]))
                          for f in failed))
    if missing:
        debt_html += ('<div class="note">Источники, которые не скачались (проверка невозможна — '
                      'это не подтверждение и не опровержение): %d шт.</div>' % len(missing))

    if links:
        bad = [(u, v) for u, v in links.items() if v.get("state") in ("dead", "blocked")]
        bad.sort(key=lambda kv: (kv[1].get("state") != "dead", kv[0]))
        if bad:
            dl = "".join(
                '<tr><td>%s</td><td class="num %s">%s</td><td>%s</td><td class="dim">%s</td></tr>'
                % ('<a href="%s">%s</a>' % (html.escape(u), html.escape(u[:88])),
                   "bad" if v.get("state") == "dead" else "warn", v.get("code"),
                   html.escape(", ".join("%s/%s" % (r.get("digest", ""), r.get("entry", ""))
                                         for r in (v.get("refs") or [])[:3])),
                   html.escape(v.get("checked", "")))
                for u, v in bad[:120])
            dead_html = ('<table><thead><tr><th>Адрес</th><th class="num">Код</th><th>Записи</th>'
                         '<th>Проверено</th></tr></thead><tbody>%s</tbody></table>' % dl)
            dead_html += ('<div class="note">Мёртвая ссылка не удаляется из архива: запись остаётся, '
                          'ссылка помечается. Закрытые бот-стеной (401/403/429) живы для читателя, '
                          'но недоступны обходу — это отдельное состояние.</div>')
        else:
            dead_html = ('<div class="note"><b>Все ссылки живы.</b> Проверено %d адресов.</div>'
                         % la.get("total", 0))
    else:
        dead_html = ('<div class="note">Аудит ссылок ещё не запускался: '
                     '<code>python scripts/audit_links.py</code>. Это честное «не знаю», а не «всё хорошо».</div>')

    tpl = _read("templates/provenance.html")
    return (tpl.replace("__STATS__", stats)
               .replace("__TABLE__", table)
               .replace("__DEBT__", debt_html)
               .replace("__DEAD__", dead_html)
               .replace("__DATE__", date)
               .replace("__REPO__", REPO_PATH)
               .replace("__QUOTE_DATE__", str(qa.get("generated") or "аудит не запускался"))
               .replace("__LINK_DATE__", str(la.get("generated") or "аудит не запускался")))


def render_hub(date, lang="ru"):
    en = lang == "en"
    tpl = tr_ui(_read("templates/index.html"), lang)
    root = "../" if en else ""
    sec = HUB_SECTIONS[lang]
    dcards = []
    for dg in DIGESTS:
        d = json.loads(_read("data/%s.json" % dg["slug"]))
        title = (dg.get("title_en") or dg["title"]) if en else dg["title"]
        blurb = (dg.get("blurb_en") or dg["blurb"]) if en else dg["blurb"]
        if dg.get("kind") == "portfolio":
            stats = (["%d projects" % len(d["entries"]),
                      "%d clusters" % len({e["cluster"] for e in d["entries"]}),
                      "★%d" % sum(e["stars"] for e in d["entries"])] if en else
                     ["%d проектов" % len(d["entries"]),
                      "кластеров: %d" % len({e["cluster"] for e in d["entries"]}),
                      "★%d" % sum(e["stars"] for e in d["entries"])])
            go = "Open the review →" if en else "Открыть разбор →"
        else:
            jp = sum(1 for e in d["entries"] if e["reg"] == "jp")
            src = sum(len(e["src"]) for e in d["entries"])
            stats = (["%d findings" % len(d["entries"]), "Japanese: %d" % jp, "%d sources" % src] if en else
                     ["%d находок" % len(d["entries"]), "японских: %d" % jp, "%d источников" % src])
            go = "Open the digest →" if en else "Открыть дайджест →"
        stats.append(" · ".join(dg["tags"]))
        if en:
            stats.append("RU")
        dcards.append(_card(root + "digests/%s/" % dg["slug"], title, blurb, stats, go))
    scards = []
    for meta in STACKS:
        st = localize_stack(stack_data(meta["slug"]), load_i18n(meta["slug"]), lang)
        cards = st.get("cards", [])
        nlinks = sum(len(c.get("links", [])) + len(c.get("other", [])) for c in cards)
        nsrc = sum(len(c.get("sources", [])) for c in cards)
        nact = sum(len(c.get("actions", [])) for c in cards)
        stats = (["%d cards" % len(cards), "%d links" % nlinks, "%d sources" % nsrc, "%d buttons" % nact] if en else
                 ["%d карточек" % len(cards), "%d связей" % nlinks, "%d источников" % nsrc, "%d кнопок" % nact])
        stats.append(" · ".join(meta["tags"]))
        blurb = (meta.get("blurb_en") or meta["blurb"]) if en else meta["blurb"]
        href = ("en/stacks/%s/" % meta["slug"]) if en else ("stacks/%s/" % meta["slug"])
        scards.append(_card(href, st["title"], blurb, stats,
                            "Open the card stack →" if en else "Открыть стек карточек →"))
    mcards = []
    for m in DOCS:
        mcards.append(_card(root + "docs/%s/" % m["slug"],
                            (m.get("title_en") or m["title"]) if en else m["title"],
                            (m.get("blurb_en") or m["blurb"]) if en else m["blurb"],
                            list(m["tags"]) + (["RU"] if en else []),
                            "Read the concept →" if en else "Читать концепт →"))
    sections = ("  <h2>%s</h2>\n  " % sec["stacks"] + "\n  ".join(scards)
                + "\n\n  <h2>%s</h2>\n  " % sec["digests"] + "\n  ".join(dcards)
                + "\n\n  <h2>%s</h2>\n  " % sec["docs"] + "\n  ".join(mcards))
    if en:
        prov = _card(
            "provenance/",
            "Archive provenance: what is verified and what is still owed",
            "Verbatim quotes from primary sources, machine-checked against the source text; “read in full / index "
            "level” marks; dead links; an open list of entries without a quote; machine-readable access "
            "(api/, feed.xml, sitemap.xml). Content is Russian.",
            ["quote audit", "link audit", "api/*.json", "feed.xml", "robots.txt", "RU"],
            "Open the provenance page →")
    else:
        prov = _card(
            "provenance/",
            "Провенанс архива: что проверено, а что ещё в долгу",
            "Дословные цитаты из первоисточников, сверенные скриптом с текстом источника; разметка «прочитано "
            "целиком / уровень индекса»; мёртвые ссылки; открытый список записей без цитаты и машиночитаемый "
            "доступ (api/, feed.xml, sitemap.xml).",
            ["аудит цитат", "аудит ссылок", "api/*.json", "feed.xml", "robots.txt"],
            "Открыть страницу провенанса →")
    sections += "\n\n  <h2>%s</h2>\n  %s" % (sec["prov"], prov)
    alt_lang = "ru" if en else "en"
    alt_href = "../" if en else "en/"
    return (tpl.replace("__SECTIONS__", sections)
               .replace("__LEDE__", HUB_LEDE[lang])
               .replace("__HOWNOTE__", HUB_NOTE[lang])
               .replace("__HOWSECT__", sec["how"])
               .replace("__LANG__", lang)
               .replace("__ALT_LANG__", alt_lang)
               .replace("__ALT_HREF__", alt_href)
               .replace("__SWITCH__", _switch_html(lang, alt_href, alt_lang))
               .replace("__DATE__", date)
               .replace("__REPO__", REPO_PATH))


def main():
    args = sys.argv[1:]
    if args and args[0] == "--widget":
        out = args[1] if len(args) > 1 else os.path.join(ROOT, "widget.html")
        want = args[2] if len(args) > 2 else None
        for meta in STACKS:
            if want == meta["slug"]:
                st = stack_data(meta["slug"])
                open(out, "w", encoding="utf-8").write(render_stack(meta, st, mode="widget"))
                print("widget:", out, os.path.getsize(out), "| stack:", meta["slug"])
                return
        dg = next((g for g in DIGESTS if want and g["slug"] == want), DIGESTS[0])
        d = json.loads(_read("data/%s.json" % dg["slug"]))
        open(out, "w", encoding="utf-8").write(renderer_for(dg.get("kind"))(d, mode="widget"))
        print("widget:", out, os.path.getsize(out), "| digest:", dg["slug"])
        return

    dates = [json.loads(_read("data/%s.json" % dg["slug"])).get("generated", "") for dg in DIGESTS]
    dates += [stack_data(s["slug"]).get("generated", "") for s in STACKS]
    date = max(dates + ["2026-01-01"])
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(render_hub(date))
    print("hub: index.html")
    os.makedirs(os.path.join(ROOT, "en"), exist_ok=True)
    open(os.path.join(ROOT, "en", "index.html"), "w", encoding="utf-8").write(render_hub(date, "en"))
    print("hub: en/index.html")
    for dg in DIGESTS:
        outdir = os.path.join(ROOT, "digests", dg["slug"])
        os.makedirs(outdir, exist_ok=True)
        d = json.loads(_read("data/%s.json" % dg["slug"]))
        open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(renderer_for(dg.get("kind"))(d))
        shutil.copy(os.path.join(ROOT, "data", dg["slug"] + ".json"), os.path.join(outdir, "data.json"))
        print("digest: digests/%s/index.html %d entries" % (dg["slug"], len(d["entries"])))
    for meta in DOCS:
        outdir = os.path.join(ROOT, "docs", meta["slug"])
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(render_doc(meta, date))
        shutil.copy(os.path.join(ROOT, "docs", meta["slug"] + ".md"), os.path.join(outdir, "source.md"))
        print("doc: docs/%s/index.html" % meta["slug"])
    for meta in STACKS:
        st = stack_data(meta["slug"])
        outdir = os.path.join(ROOT, "stacks", meta["slug"])
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(render_stack(meta, st))
        refs = sum(len(c.get("archive", [])) for c in st.get("cards", []))
        print("stack: stacks/%s/index.html %d cards, %d archive refs" % (meta["slug"], len(st["cards"]), refs))
        tr = load_i18n(meta["slug"])
        if tr:
            endir = os.path.join(ROOT, "en", "stacks", meta["slug"])
            os.makedirs(endir, exist_ok=True)
            open(os.path.join(endir, "index.html"), "w", encoding="utf-8").write(
                render_stack(meta, st, lang="en", depth=3))
            print("stack: en/stacks/%s/index.html (en)" % meta["slug"])
        else:
            print("stack: en/stacks/%s/ — перевода нет, страница не собрана (линтер предупредит)" % meta["slug"])
    all_digests = []
    for dg in DIGESTS:
        d = json.loads(_read("data/%s.json" % dg["slug"]))
        d.setdefault("kind", dg.get("kind"))     # kind живёт в реестре build.py, не в данных
        all_digests.append(d)
    try:
        import machine
        audits = machine.audit()
    except Exception as exc:                      # noqa: BLE001 — API не должно ломать HTML-сборку
        print("machine: аудиты недоступны:", exc)
        audits = {}
    provdir = os.path.join(ROOT, "provenance")
    os.makedirs(provdir, exist_ok=True)
    open(os.path.join(provdir, "index.html"), "w", encoding="utf-8").write(
        render_provenance(all_digests, audits, date))
    print("provenance: provenance/index.html")
    try:
        import machine
        for path, size in machine.write_all(all_digests, DOCS, STACKS):
            print("api: %-18s %6d байт" % (path, size))
    except Exception as exc:                      # noqa: BLE001
        print("machine: машиночитаемые файлы не собраны:", exc)
    open(os.path.join(ROOT, ".nojekyll"), "w").write("")
    print("done")
    # страховка: собранные страницы обязаны быть согласованы с шаблонами
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import check_site
        print("\nпроверка страниц:")
        return check_site.main()
    except Exception as exc:                      # проверка никогда не должна ломать сборку
        print("check_site не выполнен:", exc)
        return 0


if __name__ == "__main__":
    sys.exit(main())
