import json
from datetime import datetime
from data_model.Schemas import Expense, ExpenseCategory

def load_expenses(filepath):
    expenses =[]
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue                   
                try:
                    data = json.loads(line)
                    date_obj = datetime.strptime(data['date'], "%Y-%m-%d").date()                    
                    raw_category = data['category'].upper()
                    try:
                        category_enum = ExpenseCategory[raw_category]
                    except:
                        category_enum = ExpenseCategory.UNCATEGORIZED
                    expense = Expense(
                        id=data['id'],
                        date=date_obj,
                        amount=float(data['amount']),
                        category=category_enum,
                        description=data['description']
                    )
                    expenses.append(expense)                    
                except:
                    print("Error reading a line in the file.")                    
    except FileNotFoundError:
        print("File not found. Starting with an empty list.")            
    print("Successfully loaded", len(expenses), "expenses.")
    return expenses

def save_expenses(filepath, expenses):
    try:
        with open(filepath, 'w') as file:
            for exp in expenses:
                exp_dict = {
                    "id": exp.id,
                    "date": str(exp.date),
                    "amount": float(exp.amount),
                    "category": exp.category.name.lower(),
                    "description": exp.description
                }                
                file.write(json.dumps(exp_dict) + "\n")                
        print("Saved", len(expenses), "expenses.")        
    except:
        print("Error saving file.")
