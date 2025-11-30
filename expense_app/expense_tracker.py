import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ====================================
# Configuration
# ====================================
EXCEL_FILE = "Master_Sheet_Expenses.xlsx"
# How many timestamped backups to keep when saving the Excel file
BACKUP_RETENTION = 5

# ====================================
# Initialize Session State & Load Data
# ====================================
def load_excel_data():
    """Load data from Excel file (always read fresh to avoid stale cache)"""
    abs_path = os.path.abspath(EXCEL_FILE)
    if not os.path.exists(abs_path):
        st.error(f"Excel file '{abs_path}' not found!")
        return None
    try:
        return pd.read_excel(abs_path, sheet_name='Sheet1', engine='openpyxl')
    except Exception as e:
        st.error(f"Failed to read Excel file '{abs_path}': {e}")
        return None

def save_excel_data(df):
    """Atomically save DataFrame to Excel with a backup. Returns (success, message).

    - Writes to a temporary file in the same directory then replaces the original to avoid partial writes.
    - Creates a timestamped backup of the existing file before replacing.
    - Returns (True, info_message) on success, (False, error_message) on failure.
    """
    abs_path = os.path.abspath(EXCEL_FILE)
    dir_name = os.path.dirname(abs_path) or '.'
    try:
        # Ensure directory exists
        os.makedirs(dir_name, exist_ok=True)

        # If the target exists, create a timestamped backup
        backup_path = None
        if os.path.exists(abs_path):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{abs_path}.bak.{ts}"
            try:
                import shutil
                shutil.copy2(abs_path, backup_path)
            except Exception as be:
                # Continue even if backup fails, but report it
                return False, f"Failed to create backup '{backup_path}': {be}"
            # Purge old backups beyond retention
            try:
                import glob
                # Pattern for backups: <abs_path>.bak.*
                pattern = f"{abs_path}.bak.*"
                backups = glob.glob(pattern)
                if len(backups) > BACKUP_RETENTION:
                    # sort by modification time (oldest first)
                    backups_sorted = sorted(backups, key=lambda p: os.path.getmtime(p))
                    num_to_delete = len(backups_sorted) - BACKUP_RETENTION
                    for old in backups_sorted[:num_to_delete]:
                        try:
                            os.remove(old)
                        except Exception:
                            pass
            except Exception:
                # If purge fails, ignore — not critical
                pass

        # Write to a temporary file then atomically replace
        import tempfile
        fd, tmp_path = tempfile.mkstemp(prefix='tmp_expense_', suffix='.xlsx', dir=dir_name)
        os.close(fd)
        try:
            # Use pandas to write to the temporary file
            df.to_excel(tmp_path, sheet_name='Sheet1', index=False, engine='openpyxl')
            # Atomically replace the target
            os.replace(tmp_path, abs_path)
        except Exception as we:
            # Clean up temp file
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            return False, str(we)

        info = f"Wrote '{abs_path}'"
        if backup_path:
            info += f" (backup: '{backup_path}')"
        return True, info
    except Exception as e:
        return False, str(e)

def get_individuals():
    """Get list of individuals from the Excel file"""
    df = st.session_state.df
    individuals = df[df['Name'].notna()]['Name'].unique().tolist()
    return [i for i in individuals if pd.notna(i) and i != '']

def get_categories():
    """Get unique expense categories"""
    df = st.session_state.df
    categories = df[df['Expense Category'].notna()]['Expense Category'].unique().tolist()
    return sorted([c for c in categories if pd.notna(c) and c != ''])

def get_subcategories(category):
    """Get subcategories for a given category"""
    df = st.session_state.df
    subcats = df[df['Expense Category'] == category]['Expense SubCategory'].unique().tolist()
    return sorted([s for s in subcats if pd.notna(s) and s != ''])

def get_expected_value(category, subcategory):
    """Get expected value for a category/subcategory pair"""
    df = st.session_state.df
    match = df[(df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)]
    if not match.empty:
        val = match.iloc[0]['Expected']
        return float(val) if pd.notna(val) else 0.0
    return 0.0

def get_actual_value(category, subcategory):
    """Get actual value for a category/subcategory pair"""
    df = st.session_state.df
    match = df[(df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)]
    if not match.empty:
        val = match.iloc[0]['Actuals']
        return float(val) if pd.notna(val) else 0.0
    return 0.0

