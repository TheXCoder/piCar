# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 20:32:36 2024

@author: Phatty
"""

import math, random

def superRandom(endingValue : int = 0, fuzzFactor : int | None = None, doNegitives : bool = True, isFloat = True) -> float | int:
    value : int = random.randint(-endingValue * doNegitives == True, endingValue)
    fuzz : float = 0
    fuzzChance : int = 0
    if fuzzFactor is not None:
        fuzzChance = math.ceil(random.randint(-3,3) / 3.0)
        print((fuzzFactor+1*fuzzFactor==0)^10)
        fuzz = random.random() * (10^fuzzFactor)
    print(f"\nfuzz == {fuzz}")
    print(f"\nFuzz value == {value* fuzz * fuzzChance}")
    value += value* fuzz * fuzzChance
    if value < 0 and doNegitives == False:
        return 0
    if isFloat:
        return float(value)
    else:
        return int(value)
    