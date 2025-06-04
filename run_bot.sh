#!/bin/bash

# Переходим в папку проекта
cd "$(dirname "$0")"

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем бота
python agent.py
