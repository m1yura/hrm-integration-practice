$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot ".runvenv\Scripts\python.exe"
$log = Join-Path $PSScriptRoot "logs\start_site.log"

[Environment]::SetEnvironmentVariable("PATH", $null, "Process")

"$(Get-Date -Format o) Starting HRM site" | Out-File -FilePath $log -Encoding utf8

$applications = Start-Process `
    -FilePath $python `
    -ArgumentList "module_c_applications.py" `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Hidden `
    -PassThru

$ui = Start-Process `
    -FilePath $python `
    -ArgumentList "ui_server.py" `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Hidden `
    -PassThru

"Applications PID: $($applications.Id)" | Out-File -FilePath $log -Append -Encoding utf8
"UI PID: $($ui.Id)" | Out-File -FilePath $log -Append -Encoding utf8
"UI: http://127.0.0.1:8080" | Out-File -FilePath $log -Append -Encoding utf8

while ($true) {
    Start-Sleep -Seconds 3600
}
