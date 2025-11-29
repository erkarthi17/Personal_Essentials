import pandas as pd
import sys

try:
    # Test Excel reading
    df = pd.read_excel('Master_Sheet_Expenses.xlsx')
    print('✅ Excel file loaded successfully')
    print(f'   - Rows: {len(df)}')
    print(f'   - Columns: {len(df.columns)}')
    
    # Check for required columns
    required = ['Name', 'Monthly Income', 'Expense Category', 'Expense SubCategory', 'Expected', 'Actuals']
    missing = [c for c in required if c not in df.columns]
    
    if missing:
        print(f'❌ Missing columns: {missing}')
        sys.exit(1)
    else:
        print('✅ All required columns present')
    
    # Check individuals
    individuals = df[df['Name'].notna()]['Name'].unique()
    print(f'✅ Individuals found: {list(individuals)}')
    
    # Check categories
    categories = df[df['Expense Category'].notna()]['Expense Category'].unique()
    print(f'✅ Categories found: {len(categories)} unique categories')
    
    print('\n✅ All checks passed! App is ready to run.')
    print('\n🚀 Start the app with: streamlit run expense_tracker.py')
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
