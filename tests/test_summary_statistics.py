"""Tests for SummaryStatistics, covers every public method and property."""

import unittest
from datetime import date, timedelta

from data_model.schemas import Expense, Income
from data_model.categories import ExpenseCategory, IncomeCategory
from core.summary_statistics import SummaryStatistics


# Helpers


def _expense(
    id: str,
    d: date,
    amount: float,
    category: ExpenseCategory = ExpenseCategory.FOOD,
    description: str = "",
) -> Expense:
    return Expense(id, d, amount, category, description)


def _income(
    id: str,
    d: date,
    amount: float,
    category: IncomeCategory = IncomeCategory.SALARY,
    description: str = "",
) -> Income:
    return Income(id, d, amount, category, description)


# Core Totals


class TestCoreTotals(unittest.TestCase):

    def setUp(self) -> None:
        self.expenses = [
            _expense("e1", date(2026, 4, 1), 100.0, ExpenseCategory.FOOD),
            _expense("e2", date(2026, 4, 2), 50.0, ExpenseCategory.DRINKS),
            _expense("e3", date(2026, 4, 3), 200.0, ExpenseCategory.RENT),
        ]
        self.incomes = [
            _income("i1", date(2026, 4, 1), 3000.0, IncomeCategory.SALARY),
            _income("i2", date(2026, 4, 5), 500.0, IncomeCategory.FREELANCE),
        ]
        self.stats = SummaryStatistics(self.expenses + self.incomes)

    def test_total_spending(self):
        self.assertAlmostEqual(self.stats.total_spending, 350.0)

    def test_total_income(self):
        self.assertAlmostEqual(self.stats.total_income, 3500.0)

    def test_net_balance(self):
        # 3500 - 350 = 3150
        self.assertAlmostEqual(self.stats.net_balance, 3150.0)

    def test_no_expenses(self):
        stats = SummaryStatistics(self.incomes)
        self.assertAlmostEqual(stats.total_spending, 0.0)

    def test_no_incomes(self):
        stats = SummaryStatistics(self.expenses)
        self.assertAlmostEqual(stats.total_income, 0.0)

    def test_empty(self):
        stats = SummaryStatistics([])
        self.assertAlmostEqual(stats.total_spending, 0.0)
        self.assertAlmostEqual(stats.total_income, 0.0)
        self.assertAlmostEqual(stats.net_balance, 0.0)

    def test_negative_balance(self):
        # spending > income
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 5000.0, ExpenseCategory.RENT),
            _income("i1", date(2026, 4, 1), 1000.0),
        ])
        self.assertAlmostEqual(stats.net_balance, -4000.0)

    def test_zero_balance(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 500.0),
            _income("i1", date(2026, 4, 1), 500.0),
        ])
        self.assertAlmostEqual(stats.net_balance, 0.0)

    def test_single_expense(self):
        stats = SummaryStatistics([_expense("e1", date(2026, 4, 1), 42.0)])
        self.assertAlmostEqual(stats.total_spending, 42.0)
        self.assertAlmostEqual(stats.net_balance, -42.0)

    def test_single_income(self):
        stats = SummaryStatistics([_income("i1", date(2026, 4, 1), 99.0)])
        self.assertAlmostEqual(stats.total_income, 99.0)
        self.assertAlmostEqual(stats.net_balance, 99.0)


# Per-Category Totals


