# -*- coding: utf-8 -*-
"""
Наш основной модуль~
"""
import argparse
import os
import random
import signal
import string
import sys
import tempfile
import time
import traceback

import schedule
from vk_api import vk_api

EXIT_SUCCESS = 0  # По сигналу
EXIT_VK_API = 1  # Ошибка vk_api
EXIT_ARGUMENTS = 2  # Некорректные аргументы
EXIT_UNKNOWN = 256  # Неведомая хрень

VK_VER = 5.71  # Последняя версия на 2018.01.22

args: argparse.Namespace
vk: vk_api.VkApiMethod


def test_job():
    print("test job started!")
    guid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    print("posting w/ guid {}...".format(guid))
    result = vk.wall.post(  # FIXME: У аутентификации группы не хватает прав для wall.*
        owner_id="-{}".format(args.group_id),
        from_group=1,
        message="test message from vk_api!\nw/ guid = {}".format(guid),
        signed=1
    )
    print("result: {}".format(result))


def change_rule_of_the_day():
    print("changing rule to... {}")

def main():
    """
    Собственно, основной метод...

    :return: код возврата
    """
    arg_parser = argparse.ArgumentParser(
        prog="laszlo-vk-bot",
        description="Бот для автообновления правил в сообществе VK.",
        epilog="При проблемах пишите в https://github.com/saber-nyan/laszlo-vk-bot/issues",
        add_help=True
    )
    arg_parser.add_argument(
        '--debug',
        action='store_true',
        help='Режим отладки, не трогать'
    )
    arg_parser.add_argument(
        '-d', '--days',
        action='store',
        default=1,
        type=int,
        help="Количество дней до смены правил",
        metavar="ДНЕЙ",
        dest='days'
    )
    arg_parser.add_argument(
        '-i', '--group-id',
        action='store',
        required=True,
        type=int,
        help="ID сообщества, см. README.md",
        metavar="ID",
        dest='group_id'
    )
    arg_parser.add_argument(
        '-t', '--token',
        action='store',
        required=True,
        type=str,
        help="Токен API, см. README.md",
        metavar="ТОКЕН",
        dest='api_token'
    )
    global args
    args = arg_parser.parse_args()

    print('init vk_api...')
    # noinspection PyBroadException,PyUnusedLocal
    try:
        vk_session = vk_api.VkApi(
            token=args.api_token,
            config_filename=os.path.join(tempfile.gettempdir(), 'laszlo_vk_data.json'),
            api_version=str(VK_VER)
        )
        # vk_session.auth(token_only=True)
        global vk
        vk = vk_session.get_api()
    except Exception as e:
        err_msg = "Ошибка при попытке залогиниться!\n\nПодробнее:\n{}".format(
            traceback.format_exc()
        )
        print(err_msg, file=sys.stderr)
        return EXIT_VK_API

    if args.debug:
        schedule.every(2).seconds.do(test_job).tag('test-job')
    else:
        schedule.every(args.days).do()

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
    print("stopping...")
    sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    print("init...")
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    # noinspection PyBroadException
    try:
        sys.exit(main())
    except Exception as exc:
        err_str = """
Случилась неведомая хрень...

Если это не проблемы с сетью или сервером VK, то:
Напишите в https://github.com/saber-nyan/laszlo-vk-bot/issues или на
saber-nyan@ya.ru и приложите:

{}""".format(traceback.format_exc())
        print(err_str, file=sys.stderr)
        sys.exit(EXIT_UNKNOWN)
