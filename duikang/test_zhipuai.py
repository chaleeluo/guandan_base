#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/1 12:25 下午
# @Author  : luoyiwen
# @File    : test_zhipuai.py

import os

from action.make_act import GuandanLLM
from action.setting import Settings
from utils import *
from rule import gdgame
from agent import GuaDannAgent
import json
from rich.console import Console


env = gdgame.GDGameEnv(1)
agent = GuaDannAgent()
console = Console()
settings = Settings()

guandanLLM = GuandanLLM()

def run_one_game(i):
    env.ResetGameDeck()
    history_data = []  # 用于保存历史信息的列表
    round_number = 1  # 用于记录当前轮数
    bot_long_memory = []
    bot_short_memory = []
    for _ in range(4):
        bot_short_memory.append([f'{i + 1}th Game Start'])
        bot_long_memory.append([f'{i + 1}th Game Start'])
    while not env.CheckGameOver():
        boardinfo = env.GetBoardInfo("v3")
        avails = boardinfo.acts
        candidates = []
        choice_llm = []
        for avail in avails:
            candidates.append({'pattern': avail.pattern, 'value': avail.value, 'cards': avail.cards})
        candidates_results = parse_candidates(candidates)
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
        history_data = parse_history(history)
        # print('其他玩家出牌', other_user)
        # c = random.choice(candidates)
        # print('自己选择的出牌', c)
        if currseatid == 0:
            opponent_name = [1, 3]
            teammate_name = [2]
            act, comm, bot_short_memory, bot_long_memory = guandanLLM.make_act(history_data[-1:], opponent_name, currseatid, teammate_name,
                                                                                   candidates_results,
                                                                                   True, i, round_number,
                                                                                   bot_short_memory=bot_short_memory,
                                                                                   bot_long_memory=bot_long_memory,
                                                                                   console = console,
                                                                                   log_file_name = '',
                                                                                   mode = "second_tom")

            print("act is ", act, comm, bot_short_memory, bot_long_memory)

                # try:
                # output = agent.generate_decision(history_data[-1:], other_user, parsed_results, True)
                #    act, comm, bot_short_memory, bot_long_memory = guandanLLM.make_act(history_data[-1:], other_user, 0, parsed_results,
                #                                 i, round_number, verbose_print=True, bot_short_memory=bot_short_memory, bot_long_memory=bot_long_memory,
                #                                 )
                #    print("act is ", act, comm, bot_short_memory, bot_long_memory)

                #    choice_llm = candidates[int(act)]
                # except:
                #    choice_llm = rule_based_combination(candidates, rule='bestP_lowV')



            env.HandPlay(currseatid, choice_llm['pattern'], choice_llm['cards'])
            print('llm输出选择', parse_candidates([choice_llm]))
        else:
            choice_llm = []
            choice = rule_based_combination(candidates, rule='random')
            env.HandPlay(currseatid, choice['pattern'], choice['cards'])
            # print('seatid0过牌')
        # 将当前轮次的历史信息保存到列表中
        # 构造round_info
        round_info = {
            'round': round_number,
            'player_actions': history_data,
            'self_action': candidates_results([choice_llm]) if choice_llm else {"seatid": 0, "pattern": "过牌", "cards": []}
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

    long_memory = '\n'.join(history_data)

    memory_summarization = guandanLLM.get_summarization(history_data, long_memory, history_data, no_highsight_obs=True)

    guandanLLM.add_long_memory(f"{i + 1}th Game Start! \n" + memory_summarization)

    rewards = env.GetReward()  ##只有最后才会出来reward
    print(f'rewards ===========>  {rewards}')
    return rewards[0]


if __name__ == '__main__':
    score = 0
    times = 10
    scores = []
    count = 0
    for i in range(times):
        count += 1
        score += run_one_game(i)
        scores.append(score / count)
        print(f'average scores over {count} games, is {score / count}')
        print('scores', scores)