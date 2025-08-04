import json
from pathlib import Path
import random

ROOT = Path(__file__).parent.resolve()
TABLE_DIR = ROOT / "loot-tables-1-16"


class Item:

    def __init__(self, name: str, count: int = 1):
        self.name = name
        self.count = count

    @property
    def id(self) -> str:
        return f"Item : {self.name}"

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return self.name == other.name

    def __repr__(self) -> str:
        return (
            f"{self.id}"
            f"{' : ' + str(self.count) + 'x' if self.count != 1 else ''}"
        )


class EnchantedItem(Item):

    def __init__(
        self,
        name: str,
        count: int = 1,
        enchantment: str | None = None,
        level: int = 1,
    ):
        super().__init__(name, count)
        if enchantment is not None:
            self.enchantment = enchantment
            self.level = level
        else:
            self.enchantment, self.level = self.get_enchantment()

    def get_enchantment(self) -> tuple[str, int]:
        with open("enchantment.json") as fp:
            enchantment_info = json.load(fp)
        possible_enchants = [
            enchantment
            for enchantment in enchantment_info
            if (
                "any" in enchantment_info[enchantment]["applicable"] or 
                any(item in self.name for item in enchantment_info[enchantment]["applicable"])
            )
        ]
        selected_enchant = random.choice(possible_enchants).replace("minecraft:", "")
        selected_level = random.randint(1, enchantment_info[selected_enchant]["level"])
        return selected_enchant, selected_level

    @property
    def id(self) -> str:
        return (
            f"EnchantedItem : {self.name} : "
            f"{self.enchantment} {'I' * self.level}"
        )

    def same_enchanted_item(self, other):
        if not isinstance(other, EnchantedItem):
            return False
        return (
            self.name == other.name
            and self.enchantment == other.enchantment
        )

    def __eq__(self, other):
        if not isinstance(other, EnchantedItem):
            return False
        return (
            self.name == other.name
            and self.enchantment == other.enchantment
            and self.level == other.level
        )


class ItemGroup:

    def __init__(
        self,
        items: list[Item] = [],
        regular_items: list[Item] = [],
        enchanted_items: list[EnchantedItem] = [],
        rolls: int = 0,
    ):
        self.items = [item for item in items if not isinstance(item, EnchantedItem)] + regular_items
        self.enchanted_items = [item for item in items if isinstance(item, EnchantedItem)] + enchanted_items
        self.rolls = rolls
        self.combine_stacks()

    @classmethod
    def merge(cls, *item_groups: "ItemGroup"):
        return cls(
            regular_items=[item for item_group in item_groups for item in item_group.items],
            enchanted_items=[ench_item for item_group in item_groups for ench_item in item_group.enchanted_items],
            rolls=sum(item_group.rolls for item_group in item_groups),
        )

    def combine_stacks(self):
        combined_items = {}
        for item in self.items:
            if item.name in combined_items:
                combined_items[item.name].count += item.count
            else:
                combined_items[item.name] = item

        combined_ench_items = {}
        for ench_item in self.enchanted_items:
            if ench_item.id in combined_ench_items:
                combined_ench_items[ench_item.id].count += ench_item.count
            else:
                combined_ench_items[ench_item.id] = ench_item

        self.items = list(combined_items.values())
        self.enchanted_items = list(combined_ench_items.values())

    def contains_at_least(self, required_item: Item):
        if required_item not in self:
            return False
        contained_item = self.items[self.items.index(required_item)]
        if required_item.count <= contained_item.count:
            return True
        return False

    def release(self, required_item: Item):
        if required_item not in self:
            return False
        if isinstance(required_item, EnchantedItem):
            item_list = self.enchanted_items
        else:
            item_list = self.items
        contained_item = item_list[item_list.index(required_item)]
        if contained_item.count < required_item.count:
            return False
        if contained_item.count == required_item.count:
            item_list.remove(contained_item)
            return True
        contained_item.count -= required_item.count
        return True

    @property
    def all_items(self) -> list[Item]:
        return self.items + self.enchanted_items

    def __add__(self, other):
        if not isinstance(other, ItemGroup):
            return NotImplemented
        combined = ItemGroup(
            regular_items=(self.items + other.items),
            enchanted_items=(self.enchanted_items + other.enchanted_items),
            rolls=(self.rolls + other.rolls),
        )
        return combined

    def __contains__(self, item: Item):
        return item in self.all_items

    def __repr__(self) -> str:
        self.items.sort(key=lambda x: str(x))
        self.enchanted_items.sort(key=lambda x: str(x))
        return (
            f"ItemGroup : {self.rolls} rolls"
            f"\n{'\n'.join(str(item) for item in self.items)}"
            f"\n{'\n'.join(str(item) for item in self.enchanted_items)}"
        )


