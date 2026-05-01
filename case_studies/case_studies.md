# Budget Alert System - Test Case Studies

## Running case studies

you can run case by the following command

```bash
python main.py < case_studies/{number}.txt
```

> Make sure you are in the parent directory, not in the case_studies directory

## Case Study 1: Single Transaction Threshold Alert

**Objective:** Validate the core functionality of single transaction budget rules, ensuring users receive alerts when individual expenses exceed predefined thresholds.

**Scope:** This test case verifies the minimal expected behavior of the budget alert system.

**Test Procedure:**

1. **Rule Configuration**
   - Create a Single Transaction Rule
   - Define the monetary threshold for triggering alerts
   - Select the appropriate alert delivery mechanism

2. **Test Execution**
   - Add an expense transaction that exceeds the configured threshold

3. **Expected Outcome**
   - System successfully triggers and displays the alert notification

**Success Criteria:** Alert is generated and presented to the user upon exceeding the threshold.

---

## Case Study 2: Category-Based Periodic Spending Analysis

**Objective:** Detect excessive spending patterns within specific expense categories over defined time periods, particularly useful for identifying subscription overuse or category-specific budget violations.

**Scope:** This test case evaluates the system's ability to aggregate category expenses across time windows and apply threshold-based alerting logic.

**Test Procedure:**

1. **Initial Setup**
   - Configure a Category Budget Rule with defined:
     - Target expense category (Category A)
     - Monitoring time period (e.g., days, weeks, months)
     - Spending threshold for the period

2. **Baseline Establishment**
   - Add initial expense (X) to Category A
   - Verify no alert is triggered (baseline within threshold)

3. **Threshold Exceedance Testing**
   - Add secondary expense (Y) to Category A
   - Confirm cumulative amount (X + Y) exceeds threshold
   - Validate alert is triggered

4. **Cross-Category Validation**
   - Add expense (Z) to Category B (different category)
   - Verify no alert is triggered for Category A rule

5. **Time Period Boundary Testing**
   - Add expense (K) to Category A where:
     - Transaction date falls outside the defined monitoring period
     - Cumulative amount with historical expenses (K + X) exceeds threshold
   - Validate that out-of-period transactions do not trigger alerts

6. **Reporting**
   - Generate and display summary statistics for all test transactions

**Success Criteria:**
- Alert triggers only when cumulative category spending exceeds threshold within the defined period
- Cross-category and out-of-period transactions do not generate false positives
- System correctly aggregates expenses within the time window

---

## Case Study 3: Bulk Data Import and Validation

**Objective:** Verify the system's ability to import and process pre-configured budget rules, expense transactions, and income records from external data files, ensuring accurate data loading for advanced users.

**Target Audience:** Technical users who require automated configuration through file-based imports.

**Test Data Location:** `/data` directory containing:
- `expenses.jsonl` - Historical expense transactions (JSON Lines format)
- `incomes.jsonl` - Income records (JSON Lines format)
- `rules.json` - Budget rule configurations (JSON format)

**Test Procedure:**

1. **Data Import**
   - Load all three data files into the system
   - Parse JSONL format for transactions and JSON for rules

2. **Validation**
   - Verify correct parsing of all records:
     - Expense entries with proper category mapping
     - Income records with appropriate classification
     - Rule configurations with correct operators, thresholds, and periods

3. **Reporting**
   - Generate comprehensive summary statistics including:
     - Total number of expenses loaded
     - Total number of income records loaded
     - Number of rules successfully parsed
     - Category distribution summary (optional)
     - Date range coverage (optional)

**Success Criteria:**
- All records from all three files are correctly loaded and parsed
- No data loss or parsing errors
- Summary statistics accurately reflect the imported data
- System ready for rule evaluation with imported data

---

## Appendix: Test Data Format Specifications

### expenses.jsonl Format
```json
{"id": "string", "date": "YYYY-MM-DD", "amount": float, "category": "string", "description": "string"}