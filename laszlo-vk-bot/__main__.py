# -*- coding: utf-8 -*-
"""
Наш основной модуль~
"""

import signal
import sys
import traceback


EXIT_SUCCESS = 0
EXIT_UNKNOWN = 256


def main():
    """
    Собственно, основной метод...

    :return: код возврата
    """
    return EXIT_SUCCESS


# noinspection PyUnusedLocal
def exit_handler(sig, frame):
    """
    Обработчик сигнала остановки.

    :param sig: тип сигнала, здесь ``SIGINT`` или ``SIGTERM``
    :param frame: фрейм, во время выполнения которого был пойман сигнал
    """
    return EXIT_SUCCESS


if __name__ == '__main__':
    print("init...")
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    # noinspection PyBroadException
    try:
        sys.exit(main())
    except Exception as exc:
        err_str = """Случилась неведомая хрень...
        Если это не проблемы с сетью или сервером VK, то:
        Напишите в https://github.com/saber-nyan/laszlo-vk-bot/issues или на
        saber-nyan@ya.ru и приложите:
        
        {}""".format(traceback.format_exc())
        print(err_str, file=sys.stderr)
        sys.exit(EXIT_UNKNOWN)
