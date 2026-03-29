import json
from data_model.Schemas import Expense, ExpenseCategory
from datetime import datetime

def load_expenses(filepath):
    expenses = []
    with open(filepath, 'r') as file:
        for line in file:
            data = json.loads(line.strip())
            date_obj = datetime.strptime(data['date'], "%Y-%m-%d").date()            
            expense = Expense(
                id=data['id'],
                date=date_obj,
                amount=data['amount'],
                category=ExpenseCategory[data['category'].upper()],
                description=data['description']
            )
            expenses.append(expense)
    return expenses
