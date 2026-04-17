from datetime import timedelta
from data_model.rules import BudgetRule
from data_model.schemas import Transaction

class RuleManager:
    def __init__(self):
        self.rules: list[BudgetRule] = []

    def add_rule(self, rule: BudgetRule):
        self.rules.append(rule)

    def process_transaction(self, transaction: Transaction, history: list[Transaction]):
        periods = [rule.period for rule in self.rules if rule.period is not None]

        if periods:
            max_period = max(periods)
            cutoff_date = transaction.date - timedelta(days=max_period)

            recent_history = [
                t for t in history
                if cutoff_date <= t.date <= transaction.date
            ]
        else:
            recent_history = []

        for rule in self.rules:
            rule.evaluate(transaction=transaction, history=recent_history)