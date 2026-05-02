# Smoke-test the Google Apps Script enquiry webhook (same payload shape as the site).
# Usage (from repo root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\google-apps-script\test-enquiry-webhook.ps1
# Optional:
#   .\google-apps-script\test-enquiry-webhook.ps1 -WebAppUrl "https://script.google.com/macros/s/.../exec" -Secret "your-secret"

param(
  [string] $WebAppUrl = "",
  [string] $Secret = "",
  [string] $First = "PS",
  [string] $Last = "Test",
  [string] $Email = "ps-test@example.com",
  [string] $Phone = "+60 82347982"
)

$ErrorActionPreference = "Stop"
# This file lives at repo/google-apps-script/test-enquiry-webhook.ps1
$repoRoot = Split-Path $PSScriptRoot -Parent
$configPath = Join-Path $repoRoot "js\enquiry-config.js"

if (-not $WebAppUrl -or -not $Secret) {
  if (Test-Path -LiteralPath $configPath) {
    $cfg = Get-Content -LiteralPath $configPath -Raw
    if (-not $WebAppUrl) {
      $m = [regex]::Match($cfg, 'webAppUrl:\s*"([^"]+)"')
      if ($m.Success) { $WebAppUrl = $m.Groups[1].Value }
    }
    if (-not $Secret) {
      $m = [regex]::Match($cfg, 'secret:\s*"([^"]+)"')
      if ($m.Success) { $Secret = $m.Groups[1].Value }
    }
  }
}

if (-not $WebAppUrl) {
  Write-Error "WebAppUrl missing. Pass -WebAppUrl or keep js/enquiry-config.js next to this script path logic."
}
if (-not $Secret) {
  Write-Error "Secret missing. Pass -Secret or ensure enquiry-config.js contains secret."
}

$payload = [ordered]@{
  secret      = $Secret
  first       = $First
  last        = $Last
  email       = $Email
  phone       = $Phone
  source      = "powershell_test"
  pageUrl     = "https://example.com/ps1-test"
  message     = "test-enquiry-webhook.ps1"
  userAgent   = "PowerShell/$($PSVersionTable.PSVersion)"
  submittedAt = (Get-Date).ToUniversalTime().ToString("o")
}

$body = ($payload | ConvertTo-Json -Compress)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)

$response = Invoke-WebRequest -Uri $WebAppUrl -Method Post -Body $bytes `
  -ContentType "application/json; charset=utf-8" `
  -MaximumRedirection 5 -UseBasicParsing

Write-Host "HTTP $($response.StatusCode)"
Write-Host $response.Content
