# french_reminder/__init__.py
"""
Модуль напоминаний об изучении французского языка для TFSL теста
"""

from .french_tracker import (
    setup_french_scheduler,
    send_french_study_reminder,
    test_french_reminder
)

__all__ = [
    'setup_french_scheduler',
    'send_french_study_reminder',
    'test_french_reminder'
]