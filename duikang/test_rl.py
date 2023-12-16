#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 8:43 上午
# @Author  : luoyiwen
# @File    : test_rl.py
import json
import os
import sys

import numpy as np
import random

from .utils import rule_based_combination, rl_based_combination
from rule import gdgame
from utils import *

env = gdgame.GDGameEnv(1)


def run_one_game():
    env.ResetGameDeck()
    round_number = 1
    while not env.CheckGameOver():
        boardinfo = env.GetBoardInfo("v3")
        avails = boardinfo.acts
        candidates = []
        print('round number', round_number)
        for avail in avails:
            candidates.append({'pattern': avail.pattern, 'value': avail.value, 'cards': avail.cards})  ##自己玩家的出牌信息
        # print('candidates',parse_candidates(candidates))
        currseatid = boardinfo.currseatid

        gameinfo = env.GetGameInfo()
        mainface = gameinfo.mainface
        maincardid = gameinfo.maincardid
        hands = [x for x in boardinfo.mulhandcards[currseatid]]
        history = []
        for h in gameinfo.actions:
            history.append({'seatid': h.seatid, 'pattern': h.pattern, 'cards': h.cards})  ##其他玩家的信息
        # 选择动作
        if currseatid == 0:
            c = rl_based_combination(currseatid, hands, gameinfo.actions, maincardid, gameinfo.GetFirstPlay(), gameinfo.GetRanking())
            # print('xaunze',parse_candidates([c]))
        else:
            c = rule_based_combination(candidates, rule='random')
        env.HandPlay(currseatid, c['pattern'], c['cards'])
        round_number += 1
    rewards = env.GetReward()
    print(f'rewards ===========>  {rewards}')
    print('current seat id', currseatid)
    return rewards[0]


if __name__ == '__main__':
    score = 0
    times = 100
    for i in range(times):
        score += run_one_game()
    print(f'average scores over {times} games, is {score / times}')