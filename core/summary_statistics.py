"""
Crunches numbers on a list of transactions — totals, category breakdowns,
daily/weekly/monthly aggregations, and simple trend comparisons.
"""

from collections import defaultdict
from datetime import date, timedelta
from functools import cached_property
from typing import TypedDict

from data_model.schemas import Transaction, Expense, Income
from data_model.categories import ExpenseCategory, IncomeCategory

__all__ = ["SummaryStatistics", "SummaryReport"]


class SummaryReport(TypedDict):
    """Shape of the dict returned by SummaryStatistics.summary()."""

    total_spending: float
    total_income: float
    net_balance: float
    spending_by_category: dict[ExpenseCategory, float]
    income_by_category: dict[IncomeCategory, float]
    top_3_spending_categories: list[tuple[ExpenseCategory, float]]
    top_3_income_categories: list[tuple[IncomeCategory, float]]
    last_7_days_spending: dict[date, float]
    last_30_days_spending: dict[date, float]
    avg_daily_spending_7d: float
    avg_daily_spending_30d: float
    spending_change_7d_pct: float | None
    spending_change_30d_pct: float | None


class SummaryStatistics:
    """Takes a mixed list of Expense/Income transactions and exposes
    every stat you'd want on a personal finance dashboard.

    Category breakdowns are cached after the first call so we're not
    looping through everything repeatedly. Public getters hand back
    copies so nobody accidentally corrupts the cache.

    Usage::

        stats = SummaryStatistics(transactions)
        print(stats.total_spending)
        print(stats.net_balance)
        report = stats.summary()
    """

    def __init__(self, transactions: list[Transaction]) -> None:
        self._transactions = transactions
        # split once up front so we don't isinstance-check on every method call
        self._expenses: list[Expense] = [
            t for t in transactions if isinstance(t, Expense)
        ]
        self._incomes: list[Income] = [
            t for t in transactions if isinstance(t, Income)
        ]

    # Core Totals

    @property
    def total_spending(self) -> float:
        """Sum of every expense. Returns 0.0 if there aren't any."""
        return sum(e.amount for e in self._expenses)

    @property
    def total_income(self) -> float:
        """Sum of every income. Returns 0.0 if there aren't any."""
        return sum(i.amount for i in self._incomes)

    @property
    def net_balance(self) -> float:
        """Income minus spending. Positive = you're saving, negative = uh oh."""
        return self.total_income - self.total_spending

    # Per-Category Totals (cached)

    @cached_property
    def _cached_spending_by_category(self) -> dict[ExpenseCategory, float]:
        """Build the category→total mapping once, sorted biggest-first."""
        totals: defaultdict[ExpenseCategory, float] = defaultdict(float)
        for e in self._expenses:
            totals[e.category] += e.amount
        return dict(
            sorted(totals.items(), key=lambda item: item[1], reverse=True)
        )

    @cached_property
    def _cached_income_by_category(self) -> dict[IncomeCategory, float]:
        """Same idea but for income categories."""
        totals: defaultdict[IncomeCategory, float] = defaultdict(float)
        for i in self._incomes:
            totals[i.category] += i.amount
        return dict(
            sorted(totals.items(), key=lambda item: item[1], reverse=True)
        )

    def spending_by_category(self) -> dict[ExpenseCategory, float]:
        """Spending per category, highest first. Returns a copy so
        callers can't mess with our cache."""
        return dict(self._cached_spending_by_category)

    def income_by_category(self) -> dict[IncomeCategory, float]:
        """Income per category, highest first. Also a copy."""
        return dict(self._cached_income_by_category)

    # Top-N Categories

    def top_spending_categories(
        self, n: int = 3
    ) -> list[tuple[ExpenseCategory, float]]:
        """The n biggest expense categories. Might return fewer than n
        if there simply aren't that many categories."""
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        return list(self._cached_spending_by_category.items())[:n]

    def top_income_categories(
        self, n: int = 3
    ) -> list[tuple[IncomeCategory, float]]:
        """The n biggest income categories. Same deal as above."""
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        return list(self._cached_income_by_category.items())[:n]

    # Time-Based Totals

    def daily_spending(
        self,
        start: date | None = None,
        end: date | None = None,
    ) -> dict[date, float]:
        """Daily spending totals. If you give both start and end, days
        with no spending still show up as 0.0 — handy for charts.
        Both bounds are inclusive."""
        self._validate_date_range(start, end)
        filtered = self._filter_by_date(self._expenses, start, end)
        totals: defaultdict[date, float] = defaultdict(float)
        for e in filtered:
            totals[e.date] += e.amount
        if start is not None and end is not None:
            self._fill_missing_dates(totals, start, end)
        return dict(sorted(totals.items()))

    def daily_income(
        self,
        start: date | None = None,
        end: date | None = None,
    ) -> dict[date, float]:
        """Same as daily_spending but for income records."""
        self._validate_date_range(start, end)
        filtered = self._filter_by_date(self._incomes, start, end)
        totals: defaultdict[date, float] = defaultdict(float)
        for i in filtered:
            totals[i.date] += i.amount
        if start is not None and end is not None:
            self._fill_missing_dates(totals, start, end)
        return dict(sorted(totals.items()))

    def weekly_spending(self) -> dict[tuple[int, int], float]:
        """Spending grouped by ISO (year, week). Sorted chronologically."""
        totals: defaultdict[tuple[int, int], float] = defaultdict(float)
        for e in self._expenses:
            iso = e.date.isocalendar()
            totals[(iso.year, iso.week)] += e.amount
        return dict(sorted(totals.items()))

    def monthly_spending(self) -> dict[tuple[int, int], float]:
        """Spending grouped by (year, month). Sorted chronologically."""
        totals: defaultdict[tuple[int, int], float] = defaultdict(float)
        for e in self._expenses:
            totals[(e.date.year, e.date.month)] += e.amount
        return dict(sorted(totals.items()))

    def weekly_income(self) -> dict[tuple[int, int], float]:
        """Income grouped by ISO (year, week)."""
        totals: defaultdict[tuple[int, int], float] = defaultdict(float)
        for i in self._incomes:
            iso = i.date.isocalendar()
            totals[(iso.year, iso.week)] += i.amount
        return dict(sorted(totals.items()))

    def monthly_income(self) -> dict[tuple[int, int], float]:
        """Income grouped by (year, month)."""
        totals: defaultdict[tuple[int, int], float] = defaultdict(float)
        for i in self._incomes:
            totals[(i.date.year, i.date.month)] += i.amount
        return dict(sorted(totals.items()))

    # Spending Trends

    def spending_trend(
        self,
        days: int = 7,
        ref_date: date | None = None,
    ) -> dict[date, float]:
        """Daily spending for the last `days` days ending on ref_date.
        Defaults to today if ref_date isn't given."""
        self._validate_days(days)
        ref = ref_date or date.today()
        start = ref - timedelta(days=days - 1)
        return self.daily_spending(start=start, end=ref)

    def average_daily_spending(
        self,
        days: int = 30,
        ref_date: date | None = None,
    ) -> float:
        """Average daily spending over the window. We always divide by
        the full window size, not just the days that had spending —
        otherwise a single big purchase day would look misleadingly high."""
        self._validate_days(days)
        ref = ref_date or date.today()
        start = ref - timedelta(days=days - 1)
        filtered = self._filter_by_date(self._expenses, start, ref)
        total = sum(e.amount for e in filtered)
        return total / days

    def spending_change(
        self,
        days: int = 7,
        ref_date: date | None = None,
    ) -> float | None:
        """How much spending changed vs the previous window of the same
        length, as a percentage. Returns None if the previous window
        was zero (can't divide by zero)."""
        self._validate_days(days)

        ref = ref_date or date.today()
        current_start = ref - timedelta(days=days - 1)
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days - 1)

        current_total = sum(
            e.amount
            for e in self._filter_by_date(self._expenses, current_start, ref)
        )
        prev_total = sum(
            e.amount
            for e in self._filter_by_date(self._expenses, prev_start, prev_end)
        )

        if prev_total == 0.0:
            return None
        return ((current_total - prev_total) / prev_total) * 100.0

    # Full Summary Report

    def summary(self, ref_date: date | None = None) -> SummaryReport:
        """Everything in one dict — plug this straight into a dashboard
        or report template."""
        ref = ref_date or date.today()
        return SummaryReport(
            total_spending=self.total_spending,
            total_income=self.total_income,
            net_balance=self.net_balance,
            spending_by_category=self.spending_by_category(),
            income_by_category=self.income_by_category(),
            top_3_spending_categories=self.top_spending_categories(3),
            top_3_income_categories=self.top_income_categories(3),
            last_7_days_spending=self.spending_trend(7, ref),
            last_30_days_spending=self.spending_trend(30, ref),
            avg_daily_spending_7d=self.average_daily_spending(7, ref),
            avg_daily_spending_30d=self.average_daily_spending(30, ref),
            spending_change_7d_pct=self.spending_change(7, ref),
            spending_change_30d_pct=self.spending_change(30, ref),
        )

    # Private Helpers

    def _filter_by_date[T: Transaction](
        self,
        records: list[T],
        start: date | None = None,
        end: date | None = None,
    ) -> list[T]:
        """Keep only records that fall within [start, end]. Either bound
        can be None to leave that side open."""
        result = records
        if start is not None:
            result = [r for r in result if r.date >= start]
        if end is not None:
            result = [r for r in result if r.date <= end]
        return result

    @staticmethod
    def _fill_missing_dates(
        totals: defaultdict[date, float],
        start: date,
        end: date,
    ) -> None:
        """Plug in 0.0 for any dates in the range that don't have entries yet."""
        current = start
        while current <= end:
            totals.setdefault(current, 0.0)
            current += timedelta(days=1)

    @staticmethod
    def _validate_days(days: int) -> None:
        if days <= 0:
            raise ValueError(f"days must be positive, got {days}")

    @staticmethod
    def _validate_date_range(
        start: date | None,
        end: date | None,
    ) -> None:
        if start is not None and end is not None and start > end:
            raise ValueError(
                f"start ({start}) must not be after end ({end})"
            )
