# 💰 Monthly Expense Tracker

A modern, user-friendly web application built with Streamlit for managing personal and family expenses. The app reads from and saves to an Excel master sheet, allowing dynamic management of expenses, income, and financial insights.

---

## ✨ Features

### 📝 Manage Expenses
- **Dynamic dropdowns** for Categories and Subcategories (loaded from Excel)
- **Auto-retrieve values** - When you select a category/subcategory, current Expected and Actual values are auto-populated
- **Update Expected & Actual** - Modify both values through the web GUI
- **Real-time Excel sync** - All changes are immediately saved to `Master_Sheet_Expenses.xlsx`
- **Expense summary table** - View all expenses with variance calculations

### 👥 Individual Income Management
- **Manage multiple individuals** - Select any person from the master sheet
- **Update monthly income** - Set or modify income for each person
- **View income summary** - See all individuals' income at a glance
- **Real-time sync** - Changes saved instantly to Excel

### 📊 Dashboard
- **Key metrics** - Total Expected, Total Actual, Variance, Overspent items count
- **Category comparison charts** - Visual representation of Expected vs Actual by category
- **Variance analysis** - See which categories are over/under budget
- **Color-coded charts** - Red for overspending, Green for under budget

### 📈 Analysis & Insights
- **Top overspent items** - Identify where you're spending the most above budget
- **Under budget items** - See where you've saved money
- **Category breakdown** - Understand budget distribution by category
- **Budget utilization** - Track overall spending vs budget percentage

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Excel file: `Master_Sheet_Expenses.xlsx`

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
streamlit run expense_tracker.py
```

3. **Open in browser:**
The app will automatically open at `http://localhost:8501`

---

## 📋 Excel File Structure

The app expects `Master_Sheet_Expenses.xlsx` with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| **Name** | Individual name | "Karthick Kannan", "Pooja", "Sai" |
| **Monthly Income** | Monthly income for that person | 5000.00 |
| **Expense Category** | High-level category | "Living Expenses", "Loans and Debt", "Utilities" |
| **Expense SubCategory** | Specific expense type | "Home Rent", "Water Bill", "Electricity" |
| **Expected** | Budgeted amount | 750.00 |
| **Actuals** | Actual spending amount | 755.50 |

### Example Structure:
```
Name              | Monthly Income | Expense Category  | Expense SubCategory | Expected | Actuals
Karthick Kannan   | 5000           | Living Expenses   | Home Rent          | 750      | 750
Pooja             | 3500           | Living Expenses   | Groceries          | 300      | 325
(blank)           | (blank)        | Utilities         | Wi-Fi              | 33.61    | 35.00
```

---

## 🎯 Usage Guide

### Tab 1: 📝 Manage Expenses

1. **Select a category** from the dropdown
2. **Select a subcategory** - Values auto-populate from Excel
3. **Current values displayed** - Shows what's currently in the spreadsheet
4. **Update amounts** - Modify Expected and Actual values
5. **Click "Save Changes"** - Data updates in Excel instantly
6. **View summary table** - See all expenses at a glance

### Tab 2: 👥 Individual Income

1. **Select an individual** from dropdown
2. **Current income displayed** - Shows current value from Excel
3. **Enter new income** - Input the updated amount
4. **Click "Update Income"** - Saved to Excel immediately
5. **View summary** - See all individuals' incomes

### Tab 3: 📊 Dashboard

- View key metrics at the top
- See visual charts comparing Expected vs Actual
- Analyze variance by category
- Identify budget issues

### Tab 4: 📈 Analysis

- Find top overspent items
- See under budget categories
- View category distribution
- Check overall budget utilization percentage

---

## 🔄 Data Flow

```
Excel File (Master_Sheet_Expenses.xlsx)
         ↓
    Streamlit App
    ↙ (Read) ↘ (Write)
Dropdowns     Update Form
             ↓
         Excel File (Updated)
```

### When you make changes:
1. Fill in the form with new values
2. Click "Save Changes" or "Update Income"
3. ✅ Data is instantly written to Excel
4. Dashboard updates automatically
5. Session state syncs with file

---

## 💡 Tips & Best Practices

### Keeping Excel Organized
- Keep individual names in the first few rows
- Use consistent category names
- Keep subcategory names descriptive
- Update values regularly for accurate insights

### Budget Management
- Review **Analysis tab** weekly
- Use **Dashboard** to spot overspending early
- Update **Actuals** as expenses occur
- Monitor **Budget Utilization %** closely

### Multi-User Usage
- The app reads/writes to the same Excel file
- Each user sees the same data
- Changes by one user are visible to others after refresh
- Consider version control for the Excel file

---

## 📊 Example Workflow

**Scenario:** Monthly expense tracking for a family

1. **Start of month** - Set Expected values based on budget
2. **Throughout month** - As expenses occur, update Actuals in the app
3. **Mid-month review** - Check Dashboard for overspending
4. **Adjust if needed** - Update Expected values if circumstances change
5. **End of month** - Run Analysis to understand spending patterns
6. **Plan next month** - Use insights to adjust next month's budget

---

## 🛠️ Troubleshooting

### App won't start
- Ensure Excel file `Master_Sheet_Expenses.xlsx` exists in the app folder
- Check Python version: `python --version` (should be 3.7+)
- Verify dependencies: `pip install -r requirements.txt`

### Changes not saving
- Confirm Excel file is not open in another program
- Check file permissions in the app folder
- Verify `openpyxl` is installed: `pip install openpyxl`

### No categories appear in dropdown
- Check Excel file has data in "Expense Category" column
- Ensure cells aren't empty or contain only spaces
- Verify sheet name is "Sheet1"

### Auto-populate not working
- Verify category and subcategory exist in Excel
- Check spelling matches exactly (case-sensitive category names)
- Ensure values are in the correct columns

---

## 📝 Requirements

```
streamlit                    # Web app framework
pandas>=2.0                  # Data manipulation
matplotlib                   # Charting
openpyxl                     # Excel file handling
pyarrow>=13.0                # Arrow format support
```

Install all: `pip install -r requirements.txt`

---

## 📄 File Structure

```
expense_app/
├── expense_tracker.py              # Main application
├── Master_Sheet_Expenses.xlsx       # Data source (your Excel file)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🎨 Features Highlight

| Feature | Benefit |
|---------|---------|
| 📌 **Auto-populate values** | No manual data entry when updating |
| 💾 **Instant Excel sync** | Always up-to-date Excel file |
| 👥 **Multi-individual support** | Track family/team finances |
| 📊 **Visual analytics** | Understand spending at a glance |
| 🎯 **Budget tracking** | Know exactly where you stand |
| 📈 **Trend analysis** | Make informed financial decisions |

---

## 🔒 Data Safety

- All data stored in Excel file (yours to keep)
- No cloud storage or external servers
- No login required
- Local file-based persistence

---

## 📞 Support & Feedback

- **Issue found?** Check the troubleshooting section
- **Want a feature?** Feel free to suggest improvements
- **Data backup?** Always keep backups of your Excel file

---

## 📜 License

This project is open for personal and family use.

---

**Happy tracking! 💰📊**
