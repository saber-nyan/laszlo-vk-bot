# -*- coding: utf-8 -*-
"""
Состояние нашего бота.
"""
from typing import List


class BotState:
    """
    Состояние бота.
    """

    last_post_id: int
    """
    ID последнего поста *с правилами*, для удаления.
    """

    used_rules: List[int]
    """
    Список хэшей исползованных правил, для предотвращения повторений.
    Впрочем, если правила кончатся, то идем по кругу.
    
    Хэшируется как ``hash(frozenset(o[0].items()))``
    """

    now_ticks: int
    """
    Количество прошедших тиков.
    """

    trigger_count: int
    """
    Количество срабатываний (смен правила).
    """

    def __init__(self):
        self.last_post_id = None
        self.used_rules = []
        self.now_ticks = 0
        self.trigger_count = 0

    def __str(self):
        return "STATE: Last post #{}; used {}".format(self.last_post_id,
                                                      self.used_rules)

    def __repr__(self):
        return self.__str()

    def __str__(self):
        return self.__str()
