import random
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

import os

os.environ["OPENAI_API_BASE"] = "https://openai.api2d.net/v1"
os.environ["OPENAI_API_KEY"] = "fk193574-JC4P6uf3KOUAd3Xipa0wI8XU5HdpyDIg"

import zhipuai
zhipuai.api_key = "e5014084d3b10bafbb65a0e9cb1c9be2.WJlAemhCXKHBSKqH"

from action.zhipuai_llm import ZhipuAILLM

zhipuai_model = ZhipuAILLM(model="chatglm_turbo", temperature=0, zhipuai_api_key=zhipuai.api_key)
zhipuai_model.generate(['你好'])

model = "chatglm_turbo" #用于配置大模型版本

def getText(role, content, text = []):
    # role 是指定角色，content 是 prompt 内容
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

question = getText("user", "你好")
print(question)

# 请求模型
response = zhipuai.model_api.invoke(
    model=model,
    prompt=question
)
print(response)


class GuaDannAgent:
    def __init__(self,):
        self.llm = OpenAI(model_name="gpt-3.5-turbo")
        self.zhipuai_model = ZhipuAILLM(model="chatglm_std", temperature=0, zhipuai_api_key=zhipuai.api_key)
        template = """{question}\n\n"""
        self.prompt = PromptTemplate(template=template, input_variables=["question"])

    def generate_chat_completion(self, question):
        llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)
        return llm_chain.run(question)

    def generate_zhipu_completion(self, question):
        llm_chain = LLMChain(prompt=self.prompt, llm=self.zhipuai_model)
        return llm_chain.run(question)

    
    def generate_decision(self,history_data, other_user, candidates, zhipu = False):
        # 创建游戏提示信息，包括游戏规则、其他玩家的出牌信息和你的手牌
        rule = '掼蛋游戏的技巧包括记牌、进贡回贡、炸弹使用、红桃配配、双贡打牌、控牌、送牌、抓牌、插牌、理牌、组火和冲刺等多个方面。要记住牌的分布，善用炸弹、配好红桃、灵活运用各种牌型，尤其在双贡和冲刺时要善于判断时机。'
        input_prompt = f'假设你在控制seatid:0的玩家，基于以下规则:{rule}'
        input_prompt += f"历史出牌信息: {history_data}"
        input_prompt += f"当前其他玩家的出牌信息: {other_user}; 你所拥有的手牌出牌组合信息为:{candidates}, 总共有 {len(candidates)-1} 种出牌选择;"
        input_prompt += str(f"结合以上玩家出牌信息，以及你所拥有的手牌出牌组合信息，输出你的一个出牌数字选择 (从所有出牌组合中选择一个，仅输出为一个数字, 确保数字严格小于等于总的出牌选择{len(candidates)-1})")
        # 调用AI模型生成决策
        # print('input prompt',input_prompt)
        if (len(candidates)-1)==0:
            print('AI output:过牌')
            return 0
        else:
            if self.generate_zhipu_completion(input_prompt)==None:
                return random.randint(0, len(candidates) - 1)  # 生成小于m的随机整数
            elif zhipu == True:
                print('lenght',len(input_prompt),len(history_data),len(other_user),len(candidates))
                output= self.generate_zhipu_completion(input_prompt)
                print('AI Output:', output)
            else:
                print('lenght',len(input_prompt),len(history_data),len(other_user),len(candidates))
                output= self.generate_chat_completion(input_prompt)
                print('AI Output:', output)



        return output
