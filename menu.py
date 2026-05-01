"""Menu interface for Personal Budget Assistant"""

import sys
import uuid
from datetime import date
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from data_model.schemas import Expense, Income
from data_model.categories import ExpenseCategory, IncomeCategory
from data_model.rules import RuleOperator, BudgetRule
from core.summary_statistics import SummaryReport, SummaryStatistics
from core.rule_manager import RuleManager
from core.concrete_rules import (
    CategoryBudgetRule,
    SingleTransactionRule,
    PercentageThresholdRule,
    UncategorizedWarningRule,
    ConsecutiveOverspendRule,
)
from core.concrete_alerts import ConsoleAlert, FileAlert
from tools.category_parser import ExpenseCategoryParser
from tools.input_parser import ExpenseParser, IncomeParser
from tools.output_parser import GenericOutputParser


class BudgetMenu:
    """Main menu interface for Personal Budget Assistant"""

    def __init__(self):
        """Initialize with your existing data structures"""
        self.expenses: list[Expense] = []
        self.incomes: list[Income] = []
        self.rule_manager = RuleManager()
        self.expenses_file = Path("data/expenses.jsonl")
        self.incomes_file = Path("data/incomes.jsonl")
        self.rules_file = Path("data/rules.json")
        self.expenses_file.parent.mkdir(parents=True, exist_ok=True)
        self.expenses_file.touch(exist_ok=True)
        self.incomes_file.touch(exist_ok=True)
        if not self.rules_file.exists():
            self.rules_file.write_text("[]")

        self._load_data()

    def run(self):
        """Main program loop"""
        self._show_welcome()

        while True:
            self._show_menu()
            choice = input("\nChoose: ").strip()

            if choice == "1":
                self._add_expense()
            elif choice == "2":
                self._add_income()
            elif choice == "3":
                self._view_transactions()
            elif choice == "4":
                self._show_summary()
            elif choice == "5":
                self._check_alerts()
            elif choice == "6":
                self._configure_rules()
            elif choice == "7":
                self._save_data()
            elif choice == "8":
                if self._confirm_exit():
                    break
            else:
                print("Invalid choice. Enter 1-8.")

    def _show_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 50)
        print("   PERSONAL BUDGET ASSISTANT".center(50))
        print("=" * 50)
        print(f"\n{len(self.expenses)} expenses, {len(self.incomes)} incomes loaded")
        print(f"{len(self.rule_manager.rules)} budget rules active\n")

    def _show_menu(self):
        """Display menu options"""
        print("\n" + "-" * 40)
        print("MAIN MENU")
        print("-" * 40)
        print("1. Add Expense")
        print("2. Add Income")
        print("3. View Transactions")
        print("4. Spending Summary")
        print("5. Check Alerts")
        print("6. Configure Budget Rules")
        print("7. Save Data")
        print("8. Exit")
        print("-" * 40)

    def _load_data(self):
        """Load transactions and rules from files"""
        # 1. Load Expenses
        if getattr(self, "expenses_file", None):
            parser = ExpenseParser(self.expenses_file)
            self.expenses = list(parser.parse())
            print(f"Loaded {len(self.expenses)} expenses")

        # 2. Load Incomes
        if getattr(self, "incomes_file", None):
            parser = IncomeParser(self.incomes_file)
            self.incomes = list(parser.parse())
            print(f"Loaded {len(self.incomes)} incomes")

        # 3. Load Rules
        if getattr(self, "rules_file", None):
            if not self.rules_file.exists():
                print("No rules file found. Starting with default/empty rules.")
            elif self.rules_file.stat().st_size == 0:
                print("Rules file is empty. Starting with no active rules.")
            else:
                try:
                    with open(self.rules_file, "r", encoding="utf-8") as rf:
                        rule_dicts = json.load(rf)

                    rule_classes_map = {
                        "CategoryBudgetRule": CategoryBudgetRule,
                        "SingleTransactionRule": SingleTransactionRule,
                        "PercentageThresholdRule": PercentageThresholdRule,
                        "UncategorizedWarningRule": UncategorizedWarningRule,
                        "ConsecutiveOverspendRule": ConsecutiveOverspendRule,
                    }

                    alert_classes_map = {
                        "ConsoleAlert": ConsoleAlert,
                        "FileAlert": FileAlert,
                    }

                    for r_data in rule_dicts:
                        rule = BudgetRule.from_dict(
                            r_data,
                            rule_classes_map=rule_classes_map,
                            alert_classes_map=alert_classes_map,
                        )
                        self.rule_manager.add_rule(rule)
                    print(f"Loaded {len(self.rule_manager.rules)} active rules")
                except json.JSONDecodeError:
                    print(
                        "Error: The budget rules file is malformed or corrupted. Cannot load rules."
                    )
                except PermissionError:
                    print(f"Error: Permission denied when trying to read rules file.")
                except Exception as e:
                    print(f"Unexpected error loading rules data: {e}")

    def _save_data(self):
        """Save transactions to JSONL file"""
        try:
            output_parser = GenericOutputParser()

            if self.expenses:
                output_parser(self.expenses_file, self.expenses)

            if self.incomes:
                output_parser(self.incomes_file, self.incomes)

            rule_dicts = [rule.to_dict() for rule in self.rule_manager.rules]
            with open(self.rules_file, "w", encoding="utf-8") as rf:
                json.dump(rule_dicts, rf, indent=4)

            print(f"Saved {len(self.expenses)} expenses")
            print(f"Saved {len(self.incomes)} incomes")
            print(f"Saved {len(self.rule_manager.rules)} rules")
        except Exception as e:
            print(f"Error saving: {e}")

    def _add_expense(self):
        """Add a new expense transaction"""
        print("\n" + "-" * 40)
        print("ADD EXPENSE")
        print("-" * 40)

        while True:
            date_str = input("Date (YYYY-MM-DD) [today]: ").strip()
            if not date_str:
                trans_date = date.today()
                break
            try:
                trans_date = date.fromisoformat(date_str)
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD")

        while True:
            try:
                amount = float(input("Amount (HK$): "))
                if amount > 0:
                    break
                print("Amount must be positive")
            except ValueError:
                print("Enter a valid number")

        print("\nExpense Categories:")
        for cat in ExpenseCategory:
            print(f"   - {cat.name}")

        category_str = input("Category: ").strip().upper()
        category = ExpenseCategoryParser(category_str)
        print(f"Category: {category.name}")

        description = input("Description: ").strip()
        if not description:
            description = "No description"

        expense = Expense(
            id=str(uuid.uuid4())[:8],
            date=trans_date,
            amount=amount,
            category=category,
            description=description,
        )

        self.expenses.append(expense)
        print(f"\nExpense added: ${amount:.2f} | {category.name} | {description}")

        self.rule_manager.process_transaction(expense, self.expenses)

    def _add_income(self):
        """Add a new income transaction"""
        print("\n" + "-" * 40)
        print("ADD INCOME")
        print("-" * 40)

        while True:
            date_str = input("Date (YYYY-MM-DD) [today]: ").strip()
            if not date_str:
                trans_date = date.today()
                break
            try:
                trans_date = date.fromisoformat(date_str)
                break
            except ValueError:
                print("Invalid date format")

        while True:
            try:
                amount = float(input("Amount (HK$): "))
                if amount > 0:
                    break
                print("Amount must be positive")
            except ValueError:
                print("Enter a valid number")

        print("\nIncome Categories:")
        for cat in IncomeCategory:
            print(f"   - {cat.name}")

        category_str = input("Category: ").strip().upper()
        category = getattr(IncomeCategory, category_str, None)
        if category is None:
            print(f"Unknown category, using {IncomeCategory.UNCATEGORIZED.name}")
            category = IncomeCategory.UNCATEGORIZED

        description = input("Description: ").strip()
        if not description:
            description = "No description"

        income = Income(
            id=str(uuid.uuid4())[:8],
            date=trans_date,
            amount=amount,
            category=category,
            description=description,
        )

        self.incomes.append(income)
        print(f"\nIncome added: +${amount:.2f} | {category.name}")

    def _view_transactions(self):
        """View all transactions or filter them by date/category"""
        if not self.expenses and not self.incomes:
            print("\nNo transactions yet.")
            return

        print("\n" + "-" * 40)
        print("VIEW TRANSACTIONS")
        print("-" * 40)
        print("1. View All")
        print("2. Filter by Date")
        print("3. Filter by Category")

        choice = input("\nChoose filter option: ").strip()

        filtered_expenses = self.expenses
        filtered_incomes = self.incomes

        if choice == "2":
            start_date = None
            while True:
                start_str = input(
                    "Start Date (YYYY-MM-DD) [Leave blank for no start]: "
                ).strip()
                if not start_str:
                    break
                try:
                    start_date = date.fromisoformat(start_str)
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD or leave blank.")

            end_date = None
            while True:
                end_str = input(
                    "End Date (YYYY-MM-DD) [Leave blank for no end]: "
                ).strip()
                if not end_str:
                    break
                try:
                    end_date = date.fromisoformat(end_str)
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD or leave blank.")

            if start_date:
                filtered_expenses = [
                    e for e in filtered_expenses if e.date >= start_date
                ]
                filtered_incomes = [i for i in filtered_incomes if i.date >= start_date]

            if end_date:
                filtered_expenses = [e for e in filtered_expenses if e.date <= end_date]
                filtered_incomes = [i for i in filtered_incomes if i.date <= end_date]

        elif choice == "3":
            cat_str = (
                input("Enter category name (e.g., FOOD, SALARY, RENT): ")
                .strip()
                .upper()
            )
            filtered_expenses = [
                e for e in filtered_expenses if e.category.name == cat_str
            ]
            filtered_incomes = [
                i for i in filtered_incomes if i.category.name == cat_str
            ]

        elif choice != "1":
            print("Invalid choice. Displaying all transactions.")

        self._print_transaction_list(filtered_expenses, filtered_incomes)

    def _print_transaction_list(self, expenses, incomes):
        """Helper to print a list of transactions to the console"""
        if not expenses and not incomes:
            print("\nNo transactions found matching your criteria.")
            return

        print("\n" + "-" * 70)
        print(
            f"{'Type':<8} {'Date':<12} {'Amount':<10} {'Category':<15} {'Description'}"
        )
        print("-" * 70)

        for e in expenses:
            print(
                f"{'Expense':<8} {e.date}  -${e.amount:<9.2f} {e.category.name:<15} {e.description[:30]}"
            )

        for i in incomes:
            print(
                f"{'Income':<8} {i.date}  +${i.amount:<9.2f} {i.category.name:<15} {i.description[:30]}"
            )

        print("-" * 70)
        total_expense = sum(e.amount for e in expenses)
        total_income = sum(i.amount for i in incomes)
        print(f"Total Expenses: ${total_expense:.2f}")
        print(f"Total Income: ${total_income:.2f}")
        print(f"Net Balance: ${total_income - total_expense:.2f}")

    def _show_summary(self):
        """Show spending summary using your SummaryStatistics"""
        if not self.expenses:
            print("\nNo expense data to summarize.")
            return

        all_transactions = self.expenses + self.incomes
        stats = SummaryStatistics(all_transactions)
        report: SummaryReport = stats.summary()

        print("\n" + "=" * 50)
        print("SPENDING SUMMARY")
        print("=" * 50)

        print(f"\nTotal Spending: ${report['total_spending']:.2f}")
        print(f"Total Income: ${report['total_income']:.2f}")
        print(f"Net Balance: ${report['net_balance']:.2f}")

        print("\nSpending by Category:")
        for cat, amt in report["spending_by_category"].items():
            pct = (
                (amt / report["total_spending"] * 100)
                if report["total_spending"] > 0
                else 0
            )
            bar = "█" * int(pct / 2)
            print(f"   {cat.name:<15} ${amt:>8.2f}  ({pct:>5.1f}%) {bar}")

        print("\nIncome by Category:")
        for cat, amt in report["income_by_category"].items():
            pct = (
                (amt / report["total_income"] * 100)
                if report["total_income"] > 0
                else 0
            )
            bar = "█" * int(pct / 2)
            print(f"   {cat.name:<15} ${amt:>8.2f}  ({pct:>5.1f}%) {bar}")

        print("\nTop Spending Categories:")
        for i, (cat, amt) in enumerate(report["top_3_spending_categories"], 1):
            print(f"   {i}. {cat.name}: ${amt:.2f}")


        print("\nTop Income Categories:")
        for i, (cat, amt) in enumerate(report["top_3_income_categories"], 1):
            print(f"   {i}. {cat.name}: ${amt:.2f}")

        print("\nSpending Trends:")
        print(f"   Last 7 days avg: ${report['avg_daily_spending_7d']:.2f}/day")
        print(f"   Last 30 days avg: ${report['avg_daily_spending_30d']:.2f}/day")

        if report["spending_change_7d_pct"] is not None:
            change = report["spending_change_7d_pct"]
            if change > 0:
                print(f"   +{change:.1f}% increase vs previous 7 days")
            elif change < 0:
                print(f"   {change:.1f}% decrease vs previous 7 days")
            else:
                print(f"   No change vs previous 7 days")

        print("\nTime-based Totals (Recent):")

        if report.get("weekly_spending"):
            print("   Weekly Spending:")
            sorted_weeks = sorted(report["weekly_spending"].items(), reverse=True)[:4]
            for (year, week), amt in sorted_weeks:
                print(f"      Week {week}, {year}: ${amt:.2f}")

        if report.get("monthly_spending"):
            print("   Monthly Spending:")
            sorted_months = sorted(report["monthly_spending"].items(), reverse=True)[:4]
            for (year, month), amt in sorted_months:
                print(f"      {year}-{month:02d}: ${amt:.2f}")

    def _check_alerts(self):
        """Check all budget rules"""
        if not self.rule_manager.rules:
            print("\nNo budget rules configured.")
            print("   Use option 6 to add rules.")
            return

        print("\n" + "-" * 40)
        print("CHECKING BUDGET RULES")
        print("-" * 40)

        print("\nActive Rules:")
        for i, rule in enumerate(self.rule_manager.rules, 1):
            rule_type = rule.__class__.__name__
            period = getattr(rule, "period", "N/A")
            print(f"   {i}. {rule_type} - {period} days")

        print("\n" + "-" * 40)
        print("Alerts will appear when you add transactions that violate rules.")
        print("Current status: Ready")

    def _configure_rules(self):
        """Configure budget rules"""
        print("\n" + "-" * 40)
        print("CONFIGURE BUDGET RULES")
        print("-" * 40)
        print("1. View All Rules")
        print("2. Add Category Budget Rule (period-based cap)")
        print("3. Add Single Transaction Rule")
        print("4. Add Percentage Threshold Rule")
        print("5. Add Uncategorized Warning Rule")
        print("6. Add Consecutive Overspend Rule")
        print("7. Delete Rule")
        print("8. Clear All Rules")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            self._view_rules()
        elif choice == "2":
            self._add_category_rule()
        elif choice == "3":
            self._add_single_transaction_rule()
        elif choice == "4":
            self._add_percentage_rule()
        elif choice == "5":
            self._add_uncategorized_rule()
        elif choice == "6":
            self._add_consecutive_overspend_rule()
        elif choice == "7":
            self._delete_rule()
        elif choice == "8":
            self.rule_manager.rules.clear()
            print("All rules cleared")
        else:
            print("Invalid choice")

    def _view_rules(self):
        """View all configured rules"""
        if not self.rule_manager.rules:
            print("\nNo rules configured.")
            return

        print("\nCurrent Budget Rules:")
        print("-" * 50)
        for i, rule in enumerate(self.rule_manager.rules, 1):
            print(f"\n{i}. {rule.__class__.__name__}")
            if hasattr(rule, "period"):
                print(f"   Period: {rule.period} days")
            if hasattr(rule, "threshold"):
                print(f"   Threshold: {rule.threshold}")
            print(f"   Alert: {rule.alert.__class__.__name__}")

    def _add_category_rule(self):
        """Add category budget rule"""
        print("\nAdd Category Budget Rule")
        print(
            "This rule alerts when spending in a category exceeds a limit over N days"
        )

        period = self._get_period_input()

        threshold = self._get_threshold_input()

        operator = self._get_operator_input()

        alert = self._get_alert_type()

        rule = CategoryBudgetRule(
            period=period,
            operator=operator,
            threshold=threshold,
            alert=alert,
        )

        self.rule_manager.add_rule(rule)
        print(f"Category budget rule added: ${threshold:.2f} over {period} days")

    def _add_single_transaction_rule(self):
        """Add single transaction rule"""
        print("\nAdd Single Transaction Rule")
        print("This rule alerts when a single expense exceeds a threshold")

        threshold = self._get_threshold_input()
        operator = self._get_operator_input()
        alert = self._get_alert_type()

        rule = SingleTransactionRule(
            period=1,
            operator=operator,
            threshold=threshold,
            alert=alert,
        )

        self.rule_manager.add_rule(rule)
        print(f"Single transaction rule added: > ${threshold:.2f}")

    def _add_percentage_rule(self):
        """Add percentage threshold rule"""
        print("\nAdd Percentage Threshold Rule")
        print("This rule alerts when a category exceeds a percentage of total spending")

        threshold = self._get_percentage_input()
        period = self._get_period_input()
        operator = self._get_operator_input()
        alert = self._get_alert_type()

        rule = PercentageThresholdRule(
            period=period,
            operator=operator,
            threshold=threshold,
            alert=alert,
        )

        self.rule_manager.add_rule(rule)
        print(f"Percentage rule added: > {threshold * 100:.0f}% over {period} days")

    def _add_uncategorized_rule(self):
        """Add uncategorized warning rule"""
        print("\nAdd Uncategorized Warning Rule")
        print("This rule alerts when an expense is marked as UNCATEGORIZED")

        alert = self._get_alert_type()

        rule = UncategorizedWarningRule(
            period=1,
            operator=RuleOperator.GT,
            threshold=0,
            alert=alert,
        )

        self.rule_manager.add_rule(rule)
        print("Uncategorized warning rule added")

    def _add_consecutive_overspend_rule(self):
        """Add consecutive overspend rule"""
        print("\nAdd Consecutive Overspend Rule")
        print("This rule alerts when you exceed a daily limit for N consecutive days")

        threshold = self._get_threshold_input()
        period = self._get_period_input()
        alert = self._get_alert_type()

        rule = ConsecutiveOverspendRule(
            period=period,
            operator=RuleOperator.GT,
            threshold=threshold,
            alert=alert,
        )

        self.rule_manager.add_rule(rule)
        print(f"Consecutive overspend rule added: > ${threshold:.2f} for {period} days")

    def _delete_rule(self):
        """Delete a rule"""
        if not self.rule_manager.rules:
            print("\nNo rules to delete.")
            return

        print("\nSelect rule to delete:")
        for i, rule in enumerate(self.rule_manager.rules, 1):
            print(f"{i}. {rule.__class__.__name__}")

        try:
            idx = int(input("Number: ")) - 1
            if 0 <= idx < len(self.rule_manager.rules):
                removed = self.rule_manager.rules.pop(idx)
                print(f"Deleted: {removed.__class__.__name__}")
            else:
                print("Invalid number")
        except ValueError:
            print("Invalid input")

    def _get_period_input(self) -> int:
        """Get period (number of days) from user"""
        while True:
            try:
                period = int(input("Period (number of days): "))
                if period > 0:
                    return period
                print("Period must be positive")
            except ValueError:
                print("Enter a valid number")

    def _get_threshold_input(self) -> float:
        """Get threshold amount from user"""
        while True:
            try:
                threshold = float(input("Threshold amount (HK$): "))
                if threshold > 0:
                    return threshold
                print("Threshold must be positive")
            except ValueError:
                print("Enter a valid number")

    def _get_percentage_input(self) -> float:
        """Get percentage threshold (0-1) from user"""
        while True:
            try:
                pct = float(input("Percentage (e.g., 0.3 for 30%): "))
                if 0 < pct <= 1:
                    return pct
                print("Enter a value between 0 and 1")
            except ValueError:
                print("Enter a valid number")

    def _get_operator_input(self) -> RuleOperator:
        """Get comparison operator from user"""
        print("\nOperators:")
        print("1. Greater than (>)")
        print("2. Greater than or equal (>=)")

        choice = input("Choose operator: ").strip()
        if choice == "1":
            return RuleOperator.GT
        else:
            return RuleOperator.GTE

    def _get_alert_type(self):
        """Get alert type from user"""
        print("\nAlert Types:")
        print("1. Console Alert (print to screen)")
        print("2. File Alert (save to file)")

        choice = input("Choose: ").strip()
        if choice == "2":
            return FileAlert()
        return ConsoleAlert()

    def _confirm_exit(self):
        """Save and exit"""
        save = input("\nSave before exit? (y/n): ").lower()
        if save == "y":
            self._save_data()

        print("\nThank you for using Budget Assistant!")
        return True
