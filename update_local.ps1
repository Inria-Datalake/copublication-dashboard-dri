# =====================================================
# Script de mise à jour locale + GitHub
# Usage: .\update_local.ps1
#        .\update_local.ps1 -message "Ma description"
#        .\update_local.ps1 -with_data  (si nouveau xlsx)
# =====================================================

param(
    [string]$message = "Mise à jour dashboard",
    [switch]$with_data
)

$DASHBOARD = "C:\Users\abapst\nb_python\Copublications\dashboard"
$XLSX = "$DASHBOARD\dashboard.xlsx"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " MISE A JOUR DASHBOARD COPUBLICATIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Aller dans le dossier dashboard
Set-Location $DASHBOARD

# 2. Pousser le code sur GitHub
Write-Host "`n[1/2] Push du code sur GitHub..." -ForegroundColor Yellow
git add .
git commit -m $message
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Code pousse sur GitHub" -ForegroundColor Green
} else {
    Write-Host "Rien a pousser ou erreur Git" -ForegroundColor Yellow
}

# 3. Upload du fichier Excel si demande
if ($with_data) {
    Write-Host "`n[2/2] Upload du fichier Excel sur la VM..." -ForegroundColor Yellow
    if (Test-Path $XLSX) {
        wsl scp /mnt/c/Users/abapst/nb_python/Copublications/dashboard/dashboard.xlsx pocdatalake:~/apps/copublications-dashboard/
        Write-Host "OK - Fichier Excel uploade" -ForegroundColor Green
    } else {
        Write-Host "ERREUR - dashboard.xlsx introuvable dans $DASHBOARD" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Maintenant lance update_vm.sh sur la VM" -ForegroundColor Cyan
Write-Host " ssh pocdatalake" -ForegroundColor White
Write-Host " bash ~/update_vm.sh" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
