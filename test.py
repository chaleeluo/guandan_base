#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/5 1:58 下午
# @Author  : luoyiwen
# @File    : test.py

# 1-100 质数

def cnt_primer(n):
    lst = [2, 3]
    for i in range(2, n):
        if i % 2 != 0 and i % 3 != 0 and i % 5 != 0:
            lst.append(i)
    return lst

def cnt_primer(n):
    res = []
    for i in range(2, n):
        j = 2
        while j < i and i % j != 0:
            j += 1
        if i == j:
            res.append(i)
    return res

print(cnt_primer(100))

# 组合数 n个元素取m个 几种取法
# 6取3
class comb():
    def lst_comb(self, n, m):
        res = []
        self.comb(n, m, res)
        return res

    def comb(self, n, m, res):
        if n == m:
            return n

        if m < n:
            n[0] + self.comb()

print(print_comb(10, 5))

# 1. 求解排列
def permute(nums):
    res = []
    backtrack(nums, [], res)
    return res

def backtrack(nums, path, res):
    if not nums:
        res.append(path)
    for i in range(len(nums)):
        backtrack(nums[:i] + nums[i+1:], path + [nums[i]], res)

print(permute([1, 2, 3]))
# 输出：
# [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]

# 1. 求解组合
def combine(n, k):
    res = []
    backtrack(n, k, [], res, 1)
    return res

def backtrack(n, k, path, res, start):
    if k == 0:
        res.append(path)
        return
    for i in range(start, n + 1):
        backtrack(n, k - 1, path + [i], res, i + 1)

print(combine(4, 2))
# 输出：
# [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]