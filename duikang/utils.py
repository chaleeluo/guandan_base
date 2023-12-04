import numpy as np
import random

poker_type_dict = {
    "过牌": 0,
    "单牌": 1,
    "对牌": 2,
    "三张": 3,
    "三带⼆": 4,
    "⽊板": 5,
    "钢板": 6,
    "顺⼦": 7,
    "四炸": 8,
    "五炸": 9,
    "同花顺": 10,
    "六炸": 11,
    "七炸": 12,
    "⼋炸": 13,
    "九炸": 14,
    "⼗炸": 15,
    "天王炸": 16
}

# 第一个表格的字典表示
flower_dict = {
    "⽅⽚": 0,
    "梅花": 1,
    "红⼼": 2,
    "⿊桃": 3,
    "⼩王": 4,
    "⼤王": 5
}

# 第二个表格的字典表示，将牌面值的键表示为字符串
value_dict = {
    "2": 0,
    "3": 1,
    "4": 2,
    "5": 3,
    "6": 4,
    "7": 5,
    "8": 6,
    "9": 7,
    "10": 8,
    "J": 9,
    "Q": 10,
    "K": 11,
    "A": 12,
    "⼩王": 13,
    "⼤王": 14
}


def reverse_calculate_cardid(cardid):

    flower_id, value = divmod(cardid, 256)
    for flower, id in flower_dict.items():
        if id == flower_id:
            break
    for val, num in value_dict.items():
        if num == value:
            break
    if cardid == 14:
        return "⼤王",None
    if cardid == 13:
        return "⼩王",None
    
    return flower, val

def parse_candidates(candidates):
    parsed_results = []  # 创建一个新的空列表，用于存储解析结果

    for candidate in candidates:
        pattern_id = candidate['pattern']  # 牌型的ID，例如7代表顺子
        pattern_name = list(poker_type_dict.keys())[list(poker_type_dict.values()).index(pattern_id)]  # 根据ID获取牌型名称
        value = candidate['value']  # 牌的大小，例如6
        cards_ids = candidate['cards']  # 牌的cardid列表，例如[520, 521, 522]

        # 解析cardid列表为具体的花色和牌面值
        cards = []
        for card_id in cards_ids:
            if card_id == 14:
                card = "⼤王"
            elif card_id == 13:
                card = "⼩王"
            else:
                flower, val = reverse_calculate_cardid(card_id)  # 使用逆向计算函数解析cardid
                card = f"{flower} {val}"
            cards.append(card)

        # 将解析结果存入字典
        parsed_result = {
            'pattern': pattern_name,
            'value': value,
            'hand_cards': cards
        }

        # 将字典添加到新的列表中
        parsed_results.append(parsed_result)

    return parsed_results  # 返回解析结果

def parse_history(history):
    parsed_results = []  # 创建一个新的空列表，用于存储解析结果

    for entry in history:
        seat_id = entry['seatid']  # 当前出牌玩家座位号
        pattern_id = entry['pattern']  # 牌型的ID
        pattern_name = list(poker_type_dict.keys())[list(poker_type_dict.values()).index(pattern_id)]  # 根据ID获取牌型名称
        card_ids = entry['cards']  # 牌的cardid列表

        # 解析cardid列表为具体的花色和牌面值
        cards = []
        for card_id in card_ids:
            if card_id == 14:
                card = "⼤王"
            elif card_id == 13:
                card = "⼩王"
            else:
                flower, val = reverse_calculate_cardid(card_id)  # 使用逆向计算函数解析cardid
                card = f"{flower} {val}"
            cards.append(card)

        # 将解析结果存入字典
        parsed_result = {
            'seatid': seat_id,
            'pattern': pattern_name,
            'cards': cards
        }

        # 将字典添加到新的列表中
        parsed_results.append(parsed_result)

    return parsed_results  # 返回解析结果


def calculate_combination_priority(combination):  
    pattern_value = poker_type_dict.get(combination['pattern'], -1)  # 获取牌型对应的数值
    return pattern_value, combination['value']


def rule_based_combination(candidates,rule='bestP_lowV'):
    if rule=='bestP_lowV':
        valid_combinations = [combination for combination in candidates if combination['value'] >= 0]
        if valid_combinations:
            # 按照牌型数值和value进行排序，选择牌型数值最高的组合
            sorted_combinations = sorted(valid_combinations, key=lambda x: calculate_combination_priority(x), reverse=True)
            
            # 找到同样pattern下value最低的组合
            best_pattern_value = sorted_combinations[0]['pattern']
            lowest_value_combinations = [combination for combination in sorted_combinations if combination['pattern'] == best_pattern_value]
            
            # 选择value最低的组合
            chosen_combination = min(lowest_value_combinations, key=lambda x: x['value'])
            return chosen_combination
        else:
            return candidates[0]
    if rule=='random':
        return random.choice(candidates)

