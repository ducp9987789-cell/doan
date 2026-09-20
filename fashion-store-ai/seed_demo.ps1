# ============================================================================== #
#            FASHION STORE AI - SCRIPT CHẠY SEED DỮ LIỆU DEMO (POWERSHELL)       #
# ============================================================================== #

param (
    [switch]$Reset
)

Write-Host "---------------------------------------------------------" -ForegroundColor Cyan
Write-Host "  Fashion Store AI - Khởi tạo dữ liệu mẫu Demo (PowerShell)" -ForegroundColor Green
Write-Host "---------------------------------------------------------" -ForegroundColor Cyan

# Kiểm tra xem Docker backend container có đang chạy không
$dockerRunning = (docker ps -q -f name=fashion-backend)

if ($dockerRunning) {
    Write-Host "[*] Phát hiện Docker Container 'fashion-backend' đang chạy." -ForegroundColor Yellow
    Write-Host "[*] Đang thực thi seed bên trong Docker container..." -ForegroundColor Yellow
    if ($Reset) {
        docker compose exec backend python seed_demo.py --reset
    } else {
        docker compose exec backend python seed_demo.py
    }
} else {
    Write-Host "[*] Thực thi trực tiếp qua môi trường Python nội bộ..." -ForegroundColor Yellow
    Push-Location backend
    try {
        if (Test-Path ".venv\Scripts\python.exe") {
            $pythonCmd = ".venv\Scripts\python.exe"
        } else {
            $pythonCmd = "python"
        }
        
        if ($Reset) {
            & $pythonCmd seed_demo.py --reset
        } else {
            & $pythonCmd seed_demo.py
        }
    } finally {
        Pop-Location
    }
}