class TestPerCategoryTotals(unittest.TestCase):

    def setUp(self) -> None:
        self.transactions = [
            _expense("e1", date(2026, 4, 1), 100.0, ExpenseCategory.FOOD),
            _expense("e2", date(2026, 4, 2), 60.0, ExpenseCategory.FOOD),
            _expense("e3", date(2026, 4, 3), 200.0, ExpenseCategory.RENT),
            _expense("e4", date(2026, 4, 4), 30.0, ExpenseCategory.DRINKS),
            _income("i1", date(2026, 4, 1), 3000.0, IncomeCategory.SALARY),
            _income("i2", date(2026, 4, 5), 500.0, IncomeCategory.SALARY),
            _income("i3", date(2026, 4, 6), 200.0, IncomeCategory.FREELANCE),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_spending_values(self):
        result = self.stats.spending_by_category()
        self.assertAlmostEqual(result[ExpenseCategory.FOOD], 160.0)
        self.assertAlmostEqual(result[ExpenseCategory.RENT], 200.0)
        self.assertAlmostEqual(result[ExpenseCategory.DRINKS], 30.0)

    def test_spending_sorted_descending(self):
        values = list(self.stats.spending_by_category().values())
        self.assertEqual(values, sorted(values, reverse=True))

    def test_income_values(self):
        result = self.stats.income_by_category()
        self.assertAlmostEqual(result[IncomeCategory.SALARY], 3500.0)
        self.assertAlmostEqual(result[IncomeCategory.FREELANCE], 200.0)

    def test_income_sorted_descending(self):
        values = list(self.stats.income_by_category().values())
        self.assertEqual(values, sorted(values, reverse=True))

    def test_empty(self):
        stats = SummaryStatistics([])
        self.assertEqual(stats.spending_by_category(), {})
        self.assertEqual(stats.income_by_category(), {})

    def test_same_category_merges(self):
        # two FOOD expenses → one entry
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 50.0, ExpenseCategory.FOOD),
            _expense("e2", date(2026, 4, 2), 75.0, ExpenseCategory.FOOD),
        ])
        result = stats.spending_by_category()
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[ExpenseCategory.FOOD], 125.0)

    def test_spending_returns_copy(self):
        # mutating the copy must not affect the cache
        copy = self.stats.spending_by_category()
        copy[ExpenseCategory.FOOD] = 999.0
        self.assertAlmostEqual(
            self.stats.spending_by_category()[ExpenseCategory.FOOD], 160.0
        )

    def test_income_returns_copy(self):
        copy = self.stats.income_by_category()
        copy[IncomeCategory.SALARY] = 999.0
        self.assertAlmostEqual(
            self.stats.income_by_category()[IncomeCategory.SALARY], 3500.0
        )

    def test_only_incomes(self):
        stats = SummaryStatistics([_income("i1", date(2026, 4, 1), 1000.0)])
        self.assertEqual(stats.spending_by_category(), {})

    def test_only_expenses(self):
        stats = SummaryStatistics([_expense("e1", date(2026, 4, 1), 100.0)])
        self.assertEqual(stats.income_by_category(), {})


# Top-N Categories


class TestTopCategories(unittest.TestCase):

    def setUp(self) -> None:
        self.transactions = [
            _expense("e1", date(2026, 4, 1), 500.0, ExpenseCategory.RENT),
            _expense("e2", date(2026, 4, 2), 300.0, ExpenseCategory.FOOD),
            _expense("e3", date(2026, 4, 3), 150.0, ExpenseCategory.ENTERTAINMENT),
            _expense("e4", date(2026, 4, 4), 80.0, ExpenseCategory.DRINKS),
            _expense("e5", date(2026, 4, 5), 40.0, ExpenseCategory.TRAFFIC),
            _income("i1", date(2026, 4, 1), 3000.0, IncomeCategory.SALARY),
            _income("i2", date(2026, 4, 2), 500.0, IncomeCategory.FREELANCE),
            _income("i3", date(2026, 4, 3), 200.0, IncomeCategory.INVESTMENT),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_top_3_spending(self):
        result = self.stats.top_spending_categories(3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], (ExpenseCategory.RENT, 500.0))
        self.assertEqual(result[1], (ExpenseCategory.FOOD, 300.0))
        self.assertEqual(result[2], (ExpenseCategory.ENTERTAINMENT, 150.0))

    def test_top_1(self):
        result = self.stats.top_spending_categories(1)
        self.assertEqual(result[0][0], ExpenseCategory.RENT)

    def test_n_exceeds_available(self):
        # only 5 categories — asking for 100 returns all 5
        result = self.stats.top_spending_categories(100)
        self.assertEqual(len(result), 5)

    def test_top_0(self):
        self.assertEqual(self.stats.top_spending_categories(0), [])

    def test_empty(self):
        stats = SummaryStatistics([])
        self.assertEqual(stats.top_spending_categories(3), [])
        self.assertEqual(stats.top_income_categories(3), [])

    def test_negative_n_spending(self):
        with self.assertRaises(ValueError):
            self.stats.top_spending_categories(-1)

    def test_negative_n_income(self):
        with self.assertRaises(ValueError):
            self.stats.top_income_categories(-1)

    def test_top_2_income(self):
        result = self.stats.top_income_categories(2)
        self.assertEqual(result[0], (IncomeCategory.SALARY, 3000.0))
        self.assertEqual(result[1], (IncomeCategory.FREELANCE, 500.0))

    def test_income_n_exceeds_available(self):
        result = self.stats.top_income_categories(100)
        self.assertEqual(len(result), 3)


