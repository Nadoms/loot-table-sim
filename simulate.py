from pathlib import Path

from loot_table import *





def main():
    table_path = TABLE_DIR / "ruined_portal.json"
    table = read_table(table_path)
    item_group = table.generate()
    print(item_group)


if __name__ == "__main__":
    main()
