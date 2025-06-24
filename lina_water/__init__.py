"""
Модуль напоминания о воде для Лины
"""

from .water_reminder import (
    setup_water_scheduler,
    send_water_reminder,
    test_water_reminder,
)

_all_ = [
    'setup_water_scheduler',
    'send_water_reminder',
    'test_water_reminder',
]