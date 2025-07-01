from argparse import ArgumentParser
import itertools
from pathlib import Path

from loot_table import *


def get_groups(table_path: Path, chests: int) -> list[ItemGroup]:
    table = read_table(table_path)
    item_groups = []

    for _ in range(chests):
        item_group = table.generate()
        item_groups.append(item_group)

    return item_groups


def parse_items(str_items: list[str]) -> list[Item]:
    items = []
    for str_item in str_items:
        item_info = str_item.split(":")
        name = item_info[0]

        if len(item_info) == 1:
            item = Item(name=name)
        else:
            enchantment = item_info[1]
            item = EnchantedItem(name=name, enchantment=enchantment)
        items.append(item)

    return items


def analyse_groups(
    groups: list[ItemGroup],
    chests: int,
    items: list[Item],
    ench_items: list[EnchantedItem]
):
    combo = ItemCombo(*items)
    combo.compare(groups)
    print(combo)


class ItemCombo:

    def __init__(self, *items: Item):
        self.items = items
        self.combos : list[list[Item]]
        self.generate_combinations()

    def generate_combinations(self):
        self.combos = []
        for r in range(1, len(self.items) + 1):
            self.combos.extend(itertools.combinations(self.items, r))

    def compare(self, groups: list[ItemGroup]):
        self.appearances = [0] * len(self.combos)
        for i, combo in enumerate(self.combos):
            combo_absent = False
            for group in groups:
                if any(combo_item not in group.all_items for combo_item in combo):
                    continue
                self.appearances[i] += 1

    def __repr__(self):
        return (
            f"ItemCombo"
            f"\n{'\n'.join(str(self.appearances[i]) + 'x : ' + str(self.combos[i]) for i in range(len(self.combos)))}"
        )


def simulate(
    table_path: Path,
    chests: int,
    str_items: list[str],
    str_ench_items: list[str],
):
    item_groups = get_groups(table_path, chests)
    items = parse_items(str_items)
    ench_items = parse_items(str_ench_items)
    idk = analyse_groups(item_groups, chests, items, ench_items)
    mega_group = ItemGroup.merge(*item_groups)
    print(mega_group)


def main():
    argparser = ArgumentParser()
    argparser.add_argument(
        "-t",
        "--table",
        type=Path,
        default=TABLE_DIR / "ruined_portal.json",
        help="Path to the loot table JSON",
    )
    argparser.add_argument(
        "-c",
        "--chests",
        type=int,
        default=10000,
        help="Number of chests to simulate",
    )
    argparser.add_argument(
        "-i",
        "--items",
        type=str,
        default=[],
        nargs="*",
        help="The items to focus the report on"
    )
    argparser.add_argument(
        "-e",
        "--ench-items",
        type=str,
        default=[],
        nargs="*",
        help="The enchanted items to focus the report on"
    )
    args = argparser.parse_args()
    simulate(args.table, args.chests, args.items, args.ench_items)


if __name__ == "__main__":
    main()
