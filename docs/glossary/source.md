# Глоссарий: термины, без которых записи читаются тяжело

Архив говорит на языке своих находок — capability, tuple space, performatives. Здесь короткие определения
и ссылки на записи, где термин работает по делу.

**Это объяснение агента, а не факт из источника.** Определения нужны, чтобы читать записи с порога;
проверять и цитировать следует первоисточники, указанные в каждой записи.

## Агенты и протоколы

**ACL / performatives.** Язык сообщений агентов, где смысл задаётся не данными, а речевым актом:
`inform`, `request`, `propose`, `agree`, `refuse`. Агент не просто передаёт структуру — он заявляет
намерение, и получатель может на него ответить. → [FIPA-ACL / KQML](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-fipa)

**Мобильный код.** Программа, которая переносится к данным вместе со своим состоянием и продолжает
выполнение на чужой машине. Противоположность «принеси данные ко мне». → [General Magic / Telescript](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-genmagic)

**Tuple space.** Общее ассоциативное пространство, куда процессы кладут кортежи и откуда читают по шаблону,
не зная друг о друге. Связь «по данным», а не «по адресу». → [Linda / JavaSpaces / Jini](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-linda)

**Overlay.** Сеть поверх сети: узлы соединены туннелями там, где нужная функция не поддержана
инфраструктурой. Так жил MBone, пока маршрутизаторы не научились multicast. → [IP multicast и MBone](https://kostyk348.github.io/lost-tech-museum/digests/rfc-graveyard/#c-ipmulticast)

## Системы и железо

**Capability-адресация.** Доступ определяется не «кто ты» (права), а «что у тебя на руках» — неподделываемый
идентификатор объекта; передал capability — передал доступ. → [Intel iAPX 432](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-iapx432)

**Персистентность имён (9P).** Любой ресурс — файл: окно, сеть, процесс. Открыл, прочитал, записал —
и вся система однородна, а сеть становится продолжением локальной файловой системы. → [Plan 9](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-plan9)

**Образ как артефакт.** Программа и её состояние — единый живой образ (image), а не набор файлов на диске;
развёртывание = передача образа. → [Self / Smalltalk](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-self)

**Структурный стор.** Вместо файлов и папок — записи с полями, индексом и запросами: документ как строка
базы, а не как файл. → [Newton «Soup»](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-newton)

**Микроядро и сообщения.** Минимум в ядре, остальное — серверы, общающиеся сообщениями; переносимость
и изоляция сбоев вместо монолита «всё в привилегированном режиме». → [Inferno](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-inferno)

**Троичная логика.** Счёт в системе с тремя состояниями (балансное троичное), вместо двух; экономичнее
по разрядам, но требует всей индустрии вокруг себя. → [Setun](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-setun)

## Сеть и стандарты

**ASN.1 / X.400 / X.500.** Абстрактная нотация данных и два стандарта: почта (X.400) и каталог (X.500).
Тяжёлые, но живые частями: ASN.1 пережил своих хозяев и работает в TLS и мобильных сетях. → [OSI](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-osi)

**Открытая лицензия на спеку.** Спецификация, которую можно реализовать без разрешения и без пошлины —
прежде, чем «open» стало маркетинговым словом. → [TRON / BTRON](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-tron)

**Групповая адресация.** Адрес, за которым стоит множество получателей: издатель не знает, кому
достанется датаграмма, а сеть доставляет всем членам группы. → [IP multicast](https://kostyk348.github.io/lost-tech-museum/digests/rfc-graveyard/#c-ipmulticast)

## Что делают люди

**Calm technology.** Технология, которая работает на периферии внимания и уходит в фон, когда не нужна;
противоположность экрану, требующему взгляда. → [Weiser](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-weiser)

**Логическое программирование.** Программа как набор утверждений и правил вывода, а не последовательность
команд; машина ищет доказательство цели. → [Пятое поколение](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-fgcs)

**Вертикальная интеграция против открытого стандарта.** Закрытый формат выигрывает, пока владелец
контролирует весь стек; открытый — как только появляется дешёвая альтернатива. Через этот выбор прошли
i-mode, PC-98, FeliCa и Minitel. → [i-mode](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-imode) ·
[PC-98](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-pc98) ·
[FeliCa](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-felica) ·
[Minitel](https://kostyk348.github.io/lost-tech-museum/digests/lost-ideas-1980s-2000s/#c-minitel)

---

Машиночитаемые версии всего архива: [api/entries.json](https://kostyk348.github.io/lost-tech-museum/api/entries.json),
[api/entries.csv](https://kostyk348.github.io/lost-tech-museum/api/entries.csv),
[api/museum.bib](https://kostyk348.github.io/lost-tech-museum/api/museum.bib).
