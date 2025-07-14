from typing import Callable
from loot_table import *


class Req:

    def __init__(self, conditions: list[Callable[[ItemGroup], bool]]):
        self.size = len(conditions)
        self.conditions = conditions
        self.appearances = [0] * self.size

    def check(self, group: ItemGroup) -> list[int]:
        result = [0] * self.size
        for i, condition in enumerate(self.conditions):
            result[i] = int(condition(group))
        return result

    def check_all(self, groups: list[ItemGroup]):
        for group in groups:
            result = self.check(group)
            self.accumulate(result)

    def accumulate(self, result: list[int]):
        for i in range(self.size):
            self.appearances[i] += result[i]


class Req1(Req):

    def __init__(self, conditions: Callable[[ItemGroup], bool]):
        super().__init__([conditions])


class NoReq(Req):

    def __init__(self):
        super().__init__([])


def pick_req(requirement: str) -> Callable[[ItemGroup], bool]:
    func = eval(requirement)
    return func
