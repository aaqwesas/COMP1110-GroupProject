# Personal Budget and Spending Assistant

## Introduction
University students and young adults often struggle to manage their finances, with expenses spread across multiple categories like food, transport, and subscriptions. Without a clear system, it's easy to lose track of spending and accidentally exceed budgets in certain areas.

This project is a text-based Python budgeting program providing a structured system that allows users to set category-specific limits, track daily transactions, and receive rule-based alerts when they are close to overspending. By promoting better financial awareness, this application helps students stay within their means and build responsible money habits. 

## Key Features
- **Record Transactions:** Log income and expenses with precise details (date, amount, category, description).
- **Text-Based Menu Interface:** An interactive CLI to seamlessly navigate through adding transactions, viewing summaries, and configuring settings.
- **Advanced Filtering:** View all transactions or filter them efficiently by date or specific categories.
- **Comprehensive Spending Summaries:** Compute and view total spending, income, net balance, top 3 spending categories, and periodic trends (7-day/30-day averages, weekly, and monthly totals).
- **Rule-Based Alerts:** Define customized rules to trigger alerts (Console or File based). Available rules include:
  - **Category Budget Rule:** Limit spending within a category over a specified time period.
  - **Single Transaction Rule:** Warn when a single transaction exceeds a given threshold.
  - **Percentage Threshold Rule:** Alert if a category exceeds a certain percentage of the overall budget.
  - **Consecutive Overspend Rule:** Warn if daily limits are exceeded for predefined consecutive days.
  - **Uncategorized Warning Rule:** Flag expenses that are left uncategorized.
- **Data Persistence:** Input and output data, as well as configured rules, are efficiently stored natively in JSON/JSONL format allowing users to save and load data seamlessly for future use.

## Project Structure
The repository is modularized into several key directories:
- `main.py` & `menu.py`: The entry point and interactive CLI menu of the application.
- `core/`: Contains the core logic for the budgeting application, including the Rule Manager, specific rule types (`concrete_rules.py`), alert dispatches (`concrete_alerts.py`), and Summary Statistics computation.
- `data_model/`: Defines the foundational Pydantic/dataclass schemas representing Expenses, Incomes, Categories, and Rules.
- `tools/`: Consists of utilities necessary to parse inputs (`input_parser.py`), format outputs (`output_parser.py`), and a test data generator (`generate_test_data.py`).
- `data/`: Local storage directory holding active transactions, budgets, and sample data sets for testing purposes.
- `case_studies/`: Curated scenario scripts to evaluate how the system handles different spending profiles.
- `tests/`: Comprehensive test suites verifying code functionality safely against edge cases.

## Installation and Set up

1. Clone the repository.
   ```bash
   git clone <https://github.com/aaqwesas/COMP1110-GroupProject.git>
   cd COMP1110-GroupProject
2. Run the application.
   ```bash
   python main.py
