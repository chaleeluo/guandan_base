#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/1 7:43 下午
# @Author  : luoyiwen
# @File    : make_act.py

from datetime import datetime

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from typing import List, Optional, Tuple
from langchain.base_language import BaseLanguageModel
from pydantic import BaseModel, Field
import time

import zhipuai

from . import util
from .zhipuai_llm import ZhipuAILLM

zhipuai.api_key = "e5014084d3b10bafbb65a0e9cb1c9be2.WJlAemhCXKHBSKqH" #填写控制台中获取的 APIKey 信息
zhipuai_model = ZhipuAILLM(model="chatglm_std", temperature=0, zhipuai_api_key=zhipuai.api_key)

class GuandanLLM():

    def __init__(self,):
        self.llm = ZhipuAILLM(model="chatglm_std", temperature=0, zhipuai_api_key=zhipuai.api_key)
        template = """{question}\n\n"""
        self.prompt = PromptTemplate(template=template, input_variables=["question"])


    """A character with memory and innate characteristics."""
    game_name = '惯蛋'
    rule = '掼蛋游戏的技巧包括记牌、进贡回贡、炸弹使用、红桃配配、双贡打牌、控牌、送牌、抓牌、插牌、理牌、组火和冲刺等多个方面。要记住牌的分布，善用炸弹、配好红桃、灵活运用各种牌型，尤其在双贡和冲刺时要善于判断时机。' \
           '座位序号为0和座位序号为2的为队友，座位序号为1和座位序号为3的为队友'
    observation_rule = "observation是一个字典, 主要记录的是: 'seatid'代表玩家位置, 'pattern'代表出牌模式, 'cards'代表具体出的牌"
    game_pattern = ''
    name: str = ''
    # game_name: str
    # observation_rule: str
    """The traits of the character you wish not to change."""
    """Current activities of the character."""
    llm: BaseLanguageModel

    """The retriever to fetch related memories."""
    verbose: bool = False

    belief: str = ""
    pattern: str = ""
    long_belief: str = ""
    counter_belief: str = ""
    plan: str = ""
    high_plan: str = ""
    """The current plan of the agent."""

    memory: List = ['']
    summary: str = ""  #: :meta private:
    summary_refresh_seconds: int = 3600  #: :meta private:
    last_refreshed: datetime = Field(default_factory=datetime.now)  #: :meta private:

    memory_importance: float = 0.0  #: :meta private:
    max_tokens_limit: int = 1200  #: :meta private:
    read_observation: str = ""  #: :meta private:

    # rule: str = ""  #: :meta private:
    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    # 先拆牌 逢人配 算牌力 评估主助攻  记牌

    def make_act(self, observation: str, opponent_name: str, player_index: int, teammate_name: int, valid_action_list: List,
                 verbose_print: bool, game_idx: int, round: int, bot_short_memory: List, bot_long_memory: List, console,
                 log_file_name='', mode='second_tom') -> Tuple[bool, str]:
        readable_text_amy_obs = self.convert_obs(observation, opponent_name, player_index, teammate_name, valid_action_list)
        if verbose_print:
            console.print('readable_text_obs: ', style="red")
            print(readable_text_amy_obs)

        time.sleep(0)
        if len(bot_short_memory[player_index]) == 1:
            short_memory_summary = f'{game_idx + 1}th Game Start \n' + readable_text_amy_obs
        else:
            short_memory_summary = self.get_short_memory_summary(observation=readable_text_amy_obs,
                                                                 recipient_name=opponent_name,
                                                                 teammate_name=teammate_name,
                                                                 short_memory_summary='\n'.join(
                                                                     bot_short_memory[player_index]))

        if verbose_print:
            console.print('short_memory_summary: ', style="yellow")
            print(short_memory_summary)

        time.sleep(0)
        if round <= 1:
            self.pattern = self.get_pattern(opponent_name, teammate_name, self.game_pattern, short_summarization=short_memory_summary, mode=mode)
            console.print('pattern: ', style="blue")
            print(self.pattern)

        time.sleep(0)
        print(opponent_name)

        if mode == 'second_tom' or mode == 'first_tom':
            belief = self.get_belief(readable_text_amy_obs, opponent_name, short_memory_summary=short_memory_summary,
                                     pattern=self.pattern, mode=mode)
            if verbose_print:
                console.print(self.name + " belief: ", style="deep_pink3")
                print(self.name + " belief: " + str(belief))

        else:
            belief = ''

        time.sleep(0)
        plan = self.planning_module(readable_text_amy_obs, opponent_name, belief=belief,
                                    valid_action_list=valid_action_list, short_memory_summary=short_memory_summary,
                                    pattern=self.pattern, last_plan='', mode=mode)
        if verbose_print:
            console.print(self.name + " plan: ", style="orchid")
            print(self.name + " plan: " + str(plan))

        time.sleep(0)
        promp_head = ''
        act, comm = self.action_decision(readable_text_amy_obs, valid_action_list, promp_head,
                                         short_memory_summary=short_memory_summary)

        if log_file_name is not None:
            util.get_logging(logger_name=log_file_name + '_obs',
                             content={str(game_idx + 1) + "_" + str(round): {"raw_obs": observation,
                                                                             "readable_text_obs": readable_text_amy_obs}})
            util.get_logging(logger_name=log_file_name + '_short_memory',
                             content={str(game_idx + 1) + "_" + str(round): {
                                 "raw_short_memory": '\n'.join(bot_short_memory[player_index]),
                                 "short_memory_summary": short_memory_summary}})
            util.get_logging(logger_name=log_file_name + '_pattern_model',
                             content={str(game_idx + 1) + "_" + str(round): self.pattern})
            util.get_logging(logger_name=log_file_name + '_belief',
                             content={str(game_idx + 1) + "_" + str(round): {
                                 "belief": str(belief)}})
            util.get_logging(logger_name=log_file_name + '_plan',
                             content={str(game_idx + 1) + "_" + str(round): {
                                 "plan": str(plan)}})
            util.get_logging(logger_name=log_file_name + '_act',
                             content={str(game_idx + 1) + "_" + str(round): {
                                 "act": str(act), "talk_sentence": str(comm)}})

        while act not in valid_action_list:
            print('Action + ', str(act), ' is not a valid action in valid_action_list, please try again.\n')
            promp_head += 'Action {act} is not a valid action in {valid_action_list}, please try again.\n'
            act, comm = self.action_decision(readable_text_amy_obs, valid_action_list, promp_head, act)
        print(self.name + " act: " + str(act))
        print(comm)

        bot_short_memory[player_index].append(
            f"{self.name} have the observation {readable_text_amy_obs}, try to take action: {act} and say {comm} to {opponent_name}")
        bot_short_memory[((player_index + 1) % 2)].append(
            f"{self.name} try to take action: {act} and say {comm} to {opponent_name}")

        bot_long_memory[player_index].append(
            f"{self.name} have the observation {observation}, try to take action: {act} and say {comm} to {opponent_name}")
        return act, comm, bot_short_memory, bot_long_memory



    def add_long_memory(self, memory_content: str) -> List[str]:
        """Add an observation or memory to the agent's memory."""
        self.memory.append(memory_content)
        return self.memory

    def planning_module(self, observation: str, recipient_name: str, previous_conversation: List[str] = None,
                        belief: str = None, valid_action_list: List[str] = None, short_memory_summary: str = "",
                        pattern: str = "", last_plan: str = "", mode: str = "second_tom") -> str:
        """Make Plans and Evaluate Plans."""
        """Combining these two modules together to save costs"""

        if mode == 'second_tom':
            prompt = PromptTemplate.from_template(
                "你是一个背后观测NPC角色的客观玩家{initiator_name}, 你在和{recipient_name}一起玩名为{game_name}的游戏"
                + " 这个游戏的规则是: {rule} \n"
                + '{pattern}\n'
                + " 你现在对游戏状态的观察是: {observation}\n"
                + '{belief}\n'
                + " 理解了所有的信息，你能做以下事情吗:"
                + " 制定合理的计划:请根据你现在可以玩的动作{valid_action_list}规划几个策略，逐步赢得最终的整个{game_name}游戏。"
                + " 潜在{recipient_name}的动作和估计每个计划的赢/输/抽率:从{recipient_name}的角度，请推断{recipient_name}持有不同牌时{recipient_name}的动作(归一化到总数为100%)的概率，然后逐步计算{recipient_name}持有不同牌时的赢/输/抽率。”最后，请考虑{recipient_name}的行为模式，逐步计算每个计划的总体赢/输/平局率。树状结构的输出:"
                + " 输出:计划1:如果我执行计划1时的胜率/败率/平局率"
                  "计划1总体{initiator_name}的胜率/败率/平局率:计划1的胜率(概率)是"
                  "计划2:如果我执行计划2，{recipient_name}持有card1时的赢/输/平局率…"
                  "计划3:……继续……"
                + " 每个计划的收益数:了解你目前的观察，每个新计划，请逐步推断每个计划的赢/输收益数，输出:Plan1:行动后，锅中所有筹码:如果赢，获胜收益为(根据获胜收益规则逐步计算);行动后，锅中所有筹码:如果输，失败收益为:(根据失败收益规则逐步计算)。计划二:动作结束后，锅中所有筹码:如果赢了，赢筹码为(按获胜收益规则逐级计算);动作结束后，锅中所有筹码:如果输了，输筹码为(按失败收益规则逐级计算)。如果我在锅里的筹码数量没有变化，请直接输出。"
                + " 估计每个计划的预期筹码增益:了解所有信息并估计每个计划的赢/输/平局率，请通过逐步计算胜率*(游戏规则中的获胜收益规则)-赔率*(游戏规则中的失败收益规则)来估计当前游戏中每个计划/策略的总体平均预期筹码增益"
                + " 计划选择:请客观地逐级输出每个计划的预计芯片增益排名，并在考虑策略改进的情况下，选择预计芯片增益最高的计划/策略。"
            )

        elif mode == 'first_tom':
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色{initiator_name}后面的玩家，你正在和{recipient_name}玩棋盘游戏{game_name}。"
                + " 这个游戏的规则是: {rule} \n"
                + '{pattern}\n'
                + " 你现在对游戏状态的观察是: {observation}\n"
                + '{belief}\n'
                + " 理解了所有的信息，你能做以下事情吗:"
                + " 制定合理的计划:请根据你现在可以玩的动作{valid_action_list}规划几个策略，逐步赢得最终的整个{game_name}游戏。"
                + " 潜在的{recipient_name}的动作和估计输赢/平局率:从{recipient_name}的角度，请推断{recipient_name}持有不同牌时{recipient_name}的动作有概率(归一化到总数100%)会发生什么，然后逐步计算{recipient_name}持有不同牌时的输赢/平局率。”树状结构的输出"
                + " 输出:基于{recipient_name}的行为模式和{recipient_name}的卡片分析"
                  "总体{initiator_name}的胜率/败率/平局率:根据上面的分析，胜率(概率)是"
                + " 关于每个计划的赢和输的回报数量的潜在信念:了解游戏规则，你目前的观察，以前的行动总结，每个新计划，赢的回报规则，输的回报规则，请逐步推断你对每个计划的筹码数量的几个信念，输出:Plan1:筹码在锅中:如果赢了，获胜的回报将是(根据游戏规则中的获胜回报规则计算):动作结束后，如果输了，损失的收益为:。计划二:锅中筹码:如果赢了，获胜筹码为(根据游戏规则中的获胜收益规则计算):动作结束后，如果输了，输掉的筹码为。如果我在锅里的筹码数没有变化，请直接输出"
                + " 估计每个计划的预期筹码增益:了解游戏规则，计划和您对{game_name}的了解，请通过计算胜率*(游戏规则中的获胜收益规则)-赔率*(游戏规则中的失败收益规则)来估计当前游戏中每个计划/策略的总体平均预期筹码增益。”解释不选择方案的结果是什么，并解释为什么最终的预期芯片增益是合理的一步一步的?"
                + " 计划选择:请客观地逐级输出每个计划的预计芯片增益的排名，并考虑策略i，选择预计芯片增益最高的计划/策略。"
            )
        else:
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色{initiator_name}后面的玩家，你正在和{recipient_name}玩棋牌游戏{game_name}。"
                + " 这个游戏的规则是: {rule} \n"
                + '{pattern}\n'
                + " 你现在对游戏状态的观察是: {observation}\n"
                + " 理解了所有的信息，你能做以下事情吗:"
                + " 制定合理的计划:请根据你现在可以玩的动作{valid_action_list}规划几个策略，逐步赢得最终的整个{game_name}游戏。"
                + " 估计每个计划的赢/输/平局率:了解给定的信息，以及您对{game_name}的了解，请按照示例一步一步估计每个计划的每一步成功率和当前游戏中每个计划/策略的总体平均赢/输/平局率(归一化到总数为100%):如果我做计划1，因为我持有牌，公开信息(如果发布)和单局赢/平/输规则，我将赢或输或平(概率);…继续……总体胜率/平局率/输球率:根据分析，我可以一步一步地进行加权平均，得到总体加权平均胜率为(概率)，平均输球率为(概率)，平局率为(概率)(归一化到总数100%)"
                + " 潜在认为获胜的数量和失去偿付计划:了解游戏规则,你目前的观察,总结之前的动作,每一个新的计划,赢得回报法则,失去偿付规则,请推断几个相信关于锅的芯片数量为每个计划一步一步,输出:Plan1:薯片罐:如果获胜,获胜的回报将是(通过赢得回报计算规则的游戏规则):行动后,芯片在锅:如果输了，损失的收益是:。计划二:下注筹码:如果赢了，获胜筹码为(根据游戏规则中获胜收益规则计算):动作结束后，下注筹码:如果输了，输掉的筹码为。如果我在锅里的筹码数没有变化，请直接输出。"
                + " 估计每个计划的预期筹码增益:了解游戏规则，计划和您对{game_name}的了解，请通过计算胜率*(游戏规则中的获胜收益规则)-赔率*(游戏规则中的失败收益规则)来估计当前游戏中每个计划/策略的总体平均预期筹码增益。”解释不选择方案的结果是什么，并解释为什么最终的预期芯片增益是合理的一步一步的?"
                + " 计划选择:请客观地逐级输出每个计划的预计增益排名，并在考虑策略改进的情况下，选择预计增益最高的计划/策略。"
            )

        agent_summary_description = short_memory_summary

        belief = self.belief if belief is None else belief

        kwargs = dict(

            recent_observations=agent_summary_description,
            last_plan=last_plan,
            belief=belief,
            initiator_name=self.name,
            pattern=pattern,
            recipient_name=recipient_name,
            observation=observation,
            rule=self.rule,
            game_name=self.game_name,
            valid_action_list=set([v['pattern'] for v in valid_action_list])
        )

        plan_prediction_chain = LLMChain(llm=self.llm, prompt=prompt)
        self.plan = plan_prediction_chain.run(**kwargs)
        self.plan = self.plan.strip()

        return self.plan.strip()

    def get_belief(self, observation: str, recipient_name: str, short_memory_summary: str, pattern: str = "",
                   mode: str = "second_tom") -> str:
        """React to get a belief."""
        if mode == 'second_tom':
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色{agent_name}后面的玩家，你正在和{recipient_name}玩棋盘游戏{game_name}"
                + " 游戏规则是: {rule} \n"
                + " 你对{recipient_name}的行为模式和改进策略的估计判断是:{pattern} \n"
                + " 你现在的观测值是: {observation}\n"
                + " 你当前的游戏进度总结，包括与{recipient_name}的动作和对话: {recent_observations}\n"
                + " 了解游戏规则，你的牌，你的观察，当前游戏的进度总结，{recipient_name}的估计行为模式，{recipient_name}对你的潜在猜测模式，以及你对{game_name}的了解，你能做以下事情吗?"
                + " 分析我的牌:了解所有给定的信息和你对{game_name}的了解，请逐步分析你的牌在当前回合中的最佳组合和优势。"
                + " 对{recipient_name}牌的信念:理解所有给定的信息，请逐步客观地推断{recipient_name}牌的概率(归一化到总数100%)。"
                  "输出:{recipient_name}看到了我的历史操作(或没有)，然后在第一轮执行了action1(概率)，…继续……在这一轮之前，{recipient_name}说我的历史动作(或没有)和做过的动作1(概率)，因为{recipient_name}的行为模式和与公共牌的匹配(如果释放)，{recipient_name}倾向于有card1(概率)，card2(概率)…继续…(归一化到总数100%)。"
                + " {recipient_name}牌分析:理解所有给定的信息和你对{game_name}牌的了解，逐步分析{recipient_name}牌在当前回合中的最佳组合和优势是什么"
                +   "潜在的{recipient_name}当前对你的牌的信念:理解所有给定的信息和你对{game_name}的知识，如果你是{recipient_name}(他只能观察我的动作，不能看到我的牌)，请逐步推断{recipient_name}对你牌的信念的概率(归一化到总数100%)"
            )
        elif mode == 'first_tom':
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色{agent_name}后面的玩家，你正在和{recipient_name}玩棋盘游戏{game_name}。"
                + " 游戏规则是: {rule} \n"
                + " 你对{recipient_name}的行为模式和改进策略的估计判断是:{pattern}"
                + " 你现在的观测值是: {observation}\n"
                + " 你当前的游戏进度总结，包括与{recipient_name}的动作和对话:{recent_observations}"
                + " 了解游戏规则，你的牌，你在当前游戏中的观察，进度总结，{recipient_name}的估计行为模式，以及你对{game_name}的了解，你能做以下事情吗?"
                + " 分析我的牌:了解所有给定的信息，请逐步分析你的牌在当前回合中的最佳组合和优势。"
                + " 对{recipient_name}牌的信念:理解所有给定的信息，请逐步推断{recipient_name}牌的概率(归一化到总数100%)。"
                + " {recipient_name}牌分析:理解所有给定的信息，请逐步分析{recipient_name}牌在本轮中的最佳组合和优势是什么。"

            )
        agent_summary_description = short_memory_summary

        kwargs = dict(
            agent_summary_description=agent_summary_description,
            recent_observations=agent_summary_description,
            agent_name=self.name,
            pattern=pattern,
            recipient_name=recipient_name,
            observation=observation,
            game_name=self.game_name,
            rule=self.rule

        )
        print(recipient_name)

        belief_prediction_chain = LLMChain(llm=self.llm, prompt=prompt)
        self.belief = belief_prediction_chain.run(**kwargs)
        self.belief = self.belief.strip()
        return self.belief.strip()

    def get_pattern(self, recipient_name: str, teammate_name: str, game_pattern: str = '', last_k: int = 20, short_summarization: str = '',
                    mode: str = 'second_tom') -> str:
        """React to get a belief."""

        if mode == 'second_tom':
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色背后的玩家{agent_name}，你正在和对手{recipient_name}玩{game_name}"
                + "游戏规则是: {rule} \n"
                + " 你之前的游戏记忆包括观察，动作: {long_memory}\n"
                + "理解所有给定的信息和你对{game_name}的理解，请推断和估计尽可能多的合理{recipient_name}的游戏行为模式/偏好对于他每一轮对每个模式项归一化到总数的100%，也请推断他的牌的优势，并分析{recipient_name}的行为模式/偏好是如何受到我的行动的影响的，当他一步步持有不同的牌。输出为树状结构"
                + "输出:{}"
                + "{recipient_name}对我的游戏模式的猜测:理解所有给定的信息，请从{recipient_name}的角度推断出我在持有不同牌时的游戏模式/偏好的几个合理信念(请考虑每轮游戏中牌的优势，动作以及与公共牌(如果发布)的匹配)的详细情况，以树状结构逐步输出"
                + "输出:{}"
                + "“策略改进”:理解以上信息，思考我可以采用什么策略来开发{recipient_name}的博弈模式，以及{recipient_name}对我在整个博弈中赢得{recipient_name}的博弈模式的猜测。(注意，在游戏过程中你不能观察对手的牌，但你可以观察他的行动)。输出为树状结构"
            )
        elif mode == 'first_tom':
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色背后的玩家{agent_name}，你正在和{recipient_name}玩{game_name}"
                + "游戏规则是: {rule} \n"
                + " 你之前的游戏记忆包括观察，动作: {long_memory}\n"
                + " 请了解游戏规则，之前所有的游戏历史和你对{game_name}的了解，你能在未来的游戏中做以下事情吗? "
                + " {recipient_name}的游戏模式:理解所有给定的信息，请推断出{recipient_name}每一轮的所有可能合理的游戏模式/偏好，并对每个模式项目归一化逐步作为树结构输出"
                + "输出: {}"
                + "反思:反思你在之前的游戏中对或错的行动，一步一步地赢得或失去具体的筹码(注意，你不能在游戏中观察对手的牌，但你可以观察他的行动)"
                + "策略提升:了解以上信息，思考我可以采用什么策略来开发{recipient_name}的游戏模式，在整个游戏中逐步赢得{recipient_name}。(注意，在游戏过程中你不能观察对手的牌，但你可以观察他的行动)。输出为树状结构"
            )
        else:
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色背后的玩家{agent_name}，你正在和{recipient_name}玩{game_name}"
                + "游戏规则是: {rule} \n"
                + " 你之前的游戏记忆包括观察，动作: {long_memory}\n"
                + " 请了解游戏规则，之前所有的游戏历史和你对{game_name}的了解，你能在未来的游戏中做以下事情吗? "
                + "反思:反思你在之前的游戏中对或错的行动，一步一步地赢得游戏"
                + "策略提升:了解以上信息，思考我可以采用什么策略来开发{recipient_name}的游戏模式，在整个游戏中逐步赢得{recipient_name}。(注意，在游戏过程中你不能观察对手的牌，但你可以观察他的行动)。输出为树状结构"
            )
        reflection_chain = LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)
        long_memory = self.memory[-last_k:]
        long_memory_str = "\n\n".join([o for o in long_memory])

        kwargs = dict(
            long_memory=long_memory_str,
            game_pattern=game_pattern,
            agent_name=self.name,
            recipient_name=recipient_name,
            teammate_name=teammate_name,
            game_name=self.game_name,
            rule=self.rule

        )
        # print(kwargs)

        self.long_belief = reflection_chain.run(**kwargs)
        self.long_belief = self.long_belief.strip()
        return self.long_belief.strip()

    def get_summarization(self, recipient_name: str, game_memory: str, opponent_name: str,
                          no_highsight_obs: bool) -> str:
        """Get a long memory summarization to save costs."""
        if no_highsight_obs:
            prompt = PromptTemplate.from_template(
                "你是一个NPC角色{agent_name}后面的玩家，你正在和{recipient_name}玩棋盘游戏{game_name}。"
                + " 游戏规则是:{{rule} \n"
                + " 观测值转换规则为: {observation_rule}\n"
                + " 一个游戏记忆包括观察，行动和对话{recipient_name}是:{long_memory}"
                + " 了解游戏规则，观察游戏转换规则和游戏历史以及你对{game_name}的了解，你能做以下事情吗?"
                + " 历史总结:用行动、观察和结果信息总结游戏历史?在第一个游戏的第一轮中，name持有card1做动作....继续……"
                + " {对手牌}的牌推理:如果{对手牌}不可用，因为{agent_name}的牌是xx，公共牌(如果释放)是xxx，{对手牌}的行为是xx，所以当前的游戏结果是xx，请根据你对以上所有信息的理解，自信地一步一步以概率(总共100%)推断出{对手牌。"
            )
        else:
            prompt = PromptTemplate.from_template(
                " 你是一个NPC角色{agent_name}后面的玩家，你正在和{recipient_name}玩棋盘游戏{game_name}。"
                + " 游戏规则是: {rule} \n"
                + " 观测值转换规则为: {observation_rule}\n"
                + " 一个游戏记忆包括观察，行动和对话{recipient_name}是:{long_memory}"
                + " 了解游戏规则，观察游戏转换规则和游戏历史以及你对{game_name}的了解，你能做以下事情吗?"
                + " 历史总结:用行动、观察和结果信息总结游戏历史?在第一个游戏的第一轮中，name持有card1做动作....继续……"
            )
        reflection_chain = LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)
        kwargs = dict(
            observation_rule=self.observation_rule,
            long_memory=game_memory,
            agent_name=self.name,
            recipient_name=recipient_name,
            opponent_name=opponent_name,
            # observation=observation,
            game_name=self.game_name,
            rule=self.rule

        )
        # print(kwargs)

        self.long_belief = reflection_chain.run(**kwargs)
        self.long_belief = self.long_belief.strip()
        return self.long_belief.strip()

    def get_short_memory_summary(self, observation: str, recipient_name: str, teammate_name: str, short_memory_summary: str) -> str:
        """React to get a belief."""
        prompt = PromptTemplate.from_template(
            "你是一个NPC角色背后的玩家{agent_name}，你正在和对手{recipient_name}，队友{teammate_name}玩{game_name}"
            + " 这个游戏的规则是: {rule} \n"
            + " 你现在的观察是: {observation}\n"
            + " 当前的游戏历史包括之前的行动，观察和对话: {agent_summary_description}\n"
            + " 根据游戏规则，你的观察和你对{game_name}的了解，请总结一下当前的历史。输出为树结构，并简短响应: "
        )

        agent_summary_description = short_memory_summary

        kwargs = dict(
            agent_summary_description=agent_summary_description,
            recent_observations=agent_summary_description,
            agent_name=self.name,
            teammate_name=teammate_name,
            recipient_name=recipient_name,
            observation=observation,
            game_name=self.game_name,
            rule=self.rule

        )

        belief_prediction_chain = LLMChain(llm=self.llm, prompt=prompt)
        self.belief = belief_prediction_chain.run(**kwargs)
        self.belief = self.belief.strip()
        return self.belief.strip()

    def convert_obs(self, observation: str, recipient_name: str, user_index: str, teammate_name: str, valid_action_list: str) -> str:
        """React to get a belief."""
        prompt = PromptTemplate.from_template(
            "你是一个NPC角色背后的玩家{agent_name}，序号是{user_index}，你正在玩{game_name}，你和{teammate_name}是队友，和{recipient_name}是对手"
            + " 这个游戏的规则是: {rule} \n"
            + " 你目前观测到的信息是: {observation}\n"
            + " 你将收到一个有效的动作列表，你可以在此回合中执行 \n"
            + " 你的有效的动作列表是: {valid_action_list}\n"
            + " 观测值转换规则为: {observation_rule}\n"
            + " 请根据可读文本和你的知识，将{observation} 和 {valid_action_list}转换为{game_name}这个游戏的可读文本 (简短即可).\n"
        )
        kwargs = dict(
            user_index=user_index,
            teammate_name=teammate_name,
            agent_name=self.name,
            rule=self.rule,
            recipient_name=recipient_name,
            observation=observation,
            valid_action_list= set([v['pattern'] for v in valid_action_list]),
            game_name=self.game_name,
            observation_rule=self.observation_rule
        )
        obs_prediction_chain = LLMChain(llm=self.llm, prompt=prompt)
        self.read_observation = obs_prediction_chain.run(**kwargs)
        self.read_observation = self.read_observation.strip()
        return self.read_observation

    def action_decision(self, observation: str, valid_action_list: List[str], promp_head: str, act: str = None,
                        short_memory_summary: str = "") -> Tuple[str, str]:
        """React to a given observation."""
        """React to a given observation."""
        prompt = PromptTemplate.from_template(
            promp_head
            + "\n你的计划是: {plan}"
            + "\n 根据计划，请从可用的动作列表中选择下一个动作:{valid_action_list}(只有一个词)，并将他们分成|"
            + "\n\n"
        )

        agent_summary_description = short_memory_summary

        kwargs = dict(
            agent_summary_description=agent_summary_description,
            # current_time=current_time_str,
            # relevant_memories=relevant_memories_str,
            agent_name=self.name,
            game_name=self.game_name,
            observation=observation,
            valid_action_list=set([v['pattern'] for v in valid_action_list]),
            plan=self.plan,
            belief=self.belief,
            act=act
        )
        action_prediction_chain = LLMChain(llm=self.llm, prompt=prompt)

        result = action_prediction_chain.run(**kwargs)
        if "|" in result:
            result, result_comm = result.split("|", 1)
        else:
            result_comm = ""
        return result.strip(), result_comm.strip()