def update_expected_value(category, subcategory, value):
    """Update expected value"""
    df = st.session_state.df
    mask = (df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)
    if mask.any():
        df.loc[mask, 'Expected'] = value
        st.session_state.df = df
        success, err = save_excel_data(df)
        if not success:
            st.error(f"Failed to save Expected value: {err}")
            return False
        return True
    return False

def update_actual_value(category, subcategory, value):
    """Update actual value"""
    df = st.session_state.df
    mask = (df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)
    if mask.any():
        df.loc[mask, 'Actuals'] = value
        st.session_state.df = df
        success, err = save_excel_data(df)
        if not success:
            st.error(f"Failed to save Actual value: {err}")
            return False
        return True
    return False

def update_monthly_income(individual, income):
    """Update monthly income for an individual"""
    df = st.session_state.df
    mask = df['Name'] == individual
    if mask.any():
        df.loc[mask, 'Monthly Income'] = income
        st.session_state.df = df
        success, err = save_excel_data(df)
        if not success:
            st.error(f"Failed to save Monthly Income: {err}")
            return False
        return True
    return False

def reset_monthly():
    """Reset dynamic monthly fields across the sheet.

    This will zero 'Actuals', clear 'Payment Date', and set 'Paid' to False for all expense rows.
    It intentionally does NOT change 'Expected' or 'Monthly Income'.
    """
    df = st.session_state.df.copy()
    # Identify expense rows
    mask = (
        (df['Expense Category'].notna()) &
        (df['Expense SubCategory'].notna()) &
        (df['Expense Category'] != '') &
        (df['Expense SubCategory'] != '')
    )
    if mask.any():
        df.loc[mask, 'Actuals'] = 0
        df.loc[mask, 'Payment Date'] = pd.NaT
        df.loc[mask, 'Paid'] = False
        st.session_state.df = df
        success, msg = save_excel_data(df)
        return success, msg
    return False, "No expense rows to reset"

def get_total_income():
    """Calculate total monthly income from all individuals"""
    df = st.session_state.df
    individuals = df[df['Name'].notna()]['Name'].unique()
    total = 0.0
    for individual in individuals:
        income_row = df[df['Name'] == individual]['Monthly Income'].iloc[0]
        if pd.notna(income_row):
            total += float(income_row)
    return total

def get_total_expenses():
    """Calculate total actual expenses, excluding open dues.

    Open due: row has a Due Date in the future and Paid is False (or missing/False).
    This returns the sum of the 'Actuals' column for all non-open-due expense rows.
    """
    df = st.session_state.df
    expenses_df = df[
        (df['Expense Category'].notna()) & 
        (df['Expense SubCategory'].notna()) &
        (df['Expense Category'] != '') & 
        (df['Expense SubCategory'] != '')
    ]
    # Exclude amounts tagged against an open due from total expenses
    today = pd.to_datetime(datetime.now().date())
    def is_open_due(row):
        due = row.get('Due Date', pd.NaT)
        paid = row.get('Paid', False)
        try:
            due_dt = pd.to_datetime(due, errors='coerce')
        except Exception:
            due_dt = pd.NaT
        if pd.isna(due_dt):
            return False
        if (due_dt > today) and (not bool(paid)):
            return True
        return False

    # Filter out open dues
    mask_open = expenses_df.apply(is_open_due, axis=1)
    filtered = expenses_df[~mask_open]
    total = pd.to_numeric(filtered['Actuals'], errors='coerce').fillna(0).sum()
    return float(total)

def get_expected_money_on_hand():
    """Calculate money on hand based on allocated (Expected) amounts.

    This subtracts Expected amounts (excluding open dues) from total income.
    """
    df = st.session_state.df
    expenses_df = df[
        (df['Expense Category'].notna()) & 
        (df['Expense SubCategory'].notna()) &
        (df['Expense Category'] != '') & 
        (df['Expense SubCategory'] != '')
    ]
    # For Expected money-on-hand we treat allocated amounts as reserved now
    # (i.e. include Expected values regardless of Due Date or Paid flag)
    total_expected = pd.to_numeric(expenses_df['Expected'], errors='coerce').fillna(0).sum()
    total_income = get_total_income()
    return float(total_income - total_expected)

def get_remaining_money():
    """Calculate remaining money (Total Income - Total Actual Expenses)"""
    total_income = get_total_income()
    total_expenses = get_total_expenses()
    return total_income - total_expenses

