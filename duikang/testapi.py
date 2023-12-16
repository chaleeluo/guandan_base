#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/4 1:13 下午
# @Author  : luoyiwen
# @File    : testapi.py

import json
import urllib.request

params = {
    'position' : 0 , #当前出牌玩家座位号，从0号开始计
    'handcards' : [],#当前玩家手牌
    'card_play_action_seq' : [] ,#所有玩家出牌历史，内容细节下问具体说明
    'mainface' : 0 , #当局打的级牌
    'fstplay' : 1 ,#是否为主动发牌 0 表示压牌 1 主动发牌
    'ranks':[] ,#已经走科的玩家座位号集合，按照走科顺序排列
}


params = {"card_play_action_seq":[{"cards":[10,265,266,522,777],"seatid":0,"patterntype":4,"fstplay":1,"patternvalue":9},{"cards":[],"seatid":1,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":2,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[267,515,523,771,779],"seatid":3,"patterntype":4,"fstplay":0,"patternvalue":10},{"cards":[],"seatid":0,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":1,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":2,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[769],"seatid":3,"patterntype":1,"fstplay":1,"patternvalue":1},{"cards":[3],"seatid":0,"patterntype":1,"fstplay":0,"patternvalue":2},{"cards":[770],"seatid":1,"patterntype":1,"fstplay":0,"patternvalue":12},{"cards":[],"seatid":2,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[1037],"seatid":3,"patterntype":1,"fstplay":0,"patternvalue":13},{"cards":[],"seatid":0,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":1,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":2,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[5,517],"seatid":3,"patterntype":2,"fstplay":1,"patternvalue":4},{"cards":[],"seatid":0,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":1,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[522,778],"seatid":2,"patterntype":2,"fstplay":0,"patternvalue":9},{"cards":[12,780],"seatid":3,"patterntype":2,"fstplay":0,"patternvalue":11},{"cards":[],"seatid":0,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":1,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":2,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[264],"seatid":3,"patterntype":1,"fstplay":1,"patternvalue":7},{"cards":[],"seatid":0,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":1,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[11],"seatid":2,"patterntype":1,"fstplay":0,"patternvalue":10},{"cards":[1037],"seatid":3,"patterntype":1,"fstplay":0,"patternvalue":13},{"cards":[],"seatid":0,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":1,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[],"seatid":2,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[0,260,512,516,516],"seatid":3,"patterntype":4,"fstplay":1,"patternvalue":3},{"cards":[264,774,774,776,776],"seatid":0,"patterntype":4,"fstplay":0,"patternvalue":7},{"cards":[12,259,268,515,524],"seatid":1,"patterntype":4,"fstplay":0,"patternvalue":11},{"cards":[],"seatid":2,"patterntype":0,"fstplay":0,"patternvalue":-1},{"cards":[2,2,10,258,778],"seatid":3,"patterntype":4,"fstplay":0,"patternvalue":12}],"ailevel":0,"playtype":1,"dealcardver":"v3","bombcnt":0,"frpcardid":514,"handcards":[0,4,7,11,257,258,260,261,263,267,517,519,523,771,775,780],"ranks":[],"version":"v3","mainface":2,"fstplay":0,"position":0}
data = {
    'params':json.dumps(params)
}
print(f'data  {data}')
ret = urllib.request.urlopen('http://123.249.41.116:8080/ai/guandan/action/il' , urllib.parse.urlencode(data).encode() , 5 , context = None).read().strip()
print(f'ret {ret}')
