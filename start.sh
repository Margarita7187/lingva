#!/bin/bash

# Устанавливаем кодировку
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# Переходим в директорию проекта (укажите имя вашей папки на Replit)
cd lingva  # ИЛИ укажите имя вашего репозитория

export PORT=5000
unset PIP_USER

# Создаем виртуальное окружение если не существует
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Активируем
source venv/bin/activate

# Устанавливаем зависимости
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo "Starting application on port $PORT..."
python main.py