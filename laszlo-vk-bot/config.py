# -*- coding: utf-8 -*-
"""
Файл конфигурации бота.
"""
import os
import sys
import traceback
from pathlib import Path

try:
    from .__main__ import EXIT_ENV
except ImportError:
    from __main__ import EXIT_ENV

# настройка = os.getenv('ключ', умолчание)

# Префиксы LASZLO для устранения конфликтов с другими переменными.
# (Мало ли на что еще DEBUG сработает, например?)

# noinspection PyBroadException
try:  # см. README.md!
    RULES_PATH = os.path.expanduser(os.environ['LASZLO_RULES_PATH'])  # Путь до файла правил
    GROUP_LINK = os.environ['LASZLO_GROUP_LINK']  # Ссылка на группу
    ACCESS_TOKEN_LINK = os.environ['LASZLO_ACCESS_TOKEN_LINK']  # API Token
except:
    print("Необходимые переменные окружения не найдены или заданы неверно.\n"
          "Пожалуйста, перечитайте README.md!\n\nПодробнее:\n{}"
          .format(traceback.format_exc()), file=sys.stderr)
    sys.exit(EXIT_ENV)

# Через сколько дней должны обновиться правила?
DAYS = int(os.getenv('LASZLO_DAYS', 1))


# Домашняя директория бота. Должны быть права на запись.
HOMEDIR = os.getenv('LASZLO_HOMEDIR', os.path.join(Path.home(), '.laszlo-vk-bot'))

# Режим отладки.
DEBUG = 'LASZLO_DEBUG' in os.environ

logfmt_default = '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: %(message)s'
LOG_FORMAT = os.getenv('LASZLO_LOG_FORMAT', logfmt_default)  # Формат лога.

# Уровни (даже не пытайтесь запихнуть число!):
# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG
# NOTSET
LOG_LEVEL = os.getenv('LASZLO_LOG_LEVEL', 'INFO')  # Уровень лога.
if DEBUG:
    LOG_LEVEL = 'DEBUG'