class Loot:

    def __init__(self, name: str, weight: int):
        self.name = name
        self.weight = weight

    def generate(self) -> Item:
        return Item(self.name, 1)

    def __repr__(self) -> str:
        return f"Loot : {self.name} : {self.weight} weight"


class EnchantableLoot(Loot):

    def __init__(self, name: str, weight: int):
        super().__init__(name, weight)

    def generate(self) -> EnchantedItem:
        return EnchantedItem(self.name)


class StackableLoot(Loot):

    def __init__(self, name: str, weight: int, min_count: int, max_count: int):
        super().__init__(name, weight)
        self.min_count = min_count
        self.max_count = max_count

    def generate(self) -> Item:
        count = random.randint(self.min_count, self.max_count)
        return Item(self.name, count)

    def __repr__(self) -> str:
        return (
            f"Loot : {self.name} : "
            f"{self.weight} weight : "
            f"{self.min_count}-{self.max_count} count"
        )


class LootTable:

    def __init__(
        self,
        min_rolls: int,
        max_rolls: int,
        loots: list[Loot] = [],
    ):
        self.min_rolls = min_rolls
        self.max_rolls = max_rolls
        self.loots = loots
        self.weights = [loot.weight for loot in loots]

    def add_loot(self, loot: Loot):
        self.loots.append(loot)
        self.weights.append(loot.weight)

    def generate(self) -> ItemGroup:
        rolls = random.randint(self.min_rolls, self.max_rolls)
        chosen_loot = random.choices(
            self.loots,
            weights=self.weights,
            k=rolls
        )
        items = [loot.generate() for loot in chosen_loot]
        item_group = ItemGroup(items=items, rolls=rolls)
        return item_group

    def __repr__(self) -> str:
        return (
            f"LootTable : {self.min_rolls}-{self.max_rolls} rolls : {self.total_weight} weight"
            f"\n{'\n'.join(str(loot) for loot in self.loots)}"
        )


def read_entry(entry: dict) -> Loot:
    functions = [function_data["function"] for function_data in entry.get("functions", [])]
    name = entry["name"].replace("minecraft:", "")
    weight = entry.get("weight", 1)
    if "minecraft:set_count" in functions:
        loot = StackableLoot(
            name,
            weight,
            entry["functions"][0]["count"]["min"],
            entry["functions"][0]["count"]["max"],
        )
    elif "minecraft:enchant_randomly" in functions:
        loot = EnchantableLoot(name, weight)
    else:
        loot = Loot(name, weight)

    return loot


def read_table(path: Path) -> LootTable:
    with open(path) as fp:
        raw_table = json.load(fp)

    for pool in raw_table["pools"]:
        table = LootTable(pool["rolls"]["min"], pool["rolls"]["max"])

        for entry in pool["entries"]:
            loot = read_entry(entry)
            table.add_loot(loot)

    return table


def main():
    table_path = TABLE_DIR / "ruined_portal.json"
    print(read_table(table_path))


if __name__ == "__main__":
    main()
