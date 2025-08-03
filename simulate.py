from argparse import ArgumentParser
import itertools
from pathlib import Path

from loot_table import *
from requirement import pick_req
from util import LoadingBar


def get_groups(table_path: Path, chests: int) -> list[ItemGroup]:
    table = read_table(table_path)
    item_groups = []

    bar = LoadingBar()
    for i in range(chests):
        bar.load(i / chests)
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
        elif len(item_info) == 2:
            count = int(item_info[1])
            item = Item(name=name, count=count)
        elif len(item_info) == 3:
            count = int(item_info[1])
            enchantment = item_info[2]
            item = EnchantedItem(name=name, count=count, enchantment=enchantment)
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
            for group in groups:
                combo_absent = False
                for combo_item in combo:
                    for group_item in group.all_items:
                        if combo_item == group_item and combo_item.count <= group_item.count:
                            break
                    else:
                        combo_absent = True
                if not combo_absent:
                    self.appearances[i] += 1

    def __repr__(self):
        return (
            f"ItemCombo"
            f"\n{'\n'.join(str(self.appearances[i]) + 'x : ' + str(self.combos[i]) for i in range(len(self.combos)))}"
        )


def simulate(
    table_path: Path,
    chests: int,
    requirements_str: list[str],
    str_items: list[str],
    str_ench_items: list[str],
):
    print("// Simulating chests...")
    item_groups = get_groups(table_path, chests)

    print("// Checking requirements...")
    requirement = pick_req(requirements_str)
    print(requirement.combo_names)
    print(requirement.check_all(item_groups))
    items = parse_items(str_items)
    ench_items = parse_items(str_ench_items)
    # idk = analyse_groups(item_groups, chests, items, ench_items)
    mega_group = ItemGroup.merge(*item_groups)
    # print(mega_group)


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
        "-r",
        "--requirements",
        type=str,
        default=["noreq"],
        nargs="*",
        choices=[
            "noreq",
            "lightable",
            "completable",
            "edible",
            "nuggets",
            "couri"
        ],
        help="The requirement function to use"
    )
    argparser.add_argument(
        "-i",
        "--items",
        type=str,
        default=[],
        nargs="*",
        help="The regular items to focus the report on"
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
    simulate(args.table, args.chests, args.requirements, args.items, args.ench_items)


if __name__ == "__main__":
    main()