def add_category_subcategory(category, subcategory, expected=0.0, actuals=0.0):
    """Add a new category/subcategory combination to the Excel file"""
    df = st.session_state.df
    
    # Check if combination already exists
    existing = df[(df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)]
    if not existing.empty:
        return False, "Category/Subcategory combination already exists!"
    
    # record creation date
    today = datetime.now().strftime('%Y-%m-%d')
    # Create a new row
    new_row = pd.DataFrame({
        'Name': [None],
        'Monthly Income': [None],
        'Unnamed: 2': [None],
        'Unnamed: 3': [None],
        'Expense Category': [category],
        'Expense SubCategory': [subcategory],
        'Expected': [float(expected)],
        'Actuals': [float(actuals)],
        'Payment Date': [pd.NaT],
        'Due Date': [pd.NaT],
        'Paid': [False]
    })
    
    # Append to dataframe
    df = pd.concat([df, new_row], ignore_index=True)
    st.session_state.df = df
    success, err = save_excel_data(df)
    if not success:
        return False, f"Failed to save new category/subcategory: {err}"
    return True, f"✅ Added '{subcategory}' under '{category}'"

def remove_category_subcategory(category, subcategory):
    """Remove a category/subcategory combination from the Excel file"""
    df = st.session_state.df
    
    # Check if combination exists
    mask = (df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)
    if not mask.any():
        return False, "Category/Subcategory combination not found!"
    
    # Remove the row
    df = df[~mask]
    st.session_state.df = df
    success, err = save_excel_data(df)
    if not success:
        return False, f"Failed to save removal: {err}"
    return True, f"✅ Removed '{subcategory}' from '{category}'"

def set_paid_status(category, subcategory, paid_flag):
    """Set the Paid flag for a category/subcategory and update Payment Date when marked paid."""
    df = st.session_state.df
    mask = (df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)
    if not mask.any():
        return False, "Category/Subcategory not found"
    df.loc[mask, 'Paid'] = bool(paid_flag)
    if paid_flag:
        today = datetime.now().strftime('%Y-%m-%d')
        df.loc[mask, 'Payment Date'] = today
    else:
        # Clear payment date when unmarking paid
        df.loc[mask, 'Payment Date'] = pd.NaT
    st.session_state.df = df
    success, err = save_excel_data(df)
    if not success:
        return False, f"Failed to save Paid status: {err}"
    return True, f"✅ Set Paid={paid_flag} for '{subcategory}' in '{category}'"

def add_category(category):
    """Add a new category with placeholder subcategory"""
    df = st.session_state.df
    
    # Check if category already exists
    if category in df['Expense Category'].values:
        return False, "Category already exists!"
    
    # Create a new row with placeholder
    today = datetime.now().strftime('%Y-%m-%d')
    # Create a new row with placeholder
    new_row = pd.DataFrame({
        'Name': [None],
        'Monthly Income': [None],
        'Unnamed: 2': [None],
        'Unnamed: 3': [None],
        'Expense Category': [category],
        'Expense SubCategory': ['Other'],
        'Expected': [0.0],
        'Actuals': [0.0],
        'Payment Date': [pd.NaT],
        'Due Date': [pd.NaT],
        'Paid': [False]
    })
    
    # Append to dataframe
    df = pd.concat([df, new_row], ignore_index=True)
    st.session_state.df = df
    success, err = save_excel_data(df)
    if not success:
        return False, f"Failed to save new category: {err}"
    return True, f"✅ Added new category '{category}' with placeholder 'Other' subcategory"

def remove_category(category):
    """Remove an entire category and all its subcategories"""
    df = st.session_state.df
    
    # Check if category exists
    mask = df['Expense Category'] == category
    if not mask.any():
        return False, "Category not found!"
    
    count = mask.sum()
    
    # Remove all rows with this category
    df = df[~mask]
    st.session_state.df = df
    success, err = save_excel_data(df)
    if not success:
        return False, f"Failed to save category removal: {err}"
    return True, f"✅ Removed category '{category}' ({count} subcategories deleted)"

# Load data
if 'df' not in st.session_state:
    st.session_state.df = load_excel_data()

if st.session_state.df is None:
    st.stop()

# Ensure 'Payment Date' column exists (store ISO date string when updates happen)
cols_to_ensure = {
    'Payment Date': pd.NaT,
    'Due Date': pd.NaT,
    'Paid': False
}
for col, default in cols_to_ensure.items():
    if col not in st.session_state.df.columns:
        st.session_state.df[col] = default
        # avoid dtype surprises: coerce dates later when formatting
# Save the sheet if we added missing columns
save_result = save_excel_data(st.session_state.df)
if isinstance(save_result, tuple):
    success, err = save_result
    if not success:
        st.error(f"Failed to save master sheet after adding missing columns: {err}")
