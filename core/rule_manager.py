from datetime import timedelta
from data_model.rules import BudgetRule
from data_model.schemas import Transaction

class RuleManager:
    def __init__(self):
        self.rules: list[BudgetRule] = []

    def add_rule(self, rule: BudgetRule) -> bool:
        try:
            rule.validate()
            self.rules.append(rule)
            return True
        except ValueError as e:
            print(f"Warning: Rejected invalid rule configuration '{rule.__class__.__name__}': {e}")
            return False

    def process_transaction(self, transaction: Transaction, history: list[Transaction]):
        periods = [rule.period for rule in self.rules if rule.period is not None]

        recent_history = []
        if periods:
            max_period = max(periods)
            cutoff_date = transaction.date - timedelta(days=max_period)

            recent_history = [
                t for t in history
                if cutoff_date <= t.date <= transaction.date
            ]

        for rule in self.rules:
            rule.evaluate(transaction=transaction, history=recent_history)