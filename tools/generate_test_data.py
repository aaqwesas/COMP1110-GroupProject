from pathlib import Path
from datetime import date, timedelta
import json

OUTPUT_DIR = Path("data/sample_data")

def expense(record_id: str, when: date | str, amount: float | str, category: str, description: str) -> dict:
    if isinstance(when, date):
        when = when.isoformat()
    return {
        "id": record_id,
        "date": when,
        "amount": amount,
        "category": category,
        "description": description,
    }

def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            json.dump(record, file)
            file.write("\n")

def sample_expenses_30days() -> list[dict]:
    base = date(2026, 4, 1)
    records: list[dict] = []
    next_id = 1

    food_amounts = [32, 38, 29, 41, 35, 44, 27]
    traffic_amounts = [12, 9, 14, 11, 10]
    drink_amounts = [18, 22, 16, 20]
    entertainment_amounts = [88, 120, 76, 95]

    food_descriptions = ["Breakfast", "Lunch", "Dinner", "Groceries", "Snack"]
    traffic_descriptions = ["MTR fare", "Bus fare", "Taxi fare"]
    drink_descriptions = ["Coffee", "Milk tea", "Juice", "Water"]
    entertainment_descriptions = ["Movie", "Game top-up", "Karaoke", "Concert"]
    subscription_descriptions = ["Spotify", "YouTube Premium"]
    medical_descriptions = ["Clinic visit", "Medicine"]
    education_descriptions = ["Stationery", "Course material", "Printing"]

    for offset in range(30):
        current = base + timedelta(days=offset)

        records.append(
            expense(
                f"e{next_id:03}",
                current,
                float(food_amounts[offset % len(food_amounts)]),
                "FOOD",
                food_descriptions[offset % len(food_descriptions)],
            )
        )
        next_id += 1

        if offset % 2 == 0:
            records.append(
                expense(
                    f"e{next_id:03}",
                    current,
                    float(traffic_amounts[offset % len(traffic_amounts)]),
                    "TRAFFIC",
                    traffic_descriptions[offset % len(traffic_descriptions)],
                )
            )
            next_id += 1

        if offset % 4 == 1:
            records.append(
                expense(
                    f"e{next_id:03}",
                    current,
                    float(drink_amounts[offset % len(drink_amounts)]),
                    "DRINKS",
                    drink_descriptions[offset % len(drink_descriptions)],
                )
            )
            next_id += 1

        if offset in (0, 14):
            amount = 58.0 if offset == 0 else 68.0
            description = subscription_descriptions[0] if offset == 0 else subscription_descriptions[1]
            records.append(expense(f"e{next_id:03}", current, amount, "SUBSCRIPTION", description))
            next_id += 1

        if offset in (4, 11, 18, 25):
            index = (offset // 7) % len(entertainment_amounts)
            records.append(
                expense(
                    f"e{next_id:03}",
                    current,
                    float(entertainment_amounts[index]),
                    "ENTERTAINMENT",
                    entertainment_descriptions[index],
                )
            )
            next_id += 1

        if offset in (2, 16):
            index = 0 if offset == 2 else 1
            amount = 85.0 if index == 0 else 42.0
            records.append(
                expense(
                    f"e{next_id:03}",
                    current,
                    amount,
                    "MEDICAL",
                    medical_descriptions[index],
                )
            )
            next_id += 1

        if offset in (6, 20):
            index = 0 if offset == 6 else 1
            amount = 35.0 if index == 0 else 55.0
            records.append(
                expense(
                    f"e{next_id:03}",
                    current,
                    amount,
                    "EDUCATION",
                    education_descriptions[index],
                )
            )
            next_id += 1

    records.append(expense(f"e{next_id:03}", date(2026, 4, 3), 2400.0, "RENT", "Monthly rent"))
    return sorted(records, key=lambda record: (record["date"], record["id"]))

def case_budget_exceeded() -> list[dict]:
    return [
        expense("e001", "2026-04-10", 35.0, "FOOD", "Breakfast"),
        expense("e002", "2026-04-11", 45.0, "FOOD", "Lunch"),
        expense("e003", "2026-04-12", 58.0, "FOOD", "Dinner"),
        expense("e004", "2026-04-13", 42.0, "TRAFFIC", "MTR fare"),
        expense("e005", "2026-04-14", 65.0, "FOOD", "Groceries"),
        expense("e006", "2026-04-15", 28.0, "DRINKS", "Coffee"),
        expense("e007", "2026-04-16", 55.0, "FOOD", "Dinner"),
    ]

def case_single_large_transaction() -> list[dict]:
    return [
        expense("e001", "2026-04-08", 28.0, "FOOD", "Lunch"),
        expense("e002", "2026-04-09", 16.0, "DRINKS", "Coffee"),
        expense("e003", "2026-04-10", 820.0, "ENTERTAINMENT", "Concert ticket"),
    ]

def case_percentage_threshold() -> list[dict]:
    return [
        expense("e001", "2026-04-01", 40.0, "FOOD", "Lunch"),
        expense("e002", "2026-04-02", 20.0, "DRINKS", "Milk tea"),
        expense("e003", "2026-04-03", 35.0, "TRAFFIC", "Taxi fare"),
        expense("e004", "2026-04-04", 900.0, "RENT", "Monthly rent"),
    ]

def case_consecutive_overspend() -> list[dict]:
    return [
        expense("e001", "2026-04-12", 120.0, "FOOD", "Groceries"),
        expense("e002", "2026-04-13", 135.0, "FOOD", "Dinner"),
        expense("e003", "2026-04-14", 145.0, "FOOD", "Restaurant"),
    ]

def case_uncategorized() -> list[dict]:
    return [
        expense("e001", "2026-04-05", 50.0, "UNCATEGORIZED", "Cash expense"),
        expense("e002", "2026-04-06", 35.0, "FOOD", "Lunch"),
        expense("e003", "2026-04-07", 20.0, "UNCATEGORIZED", "Unknown purchase"),
    ]

def invalid_date_case() -> list[dict]:
    return [
        expense("e001", "04/10/2026", 40.0, "FOOD", "Lunch"),
    ]

def invalid_amount_case() -> list[dict]:
    return [
        expense("e001", "2026-04-10", "not a number", "FOOD", "Lunch"),
    ]

def missing_field_case() -> list[dict]:
    return [
        {
            "id": "e001",
            "date": "2026-04-10",
            "amount": 40.0,
            "category": "FOOD",
        }
    ]

def unknown_category_case() -> list[dict]:
    return [
        expense("e001", "2026-04-10", 40.0, "MYSTERY", "Lunch"),
    ]

def build_datasets() -> dict[str, list[dict]]:
    return {
        "sample_expenses_30days.jsonl": sample_expenses_30days(),
        "case_budget_exceeded.jsonl": case_budget_exceeded(),
        "case_single_large_transaction.jsonl": case_single_large_transaction(),
        "case_percentage_threshold.jsonl": case_percentage_threshold(),
        "case_consecutive_overspend.jsonl": case_consecutive_overspend(),
        "case_uncategorized.jsonl": case_uncategorized(),
        "invalid_date.jsonl": invalid_date_case(),
        "invalid_amount.jsonl": invalid_amount_case(),
        "missing_field.jsonl": missing_field_case(),
        "unknown_category.jsonl": unknown_category_case(),
        "empty.jsonl": [],
    }

def main() -> None:
    datasets = build_datasets()
    for filename, records in datasets.items():
        write_jsonl(OUTPUT_DIR / filename, records)
    print(f"Generated {len(datasets)} files in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
