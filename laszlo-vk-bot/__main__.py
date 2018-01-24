# -*- coding: utf-8 -*-
"""
Наш основной модуль~
"""
import logging
import os
import random
import re
import signal
import string
import sys
import tempfile
import time
from typing import Dict, List

import cson
import schedule
from vk_api import vk_api

try:
    from . import config
except ImportError:
    import config

EXIT_SUCCESS = 0  # По сигналу
EXIT_VK_API = 1  # Ошибка vk_api
EXIT_ENV = 2  # Некорректные переменные среды
EXIT_PARSE = 4  # Ошибка открытия/парсинга
EXIT_UNKNOWN = 256  # Неведомая хрень

VK_VER = 5.71  # Последняя версия на 2018.01.22

log: logging.Logger
vk: vk_api.VkApiMethod
rules: List[Dict[str, str]]  # см. rules_example.cson
group_id: int


def test_job():
    log.debug("Запущено тестовое задание!")
    guid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    log.debug("Пост с guid {}...".format(guid))
    result = vk.wall.post(
        owner_id="-{}".format(group_id),
        from_group=1,
        message="{}".format(random.choice(rules)["post_msg"]),  # TODO: dehardcode
        signed=1
    )
    log.debug("Результат: {}".format(result))


def change_rule_of_the_day():
    log.info("Правило дня изменяется на {}!")


# noinspection PyBroadException
def main():
    """
    Собственно, основной метод...

    :return: код возврата
    """

    try:
        access_token_regex = re.compile(r'access_token=(.*?)&')
        access_token = access_token_regex.findall(config.ACCESS_TOKEN_LINK)[0]
    except:
        log.critical("Неправильно задан ACCESS_TOKEN_LINK.\n\nПодробнее:\n",
                     exc_info=1)
        return EXIT_ENV

    try:
        expires_in_regex = re.compile(r'expires_in=(.*?)&')
        expires_in = int(expires_in_regex.findall(config.ACCESS_TOKEN_LINK)[0])
    except:
        expires_in = -1

    if expires_in != 0:
        log.warning("Похоже, у токена есть срок действия.\n"
                    "Если вы составляли ссылку сами, то запросите именно \'scope=73728\'!\n"
                    "\nЧерез некоторое время бот может сломаться.\n"
                    "Срок действия (сек): {}".format(expires_in))

    log.info("Парсинг файла правил...")
    try:
        with open(config.RULES_PATH, 'rb') as file:
            global rules
            rules = cson.load(file)
        log.info("...успех! Количество записей: {}".format(len(rules)))
    except:
        log.critical("Ошибка при открытии/парсинге!\n\nПодробнее:\n",
                     exc_info=1)
        return EXIT_PARSE

    log.info("Инициализация vk_api...")
    try:
        vk_session = vk_api.VkApi(
            token=access_token,
            config_filename=os.path.join(tempfile.gettempdir(), 'laszlo_vk_data.json'),
            api_version=str(VK_VER)
        )
        global vk
        vk = vk_session.get_api()
        log.info('...успех!')
    except:
        log.critical("Ошибка при попытке залогиниться!\n\nПодробнее:\n",
                     exc_info=1)
        return EXIT_VK_API

    log.info("Определение id группы...")
    try:
        group_short_name = config.GROUP_LINK.split('/')[-1]
        global group_id
        group_id = vk.groups.getById(group_id=group_short_name,
                                     version=VK_VER)[0]["id"]
        log.info("...успех! ID = {}".format(group_id))
    except:
        log.critical("Неправильно задана ссылка на группу.\n\nПодробнее:\n",
                     exc_info=1)
        return EXIT_ENV

    if config.DEBUG:
        schedule.every(10).seconds.do(test_job).tag('test-job')
    else:
        schedule.every(config.DAYS).do()

    while True:
        schedule.run_pending()
        time.sleep(1)  # Странное решение, но ЦП грузит не особо: около 200к циклов


# noinspection PyUnusedLocal
def exit_handler(sig, frame):
    """
    Обработчик сигнала остановки.

    :param sig: тип сигнала, здесь ``SIGINT`` или ``SIGTERM``
    :param frame: фрейм, во время выполнения которого был пойман сигнал
    """
    log.info("Остановка...")
    sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    print("init...")

    l_logger = logging.getLogger()
    l_logger.setLevel(config.LOG_LEVEL)
    l_logger_sh = logging.StreamHandler()
    l_logger_sh.setFormatter(logging.Formatter(config.LOG_FORMAT))
    l_logger_sh.setLevel(config.LOG_LEVEL)
    l_logger.addHandler(l_logger_sh)

    log = l_logger

    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    # noinspection PyBroadException
    try:
        sys.exit(main())
    except Exception:
        err_str = """
Случилась неведомая хрень...

Если это не проблемы с сетью или сервером VK, то:
Напишите в https://github.com/saber-nyan/laszlo-vk-bot/issues или на
saber-nyan@ya.ru и приложите:

"""
        log.critical(err_str, exc_info=1)
        sys.exit(EXIT_UNKNOWN)
