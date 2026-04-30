# Data Model Specification

This document summarizes the core data models, enumerations, and schemas driving the Personal Budget and Spending Assistant application. All models follow strict static typing and leverage Python's `dataclasses` and `Enum` standards for efficient serialization and type safety.

---

## 1. Categories (`data_model/categories.py`)

Categories are strictly enforced using the `StrEnum` class to ensure consistent case-insensitive handling and auto-numbering.

### 1.1 `ExpenseCategory`
Defines valid tracking categories for outgoing items.
*   `EDUCATION`
*   `RENT`
*   `FOOD`
*   `DRINKS`
*   `TRAFFIC`
*   `SUBSCRIPTION`
*   `ENTERTAINMENT`
*   `MEDICAL`
*   `UNCATEGORIZED`

### 1.2 `IncomeCategory`
Defines valid accumulation categories for incoming items.
*   `SALARY`
*   `BONUS`
*   `INVESTMENT`
*   `TRADE`
*   `DIVIDEND`
*   `FREELANCE`
*   `UNCATEGORIZED`

> **Note**: `Categories` is broadly typed as `ExpenseCategory | IncomeCategory`.

---

## 2. Transactions (`data_model/schemas.py`)

Both Income and Expense structures enforce immutability with strict slot assignments (`@dataclass(slots=True)`) to improve memory efficiency and schema rigidity.

### 2.1 `Expense` Schema
*   `id` (`str`): Unique identifier (UUID).
*   `date` (`date`): ISODate formatted transaction date.
*   `amount` (`float`): Decimal value of the expense (must be positive in business logic).
*   `category` (`ExpenseCategory`): Enum link bounding the transaction scope.
*   `description` (`str`): User input or note context.

### 2.2 `Income` Schema
*   `id` (`str`): Unique identifier (UUID).
*   `date` (`date`): ISODate formatted receipt date.
*   `amount` (`float`): Assessed gain magnitude.
*   `category` (`IncomeCategory`): Enum mapping.
*   `description` (`str`): Detailed description of income origin.

> **Note**: `Transaction` is union-typed as `Expense | Income`.

---

## 3. Budget Rules (`data_model/rules.py`)

Provides the underlying domain logic and logical operations evaluated dynamically during execution. The models validate that bounds are physically distinct (e.g., negative rules or empty periods will fail during post-initialization).

### 3.1 `RuleOperator`
Supported operational bounds required to evaluate a threshold. Uses Python's internal operator functions via Enum mapping:
*   `GT`: Evaluates to `>`.
*   `LT`: Evaluates to `<`.
*   `GTE`: Evaluates to `>=`.
*   `LTE`: Evaluates to `<=`.
*   `EQ`: Evaluates to `==`.

### 3.2 `BudgetRule` (Abstract Base Class)
Configures base properties for every subset budget logic. Derived concrete implementations (like `CategoryBudgetRule` or `PercentageThresholdRule` in `concrete_rules.py`) define specific behaviors matching user requirements.

Attributes:
*   `alert` (`Alert`): Assigned reaction handler (e.g. CLI Console print out or Log file dump).
*   `period` (`int`): Sliding window measured in standard days. (Must be `> 0`).
*   `operator` (`RuleOperator`): Defined operator condition.
*   `threshold` (`float`): Limiting numerical barrier constraint. (Must be `>= 0`).

Methods:
*   `evaluate(transaction, history)`: Evaluates whether the rules conditions are breached.
*   `get_range(ref_date)`: Extracts bounded timeframe interval.
*   `to_dict()` & `from_dict()`: Safely de/serialize configurations natively from `rules.json`.

---

## 4. Alerts (`data_model/alerts.py`)

Alert reactions implement a standardized notification interface. Concrete derivations exist to trigger different behavior (such as `ConsoleAlert` for immediate user UI feedback or `FileAlert` for persistent background logging).