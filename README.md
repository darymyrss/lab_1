# lab_1 — DemoScope: архитектура C4

Информационная система аналитического мониторинга и прогнозирования динамики населения РФ.
Команда 18, группа ИДБ-23-13. Зона ответственности: **Слисаренко Дарья — Front-end**, контейнер «Веб-интерфейс аналитика» (`analyst_web`).

## Лабораторные работы

| ЛР | Уровень C4 | Файлы |
|----|------------|-------|
| ЛР1 | L1 Контекст, L2 Контейнеры | `demographic-c4-project/src/context.puml.txt`, `demographic-c4-project/src/containers.puml.txt` |
| ЛР2 | L3 Компоненты | `demographic-c4-project/src/components/web-analyst-components.puml` |
| ЛР3 | L4 Код (UML Class + Python, паттерн «Стратегия») | `demographic-c4-project/src/code/heatmap-styler-classes.puml`, `demographic-c4-project/code/` |

## ЛР3: запуск кода

```bash
cd demographic-c4-project/code
python -m unittest      # 13 модульных тестов
python demo.py          # подмена стратегии классификации тепловой карты
mypy                    # строгая проверка аннотаций типов (pip install mypy)
```

## Правила оформления диаграмм

- только `Rel(от, кому, "описание", "протокол")`, без `Rel_R/L/D/U`;
- без `skinparam` в файлах участников;
- идентификаторы элементов совпадают с глоссарием ID проекта (`analyst`, `official`, `api_gateway`, `iam`, `gis_service`, …).
