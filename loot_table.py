import json
from pathlib import Path
import random

ROOT = Path(__file__).parent.resolve()
TABLE_DIR = ROOT / "loot-tables"


class Item:

    def __init__(self, name: str, count: int):
        self.name = name
        self.count = count

    def __repr__(self) -> str:
        return f"Item : {self.name} : {self.count}x"


class EnchantedItem(Item):

    def __init__(self, name: str):
        super().__init__(name, 1)
        self.enchantment, self.level = self.get_enchantment()

    def get_enchantment(self) -> tuple[str, int]:
        pass

    def __repr__(self) -> str:
        return f"Item : {self.name} : {self.enchantment} {'I' * self.level}"


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

    def generate(self) -> list[Item]:
        num_rolls = random.randint(self.min_rolls, self.max_rolls)
        chosen_loot = random.choices(
            self.loots,
            weights=self.weights,
            k=num_rolls
        )
        items = [loot.generate() for loot in chosen_loot]
        return items

    def __repr__(self) -> str:
        return (
            f"LootTable : {self.min_rolls}-{self.max_rolls} rolls : {self.total_weight} weight"
            f"\n{'\n'.join(str(loot) for loot in self.loots)}"
        )


def read_entry(entry: dict) -> Loot:
    functions = [function_data["function"] for function_data in entry.get("functions", [])]
    name = entry["name"]
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