# ====================================
# Page Config
# ====================================
st.set_page_config(page_title="Expense Tracker", layout="wide")

# ====================================
# Main UI
# ====================================
st.title("💰 Monthly Expense Tracker")
st.markdown("*Data source: Master_Sheet_Expenses.xlsx*")
st.markdown("---")

# Display Money Summary at Top
col_income, col_expenses, col_remaining = st.columns(3)

total_income = get_total_income()
total_expenses = get_total_expenses()
remaining_money = get_remaining_money()

with col_income:
    st.metric(
        "💵 Total Monthly Income",
        f"${total_income:,.2f}",
        delta=None,
        border=True
    )

with col_expenses:
    st.metric(
        "💸 Total Expenses (Actual)",
        f"${total_expenses:,.2f}",
        delta=f"{(total_expenses/total_income*100) if total_income > 0 else 0:.1f}% of income",
        border=True
    )

with col_remaining:
    # Color code based on remaining money
    if remaining_money >= 0:
        st.metric(
            "💰 Money on Hand",
            f"${remaining_money:,.2f}",
            delta="✅ Available",
            border=True
        )
    else:
        st.metric(
            "💰 Money on Hand",
            f"${remaining_money:,.2f}",
            delta="⚠️ Deficit",
            border=True
        )

# Also show Expected Money on Hand (uses allocated/Expected excluding open dues)
expected_remaining = get_expected_money_on_hand()
col_e1, col_e2, col_e3 = st.columns(3)
with col_e2:
    if expected_remaining >= 0:
        st.metric(
            "📊 Expected Money on Hand",
            f"${expected_remaining:,.2f}",
            delta="Based on allocated (Expected)",
            border=False
        )
    else:
        st.metric(
            "📊 Expected Money on Hand",
            f"${expected_remaining:,.2f}",
            delta="⚠️ Deficit (allocated)",
            border=False
        )

st.markdown("---")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Manage Expenses", "👥 Individual Income", "⚙️ Manage Categories", "📊 Dashboard", "📈 Analysis"])

