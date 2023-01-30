"""
Randomizer for FEZ.
"""

import json
import os
import random

from level import Level
from entrance import Entrance, Transition

LEVEL_INFO_FILE = "src/reference/level_info.json"

def main():
    """
    Script for randomizing FEZ.
    """

    with open(LEVEL_INFO_FILE, "r") as f:
        levels_json = json.load(f)
    
    levels = [Level.load_from_json(level) for level in levels_json]

    # Start the tree at GOMEZ_HOUSE (after the 2D section).
    tree = next(filter(lambda x: x.name == "GOMEZ_HOUSE", levels))
    levels.remove(tree)

    output_str = ""

    while len(levels) > 0:
        from_level = tree.next_leaf()
        if not from_level:
            break
        from_entrance = random.choice(from_level.unused_entrances)
        from_level.unused_entrances.remove(from_entrance)
        if not from_entrance:
            break
        if tree.total_unused_entrances() == 0 and len(levels) > 2:
            # We must connect a level that has more than one entrance, otherwise the tree is dead.
            valid_levels = [level for level in levels if len(level.unused_entrances) >= 2 and level != from_level]
            level = random.choice(valid_levels)
            valid_entrances = [entrance for entrance in level.unused_entrances if level.num_exits(entrance) >= 2]
            entrance = random.choice(valid_entrances)
        else:
            valid_levels = list(filter(lambda x: x != from_level, levels))
            level = random.choice(valid_levels)
            entrance = random.choice(level.unused_entrances)
        # Remove the entrance we used from the unused entrances list.
        level.unused_entrances.remove(entrance)
        from_level.connected_levels.append(level)
        if len(level.unused_entrances) == 0:
            # There are no more entrances for this level. Remove it from the list.
            levels.remove(level)
        output_str += str(Transition(from_entrance, entrance))
    
    with open("config.txt", "w", encoding="UTF-8") as f:
        f.write(output_str)
    
    print("Done.")

        



if __name__ == "__main__":
    main()