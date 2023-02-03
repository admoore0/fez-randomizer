"""
Randomizer for FEZ.
"""

import json
import os
import random
from typing import List

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

    for level in levels:
        if level.name.startswith("CABIN_INTERIOR"):
            continue
        for entrance in level.entrances:
            other_level = [l for l in levels if l.name == entrance.original_destination][0]
            if other_level.name.startswith("CABIN_INTERIOR"):
                continue
            matching_entrances = [e for e in other_level.entrances if e.original_destination == level.name]
            if len(matching_entrances) == 0:
                print("Misconfigured level info JSON.")

    # Start the tree at GOMEZ_HOUSE (after the 2D section).
    tree = next(filter(lambda x: x.name == "GOMEZ_HOUSE", levels))

    sewer_start = next(filter(lambda x: x.name == "SEWER_START", levels))
    levels.remove(sewer_start)

    output_str = ""

    while len(levels) > 0:
        #print(tree.pprint())
        total_unused_entrances = tree.total_unused_entrances()
        num_unconnected_levels = len([l for l in levels if not tree.contains(l)])
        from_level = tree.next_leaf()
        from_entrance = from_level.connect_from_random()
        if len(levels) == 1:
            # If there's only one level left, we're stuck. Connect to ourselves if necessary.
            def is_valid(level: Level) -> bool:
                return True
            hit = 0
        elif num_unconnected_levels == 0:
            # If every level has been hit, we have to connect back to somewhere in the tree. Avoid connecting to self.
            def is_valid(level: Level) -> bool:
                return level != from_level
            hit = 1
        elif total_unused_entrances == 1 and len(levels) > 2:
            # We must connect a level that has more than one entrance, otherwise the tree is dead. In addition, we
            # can't connect one way levels, as they require even more unused entrances.
            def is_valid(level: Level) -> bool:
                return (len(level.unused_entrances) >= 2
                        and level != from_level
                        and not level.one_way
                        and not tree.contains(level))
            hit = 2
        elif total_unused_entrances < 3:
            # We don't have an open node that we can connect a one-way level to. This also means we can't connect this
            # level to another one in the tree, as that would use up both entrances.
            def is_valid(level: Level) -> bool:
                return level != from_level and not level.one_way and not tree.contains(level)
            hit = 3
        else:
            # Do not let levels connect to themselves unless it is the only option.
            def is_valid(level: Level) -> bool:
                return not tree.contains(level)
            hit = 4

        valid_levels = list(filter(is_valid, levels))
        to_level = random.choice(valid_levels)
        to_entrance = to_level.connect_to_random()

        if(from_level == to_level):
            print(f"Level {from_level.name} connecting to itself. {hit=}")

        if to_level not in from_level.connected_levels:
            from_level.connected_levels.append(to_level)

        if to_level.name == "CABIN_INTERIOR_A":
            to_level.connected_levels.append(next(filter(lambda x: x.name == "CABIN_INTERIOR_B", levels)))
        elif to_level.name == "CABIN_INTERIOR_B":
            to_level.connected_levels.append(next(filter(lambda x: x.name == "CABIN_INTERIOR_A", levels)))
        elif to_level.name == "WELL_2":
            to_level.connected_levels.append(sewer_start)
        #     transition = connect_one_way(sewer_start, levels, tree)
        #     output_str += str(transition)
        # elif to_level.one_way:
        #     transition = connect_one_way(to_level, levels, tree)
        #     output_str += str(transition)

        if from_level in levels and len(from_level.unused_entrances) == 0:
            levels.remove(from_level)
        if to_level != from_level and len(to_level.unused_entrances) == 0:
            levels.remove(to_level)
        output_str += str(Transition(from_entrance, to_entrance))
    
    with open("config.txt", "w", encoding="UTF-8") as f:
        f.write(output_str)
    
    print("Done.")

    
def connect_one_way(level: Level, levels: List[Level], tree: Level) -> Transition:
    """
    Connect the other end of a one way level back to the tree.
    """
    from_entrance = level.connect_from_random()

    def is_valid(to_level: Level) -> bool:
        return (tree.contains(to_level) and to_level.num_exits() > 0 and not to_level.one_way
                and level != to_level)
    valid_levels = list(filter(is_valid, levels))
    if len(valid_levels) == 0:
        print("Could not connect back to tree. How?")
    to_level = random.choice(valid_levels)
    to_entrance = to_level.connect_to_random()

    level.connected_levels.append(to_level)

    # Removing the "from level" happens in the main function.
    if to_level != level and len(to_level.unused_entrances) == 0:
        levels.remove(to_level)
    
    return Transition(from_entrance, to_entrance)


if __name__ == "__main__":
    main()