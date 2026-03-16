$ErrorActionPreference = "SilentlyContinue"
$pythonExe = "C:\Users\Shrey\AppData\Local\Programs\Python\Python313\python.exe"
$scriptPath = "C:\Users\Shrey\.config\opencode\tools\telegram_bot_v2.py"
$workDir = "C:\Users\Shrey\.config\opencode"
$outFile = "C:\Users\Shrey\.config\opencode\bot_out.log"
$errFile = "C:\Users\Shrey\.config\opencode\bot_err.log"

Get-Process python* | Stop-Process -Force
Start-Sleep -Seconds 2

$proc = Start-Process $pythonExe -ArgumentList $scriptPath -WorkingDirectory $workDir -WindowStyle Hidden -PassThru -RedirectStandardOutput $outFile -RedirectStandardError $errFile
Start-Sleep -Seconds 3

if ($proc -and -not $proc.HasExited) {
    Write-Host "Bot started with PID: $($proc.Id)"
} else {
    Write-Host "Bot failed to start"
}
