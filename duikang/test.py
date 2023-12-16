import os
import sys
import numpy as np
import random
from rule import gdgame

env = gdgame.GDGameEnv(1)

def run_one_game():
    env.ResetGameDeck()
    round_number =1
    history = []

    while not env.CheckGameOver() :
        boardinfo = env.GetBoardInfo("v3")
        avails = boardinfo.acts 
        candidates = []
        print('round number',round_number)
        for avail in avails :
            candidates.append({'pattern':avail.pattern , 'value':avail.value , 'cards':avail.cards}) ##自己玩家的出牌信息
        print('candidates',candidates)
        currseatid = boardinfo.currseatid
        print('currentsead',currseatid)
        gameinfo = env.GetGameInfo()
        mainface = gameinfo.mainface
        maincardid = gameinfo.maincardid
        hands = [x for x in boardinfo.mulhandcards[currseatid]]
        for h in gameinfo.actions :
            history.append({'seatid':h.seatid , 'pattern':h.pattern , 'cards':h.cards}) ##其他玩家的信息
        print('history',history)
        #随机选择动作
        if currseatid ==0: ## seatid=0为自己玩家
            c=candidates[0]
        else:
            c = random.choice(candidates)
        print('c',c)
        env.HandPlay(currseatid , c['pattern'] , c['cards'])
        round_number += 1 
    rewards = env.GetReward()
    print(f'rewards ===========>  {rewards}')
    print('current seat id',currseatid)


if __name__ == '__main__':
    run_one_game()