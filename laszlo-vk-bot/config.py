# -*- coding: utf-8 -*-
"""
Файл конфигурации бота.
"""
import os
import sys
import traceback
from pathlib import Path

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
    sys.exit(2)  # Рекурсивные импорты - плохо.

# Через сколько дней должны обновиться правила?
DAYS = float(os.getenv('LASZLO_DAYS', 1))

# Через сколько *смен правил* бот должен дать передышку длиной в REST_DAYS?
# Важно, что это не дни, а срабатывания!
# -1 = отключить
REST = int(os.getenv('LASZLO_REST', -1))

# Длина передышки, в днях.
REST_DAYS = float(os.getenv('LASZLO_REST_DAYS', -1))

# Удалять старый пост с правилами после постинга нового? Если '1', то да.
DELETE_PREV_POST = True if os.getenv('LASZLO_DELETE_PREV_POST', 1) == 1 else False

# Количество попыток удалить старый пост. -1 = бесконечно, не рекомендую
DELETE_MAX_TRIES = int(os.getenv('LASZLO_DELETE_MAX_TRIES', 3))

# Количество попыток отправить пост. -1 = бесконечно, не рекомендую
POST_MAX_TRIES = int(os.getenv('LASZLO_POST_MAX_TRIES', 100))

# Задержка между тиками, в секундах. Чем меньше - тем точнее таймер, но сильнее нагружается ЦП.
TICK_DELAY = float(os.getenv('LASZLO_TICK_DELAY', 10))

# Домашняя директория бота. Должны быть права на запись, грузит состояние оттуда.
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
