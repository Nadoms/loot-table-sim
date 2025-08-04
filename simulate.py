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


def simulate(
    table_path: Path,
    chests: int,
    str_requirements: list[str],
    str_items: list[str],
    str_ench_items: list[str],
):
    print("// Simulating chests...")
    item_groups = get_groups(table_path, chests)

    print("// Checking requirements...")
    requirement = pick_req(str_requirements, str_items, str_ench_items)
    print(requirement.combo_names)
    print(requirement.check_all(item_groups))

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
        default=[],
        nargs="*",
        choices=[
            "no_req",
            "lightable",
            "completable",
            "edible",
            "nuggets",
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