# Daily Spending


class TestDailySpending(unittest.TestCase):

    def setUp(self) -> None:
        # Apr 1 has two expenses (should sum), Apr 2 has none
        self.transactions = [
            _expense("e1", date(2026, 4, 1), 50.0, ExpenseCategory.FOOD),
            _expense("e2", date(2026, 4, 1), 30.0, ExpenseCategory.DRINKS),
            _expense("e3", date(2026, 4, 3), 100.0, ExpenseCategory.RENT),
            _expense("e4", date(2026, 4, 5), 25.0, ExpenseCategory.FOOD),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_no_bounds(self):
        # only days with spending appear
        result = self.stats.daily_spending()
        self.assertAlmostEqual(result[date(2026, 4, 1)], 80.0)
        self.assertNotIn(date(2026, 4, 2), result)

    def test_with_bounds_fills_zeros(self):
        # gap days become 0.0
        result = self.stats.daily_spending(
            start=date(2026, 4, 1), end=date(2026, 4, 5)
        )
        self.assertEqual(len(result), 5)
        self.assertAlmostEqual(result[date(2026, 4, 2)], 0.0)
        self.assertAlmostEqual(result[date(2026, 4, 4)], 0.0)

    def test_sorted(self):
        result = self.stats.daily_spending(
            start=date(2026, 4, 1), end=date(2026, 4, 5)
        )
        self.assertEqual(list(result.keys()), sorted(result.keys()))

    def test_start_only(self):
        result = self.stats.daily_spending(start=date(2026, 4, 3))
        self.assertNotIn(date(2026, 4, 1), result)
        self.assertIn(date(2026, 4, 3), result)

    def test_end_only(self):
        result = self.stats.daily_spending(end=date(2026, 4, 3))
        self.assertNotIn(date(2026, 4, 5), result)
        self.assertIn(date(2026, 4, 1), result)

    def test_empty(self):
        self.assertEqual(SummaryStatistics([]).daily_spending(), {})

    def test_same_day_aggregation(self):
        # 50 + 30 on Apr 1
        self.assertAlmostEqual(
            self.stats.daily_spending()[date(2026, 4, 1)], 80.0
        )

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            self.stats.daily_spending(
                start=date(2026, 4, 15), end=date(2026, 4, 1)
            )

    def test_single_day_range(self):
        result = self.stats.daily_spending(
            start=date(2026, 4, 1), end=date(2026, 4, 1)
        )
        self.assertEqual(len(result), 1)

    def test_range_outside_data(self):
        # no transactions in May → all zeros
        result = self.stats.daily_spending(
            start=date(2026, 5, 1), end=date(2026, 5, 3)
        )
        self.assertEqual(len(result), 3)
        self.assertTrue(all(v == 0.0 for v in result.values()))


# Daily Income


class TestDailyIncome(unittest.TestCase):

    def setUp(self) -> None:
        self.transactions = [
            _income("i1", date(2026, 4, 1), 1000.0, IncomeCategory.SALARY),
            _income("i2", date(2026, 4, 1), 200.0, IncomeCategory.FREELANCE),
            _income("i3", date(2026, 4, 3), 500.0, IncomeCategory.SALARY),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_no_bounds(self):
        result = self.stats.daily_income()
        self.assertAlmostEqual(result[date(2026, 4, 1)], 1200.0)
        self.assertNotIn(date(2026, 4, 2), result)

    def test_with_bounds_fills_zeros(self):
        result = self.stats.daily_income(
            start=date(2026, 4, 1), end=date(2026, 4, 3)
        )
        self.assertEqual(len(result), 3)
        self.assertAlmostEqual(result[date(2026, 4, 2)], 0.0)

    def test_empty(self):
        self.assertEqual(SummaryStatistics([]).daily_income(), {})

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            self.stats.daily_income(
                start=date(2026, 4, 10), end=date(2026, 4, 1)
            )

    def test_expenses_excluded(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 100.0),
            _income("i1", date(2026, 4, 1), 500.0),
        ])
        self.assertAlmostEqual(stats.daily_income()[date(2026, 4, 1)], 500.0)


# Weekly & Monthly Spending


