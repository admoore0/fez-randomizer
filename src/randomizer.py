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

    output_str = ""

    while len(levels) > 0:
        total_unused_entrances = tree.total_unused_entrances()
        from_level = tree.next_leaf()
        from_entrance = from_level.connect_from_random()
        if total_unused_entrances == 1 and len(levels) > 2:
            # We must connect a level that has more than one entrance, otherwise the tree is dead. In addition, we
            # can't connect one way levels, as they require even more unused entrances.
            def is_valid(level: Level) -> bool:
                return (len(level.unused_entrances) >= 2
                        and level != from_level
                        and not level.one_way)
            
            valid_levels = [level for level in levels if is_valid(level)]
            level = random.choice(valid_levels)
            valid_entrances = [entrance for entrance in level.unused_entrances if level.num_exits(entrance) >= 2]
            entrance = random.choice(valid_entrances)
            hit = 1
        elif total_unused_entrances < 3:
            # We have an open node that we can connect a one-way level to.
            def is_valid(level: Level) -> bool:
                return level != from_level and not level.one_way
            hit = 2
        else:
            # Do not let levels connect to themselves unless it is the only option.
            def is_valid(level: Level) -> bool:
                if len(levels) == 1:
                    return True
                else:
                    return level != from_level
            hit = 3

        valid_levels = list(filter(is_valid, levels))
        to_level = random.choice(valid_levels)
        to_entrance = to_level.connect_to_random()
        from_level.connected_levels.append(level)

        if len(from_level.unused_entrances) == 0:
            levels.remove(from_level)
        if to_level != from_level and len(to_level.unused_entrances) == 0:
            levels.remove(to_level)
        output_str += str(Transition(from_entrance, to_entrance))
    
    with open("config.txt", "w", encoding="UTF-8") as f:
        f.write(output_str)
    
    print("Done.")

        



if __name__ == "__main__":
    main()