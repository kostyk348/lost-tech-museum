# Музей потерянных идей

Архив находок агента **Information search**: забытые технологии, протоколы, стандарты, патенты и практики,
которые были впереди своего времени — и которые стоит переизобрести сегодня.

**Сайт (GitHub Pages):** https://kostyk348.github.io/lost-tech-museum/

## Дайджесты

| Дайджест | Что внутри |
|---|---|
| [lost-ideas-1980s-2000s](digests/lost-ideas-1980s-2000s/) | 35 идей 1980–2006: TRON/BTRON, Fifth Generation, i-mode, FeliCa, ucode, Minitel, Telescript, FIPA-ACL, Xanadu, Plan 9/Inferno, BeOS, Transputer/Occam, Linda/Jini, Self, iAPX 432, Workplace OS, WinFS, HailStorm, NeWS, OSI, Usenet, Gopher, Setun, OGAS, HyperCard, Newton Soup, calm technology |

## Структура

```
data/<slug>.json          данные дайджеста: находки + питчи (единственный источник правды)
templates/dashboard.html  шаблон страницы дайджеста (page / widget режимы)
templates/index.html      шаблон главной страницы-хаба
scripts/build.py          сборка: index.html + digests/<slug>/index.html (+ --widget)
digests/<slug>/index.html результат сборки, его не правят руками
```

## Как обновлять

```bash
python scripts/build.py            # пересобрать весь сайт
python scripts/build.py --widget /path/widget.html   # компактный виджет для чата
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

## Принципы

1. Факты — только со ссылкой на источник; интерпретация помечается явно.
2. Ничего не выбрасывается: устаревшие находки остаются в архиве с пометкой.
3. HTML всегда генерируется из JSON — страницы и данные не расходятся.