class TestWeeklyAndMonthlySpending(unittest.TestCase):

    def setUp(self) -> None:
        self.transactions = [
            # Jan 5 & 6 → same ISO week
            _expense("e1", date(2026, 1, 5), 100.0, ExpenseCategory.FOOD),
            _expense("e2", date(2026, 1, 6), 50.0, ExpenseCategory.FOOD),
            _expense("e3", date(2026, 1, 15), 200.0, ExpenseCategory.RENT),
            _expense("e4", date(2026, 2, 10), 75.0, ExpenseCategory.DRINKS),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_weekly_grouping(self):
        result = self.stats.weekly_spending()
        iso_w = date(2026, 1, 5).isocalendar()
        self.assertIn((iso_w.year, iso_w.week), result)

    def test_weekly_same_week_sums(self):
        result = self.stats.weekly_spending()
        iso_w = date(2026, 1, 5).isocalendar()
        self.assertAlmostEqual(result[(iso_w.year, iso_w.week)], 150.0)

    def test_monthly_grouping(self):
        result = self.stats.monthly_spending()
        self.assertAlmostEqual(result[(2026, 1)], 350.0)
        self.assertAlmostEqual(result[(2026, 2)], 75.0)

    def test_monthly_sorted(self):
        keys = list(self.stats.monthly_spending().keys())
        self.assertEqual(keys, sorted(keys))

    def test_weekly_sorted(self):
        keys = list(self.stats.weekly_spending().keys())
        self.assertEqual(keys, sorted(keys))

    def test_empty(self):
        stats = SummaryStatistics([])
        self.assertEqual(stats.weekly_spending(), {})
        self.assertEqual(stats.monthly_spending(), {})


# Weekly & Monthly Income


class TestWeeklyAndMonthlyIncome(unittest.TestCase):

    def setUp(self) -> None:
        self.transactions = [
            _income("i1", date(2026, 1, 5), 2000.0, IncomeCategory.SALARY),
            _income("i2", date(2026, 1, 6), 300.0, IncomeCategory.FREELANCE),
            _income("i3", date(2026, 2, 10), 2000.0, IncomeCategory.SALARY),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_weekly_same_week_sums(self):
        result = self.stats.weekly_income()
        iso_w = date(2026, 1, 5).isocalendar()
        self.assertAlmostEqual(result[(iso_w.year, iso_w.week)], 2300.0)

    def test_monthly_grouping(self):
        result = self.stats.monthly_income()
        self.assertAlmostEqual(result[(2026, 1)], 2300.0)
        self.assertAlmostEqual(result[(2026, 2)], 2000.0)

    def test_monthly_sorted(self):
        keys = list(self.stats.monthly_income().keys())
        self.assertEqual(keys, sorted(keys))

    def test_empty(self):
        stats = SummaryStatistics([])
        self.assertEqual(stats.weekly_income(), {})
        self.assertEqual(stats.monthly_income(), {})

    def test_expenses_excluded(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 1, 5), 100.0),
            _income("i1", date(2026, 1, 5), 500.0),
        ])
        self.assertAlmostEqual(stats.monthly_income()[(2026, 1)], 500.0)


# Spending Trend


class TestSpendingTrend(unittest.TestCase):

    def setUp(self) -> None:
        self.ref = date(2026, 4, 9)
        self.transactions = [
            _expense("e1", date(2026, 4, 3), 10.0),
            _expense("e2", date(2026, 4, 5), 20.0),
            _expense("e3", date(2026, 4, 7), 30.0),
            _expense("e4", date(2026, 4, 9), 40.0),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_7_days_length(self):
        self.assertEqual(
            len(self.stats.spending_trend(days=7, ref_date=self.ref)), 7
        )

    def test_boundaries(self):
        result = self.stats.spending_trend(days=7, ref_date=self.ref)
        self.assertIn(self.ref - timedelta(days=6), result)  # start
        self.assertIn(self.ref, result)                       # end

    def test_values(self):
        result = self.stats.spending_trend(days=7, ref_date=self.ref)
        self.assertAlmostEqual(result[date(2026, 4, 3)], 10.0)
        self.assertAlmostEqual(result[date(2026, 4, 4)], 0.0)  # gap day
        self.assertAlmostEqual(result[date(2026, 4, 9)], 40.0)

    def test_30_days(self):
        self.assertEqual(
            len(self.stats.spending_trend(days=30, ref_date=self.ref)), 30
        )

    def test_1_day(self):
        result = self.stats.spending_trend(days=1, ref_date=self.ref)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[self.ref], 40.0)

    def test_invalid_days(self):
        with self.assertRaises(ValueError):
            self.stats.spending_trend(days=0)
        with self.assertRaises(ValueError):
            self.stats.spending_trend(days=-5)


