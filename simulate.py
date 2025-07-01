from argparse import ArgumentParser
from pathlib import Path

from loot_table import *


def simulate(table_path: Path, chests: int, items: list[str]):
    table = read_table(table_path)
    mega_group = ItemGroup()

    for _ in range(chests):
        item_group = table.generate()
        mega_group += item_group
    print(mega_group)


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument(
        "-t",
        "--table",
        type=Path,
        default=TABLE_DIR / "ruined_portal.json",
        help="Path to the loot table JSON file",
    )
    argparser.add_argument(
        "-c",
        "--chests",
        type=int,
        default=10000,
        help="Number of chests to simulate",
    )
    argparser.add_argument(
        "items",
        nargs="*",
        help="The items to focus the report on"
    )
    args = argparser.parse_args()
    simulate(args.table, args.chests, args.items)
