#!/bin/bash
# ============================================================================== #
#            FASHION STORE AI - SCRIPT CHẠY SEED DỮ LIỆU DEMO (BASH)             #
# ============================================================================== #

echo "---------------------------------------------------------"
echo "  Fashion Store AI - Khởi tạo dữ liệu mẫu Demo (Bash)"
echo "---------------------------------------------------------"

RESET_FLAG=""
if [ "$1" == "--reset" ]; then
    RESET_FLAG="--reset"
fi

if [ "$(docker ps -q -f name=fashion-backend)" ]; then
    echo "[*] Đang thực thi seed bên trong Docker container 'fashion-backend'..."
    docker compose exec backend python seed_demo.py $RESET_FLAG
else
    echo "[*] Thực thi trực tiếp qua môi trường Python nội bộ..."
    cd backend || exit 1
    if [ -f ".venv/bin/python" ]; then
        .venv/bin/python seed_demo.py $RESET_FLAG
    else
        python3 seed_demo.py $RESET_FLAG
    fi
    cd ..
fi
