# Музей потерянных идей

[![Release](https://img.shields.io/github/v/release/kostyk348/lost-tech-museum?sort=semver&color=blue)](https://github.com/kostyk348/lost-tech-museum/releases)
[![Last commit](https://img.shields.io/github/last-commit/kostyk348/lost-tech-museum?branch=master)](https://github.com/kostyk348/lost-tech-museum/commits/master)

Архив находок агента **Information search**: забытые технологии, протоколы, стандарты, патенты и практики,
которые были впереди своего времени — и которые стоит переизобрести сегодня.

**Сайт (GitHub Pages):** https://kostyk348.github.io/lost-tech-museum/

## Дайджесты

| Дайджест | Что внутри |
|---|---|
| [lost-ideas-1980s-2000s](digests/lost-ideas-1980s-2000s/) | 35 идей 1980–2006: TRON/BTRON, Fifth Generation, i-mode, FeliCa, ucode, Minitel, Telescript, FIPA-ACL, Xanadu, Plan 9/Inferno, BeOS, Transputer/Occam, Linda/Jini, Self, iAPX 432, Workplace OS, WinFS, HailStorm, NeWS, OSI, Usenet, Gopher, Setun, OGAS, HyperCard, Newton Soup, calm technology |
| [rfc-graveyard](digests/rfc-graveyard/) | 15 протоколов и стандартов, описанных до последней запятой и не прижившихся: кандидаты в IPv6 (TUBA, CATNIP, SIPP, Nimrod), IP multicast/MBone, RSVP/IntServ, WHOIS++/CRISP, мосты X.400/MIXER, Classical IP over ATM, POP2, Time Protocol, SET, UDDI, Web Intents, PubSubHubbub → WebSub. У каждой записи — дословная цитата из первоисточника и сверенный статус RFC |

## Стеки карточек

Стек — инструмент, собранный поверх архива: карточки, фоны (шаблоны), двусторонние связи и кнопки-действия.
Собирает агент **Chartessa**; в `stacks/` пишет только он, в `data/` — только Archivessa. Связи двусторонние:
карточка стека ссылается на запись архива, а запись показывает, в каких стеках используется (🧩).

| Стек | Что внутри |
|---|---|
| [agent-protocols](stacks/agent-protocols/) | 8 карточек: FIPA-ACL/KQML, Telescript, Linda/Jini, HailStorm, OSI, Fifth Generation + чек-лист «чего не хватает вашему агентному протоколу»; 6 записей архива, кнопки с белым списком инструментов |

## Структура

```
data/<slug>.json           данные дайджеста: находки + питчи (единственный источник правды)
stacks/<slug>/stack.json   данные стека: карточки, фоны, связи, действия, источники
templates/dashboard.html   шаблон страницы дайджеста (page / widget режимы)
templates/stack.html       шаблон страницы стека (карточки-фоны page / widget)
templates/index.html       шаблон главной страницы-хаба
scripts/build.py           сборка: index.html + digests/<slug>/ + docs/<slug>/ + stacks/<slug>/ (+ --widget)
scripts/lint_stacks.py     проверка целостности стеков: связи, фон, источники, белый список инструментов
digests/<slug>/index.html  результат сборки, его не правят руками
stacks/<slug>/index.html   результат сборки, его не правят руками
```

## Как обновлять

```bash
python scripts/build.py            # пересобрать весь сайт (+ проверка страниц внутри)
python scripts/lint_stacks.py      # проверить стеки (код 1 — публиковать нельзя)
python scripts/quotes.py --fetch    # скачать первоисточники и вытащить дословные цитаты (сверка провенанса)
python scripts/build.py --widget /path/widget.html            # компактный виджет дайджеста для чата
python scripts/build.py --widget /path/widget.html <slug>     # дайджест или стек
git add -A && git commit -m "digest: ..." && git push
```

## Формат находки

```json
{
  "id": "tron", "name": "TRON / BTRON", "reg": "jp|other", "years": "1984 — н.в.",
  "eras": ["80", "90"], "dom": "os|net|ui|ai|hw|soc", "gap": 4,
  "what": "что это было", "why": "почему было круто", "death": "почему не выжило",
  "now": "где это сейчас", "pitch": "что внедрить сегодня",
  "src": [{"u": "https://…", "t": "название источника", "r": 1}]
}
```

`gap` (1–5) и `pitch` — оценка и рекомендация агента, а не цитата. `r: 1` — источник прочитан целиком (`✓` в интерфейсе),
`r: 0` — взят из индекса поиска (`↗`).

**Дословная цитата — обязательна для факта.** У источника может быть поле `q`: фрагмент первоисточника слово в слово
(переносы строк нормализованы, многоточие `…` означает сокращение). Интерфейс показывает такие фрагменты отдельным блоком
с меткой «цитата» — чтобы читатель видел, что является фактом, а что пересказом. Сверить цитаты с первоисточниками:
`python scripts/quotes.py --fetch` (скачивает тексты в `cache/quotes/` и проверяет, что каждая цитата действительно
есть в первоисточнике; код 1 — публиковать нельзя).

## Формат карточки стека

```json
{
  "slug": "agent-protocols",
  "title": "…", "subtitle": "…", "generated": "YYYY-MM-DD",
  "archive": { "slug": "lost-ideas-1980s-2000s", "title": "…" },
  "backgrounds": { "fact": { "name": "карточка факта", "layout": "list", "note": "…" } },
  "cards": [{
    "id": "fipa", "title": "FIPA-ACL / KQML", "subtitle": "1993 — 2005", "bg": "fact", "gap": 5,
    "fields": [{ "lbl": "Что это было", "val": "…", "to": "checklist" }],
    "archive": ["fipa"],
    "links": [{ "to": "osi", "why": "почему правильный стандарт не принимают" }],
    "actions": [{ "t": "Сравнить с MCP", "p": "текст промпта", "tools": ["web_search", "read_file"] }],
    "sources": [{ "u": "https://…", "t": "…", "r": 1, "kind": "archive|inherited|self" }]
  }]
}
```

`bg` — фон-шаблон из `backgrounds` (`list`, `cols`, `table`). `links` задаются в одну сторону, обратная сторона
(«сюда ведут») считается сборкой — поэтому связь всегда двусторонняя. `tools` — белый список инструментов действия
(пустой список = «без инструментов»); произвольный код в действии запрещён и ловится линтером.

## Принципы

1. Факты — только со ссылкой на источник; интерпретация помечается явно.
2. Ничего не выбрасывается: устаревшие находки остаются в архиве с пометкой.
3. HTML всегда генерируется из JSON — страницы и данные не расходятся.
