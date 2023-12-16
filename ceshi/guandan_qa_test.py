#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/10/31 2:19 下午
# @Author  : luoyiwen
# @File    : guandan_qa.py
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.prompts import HumanMessagePromptTemplate, PromptTemplate, ChatPromptTemplate
from langchain.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA, LLMChain, SimpleSequentialChain
import os
import json

os.environ["OPENAI_API_BASE"] = "https://openai.api2d.net/v1"
os.environ["OPENAI_API_KEY"] = "fk193574-JC4P6uf3KOUAd3Xipa0wI8XU5HdpyDIg"

# 加载文件夹中的所有txt类型的文件
loader = PyPDFLoader('./file/掼蛋App-2.6.6.pdf')
# 将数据转成 document 对象，每个文件会作为一个 document
pdf = loader.load()

# 初始化加载器
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
# 切割加载的 document
split_docs = text_splitter.split_documents(pdf)

# 初始化 openai 的 embeddings 对象
embeddings = OpenAIEmbeddings()
# 将 document 通过 openai 的 embeddings 对象计算 embedding 向量信息并临时存入 Chroma 向量数据库，用于后续匹配查询
docsearch = Chroma.from_documents(split_docs, embeddings)

# 创建问答对象
qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.as_retriever(), return_source_documents=False) ## false
# 进行问答
results=[]
for i in range(30):
    # 产品描述：需求背景-每日任务/活动
    result = qa({"query":
    '''
    新增了几个产品需求？分别总结和抽取每个需求的需求背景描述、产品界面变化和用户交互流程，对与每个产品需求请使用如下的JSON格式返回数据
    {{
    "产品需求":"a",
    "需求背景描述":"b",
    "产品界面变化":"c",
    "用户交互流程":"d"
    }}
    Extracted:
    '''
    })
    print('qaresult',result)

    # todo: CHECK 1

    # 输出每个步骤对应的具体测试

    # task1: 获取测试描述，对应用户输入的通用限制和界面展示的通用限制
    _input = qa({"query": "产品需求需要哪几个输入？"})
    _restrict = qa({"query": "对应的输入有哪几个限制？"})
    _task = qa({"query": "当前任务的测试项"})
    _steps = qa({"query": "当前任务的测试步骤"})
    query_input = [_input, _restrict, _task, _steps]
    print(query_input)

    human_msg_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template=
            '''
            根据当前每个产品需求对应的{query_input}JSON数据、测试项，总结和抽取相应的测试描述，按以下格式返回：
            {{
            "产品需求":"a",
            "需要的用户输入":"b",
            "用户输入的通用限制":"c",
            "界面展示的通用限制":"d",
            "当前任务的测试步骤":"e",
            }}       
            Extracted: 
            ''',
            input_variables=["query_input"]
        )
    )
    # print('human message prompt',human_msg_prompt)

    chat_prompt_template = ChatPromptTemplate.from_messages([human_msg_prompt])
    chain = LLMChain(llm=ChatOpenAI(temperature=0.9), prompt=chat_prompt_template)


    # task2：生成对应步骤的测试文案
    second_prompt = PromptTemplate(
            template=
            '''
            给定对应的JSON数据，根据%测试描述 {test_json}中"当前任务的测试步骤"字段，对没一个字段分别生成具体的测试步骤，按以下格式返回：
            {{
            "测试项":"a",
            "预置条件":"b",
            "测试步骤":"c",
            "测试期望结果":"d",
            }}       
            Extracted: 
            ''',
            input_variables=["test_json"]
    )

    chain_two = LLMChain(llm=ChatOpenAI(temperature=0.9), prompt=second_prompt)

    overall_chain = SimpleSequentialChain(chains=[chain, chain_two])


    # 将 query_input 数据作为输入传递给第一个 chain
    output_from_chain1 = chain.run(query_input)

    # todo: CHECK 2

    # 将输出结果作为输入传递给第二个 chain
    output_from_chain2 = overall_chain.run(output_from_chain1)

    # todo: CHECK 3

    # 输出第二个 chain 的结果
    print(output_from_chain2)
    results.append(output_from_chain2)

    print('all result',results)
    # 保存到 JSON 文件
    output_file_path = "all_results_new3.json"
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print(f"All results saved to {output_file_path}")