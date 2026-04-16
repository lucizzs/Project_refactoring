# Library Management System — Refactoring Project

## Опис

Рефакторинг реального навчального проєкту з GitHub:  
**[Uthpal-p/Library-Management-system-using-Python](https://github.com/Uthpal-p/Library-Management-system-using-Python)**  
(0 зірок, 0 форків, 1 файл `main_lms.py`, 123 рядки)

Оригінальна система дозволяє адміністратору бібліотеки переглядати книги, видавати їх читачам, приймати повернення і розраховувати штраф за прострочення. Зв'язок із CSV через `pandas` замінено на in-memory структури для можливості unit-тестування — всі code smells збережені.

---

## Структура проєкту

```
project-root/
├── original_code.py          ← legacy-версія зі збереженими code smells
├── refactored_code.py        ← рефакторована версія (10 технік)
├── tests/
│   └── test_cases.py         ← 40 юніт-тестів (працюють на обох версіях)
├── docs/
│   └── refactoring_report.md ← детальний звіт по кожній техніці
└── README.md
```

---

## Запуск

```bash
# 1. Встановити pytest
pip install pytest

# 2. Тести рефакторованої версії
python -m pytest tests/test_cases.py -v

# 3. Тести оригінальної версії
LIBRARY_IMPL=original python -m pytest tests/test_cases.py -v
```

---

## Застосовані техніки рефакторингу (10)

| # | Техніка | Code Smell |
|---|---|---|
| 1 | Move Import to Top Level | `import` всередині функцій |
| 2 | Replace Magic Number with Named Constant | числа в логіці без контексту |
| 3 | Replace Type Code with Enum | рядки `'AVAILABLE'` / `'BORROWED'` |
| 4 | Introduce Value Object | книга як анонімний `dict` |
| 5 | Replace Primitive with Object | дати як рядки `'dd-mm-yyyy'` |
| 6 | Extract Method | fine-логіка вбудована в `give_back` |
| 7 | Encapsulate Variable | глобальний список `books` |
| 8 | Rename Variable | `a`, `b`, `l`, `x`, `col`, `Fine` |
| 9 | Consolidate Duplicate Code | однаковий пошук у `borrow` і `give_back` |
| 10 | Replace Recursive Validator / Remove Redundant Conditional | вкладена рекурсія + `elif` що завжди `True` |

---

## Ключові метрики

| Метрика | Original | Refactored |
|---|---|---|
| Класів | 0 | 4 |
| Глобальних змінних-станів | 1 | **0** |
| Імпортів всередині функцій | 2 | **0** |
| Вкладених функцій | 2 | **0** |
| Цикломатична складність | 31 | **14 (−55%)** |
| Юніт-тести | 0 | **40** |
