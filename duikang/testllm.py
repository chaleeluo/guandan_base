import os
import sys
import numpy as np
import random
from rule import gdgame
from utils import *
from agent import GuaDannAgent
import json

env = gdgame.GDGameEnv(1)
agent=GuaDannAgent()
def run_one_game(i):
    env.ResetGameDeck()
    history_data = []  # 用于保存历史信息的列表
    round_number = 1  # 用于记录当前轮数
    while not env.CheckGameOver():
        boardinfo = env.GetBoardInfo("v3")
        avails = boardinfo.acts
        candidates = []
        choice_llm=[]
        for avail in avails:
            candidates.append({'pattern': avail.pattern, 'value': avail.value, 'cards': avail.cards})
        parsed_results = parse_candidates(candidates)
        # print('当前自己手牌', parsed_results)
        currseatid = boardinfo.currseatid
        # print('current seat id',currseatid)
        gameinfo = env.GetGameInfo()
        mainface = gameinfo.mainface
        maincardid = gameinfo.maincardid
        hands = [x for x in boardinfo.mulhandcards[currseatid]]
        history = []
        for h in gameinfo.actions:
            history.append({'seatid': h.seatid, 'pattern': h.pattern, 'cards': h.cards})
        other_user = parse_history(history)
        # print('其他玩家出牌', other_user)
        # c = random.choice(candidates)
        # print('自己选择的出牌', c)
        if currseatid ==0:
            try:
                output = agent.generate_decision(history_data[-1:],other_user, parsed_results)
                choice_llm=candidates[int(output)]
            except:
                choice_llm=rule_based_combination(candidates,rule='bestP_lowV')
            
            env.HandPlay(currseatid, choice_llm['pattern'],choice_llm['cards'])
            print('llm输出选择', parse_candidates([choice_llm]))
        else:
            choice_llm=[]
            choice = rule_based_combination(candidates,rule='random')
            env.HandPlay(currseatid, choice['pattern'],choice['cards'])
            print('seatid0过牌')
        # 将当前轮次的历史信息保存到列表中
        # 构造round_info
        round_info = {
            'round': round_number,
            'player_actions': other_user,
            'self_action': parse_candidates([choice_llm]) if choice_llm else {"seatid": 0, "pattern": "过牌", "cards": []}
        }
        history_data.append(round_info)

        # 执行动作
        
        
        round_number += 1  # 轮次加1
        # if round_number>3:
        #     break ## for debug purpose
        
        # 将历史信息保存为JSON文件
        output_dir = 'memory'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'history{i}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False)


    rewards = env.GetReward() ##只有最后才会出来reward
    print(f'rewards ===========>  {rewards}')
    return rewards[0]





if __name__ == '__main__':
    score=0
    times=10
    scores=[]
    count=0
    for i in range(times):
        count+=1
        score+=run_one_game(i)
        scores.append(score/count)
        print(f'average scores over {count} games, is {score/count}')
        print('scores',scores)