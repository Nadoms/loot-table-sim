from pathlib import Path

from loot_table import *





def main():
    table_path = TABLE_DIR / "ruined_portal.json"
    print(read_table(table_path))


if __name__ == "__main__":
    main()