# ====================================
# TAB 1: Manage Expenses
# ====================================
with tab1:
    st.header("📝 Manage Expenses")
    with st.expander("Monthly Reset (Admin)", expanded=False):
        st.write("Use this to reset monthly dynamic values. This will set all 'Actuals' to 0, clear 'Payment Date', and uncheck 'Paid' for all expense rows. It will NOT change 'Expected' or 'Monthly Income'.")
        confirm = st.text_input("Type RESET to confirm", value="", key="reset_confirm_input")
        if st.button("Reset Monthly Values", key="reset_monthly_btn"):
            if confirm.strip().upper() == "RESET":
                ok, m = reset_monthly()
                if ok:
                    st.success("Monthly values reset successfully.")
                    st.info(m)
                    st.balloons()
                    st.experimental_rerun()
                else:
                    st.error(f"Reset failed: {m}")
            else:
                st.error("Confirmation text does not match 'RESET'. Type RESET to proceed.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add/Update Expense Values")
        
        # Get categories and subcategories
        categories = get_categories()
        if not categories:
            st.error("No expense categories found in Excel!")
        else:
            selected_category = st.selectbox(
                "Select Expense Category",
                categories,
                key="category_select"
            )
            
            subcategories = get_subcategories(selected_category)
            if subcategories:
                selected_subcategory = st.selectbox(
                    "Select Expense SubCategory",
                    subcategories,
                    key="subcategory_select"
                )
                
                # Get current values (prefer fresh read from Excel so UI shows latest saved values)
                current_expected = 0.0
                current_actual = 0.0
                try:
                    df_disk = load_excel_data()
                except Exception:
                    df_disk = None

                if df_disk is not None:
                    match_disk = df_disk[(df_disk['Expense Category'] == selected_category) & (df_disk['Expense SubCategory'] == selected_subcategory)]
                    if not match_disk.empty:
                        current_expected = match_disk.iloc[0].get('Expected', 0.0)
                        current_actual = match_disk.iloc[0].get('Actuals', 0.0)
                        # coerce to float safely
                        try:
                            current_expected = float(pd.to_numeric(current_expected, errors='coerce'))
                        except Exception:
                            current_expected = 0.0
                        try:
                            current_actual = float(pd.to_numeric(current_actual, errors='coerce'))
                        except Exception:
                            current_actual = 0.0
                    else:
                        # fallback to session-state
                        current_expected = get_expected_value(selected_category, selected_subcategory)
                        current_actual = get_actual_value(selected_category, selected_subcategory)
                else:
                    current_expected = get_expected_value(selected_category, selected_subcategory)
                    current_actual = get_actual_value(selected_category, selected_subcategory)
                
                st.info(f"📌 Current Values for '{selected_subcategory}'")
                st.write(f"**Expected:** ${current_expected:.2f}")
                st.write(f"**Actual:** ${current_actual:.2f}")
                
                st.markdown("---")
                
                # Input fields for new values (Expected & Actual)
                new_expected = st.number_input(
                    "Update Expected Amount ($)",
                    min_value=0.0,
                    value=current_expected,
                    step=0.01,
                    format="%.2f",
                    key="new_expected"
                )
                
                new_actual = st.number_input(
                    "Update Actual Amount ($)",
                    min_value=0.0,
                    value=current_actual,
                    step=0.01,
                    format="%.2f",
                    key="new_actual"
                )
                
                # Get current due date and paid flag for this item
                df_local = st.session_state.df
                match = df_local[(df_local['Expense Category'] == selected_category) & (df_local['Expense SubCategory'] == selected_subcategory)]
                if not match.empty:
                    raw_due = match.iloc[0].get('Due Date', pd.NaT)
                    raw_paid = match.iloc[0].get('Paid', False)
                else:
                    raw_due = pd.NaT
                    raw_paid = False

                if pd.notna(raw_due):
                    try:
                        current_due = pd.to_datetime(raw_due, errors='coerce').date()
                    except Exception:
                        current_due = None
                else:
                    current_due = None

                has_due = st.checkbox("Has Due Date", value=(current_due is not None), key="has_due")
                if has_due:
                    due_val = st.date_input("Due Date", value=current_due if current_due is not None else datetime.now().date(), key="due_date_input")
                else:
                    due_val = None

                paid_flag = st.checkbox("Paid", value=bool(raw_paid), key="paid_checkbox")

                col_save, col_clear = st.columns(2)
                
                with col_save:
                    if st.button("💾 Save Changes", width='stretch', key="save_expense"):
                        updated_expected = update_expected_value(selected_category, selected_subcategory, new_expected)
                        updated_actual = update_actual_value(selected_category, selected_subcategory, new_actual)

                        # Update Due Date field
                        mask = (st.session_state.df['Expense Category'] == selected_category) & (st.session_state.df['Expense SubCategory'] == selected_subcategory)
                        if has_due and due_val is not None:
                            st.session_state.df.loc[mask, 'Due Date'] = pd.to_datetime(due_val).strftime('%Y-%m-%d')
                        else:
                            st.session_state.df.loc[mask, 'Due Date'] = pd.NaT
                        # Save and check result
                        save_ok, save_msg = save_excel_data(st.session_state.df)
                        if not save_ok:
                            st.error(f"Failed to save Due Date change: {save_msg}")
                        else:
                            # Update Paid flag (this will also set Payment Date appropriately)
                            success_paid, msg_paid = set_paid_status(selected_category, selected_subcategory, paid_flag)

                            if (updated_expected or updated_actual or success_paid):
                                st.success(f"✅ Updated '{selected_subcategory}'")
                                st.balloons()
                                st.rerun()

                with col_clear:
                    if st.button("🔄 Refresh", width='stretch', key="refresh_expense"):
                        st.rerun()
            else:
                st.warning("No subcategories found for this category")
    
    with col2:
        st.subheader("Expense Summary Table")
        
        # Get all non-empty expenses
        df = st.session_state.df
        summary_data = df[
            (df['Expense Category'].notna()) & 
            (df['Expense SubCategory'].notna()) &
            (df['Expense Category'] != '') & 
            (df['Expense SubCategory'] != '')
        ].copy()
        
        summary_data['Expected'] = pd.to_numeric(summary_data['Expected'], errors='coerce').fillna(0)
        summary_data['Actuals'] = pd.to_numeric(summary_data['Actuals'], errors='coerce').fillna(0)
        summary_data['Variance'] = summary_data['Actuals'] - summary_data['Expected']
        
        # Create display dataframe and include Payment Date, Due Date, Paid
        display_df = summary_data[[
            'Expense Category',
            'Expense SubCategory',
            'Expected',
            'Actuals',
            'Variance',
            'Due Date',
            'Paid',
            'Payment Date'
        ]].copy()

        # Format numeric columns
        display_df['Expected'] = pd.to_numeric(display_df['Expected'], errors='coerce').fillna(0).apply(lambda x: f"${x:.2f}")
        display_df['Actuals'] = pd.to_numeric(display_df['Actuals'], errors='coerce').fillna(0).apply(lambda x: f"${x:.2f}")
        display_df['Variance'] = summary_data['Variance'].apply(
            lambda x: f"${x:.2f} 📈" if x > 0 else f"${x:.2f} 📉" if x < 0 else "$0.00 ✓"
        )

        # Format due date and payment date (handle NaT or missing values)
        display_df['Due Date'] = pd.to_datetime(display_df['Due Date'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('-')
        display_df['Payment Date'] = pd.to_datetime(display_df['Payment Date'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('-')
        # Format Paid as Yes/No
        display_df['Paid'] = display_df['Paid'].apply(lambda x: 'Yes' if bool(x) else 'No')

        st.dataframe(display_df, width='stretch', hide_index=True)

# ====================================
# TAB 2: Individual Income
# ====================================
with tab2:
    st.header("👥 Individual Income Management")
    
    individuals = get_individuals()
    
    if individuals:
        selected_individual = st.selectbox(
            "Select Individual",
            individuals,
            key="individual_select"
        )
        
        # Get current income
        df = st.session_state.df
        individual_row = df[df['Name'] == selected_individual]
        current_income = individual_row['Monthly Income'].values[0] if not individual_row.empty else 0
        current_income = float(current_income) if pd.notna(current_income) else 0.0
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"💰 Current Monthly Income for **{selected_individual}**: **${current_income:.2f}**")
        
        with col2:
            st.empty()
        
        st.markdown("---")
        
        new_income = st.number_input(
            f"Update Monthly Income for {selected_individual} ($)",
            min_value=0.0,
            value=current_income,
            step=100.0,
            format="%.2f",
            key="new_income"
        )
        
        col_save, col_reset = st.columns(2)
        
        with col_save:
            if st.button("💾 Update Income", width='stretch', key="save_income"):
                if update_monthly_income(selected_individual, new_income):
                    st.success(f"✅ Updated {selected_individual}'s income to ${new_income:.2f}")
                    st.balloons()
                    st.rerun()
        
        with col_reset:
            if st.button("🔄 Refresh", width='stretch', key="refresh_income"):
                st.rerun()
        
        st.markdown("---")
        st.subheader("Income Summary")
        
        income_summary = df[df['Name'].notna() & (df['Name'] != '')][['Name', 'Monthly Income']].drop_duplicates()
        income_summary['Monthly Income'] = pd.to_numeric(income_summary['Monthly Income'], errors='coerce').fillna(0)
        income_summary = income_summary.sort_values('Monthly Income', ascending=False)
        
        display_income = income_summary.copy()
        display_income['Monthly Income'] = display_income['Monthly Income'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(display_income, width='stretch', hide_index=True)
    else:
        st.warning("No individuals found in Excel file")

# ====================================
# TAB 3: Manage Categories
# ====================================
with tab3:
    st.header("⚙️ Manage Categories & Subcategories")
    
    tab3_col1, tab3_col2 = st.columns(2)
    
    # Left column: Add new category/subcategory
    with tab3_col1:
        st.subheader("➕ Add New Expense")
        
        add_method = st.radio(
            "Choose what to add:",
            ["Add Category & Subcategory", "Add Subcategory to Existing"],
            key="add_method"
        )
        
        if add_method == "Add Category & Subcategory":
            new_category = st.text_input(
                "New Category Name",
                placeholder="e.g., Insurance, Travel",
                key="new_cat_input"
            )
            new_subcategory = st.text_input(
                "Subcategory Name",
                placeholder="e.g., Health Insurance, Flight",
                key="new_subcat_input_1"
            )
            expected_amount = st.number_input(
                "Expected Amount ($)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
                key="expected_new_1"
            )
            
            if st.button("➕ Add Category & Subcategory", width='stretch', key="add_cat_subcat"):
                if new_category.strip() and new_subcategory.strip():
                    success, message = add_category_subcategory(new_category.strip(), new_subcategory.strip(), expected_amount)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in both category and subcategory names")
        
        else:  # Add Subcategory to Existing
            categories = get_categories()
            if categories:
                existing_category = st.selectbox(
                    "Select Existing Category",
                    categories,
                    key="existing_cat_select"
                )
                new_subcategory_2 = st.text_input(
                    "New Subcategory Name",
                    placeholder="e.g., Dental, Train",
                    key="new_subcat_input_2"
                )
                expected_amount_2 = st.number_input(
                    "Expected Amount ($)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="expected_new_2"
                )
                
                if st.button("➕ Add Subcategory", width='stretch', key="add_subcat"):
                    if new_subcategory_2.strip():
                        success, message = add_category_subcategory(existing_category, new_subcategory_2.strip(), expected_amount_2)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please enter subcategory name")
            else:
                st.error("No categories found. Add a category first.")
    
    # Right column: Remove category/subcategory
    with tab3_col2:
        st.subheader("❌ Remove Expense")
        
        remove_method = st.radio(
            "Choose what to remove:",
            ["Remove Subcategory", "Remove Entire Category"],
            key="remove_method"
        )
        
        if remove_method == "Remove Subcategory":
            categories = get_categories()
            if categories:
                sel_category = st.selectbox(
                    "Select Category",
                    categories,
                    key="cat_for_remove"
                )
                subcategories = get_subcategories(sel_category)
                if subcategories:
                    sel_subcategory = st.selectbox(
                        "Select Subcategory to Remove",
                        subcategories,
                        key="subcat_for_remove"
                    )
                    
                    st.warning(f"⚠️ This will permanently delete '{sel_subcategory}' from '{sel_category}'")
                    
                    if st.button("❌ Remove Subcategory", width='stretch', key="remove_subcat"):
                        success, message = remove_category_subcategory(sel_category, sel_subcategory)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("No subcategories found in this category")
            else:
                st.error("No categories found")
        
        else:  # Remove Entire Category
            categories = get_categories()
            if categories:
                cat_to_remove = st.selectbox(
                    "Select Category to Remove",
                    categories,
                    key="cat_to_remove"
                )
                
                num_subcats = len(get_subcategories(cat_to_remove))
                st.error(f"🚨 This will delete the entire '{cat_to_remove}' category and {num_subcats} subcategories")
                
                if st.button("❌ Remove Entire Category", width='stretch', key="remove_cat"):
                    success, message = remove_category(cat_to_remove)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error("No categories found")
    
    st.markdown("---")
    st.subheader("📋 All Categories & Subcategories")
    
    # Display all categories and subcategories
    df = st.session_state.df
    cat_list = []
    for category in get_categories():
            for subcategory in get_subcategories(category):
                exp_val = get_expected_value(category, subcategory)
                act_val = get_actual_value(category, subcategory)
                # find metadata for this category/subcategory
                match = df[(df['Expense Category'] == category) & (df['Expense SubCategory'] == subcategory)]
                if not match.empty:
                    row = match.iloc[0]
                    pd_raw = row.get('Payment Date', None)
                    due_raw = row.get('Due Date', None)
                    paid_raw = row.get('Paid', False)
                else:
                    pd_raw = None
                    due_raw = None
                    paid_raw = False

                try:
                    pd_formatted = pd.to_datetime(pd_raw, errors='coerce').strftime('%Y-%m-%d') if pd_raw is not None else '-'
                except Exception:
                    pd_formatted = '-'
                try:
                    due_formatted = pd.to_datetime(due_raw, errors='coerce').strftime('%Y-%m-%d') if due_raw is not None else '-'
                except Exception:
                    due_formatted = '-'

                cat_list.append({
                    'Category': category,
                    'Subcategory': subcategory,
                    'Expected': f"${exp_val:.2f}",
                    'Actual': f"${act_val:.2f}",
                    'Due Date': due_formatted,
                    'Paid': 'Yes' if bool(paid_raw) else 'No',
                    'Payment Date': pd_formatted
                })
    
    if cat_list:
        cat_df = pd.DataFrame(cat_list)
        st.dataframe(cat_df, width='stretch', hide_index=True)
    else:
        st.info("No categories/subcategories found")

# ====================================
# TAB 4: Dashboard
# ====================================
with tab4:
    st.header("📊 Expense Dashboard")
    
    df = st.session_state.df
    
    # Prepare data
    dashboard_df = df[
        (df['Expense Category'].notna()) & 
        (df['Expense SubCategory'].notna()) &
        (df['Expense Category'] != '') & 
        (df['Expense SubCategory'] != '')
    ].copy()
    
    dashboard_df['Expected'] = pd.to_numeric(dashboard_df['Expected'], errors='coerce').fillna(0)
    dashboard_df['Actuals'] = pd.to_numeric(dashboard_df['Actuals'], errors='coerce').fillna(0)
    dashboard_df['Variance'] = dashboard_df['Actuals'] - dashboard_df['Expected']
    # Ensure Due Date is parsed and sort dashboard by Due Date ascending (earliest first)
    dashboard_df['DueDate_dt'] = pd.to_datetime(dashboard_df.get('Due Date', pd.NaT), errors='coerce')
    dashboard_df = dashboard_df.sort_values(by='DueDate_dt', ascending=True, na_position='last')
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_expected = dashboard_df['Expected'].sum()
    total_actual = dashboard_df['Actuals'].sum()
    total_variance = total_actual - total_expected
    overspend_count = len(dashboard_df[dashboard_df['Variance'] > 0])
    
    with col1:
        st.metric("Total Expected", f"${total_expected:.2f}")
    with col2:
        st.metric("Total Actual", f"${total_actual:.2f}")
    with col3:
        st.metric("Total Variance", f"${total_variance:.2f}", 
                  delta=f"{'Over' if total_variance > 0 else 'Under'} budget")
    with col4:
        st.metric("Overspent Items", overspend_count)
    
    st.markdown("---")
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Expected vs Actual by Category")
        summary_by_cat = dashboard_df.groupby('Expense Category')[['Expected', 'Actuals']].sum()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        summary_by_cat.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c'], width=0.7)
        ax.set_title("Expected vs Actual by Category", fontsize=12, fontweight="bold")
        ax.set_xlabel("Category")
        ax.set_ylabel("Amount ($)")
        ax.legend(['Expected', 'Actual'])
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col_chart2:
        st.subheader("Variance by Category")
        variance_by_cat = dashboard_df.groupby('Expense Category')['Variance'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ['#e74c3c' if x > 0 else '#2ecc71' for x in variance_by_cat.values]
        variance_by_cat.plot(kind='barh', ax=ax, color=colors)
        ax.set_title("Variance by Category (Red=Over, Green=Under)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Variance ($)")
        plt.tight_layout()
        st.pyplot(fig)

# ====================================
# TAB 5: Analysis
# ====================================
with tab5:
    st.header("📈 Financial Analysis")
    
    df = st.session_state.df
    
    analysis_df = df[
        (df['Expense Category'].notna()) & 
        (df['Expense SubCategory'].notna()) &
        (df['Expense Category'] != '') & 
        (df['Expense SubCategory'] != '')
    ].copy()
    
    analysis_df['Expected'] = pd.to_numeric(analysis_df['Expected'], errors='coerce').fillna(0)
    analysis_df['Actuals'] = pd.to_numeric(analysis_df['Actuals'], errors='coerce').fillna(0)
    analysis_df['Variance'] = analysis_df['Actuals'] - analysis_df['Expected']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🔴 **Top 10 Overspent Items**")
        overspent = analysis_df[analysis_df['Variance'] > 0].nlargest(10, 'Variance')
        if not overspent.empty:
            for idx, row in overspent.iterrows():
                st.write(f"• {row['Expense SubCategory']}: ${row['Variance']:.2f} over budget")
        else:
            st.success("✅ No overspending!")
    
    with col2:
        st.info("🟢 **Top 10 Under Budget Items**")
        underbudget = analysis_df[analysis_df['Variance'] < 0].nsmallest(10, 'Variance')
        if not underbudget.empty:
            for idx, row in underbudget.iterrows():
                st.write(f"• {row['Expense SubCategory']}: ${abs(row['Variance']):.2f} under budget")
        else:
            st.warning("No under budget items")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📌 **Expenses by Category**")
        cat_totals = analysis_df.groupby('Expense Category')['Actuals'].sum().sort_values(ascending=False)
        total_all = cat_totals.sum()
        for cat, amount in cat_totals.items():
            pct = (amount / total_all * 100) if total_all > 0 else 0
            st.write(f"• {cat}: ${amount:.2f} ({pct:.1f}%)")
    
    with col2:
        st.info("📊 **Budget Utilization**")
        total_expected = analysis_df['Expected'].sum()
        total_actual = analysis_df['Actuals'].sum()
        
        if total_expected > 0:
            utilization = (total_actual / total_expected) * 100
            st.metric("Budget Utilization", f"{utilization:.1f}%")
            
            if utilization > 100:
                st.error(f"🚨 Over budget by {utilization - 100:.1f}%")
            elif utilization > 90:
                st.warning(f"⚠️ Approaching budget limit ({utilization:.1f}%)")
            else:
                st.success(f"✅ Within budget ({utilization:.1f}%)")

st.markdown("---")
st.caption(f"💾 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

