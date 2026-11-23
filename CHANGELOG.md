# Changelog

Формат: [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии — [SemVer](https://semver.org/lang/ru/).

Записи собраны из `git log` между тегами; каждый пункт — ссылка на коммит.
Merge-коммиты в список не попадают.

## [Unreleased]

Изменения после тега `v0.1.0` (2026-10-16). Сайт публикуется с `master`;
следующий тег ставится после зелёного CI на этом SHA.

### Добавлено

- Три новых стека карточек — `legacy-os`, `pre-web`, `hardware-and-context`
  (35 карточек, покрыты все 35 находок архива), межстековые связи с обратной
  стороной и проверкой в линтере ([4379c00](https://github.com/kostyk348/lost-tech-museum/commit/4379c00)).
- Страница провенанса, экспорт BibTeX/CSV, глоссарий, история аудитов,
  счётчик стеков на провенансе ([5c6dd03](https://github.com/kostyk348/lost-tech-museum/commit/5c6dd03)).
- Двуязычный сайт: русский в корне, английский под `/en/`, переключатель и
  `hreflang` в шапке, сидекар перевода стека ([69ac73d](https://github.com/kostyk348/lost-tech-museum/commit/69ac73d)).
- Английский виджет стека (`--widget <slug>:en`) ([6558860](https://github.com/kostyk348/lost-tech-museum/commit/6558860)).
- Английские сидекары для остальных стеков — все 43 карточки на английском
  ([8285d9b](https://github.com/kostyk348/lost-tech-museum/commit/8285d9b)).
- Очередь на воссоздание: что из архива стоит переписать и почему
  ([dc3b9c5](https://github.com/kostyk348/lost-tech-museum/commit/dc3b9c5)).
- `backlog`: Plumber v0.1 → v0.2, TRON Code v0.1, ucode v0.1
  ([0a9ca2b](https://github.com/kostyk348/lost-tech-museum/commit/0a9ca2b),
  [c0e9c6f](https://github.com/kostyk348/lost-tech-museum/commit/c0e9c6f),
  [a03a459](https://github.com/kostyk348/lost-tech-museum/commit/a03a459),
  [71cc40f](https://github.com/kostyk348/lost-tech-museum/commit/71cc40f)).
- Страница «ОПЛОТ»: разбор атак на ПЛК 2024–2026 и конструкция защищённого
  профиля для Modbus ([214d32e](https://github.com/kostyk348/lost-tech-museum/commit/214d32e));
  из конструкции убраны mbrs, агенты и почтовый аудит
  ([51b6466](https://github.com/kostyk348/lost-tech-museum/commit/51b6466)).
- Журнал триажа: 6 прогонов и 17 решений после 14.10
  ([0cb8349](https://github.com/kostyk348/lost-tech-museum/commit/0cb8349)).
- Базовый снимок статусов `rfc-index` для диффа следующего кандидата
  (9868 записей, 353 HISTORIC) ([7a73e39](https://github.com/kostyk348/lost-tech-museum/commit/7a73e39)).

### Изменено

- `provенанс`: 13 дословных цитат из первоисточников (аудит 48/48), мёртвые
  ссылки помечены и заархивированы, аудит ссылок (4 мёртвых из 151)
  ([7aab7c2](https://github.com/kostyk348/lost-tech-museum/commit/7aab7c2)).
- Долг по цитатам сокращён до 30/35, аудит 68/68
  ([5c6dd03](https://github.com/kostyk348/lost-tech-museum/commit/5c6dd03)).
- Пересобраны `api/`, `feed.xml` и английская главная после появления страницы
  ОПЛОТ ([6d2997a](https://github.com/kostyk348/lost-tech-museum/commit/6d2997a)).
- README: баннер и шапка в стиле CapsuleCraft, бейджи
  ([2740316](https://github.com/kostyk348/lost-tech-museum/commit/2740316),
  [c0bef64](https://github.com/kostyk348/lost-tech-museum/commit/c0bef64),
  [b342feb](https://github.com/kostyk348/lost-tech-museum/commit/b342feb)).

### Исправлено

- Триаж: закрыт пункт про OASIS — класс был не «тяжёлая страница», а обрыв
  тела ([8135d5b](https://github.com/kostyk348/lost-tech-museum/commit/8135d5b)).
- Триаж: закрыт пункт про arXiv в watchlist, класс снят целиком
  ([ab8a48b](https://github.com/kostyk348/lost-tech-museum/commit/ab8a48b)).
- Триаж: в журнале поправлена запись — `Range` и gz на rfc-editor недоступны,
  рычаг только повтор с паузой ([c6f83d9](https://github.com/kostyk348/lost-tech-museum/commit/c6f83d9)).
- Триаж: сканер получил `store_body` + дифф, карантин и отчёт без отпечатка
  сделаны ([d5202ec](https://github.com/kostyk348/lost-tech-museum/commit/d5202ec),
  [9a5f864](https://github.com/kostyk348/lost-tech-museum/commit/9a5f864)).

## [0.1.0] — 2026-10-16

Первый публичный выпуск: архив находок, два дайджеста, первый стек карточек и
сборка статического сайта.

### Добавлено

- Дайджест `lost-ideas-1980s-2000s`: 35 идей 1980–2006 с источниками и
  современными питчами ([9b51aa7](https://github.com/kostyk348/lost-tech-museum/commit/9b51aa7)).
- Дайджест `portfolio-review`: 33 публичных репозитория — что не закончено и что
  выпускать следующим ([937484d](https://github.com/kostyk348/lost-tech-museum/commit/937484d)).
- Дайджест `rfc-graveyard`: 15 протоколов и стандартов с дословными цитатами
  ([71e9095](https://github.com/kostyk348/lost-tech-museum/commit/71e9095)).
- Первый стек карточек — агентные протоколы (8 карточек, двусторонние связи,
  кнопки с белым списком инструментов) ([7d1066d](https://github.com/kostyk348/lost-tech-museum/commit/7d1066d)).
- Компактный виджет стека для чата ([4da7c0e](https://github.com/kostyk348/lost-tech-museum/commit/4da7c0e)).
- Виджет дайджеста для чата ([29d44ec](https://github.com/kostyk348/lost-tech-museum/commit/29d44ec)).
- Документ «концепт двух ботов (Curator + HyperCard)» и markdown→HTML
  конвейер в `build.py` ([8851b50](https://github.com/kostyk348/lost-tech-museum/commit/8851b50)).
- Журнал триажа очереди hubd: 7 кандидатов, 3 принято, 4 отклонено, у всех
  причина ([eec4972](https://github.com/kostyk348/lost-tech-museum/commit/eec4972)).
- Разбор errata RFC 1752, Historic у TUBA/CATNIP, STD 26 у Time Protocol;
  замена мёртвого источника Workplace OS ([20f402c](https://github.com/kostyk348/lost-tech-museum/commit/20f402c)).
- Документ «инженерный инструмент на egui + электротехнический слой в CAD»
  ([d17d232](https://github.com/kostyk348/lost-tech-museum/commit/d17d232)).

### Изменено

- `check_site.py` больше не хардкодит список страниц и запускается
  автоматически после сборки ([d17d232](https://github.com/kostyk348/lost-tech-museum/commit/d17d232),
  [a0f6730](https://github.com/kostyk348/lost-tech-museum/commit/a0f6730)).
- Боты названы по-настоящему: Archivessa (хранительница архива) и Chartessa
  (автор стеков) ([c53cd4d](https://github.com/kostyk348/lost-tech-museum/commit/c53cd4d)).
- Журнал триажа больше не утверждает, что `--reason` нет — опция появилась в
  hubd `adfc8d9` ([fe879d3](https://github.com/kostyk348/lost-tech-museum/commit/fe879d3)).

### Исправлено

- Разбор портфеля отдавал в `DATA` голый массив, а шаблон читает
  `DATA.entries` — страница рисовала только шапку
  ([0f02a24](https://github.com/kostyk348/lost-tech-museum/commit/0f02a24)).
- Иерархия заголовков в markdown-рендерере
  ([bc3468b](https://github.com/kostyk348/lost-tech-museum/commit/bc3468b)).
- Опечатка в README ([29d44ec](https://github.com/kostyk348/lost-tech-museum/commit/29d44ec)).

### Прочее

- `__pycache__` в `.gitignore` ([8d69f41](https://github.com/kostyk348/lost-tech-museum/commit/8d69f41)).

[Unreleased]: https://github.com/kostyk348/lost-tech-museum/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kostyk348/lost-tech-museum/releases/tag/v0.1.0
