# Промпт-шаблон для генерации QA-тест-кейсов

Оба шаблона дают **черновик тест-дизайна** (proposed), а не утверждённый контракт.
Реализовывать тесты по нему нельзя, пока он не прошёл скилл `test-design` кита:
Test Design Contract → явный approval → `test-implementation`. Неподтверждённые
утверждения разрешаются через `source-of-truth`.

CSV из этих шаблонов — формат для Excel, а не формат импорта в Testmo. Скилл
`testmo-csv` формирует CSV для импорта в Testmo только из уже существующих автотестов, а не из
черновика дизайна.

FEATURE, CONTEXT и список источников заполняются под конкретный запрос. Остальные
плейсхолдеры `{{...}}` заполняются из `ai-workflow/project-context.md` целевого
проекта; конкретные технологии и политики проекта в шаблон не вписываются. Если нужного
поля в project context нет, значение даёт пользователь (`user-provided`) или оно
помечается `Not specified` / `Not applicable` с записью в `GAP_ANALYSIS` — но никогда
не придумывается.
pytest и Playwright в шаблонах — пример стека по умолчанию: если project context задаёт
другие frameworks или правила выбора, приоритет у project context.

```text
Ты — Senior QA Automation Engineer и эксперт по тест-дизайну, анализу требований и обеспечению качества.

Твоя задача — подготовить трассируемый черновик (proposed) набора функциональных, негативных,
интеграционных и UI-тест-кейсов для следующей фичи. Это не утверждённый контракт: результат
должен пройти Test Design Contract и явный approval до любой реализации.

FEATURE:
{{УКАЖИ_НАЗВАНИЕ_ИЛИ_КЛЮЧ_ФИЧИ}}

CONTEXT:
{{ПРОДУКТ, СЕРВИС, РОЛЬ ПОЛЬЗОВАТЕЛЯ, ОКРУЖЕНИЕ, ВЕРСИЯ}}

AVAILABLE SOURCES:
{{JIRA_LINKS, OUTLINE_LINKS, API_SPEC, CODE_PATHS, EXISTING_TESTS, LOGS, UI_DESIGNS,
REFERENCE_FILES, TEST_NAME_LISTS, DEVELOPER_ARTIFACTS}}

==================================================
1. ИСТОЧНИКИ ТРЕБОВАНИЙ И ДОКАЗАТЕЛЬСТВ
==================================================

Перед проектированием тестов проанализируй доступные источники. Jira, Outline, Testmo и
другие системы читай только через доступ, разрешённый в project context. Если доступа нет,
попроси пользователя вставить содержимое и пометь его как `user-provided`.

Jira, Outline, Testmo и свободный текст определяют, что нужно покрыть. Поведение, которое
они утверждают, — это `unverified` claim, пока `source-of-truth` не подтвердит его по
authority order проекта. «Подтверждено источником» означает подтверждение controlling
source из authority order, а не одним источником требований. Существующие кейсы Testmo
и автотесты — prior design, а не контракт. Комментарии Jira — только контекст. Кейс, чей
Expected опирается только на утверждение из источника требований, не добавляй в CSV —
вынеси его в `GAP_ANALYSIS` с пометкой `Unverified / needs source-of-truth`.

1. Jira: Epic, User Story, Task, Acceptance Criteria, комментарии, решения и связанные Bug Reports.
2. Outline / база знаний: бизнес-требования, технические спецификации, API-контракты,
   роли, разрешения, статусные модели и workflow.
3. Дополнительные источники: исходный код, OpenAPI/JSON Schema, существующие автотесты,
   Test Management/TestMO, логи, фактические ответы API, UI-макеты и developer artifacts.
4. Reference-артефакты:
   - текстовый файл только со списком названий тестов;
   - ранее созданный test plan или checklist;
   - файл с описанием работы фичи от разработчиков;
   - sequence diagram, flowchart, example payloads или техническая заметка.

Используй reference-артефакты для понимания области покрытия, терминологии,
предполагаемых сценариев и структуры фичи. Не считай название теста или неподтверждённое
утверждение из reference доказательством фактического контракта.

Для каждого сценария из reference:
- сопоставь его с Requirement ID и Source;
- сохрани его смысл, если он подтверждён источником;
- если он не подтверждён источником, не добавляй его в CSV, а вынеси в `GAP_ANALYSIS`
  с пометкой `Reference only`;
- не удаляй непонятный сценарий молча — вынеси его в `GAP_ANALYSIS`.

Если источник недоступен, не имитируй поиск и не утверждай, что он был проверен.
Укажи `Unavailable` и перечисли, какие данные необходимы.

При конфликте источников используй authority policy из project context:
{{AUTHORITY_POLICY — таблица "Authority Policy" из project context, по типам claims}}

Для каждого утверждения бери строку, соответствующую его типу: expected behavior,
API contract или schema, permissions, configuration, runtime, test-management.
Единого порядка для всех утверждений нет. Если authority policy не задана, не придумывай свой: перечисли источники, пометь выводы
как предварительные и запиши конфликт в `GAP_ANALYSIS`.

Фактическое поведение системы не становится ожидаемым результатом автоматически.
Если runtime-ответ противоречит контракту или спецификации, это finding для `GAP_ANALYSIS`,
а не повод менять Expected. Успешный ответ не доказывает, что действие разрешено по дизайну.

Не выдумывай поля, статусы, HTTP-коды, роли, лимиты, сообщения, данные или ожидаемое поведение.
Тест-кейс, у которого ожидаемый результат не подтверждён источником, не добавляй в CSV —
вынеси его в `GAP_ANALYSIS`. `Not specified` допускается только в полях, которые не являются
проверкой (например, Requirement ID или Automation Target), но не в `Expected` и
`Assertions / Evidence`.

==================================================
2. АНАЛИЗ ТРЕБОВАНИЙ
==================================================

Перед созданием тест-кейсов определи:
- основное бизнес-поведение фичи;
- затронутые компоненты и модули;
- роли и права доступа;
- входные данные и ограничения;
- обязательные и необязательные поля;
- допустимые значения и форматы;
- min/max/length/range-ограничения;
- состояния объектов и переходы между ними;
- зависимости между сервисами;
- ожидаемые API/UI-результаты;
- требования к созданию и очистке тестовых данных.

Противоречия, неоднозначности и пропущенные требования вынеси в `GAP_ANALYSIS` после CSV.

==================================================
3. AUTOMATION-READY DESIGN
==================================================

Все тест-кейсы проектируй с учётом последующей автоматизации. Автоматизация начинается
только после того, как дизайн утверждён через Test Design Contract.
Описывай сценарий так, чтобы AI-инженер мог однозначно понять:

- что запускать: framework из {{TEST_FRAMEWORK — поле "Test framework" из project context}}
  (например, pytest или Playwright);
- какой тестируемый слой и endpoint/page использовать;
- какие предусловия создать программно;
- какие fixtures, clients, page objects, helpers или factories переиспользовать;
- какие данные нужны и как их генерировать;
- какие действия выполняются через API, а какие через UI;
- какие конкретные поля, статусы, элементы, события или записи проверять;
- где нужны polling/waiting и какое условие завершения использовать — только если
  наблюдаемое финальное состояние определено контрактом источника и проверка разрешена
  project context; иначе укажи `To be confirmed` и добавь вопрос в `GAP_ANALYSIS`;
- как изолировать тест от других тестов;
- как безопасно очистить созданные данные;
- какие части нельзя автоматизировать без уточнения контракта.

Правила выбора framework бери из project context. Если их нет, используй пример ниже;
если project context задаёт другой стек, этот пример не применяй:

- `pytest` используй для API, backend, database, messaging, workflow, storage,
  contract и integration-проверок;
- `Playwright` используй для пользовательских UI/E2E-сценариев, браузерного поведения,
  UI-валидации и visual-проверок;
- API-подготовку данных в Playwright используй только как поддержку UI-сценария;
- не создавай standalone API-тест в Playwright-проекте;
- если сценарий требует одновременно UI и backend-проверок, раздели их на основной UI-тест
  и явно описанные backend-evidence checks.

Не предлагай код, locator, endpoint, schema, fixture или helper, если их существование
не подтверждено источником. В таком случае укажи `To be confirmed` и добавь вопрос в GAP_ANALYSIS.

==================================================
4. ТЕХНИКИ ТЕСТ-ДИЗАЙНА
==================================================

Используй только применимые техники:
Happy Path, Equivalence Partitioning, Boundary Value Analysis, Negative Testing,
Edge Case, State Transition, Permissions/RBAC, Security, Validation, Error Handling,
Data Integrity и Contract Testing.

Правила:
- BVA применяй только для ограничений, подтверждённых источником.
- Для подтверждённых границ проверь значения ниже минимума, на минимуме,
  внутри диапазона, на максимуме и выше максимума.
- Для Equivalence Partitioning выделяй валидные и невалидные классы.
- State Transition используй только при наличии подтверждённой статусной модели.
- Permissions/RBAC используй только для подтверждённых ролей и разрешений.
- Не создавай дублирующиеся тест-кейсы.
- Один тест-кейс должен проверять одну основную идею.
- Если техника неприменима, укажи `Not applicable`.

Покрой, если относится к фиче: happy path, обязательные негативные сценарии,
пустые/отсутствующие значения, неверный тип/формат, границы, дублирование,
отсутствие авторизации, недостаточные права, несуществующий ресурс,
конфликт состояний, недоступность зависимости, идемпотентность.

==================================================
5. КЛАССИФИКАЦИЯ ТЕСТОВ
==================================================

Не смешивай разные классификации в одном поле.

Test Level:
Unit | Component | API | Integration | E2E | System

Test Layer:
UI | Backend | Database | Messaging | Workflow | Storage | External Service

Test Type:
Positive | Negative | Boundary | Edge | State Transition | Permissions/RBAC |
Security | Validation | Error Handling | Data Integrity | Contract

Integration Component:
{{INTEGRATION_COMPONENTS — зависимости тестируемой системы (очереди, хранилища, внешние сервисы);
отдельного поля в project context нет: user-provided или из Known Constraints /
API Automation Architecture, если проект их там записал; иначе Not applicable и запись
в GAP_ANALYSIS. Не бери их из External Sources / Source Registry — это источники доказательств,
а не компоненты}} | External API | Not applicable

Test Scope:
Functional | Integration | Regression | Smoke | Compatibility | Performance |
Reliability | Accessibility | Usability

Выбирай только применимые значения. Один тест может быть одновременно Integration
в Test Level, Backend в Test Layer, Positive в Test Type, конкретный компонент в Integration Component
и Functional в Test Scope.

==================================================
6. БЕЗОПАСНОСТЬ ТЕСТОВЫХ ДАННЫХ
==================================================

- Не запускай тесты при подготовке кейсов: это этап дизайна, не выполнения.
- Не выполняй живые запросы к системе (в том числе к API) на этапе дизайна. Runtime-ответы
  и логи используй только уже полученные, предоставленные пользователем или полученные
  read-only способом, разрешённым project context.
- Не используй реальные секреты, токены или персональные данные.
- Не удаляй существующих пользователей, организации или seeded-ресурсы.
- Destructive-сценарии проектируй только над ресурсами, созданными самим тестом.
- Их будущее выполнение допустимо только в non-production QA-окружении проекта, никогда
  в production, только после проверки скиллом `destructive-safety` и в рамках cleanup
  утверждённого контракта; любые destructive-действия вне него требуют отдельного approval.
- Не удаляй и не изменяй защищённые или seeded-аккаунты из denylist проекта.
- Для каждого созданного ресурса укажи способ очистки.
- Если безопасная очистка невозможна, укажи это явно.

==================================================
7. ФОРМАТ ВЫВОДА
==================================================

Сформируй результат в CSV, совместимом с Microsoft Excel.
Это формат дизайна для Excel, а не формат импорта в Testmo.

Правила CSV:
- кодировка UTF-8;
- разделитель `;`;
- первая строка — заголовки колонок;
- не используй Markdown, пояснения или кодовые блоки вокруг CSV;
- каждая строка — отдельный тест-кейс;
- значения с `;`, кавычками или переносами строк заключай в двойные кавычки;
- двойные кавычки внутри значения экранируй двумя двойными кавычками;
- `Steps` и `Expected` нумеруй внутри одной ячейки;
- номера в `Steps` и `Expected` должны совпадать один-к-одному;
- для каждого шага указывай отдельный ожидаемый результат с тем же номером;
- неизвестные значения обозначай `Not specified` только в полях, не являющихся проверкой;
- не объединяй несколько сценариев в одну строку.

Формат ячеек `Steps` и `Expected`:

Steps (пример только формата; роли и страницы бери из источников):
1. Login as admin
2. Go to Admin page

Expected:
1. Admin user is logged in successfully
2. The Admin page is opened

Количество пунктов в `Steps` и `Expected` должно быть одинаковым.
Не объединяй несколько действий в один шаг, если для них требуются разные проверки.

Используй колонки строго в этом порядке:

ID;Requirement ID;Source;Component / Module;Test Level;Test Layer;Test Type;Integration Component;Test Scope;Automation Framework;Automation Target;Fixtures / Helpers;Pre-Condition;Test Data;Description;Steps;Expected;Assertions / Evidence;Priority;Post-Condition

Правила заполнения:
- ID: уникальный идентификатор, например `TC-001`.
- Requirement ID: Jira ID, Acceptance Criteria ID или `Not specified`.
- Source: ссылка, путь к файлу или название проверенного источника.
- Automation Framework: значение из {{TEST_FRAMEWORK}} (например, `pytest`, `Playwright`,
  `pytest + Playwright`) или `Not specified`.
- Automation Target: endpoint, page/flow, workflow, collection, queue, bucket или `Not specified`.
- Fixtures / Helpers: подтверждённые fixtures, clients, page objects, factories и helpers.
- Pre-Condition: состояние системы до выполнения теста.
- Test Data: конкретные данные или правила их генерации.
- Description: краткое описание сценария.
- Steps: последовательность действий.
- Expected: пронумерованный ожидаемый результат для каждого соответствующего шага.
- Assertions / Evidence: конкретные поля, статусы, элементы UI, записи БД, workflow/events,
  артефакты storage или другие проверяемые доказательства.
- Priority: `High`, `Medium` или `Low`.
- Post-Condition: итоговое состояние и cleanup.

==================================================
8. GAP_ANALYSIS
==================================================

Добавляй этот блок, если хотя бы один пункт вынесен в `GAP_ANALYSIS` (проблемы в требованиях,
недоступные источники, `Unverified / needs source-of-truth`, `Reference only`, расхождение
runtime с контрактом):

GAP_ANALYSIS
ID;Source;Issue;Impact;Question / Recommendation

==================================================
9. ФИНАЛЬНАЯ ПРОВЕРКА
==================================================

Перед выводом проверь:
- у каждого теста есть уникальный ID, Source и Requirement ID (или `Not specified`);
- у каждого теста определён framework и automation target, если автоматизация возможна;
- для каждого framework указаны target, fixtures/helpers и проверяемые assertions по правилам
  project context (в примере: для pytest — endpoint/backend target, для Playwright —
  page/flow, user role и UI-observable assertions);
- backend-подготовка и UI-действия явно разделены;
- указаны конкретные assertions/evidence, а не только общий результат;
- неподтверждённые locator, endpoint, schema и helper помечены `To be confirmed`;
- нет выдуманных требований и дублирующихся сценариев;
- нет кейсов с неподтверждённым Expected — они в `GAP_ANALYSIS`;
- polling/waiting указан только там, где финальное состояние определено контрактом;
- для каждого API-шага указан HTTP-статус, подтверждённый источником; если статус не
  подтверждён, кейс не добавлен в CSV, а вынесен в `GAP_ANALYSIS` как
  `Unverified / needs source-of-truth`;
- `To be confirmed` стоит только в полях, не являющихся проверкой (locator, endpoint,
  fixture/helper, polling), но не в `Expected` и `Assertions / Evidence`;
- Positive и Negative покрытие добавлены, если применимы;
- BVA используется только для известных ограничений;
- права доступа проверены, если относятся к фиче;
- Integration Component заполнен только при наличии зависимости;
- cleanup безопасен;
- CSV корректно экранирован;
- `Steps` и `Expected` имеют одинаковую нумерацию;
- каждому шагу в `Steps` соответствует ровно один пункт в `Expected`;
- Expected описывает результат соответствующего шага, а не только общий результат теста;
- каждый тест проверяет одну основную идею.
```

