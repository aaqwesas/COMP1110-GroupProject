# Running case studies


you can run case by the following command

```bash
python main.py < case_studies/case_number.txt
```

> Make sure you are in the parent directory, not in the case_studies directory

# Case Study 1

case study 1 intend to trigger a normal alert when the expense exceed a certain amount, this is the minimal functionality that a user would expect when they are making their expenses

procedure:
  - add a Signle Transaction Rule
  - decide the threshold for the amount
  - Choose an alert
  - add an expense that exceed the threshold
  - alert is shown

# Case Study 2

case study 2 will try to spot if a user is spending too much on a particular category, also testing the period and threshold, this is intend to catch user who overspend on a particular category within a fixed period of time. (like a lot of subscriptions)

procedure:
  - add a Category Rule Q
  - adding an expense X on category A
  - adding another expense Y on category A that will trigger an alert
  - adding an expense Z on category B, testing if it will trigger Q alert
  - adding an expense K, where K are outside the period for A, and K + X > threshold, and test if it trigger the alert
  - show summary statistics
  - save the rule and transcations


# Case Study 3

this 
