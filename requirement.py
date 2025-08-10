from copy import deepcopy
import itertools
from random import randint
from typing import Callable

from loot_table import *
from util import LoadingBar


def parse_items(str_items: list[str]) -> list[Item]:
    items = []
    for str_item in str_items:
        item_info = str_item.split(":")
        name = item_info[0]

        if len(item_info) == 1:
            item = Item(name=name)
        elif len(item_info) == 2:
            count = int(item_info[1])
            item = Item(name=name, count=count)
        elif len(item_info) == 4:
            count = int(item_info[1])
            enchantment = item_info[2]
            level = int(item_info[3])
            item = EnchantedItem(name=name, count=count, enchantment=enchantment, level=level)
        items.append(item)

    return items


class Req:

    def __init__(self, conditions: list[Callable[[ItemGroup], bool]]):
        self.conditions = conditions
        self.condition_combos = self.generate_combinations()
        self.size = len(self.conditions)
        self.combo_size = len(self.condition_combos)
        self.appearances = [0] * self.size
        self.combo_names = [
            "+".join(condition.__name__ for condition in condition_combo)
            for condition_combo
            in self.condition_combos
        ]

    def generate_combinations(self):
        condition_combos = []
        for r in range(0, len(self.conditions) + 1):
            condition_combos.extend(itertools.combinations(self.conditions, r))
        return condition_combos

    def __call__(self, group: ItemGroup) -> list[int]:
        temp_group = deepcopy(group)
        result = [0] * self.size
        for i, condition in enumerate(self.conditions):
            result[i] = int(condition(temp_group))
        return result

    def check_combos(self, group: ItemGroup) -> list[int]:
        result = [0] * self.combo_size
        for i, condition_combo in enumerate(self.condition_combos):
            temp_group = deepcopy(group)
            result[i] = int(all(condition(temp_group) for condition in condition_combo))
        return result

    def check_all(self, groups: list[ItemGroup]):
        self.appearances = [0] * self.combo_size
        bar = LoadingBar()
        for i, group in enumerate(groups):
            bar.load(i / len(groups))
            result = self.check_combos(group)
            self.accumulate(result)
        return self.appearances

    def accumulate(self, result: list[int]):
        for i in range(self.combo_size):
            self.appearances[i] += result[i]


class MyReq(Req):

    def __init__(self,
        str_requirements: list[str],
        str_items: list[str],
    ):
        requirements = [
            eval("ReqFuncs." + requirement_str)
            for requirement_str
            in str_requirements
        ] + [
            ReqFuncs.item_requirement(item)
            for item in parse_items(str_items)
        ]
        super().__init__(requirements)


class NoReq(Req):

    def __init__(self):
        super().__init__([ReqFuncs.no_req])


class ReqFuncs:

    obby_data = [0, 7, 3, 4, 14, 12, 3, 42, 15, 0, 0]

    @classmethod
    def no_req(cls, group: ItemGroup):
        return True

    @classmethod
    def lightable(cls, group: ItemGroup):
        fns = Item("flint_and_steel")
        fire_charge = Item("fire_charge")
        flint = Item("flint")
        iron_nuggets = Item("iron_nugget", 9)
        if group.release(fns) or group.release(fire_charge):
            return True
        if flint in group and iron_nuggets in group:
            if group.contains_at_least(iron_nuggets):
                group.release(flint)
                group.release(iron_nuggets)
                return True
        return False

    @classmethod
    def edible(cls, group: ItemGroup):
        golden_carrots = Item("golden_carrot")
        golden_apple = Item("golden_apple")
        notch_apple = Item("enchanted_golden_apple")
        if group.release(golden_carrots):
            return True
        if group.release(golden_apple):
            if group.release(notch_apple) or group.release(golden_apple):
                return True
        return group.release(notch_apple) and group.release(notch_apple)

    @classmethod
    def nuggets(cls, group: ItemGroup):
        iron_nuggets = Item("iron_nugget", 27)
        return group.release(iron_nuggets)

    @classmethod
    def completable(cls, group: ItemGroup):
        obsidian = Item("obsidian", cls.determine_obby_count())
        return group.release(obsidian)

    @classmethod
    def determine_obby_count(cls):
        rp_id = randint(0, 99)
        rp_no = 0
        for obby_count, rps in enumerate(cls.obby_data):
            rp_no += rps
            if rp_id < rp_no:
                return obby_count

    @classmethod
    def item_requirement(cls, item: Item) -> Callable[[ItemGroup], bool]:
        def requirement(group: ItemGroup):
            return group.release(item)
        return requirement


def pick_req(
    str_requirements: list[str],
    str_items: list[str],
) -> (Req):
    return MyReq(str_requirements, str_items)
