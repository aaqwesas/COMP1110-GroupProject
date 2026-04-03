from data_model.rules import BudgetRule
from data_model.schemas import Transaction


class RuleManager:
    def __init__(self):
        self.rules: list[BudgetRule] = []

    def add_rule(self, rule: BudgetRule):
        self.rules.append(rule)

    def process_transaction(self, transaction: Transaction):
        for rule in self.rules:
            rule.evaluate(transaction)