# Average Daily Spending


class TestAverageDailySpending(unittest.TestCase):
    """Divides by full window size, not just days with spending."""

    def setUp(self) -> None:
        self.ref = date(2026, 4, 9)
        # 70 + 30 + 50 = 150 total
        self.transactions = [
            _expense("e1", date(2026, 4, 7), 70.0),
            _expense("e2", date(2026, 4, 8), 30.0),
            _expense("e3", date(2026, 4, 9), 50.0),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_7_day_window(self):
        # 150 / 7
        self.assertAlmostEqual(
            self.stats.average_daily_spending(days=7, ref_date=self.ref),
            150.0 / 7,
        )

    def test_3_day_window(self):
        # 150 / 3
        self.assertAlmostEqual(
            self.stats.average_daily_spending(days=3, ref_date=self.ref), 50.0
        )

    def test_empty(self):
        stats = SummaryStatistics([])
        self.assertAlmostEqual(
            stats.average_daily_spending(days=7, ref_date=self.ref), 0.0
        )

    def test_1_day(self):
        self.assertAlmostEqual(
            self.stats.average_daily_spending(days=1, ref_date=self.ref), 50.0
        )

    def test_invalid_days(self):
        with self.assertRaises(ValueError):
            self.stats.average_daily_spending(days=0, ref_date=self.ref)
        with self.assertRaises(ValueError):
            self.stats.average_daily_spending(days=-3, ref_date=self.ref)


# Spending Change


class TestSpendingChange(unittest.TestCase):
    """Compares current vs previous window of the same length"""

    def setUp(self) -> None:
        self.ref = date(2026, 4, 14)

    def test_positive(self):
        # prev 100, curr 200 → +100%
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 2), 60.0),
            _expense("e2", date(2026, 4, 5), 40.0),
            _expense("e3", date(2026, 4, 10), 120.0),
            _expense("e4", date(2026, 4, 13), 80.0),
        ])
        self.assertAlmostEqual(
            stats.spending_change(days=7, ref_date=self.ref), 100.0
        )

    def test_negative(self):
        # prev 200, curr 50 → -75%
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 2), 200.0, ExpenseCategory.RENT),
            _expense("e2", date(2026, 4, 10), 50.0),
        ])
        self.assertAlmostEqual(
            stats.spending_change(days=7, ref_date=self.ref), -75.0
        )

    def test_no_change(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 3), 100.0),
            _expense("e2", date(2026, 4, 10), 100.0),
        ])
        self.assertAlmostEqual(
            stats.spending_change(days=7, ref_date=self.ref), 0.0
        )

    def test_prev_zero_returns_none(self):
        # can't divide by zero
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 10), 100.0),
        ])
        self.assertIsNone(stats.spending_change(days=7, ref_date=self.ref))

    def test_both_zero_returns_none(self):
        stats = SummaryStatistics([])
        self.assertIsNone(stats.spending_change(days=7, ref_date=self.ref))

    def test_invalid_days(self):
        stats = SummaryStatistics([])
        with self.assertRaises(ValueError):
            stats.spending_change(days=0, ref_date=self.ref)
        with self.assertRaises(ValueError):
            stats.spending_change(days=-1, ref_date=self.ref)


# Summary Report


