# 🚀 Expense Tracker - Quick Start Guide

## Option 1: Desktop Shortcut (Easiest) ⭐

A desktop shortcut has been created for you:

1. **Look for**: `💰 Expense Tracker.lnk` on your Desktop
2. **Double-click** it anytime to launch the app
3. The browser will automatically open to `http://localhost:8501`
4. **To stop**: Close the command window that appears

---

## Option 2: Run Batch File Directly

You can also manually run the launcher:

1. Navigate to: `c:\Users\Lenovo\Desktop\KK_Data\Git_Personal\Personal_Essentials\expense_app`
2. **Double-click**: `run_app.bat`
3. A command window will appear
4. Browser automatically opens to the app
5. Press `Ctrl+C` to stop the app

---

## Option 3: Command Line

```powershell
cd "c:\Users\Lenovo\Desktop\KK_Data\Git_Personal\Personal_Essentials\expense_app"
py -3 -m streamlit run expense_tracker.py
```

---

## What Happens When You Launch?

✅ Streamlit server starts  
✅ Browser automatically opens to `http://localhost:8501`  
✅ You can access 4 tabs:
- 📝 **Manage Expenses** - Update Expected & Actual amounts
- 👥 **Individual Income** - Manage monthly income for family members
- 📊 **Dashboard** - Visual charts and metrics
- 📈 **Analysis** - Financial insights and reports

---

## Common Issues

### Q: Port 8501 already in use?
**Solution**: Kill the existing process and restart
```powershell
Get-Process streamlit | Stop-Process -Force
```

### Q: App won't load?
**Solution**: Check if Python is installed
```powershell
py -3 --version
```

### Q: Browser doesn't auto-open?
**Solution**: Manually visit: `http://localhost:8501`

### Q: "pip install" fails?
**Solution**: Use the launcher with `--reset-cache`
```powershell
py -3 -m streamlit run expense_tracker.py --client.showErrorDetails=false
```

---

## File Structure

```
expense_app/
├── expense_tracker.py           (Main app)
├── Master_Sheet_Expenses.xlsx   (Data source)
├── requirements.txt             (Dependencies)
├── run_app.bat                  (Launcher script - DOUBLE-CLICK THIS)
├── create_shortcut.ps1          (Creates desktop shortcut)
└── README.md                    (Documentation)
```

---

## Data Storage

All your expense data is stored in:
- **File**: `Master_Sheet_Expenses.xlsx`
- **Location**: Same folder as the app
- **Auto-saved**: Changes save immediately when you update values

---

## Features

✨ **Dynamic Category Management** - No hardcoding needed  
✨ **Real-time Excel Updates** - Data persists automatically  
✨ **Multi-user Support** - Track expenses for family members  
✨ **Visual Analytics** - Charts and variance analysis  
✨ **Budget Tracking** - Monitor overspending in real-time  

---

## Need Help?

1. Check the main `README.md` for detailed feature documentation
2. Verify all dependencies are installed: `pip list | findstr streamlit`
3. Restart the app if something seems stuck

---

**Last Updated**: November 29, 2025  
**Version**: 2.0 (Standalone Launcher)