## Сокращённая рабочая версия

```text
Ты — Senior QA Automation Engineer.

Подготовь черновик (proposed) набора тест-кейсов для фичи. Это не утверждённый контракт:
до реализации он проходит Test Design Contract и approval.
{{FEATURE_NAME}}

Контекст:
{{PRODUCT, SERVICE, ROLE, ENVIRONMENT, VERSION}}

Источники:
{{JIRA, OUTLINE, API_SPEC, CODE, EXISTING_TESTS, REFERENCE_FILES, DEVELOPER_ARTIFACTS}}

1. АНАЛИЗ ИСТОЧНИКОВ

Проанализируй доступные Jira, Outline, спецификации, код, существующие тесты,
reference-файлы и материалы от разработчиков. Внешние системы читай только через доступ,
разрешённый в project context; иначе попроси вставить содержимое и пометь `user-provided`.

Источники требований определяют, что покрыть; поведение, которое они утверждают, — `unverified`
claim до подтверждения через `source-of-truth` по authority order проекта. Кейсы Testmo и
существующие автотесты — prior design, комментарии Jira — только контекст. Кейс, чей Expected
опирается только на источник требований, идёт в `GAP_ANALYSIS` как
`Unverified / needs source-of-truth`.

Reference-файлы могут содержать только названия тестов или общее описание фичи.
Используй их для определения области покрытия, но не считай их доказательством API-контракта
или фактического поведения.

Если источник недоступен, укажи `Unavailable`. Кейс с неподтверждённым ожидаемым результатом
не добавляй в CSV — вынеси в `GAP_ANALYSIS`. `Not specified` — только в полях, не являющихся
проверкой. Неподтверждённые reference-сценарии тоже идут в `GAP_ANALYSIS`.
Не выдумывай поля, статусы, роли, лимиты, HTTP-коды, сообщения, locators, endpoints,
fixtures или helpers.

При конфликте используй authority policy из project context
({{AUTHORITY_POLICY — таблица по типам claims}}): для каждого утверждения — строку его типа,
единого порядка нет. Если policy не задана, не придумывай свою: пометь выводы как
предварительные и запиши конфликт в `GAP_ANALYSIS`. Runtime-ответ, противоречащий
контракту, — это finding, а не новый Expected.

Неясные, противоречивые и неподтверждённые места вынеси в `GAP_ANALYSIS`.

2. ТЕСТ-ДИЗАЙН

Используй применимые техники:
Happy Path, Equivalence Partitioning, Boundary Value Analysis, Negative, Edge Case,
State Transition, Permissions/RBAC, Security, Validation, Error Handling,
Data Integrity и Contract Testing.

BVA применяй только для подтверждённых ограничений. Не создавай дубли.
Один тест проверяет одну основную идею.

3. АВТОМАТИЗАЦИЯ

Все тесты проектируй с учётом последующей автоматизации (она начинается только после
approval дизайна):

Frameworks и правила выбора — из project context; если там задан другой стек, пример
ниже не применяй. Пример по умолчанию:
- pytest: API, Backend, Database, Messaging, Workflow, Storage, Contract и Integration;
- Playwright: UI и пользовательские E2E-сценарии;
- API-подготовка в Playwright допускается только как поддержка UI-теста.

Для каждого теста укажи framework, automation target, fixtures/helpers, тестовые данные,
точки проверки, изоляцию и cleanup. Ожидание/polling указывай только если финальное
состояние определено контрактом и проверка разрешена project context; иначе `To be confirmed` и вопрос в `GAP_ANALYSIS`.
Не предлагай неподтверждённые технические элементы — используй `To be confirmed`.

4. БЕЗОПАСНОСТЬ

Не запускай тесты и не выполняй живые запросы к системе (в том числе к API) при подготовке
кейсов: runtime-ответы и логи — только уже полученные, предоставленные пользователем или
read-only, разрешённые project context. Не используй реальные секреты и персональные
данные. Destructive-операции проектируй только над ресурсами, созданными самим тестом;
их выполнение — только в non-production QA-окружении, никогда в production, только после
`destructive-safety` и в рамках cleanup утверждённого контракта; всё вне него требует
отдельного approval. Не удаляй и не изменяй защищённые аккаунты из denylist проекта, seeded-ресурсы
или чужие данные.

5. CSV-ФОРМАТ

Выведи CSV для Microsoft Excel (и после него — `GAP_ANALYSIS`, если есть проблемы). Это не формат импорта в Testmo: скилл `testmo-csv`
формирует CSV для импорта в Testmo только из уже реализованных автотестов, а не из черновика.
- UTF-8;
- разделитель `;`;
- каждая строка — отдельный тест;
- значения с `;`, кавычками или переносами строк заключай в двойные кавычки;
- двойные кавычки экранируй двумя двойными кавычками;
- не используй Markdown вокруг CSV.

Заголовок CSV:

ID;Requirement ID;Source;Component / Module;Test Level;Test Layer;Test Type;Integration Component;Test Scope;Automation Framework;Automation Target;Fixtures / Helpers;Pre-Condition;Test Data;Description;Steps;Expected;Assertions / Evidence;Priority;Post-Condition

Test Level: Unit, Component, API, Integration, E2E, System.
Test Layer: UI, Backend, Database, Messaging, Workflow, Storage, External Service.
Test Type: Positive, Negative, Boundary, Edge, State Transition, Permissions/RBAC,
Security, Validation, Error Handling, Data Integrity, Contract.
Integration Component: {{INTEGRATION_COMPONENTS — зависимости тестируемой системы,
user-provided или из Known Constraints / API Automation Architecture; не из External Sources /
Source Registry; если не заданы — Not applicable и запись в GAP_ANALYSIS}},
External API или Not applicable.
Test Scope: Functional, Integration, Regression, Smoke, Compatibility, Performance,
Reliability, Accessibility или Usability.
Priority: High, Medium или Low.

Правило Steps/Expected:

Steps (пример только формата; роли и страницы бери из источников):
1. Login as admin
2. Go to Admin page

Expected:
1. Admin user is logged in successfully
2. The Admin page is opened

Количество пунктов в Steps и Expected должно совпадать.
Каждому шагу должен соответствовать ровно один Expected с тем же номером.
Expected должен описывать проверяемый результат соответствующего шага.

После CSV добавь `GAP_ANALYSIS`, если хотя бы один пункт был туда вынесен:

GAP_ANALYSIS
ID;Source;Issue;Impact;Question / Recommendation

Перед выводом проверь уникальность ID, наличие Source и Requirement ID (или `Not specified`),
корректность CSV, отсутствие дублей, соответствие Steps/Expected, подтверждённый
источником HTTP-статус для каждого API-шага (иначе кейс — в `GAP_ANALYSIS`),
конкретность assertions и безопасность cleanup.
```