class TestSummaryReport(unittest.TestCase):

    def setUp(self) -> None:
        self.ref = date(2026, 4, 9)
        self.transactions = [
            _expense("e1", date(2026, 4, 1), 100.0, ExpenseCategory.FOOD),
            _expense("e2", date(2026, 4, 5), 200.0, ExpenseCategory.RENT),
            _income("i1", date(2026, 4, 1), 3000.0, IncomeCategory.SALARY),
        ]
        self.stats = SummaryStatistics(self.transactions)

    def test_all_keys_present(self):
        expected = {
            "total_spending", "total_income", "net_balance",
            "spending_by_category", "income_by_category",
            "top_3_spending_categories", "top_3_income_categories",
            "last_7_days_spending", "last_30_days_spending",
            "avg_daily_spending_7d", "avg_daily_spending_30d",
            "spending_change_7d_pct", "spending_change_30d_pct",
            "weekly_spending", "monthly_spending",
        }
        self.assertEqual(set(self.stats.summary(ref_date=self.ref).keys()), expected)

    def test_totals(self):
        r = self.stats.summary(ref_date=self.ref)
        self.assertAlmostEqual(r["total_spending"], 300.0)
        self.assertAlmostEqual(r["total_income"], 3000.0)
        self.assertAlmostEqual(r["net_balance"], 2700.0)

    def test_trend_lengths(self):
        r = self.stats.summary(ref_date=self.ref)
        self.assertEqual(len(r["last_7_days_spending"]), 7)
        self.assertEqual(len(r["last_30_days_spending"]), 30)

    def test_top_3_max_length(self):
        r = self.stats.summary(ref_date=self.ref)
        self.assertLessEqual(len(r["top_3_spending_categories"]), 3)
        self.assertLessEqual(len(r["top_3_income_categories"]), 3)

    def test_empty(self):
        r = SummaryStatistics([]).summary(ref_date=self.ref)
        self.assertAlmostEqual(r["total_spending"], 0.0)
        self.assertAlmostEqual(r["total_income"], 0.0)
        self.assertAlmostEqual(r["net_balance"], 0.0)
        self.assertEqual(r["top_3_spending_categories"], [])
        self.assertEqual(r["top_3_income_categories"], [])

    def test_change_types(self):
        r = self.stats.summary(ref_date=self.ref)
        self.assertIsInstance(r["spending_change_7d_pct"], (float, type(None)))
        self.assertIsInstance(r["spending_change_30d_pct"], (float, type(None)))


# Float Precision


class TestFloatPrecision(unittest.TestCase):

    def test_small_amounts(self):
        # 0.01 + 0.02 + 0.03 ≈ 0.06
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 0.01, ExpenseCategory.FOOD),
            _expense("e2", date(2026, 4, 1), 0.02, ExpenseCategory.FOOD),
            _expense("e3", date(2026, 4, 1), 0.03, ExpenseCategory.FOOD),
        ])
        self.assertAlmostEqual(stats.total_spending, 0.06)

    def test_large_amounts(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 999999.99, ExpenseCategory.RENT),
            _income("i1", date(2026, 4, 1), 1000000.01, IncomeCategory.SALARY),
        ])
        self.assertAlmostEqual(stats.net_balance, 0.02, places=2)

    def test_many_small_amounts(self):
        # 100 × 0.1 ≈ 10.0
        transactions = [
            _expense(f"e{i}", date(2026, 4, 1), 0.1) for i in range(100)
        ]
        stats = SummaryStatistics(transactions)
        self.assertAlmostEqual(stats.total_spending, 10.0, places=5)


# Type Isolation


class TestTypeIsolation(unittest.TestCase):
    """Expenses and incomes must never leak into each other's stats"""

    def test_expense_not_in_income_category(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 100.0, ExpenseCategory.FOOD),
            _income("i1", date(2026, 4, 1), 200.0),
        ])
        self.assertNotIn(ExpenseCategory.FOOD, stats.income_by_category())

    def test_income_only_no_spending(self):
        stats = SummaryStatistics([_income("i1", date(2026, 4, 1), 5000.0)])
        self.assertAlmostEqual(stats.total_spending, 0.0)
        self.assertEqual(stats.spending_by_category(), {})
        self.assertEqual(stats.top_spending_categories(3), [])

    def test_daily_spending_excludes_income(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 50.0),
            _income("i1", date(2026, 4, 1), 3000.0),
        ])
        self.assertAlmostEqual(stats.daily_spending()[date(2026, 4, 1)], 50.0)

    def test_daily_income_excludes_expense(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 50.0),
            _income("i1", date(2026, 4, 1), 3000.0),
        ])
        self.assertAlmostEqual(stats.daily_income()[date(2026, 4, 1)], 3000.0)

    def test_weekly_income_excludes_expense(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 100.0),
            _income("i1", date(2026, 4, 1), 500.0),
        ])
        iso = date(2026, 4, 1).isocalendar()
        self.assertAlmostEqual(
            stats.weekly_income()[(iso.year, iso.week)], 500.0
        )

    def test_monthly_spending_excludes_income(self):
        stats = SummaryStatistics([
            _expense("e1", date(2026, 4, 1), 100.0),
            _income("i1", date(2026, 4, 1), 5000.0),
        ])
        self.assertAlmostEqual(stats.monthly_spending()[(2026, 4)], 100.0)


if __name__ == "__main__":
    unittest.main()
