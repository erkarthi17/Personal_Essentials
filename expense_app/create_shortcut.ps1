# Create desktop shortcut for Expense Tracker
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$AppPath = "$PSScriptRoot\run_app.bat"

# Create a WScript.Shell COM object
$WshShell = New-Object -ComObject WScript.Shell

# Create shortcut
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\💰 Expense Tracker.lnk")
$Shortcut.TargetPath = $AppPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Launch Expense Tracker Application"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,43"  # Money bag icon
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created: 💰 Expense Tracker.lnk"
Write-Host "You can now double-click it anytime to launch the app!"
