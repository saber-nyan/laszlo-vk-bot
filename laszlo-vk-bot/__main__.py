# -*- coding: utf-8 -*-
"""
Наш основной модуль~
"""
import logging
import os
import pickle
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
    from . import global_state
except ImportError:
    import config
    import global_state

EXIT_SUCCESS = 0  # По сигналу
EXIT_VK_API = 1  # Ошибка vk_api
EXIT_ENV = 2  # Некорректные переменные среды
EXIT_PARSE = 4  # Ошибка открытия/парсинга CSON
EXIT_HOMEDIR = 8  # Ошибка при работе с домашней директорией
EXIT_PICKLE = 16  # Ошибка открытия/парсинга Pickle
EXIT_UNKNOWN = 256  # Неведомая хрень

VK_VER = 5.71  # Последняя версия на 2018.01.22

STATE_PKL_PATH = os.path.join(config.HOMEDIR, 'global-state.pkl')

log: logging.Logger
vk: vk_api.VkApiMethod

rules: List[Dict[str, str]]  # см. rules_example.cson
RULES_USED = "used"
RULES_POST_MSG = "post_msg"
RULES_COMMENT_CHK = "comment_chk"
"""
Поля:

- used : использовано ли правило
- post_msg : сам текст правила
- comment_chk : скрипт для проверки комментариев, WIP
"""

group_id: int

state: global_state.BotState


# noinspection PyBroadException
def test_job():
    """
    Задание для тестирования логики.
    """
    log.debug("Запущено тестовое задание!")
    if config.DELETE_PREV_POST and state.last_post_id is not None:
        tries = 1
        while tries <= 3:
            try:
                del_result = vk.wall.delete(
                    owner_id=group_id,
                    post_id=state.last_post_id,
                    version=VK_VER
                )
                if del_result != 1:
                    raise RuntimeError("Response is {}, not \"1\"!".format(del_result))
                else:
                    break
            except:
                log.warning("Ошибка удаления поста! Ждем 5 секунд, попытка {}/3.\n"
                            "Подробнее:\n".format(tries), exc_info=1)
                tries += 1
                time.sleep(5)

    guid = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    msg = random.choice([a for a in rules if not a[RULES_USED]])["post_msg"]
    log.debug("Пост с guid {}, msg {}".format(guid, msg))
    tries = 1
    while True:
        try:
            post_result = vk.wall.post(
                owner_id=group_id,
                from_group=1,
                message=msg,
                signed=1
            )
            state.last_post_id = post_result["post_id"]
            break
        except:
            log.warning("Ошибка отправки поста! Ждем 5 секунд, попытка {}.\n"
                        "Подробнее:\n".format(tries), exc_info=1)
            tries += 1
            time.sleep(5)

    log.debug("Результат: {}".format(post_result))


def change_rule_of_the_day():
    log.info("Правило дня изменяется на {}!")


def load_state(path: str):
    """
    Загружает состояние бота из файла `pickle`.

    :param str path: путь к файлу
    """
    with open(path, 'rb') as f:
        global state
        state = pickle.load(f, fix_imports=False)  # Fuck you, compatibility.


def save_state(path: str):
    """
    Сохраняет состояние бота в файл `pickle`.

    :param str path: путь к файлу
    """
    with open(path, 'wb') as f:
        pickle.dump(state, f, pickle.HIGHEST_PROTOCOL, fix_imports=False)


# noinspection PyBroadException
def main():
    """
    Собственно, основной метод...

    :return: код возврата
    """
    try:
        if not os.path.exists(config.HOMEDIR):
            log.info("Создание домашней директории...")
            os.makedirs(config.HOMEDIR)
        elif not os.path.isdir(config.HOMEDIR):
            log.info("Пересоздание домашней директории...")
            os.remove(config.HOMEDIR)
            os.makedirs(config.HOMEDIR)
    except:
        log.critical("Ошибка при работе с домашней директорией!\n\nПодробнее:\n",
                     exc_inf=1)
        return EXIT_HOMEDIR

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

    log.info("Парсинг файла состояния...")
    global state
    try:
        load_state(STATE_PKL_PATH)
        log.info("...успех! Состояние: {}".format(state))
    except:
        log.error("Не удалось загрузить файл состояния из \"{}\", начинаю все заного.\n"
                  "Для настройки пути посмотрите \"config.py\"!\n\n"
                  "Подробнее:\n".format(STATE_PKL_PATH), exc_info=1)
        state = global_state.BotState()

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
                                     version=VK_VER)[0]["id"] * -1  # Требование ВК: -, если группа.
        log.info("...успех! ID = {}".format(group_id))
    except:
        log.critical("Неправильно задана ссылка на группу.\n\nПодробнее:\n",
                     exc_info=1)
        return EXIT_ENV

    # Почти готово, осталось понять, какие посты мы уже писали...
    all_used = True
    for rule in rules:
        rule_hash = hash(frozenset(rule.items()))
        is_used = rule_hash in state.used_rules
        rule[RULES_USED] = is_used
        if not is_used:
            all_used = False

    if all_used:
        state.used_rules = []  # Reset all hashes...
        for rule in rules:
            rule[RULES_USED] = False  # ...and keys.
    # FIXME: Выглядит тупо, как сделать по-другому?

    log.info("Запущен.")

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
    # noinspection PyBroadException
    try:
        save_state(STATE_PKL_PATH)
    except:
        log.error("Ошибка при сохранении состояния!\n"
                  "У вас есть права на запись в \"{}\"? См. \"config.py\" для настройки директорий.\n\n"
                  "Подробнее:\n".format(STATE_PKL_PATH), exc_info=1)
        sys.exit(EXIT_PICKLE)
    print("bye!")
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
        # noinspection PyBroadException
        try:
            save_state(STATE_PKL_PATH)
        except:
            log.error("Ошибка при сохранении после критической ошибки!\n\n",
                      exc_info=1)
        err_str = """
Случилась неведомая хрень...

Если это не проблемы с сетью или сервером VK, то:
Напишите в https://github.com/saber-nyan/laszlo-vk-bot/issues или на
saber-nyan@ya.ru и приложите:

"""
        log.critical(err_str, exc_info=1)
        sys.exit(EXIT_UNKNOWN)
