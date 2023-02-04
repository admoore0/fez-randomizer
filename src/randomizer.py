"""
Randomizer for FEZ.
"""

import argparse
from datetime import datetime
import hashlib
import json
import os
import random
from typing import List

from level import CollectibleInfo, Level
from entrance import Entrance, Transition

LEVEL_INFO_FILE = "src/reference/level_info.json"

def main():
    """
    Script for randomizing FEZ.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--seed", required=False, type=int, help="The random seed used for this script.")

    options = parser.parse_args()

    if options.seed:
        random.seed(options.seed)
    else:
        timestamp_as_bytes = int(datetime.now().timestamp()).to_bytes(32, "big")
        seed = int.from_bytes(hashlib.sha256(timestamp_as_bytes).digest(), "big")
        print(f"Using seed: {seed}")
        random.seed(seed)

    with open(LEVEL_INFO_FILE, "r") as f:
        levels_json = json.load(f)
    
    levels = [Level.load_from_json(level) for level in levels_json]

    entrances = []
    for level in levels:
        entrances += level.entrances

    for entrance in entrances:
        def is_matching_entrance(other: Entrance) -> bool:
            return other.original_destination == entrance.level and entrance.original_destination == other.level
        try:
            matching_entrance = next(filter(is_matching_entrance, entrances))
        except StopIteration:
            if not (entrance.level.startswith("CABIN_INTERIOR") or entrance.original_destination.startswith("CABIN_INTERIOR")):
                print(f"Misconfigured level info JSON. from={entrance}")

    random.shuffle(levels)
    removed_levels = 0
    # Because there are three one way levels and only 2 loopbacks in the graph, two single-entrance rooms will be
    # unreachable. Ensure these have no collectibles.
    for level in levels:
        if removed_levels == 4:
            break
        if not level.collectibles and len(level.entrances) == 1 and level.name not in ["GOMEZ_HOUSE", "CABIN_INTERIOR_A", "CABIN_INTERIOR_B", "WELL_2"]:
            print(f"Removing level: {level.name}")
            levels.remove(level)
            removed_levels += 1

    # Start the tree at GOMEZ_HOUSE (after the 2D section).
    tree = levels[levels.index("GOMEZ_HOUSE")]

    # Remove sewer start from the tree, as it should only be accessed by going through well_2
    sewer_start = levels.pop(levels.index("SEWER_START"))
    levels.remove("OWL")

    # A list of every level currently in the tree.
    tree_flat: List[Level] = [tree]

    # A list of levels currently not in the tree.
    unused_levels: List[Level] = levels.copy()
    unused_levels.remove("GOMEZ_HOUSE")

    transitions = []

    output_str = ""

    current_collectibles = CollectibleInfo(anti_cubes=1)

    while len([l for l in tree_flat if len(l.unused_entrances) > 0]) > 0:
        #print(tree.pprint())
        total_unused_entrances = sum([level.open_exits(current_collectibles) for level in tree_flat])
        unfinished_levels = [l for l in tree_flat if len(l.unused_entrances) > 0]
        valid_from_levels = [l for l in unfinished_levels if l.open_exits(current_collectibles) > 0]
        from_level = random.choice(valid_from_levels)
        from_entrance = from_level.connect_from_random(current_collectibles)
        if from_entrance.locked:
            current_collectibles.keys -= 1
        if from_level in unfinished_levels and len(from_level.unused_entrances) == 0:
            unfinished_levels.remove(from_level)
        if len(unused_levels) == 0 and len(unfinished_levels) == 1:
            # If there are no more untouched levels, we're stuck. Connect to ourselves if necessary.
            def is_valid(level: Level) -> bool:
                return True
            hit = 0
        elif len(unused_levels) == 0:
            # If every level has been hit, we have to connect back to somewhere in the tree. Avoid connecting to self.
            def is_valid(level: Level) -> bool:
                return level != from_level
            hit = 1
        elif len(unused_levels) == 1:
            # If there is only one unconnected level left, me must connect to it.
            def is_valid(level: Level) -> bool:
                return level in unused_levels
            hit = 2
        elif total_unused_entrances == 1:
            # We must connect a level that has more than one entrance, otherwise the tree is dead. In addition, we
            # can't connect one way levels, as they require even more unused entrances.
            def is_valid(level: Level) -> bool:
                return (level.open_exits(current_collectibles) >= 2
                        and not level.one_way
                        and level in unused_levels)
            hit = 3
        elif total_unused_entrances < 3:
            # We don't have an open node that we can connect a one-way level to. This also means we can't connect this
            # level to another one in the tree, as that would use up both entrances.
            def is_valid(level: Level) -> bool:
                return not level.one_way and level in unused_levels
            hit = 4
        else:
            # Do not let levels connect to themselves unless it is the only option.
            def is_valid(level: Level) -> bool:
                return level in unused_levels
            hit = 5

        valid_levels = list(filter(is_valid, unfinished_levels + unused_levels))
        try:
            to_level = random.choice(valid_levels)
            if to_level not in tree_flat:
                current_collectibles += to_level.collectibles
            to_entrance = to_level.connect_to_random()
        except:
            print("Unreachable entrance.")
            to_level = from_level
            to_entrance = from_entrance

        if(from_level == to_level):
            print(f"Level {from_level.name} connecting to itself. {hit=}")

        if to_level not in from_level.connected_levels:
            from_level.connected_levels.append(to_level)

        if to_level not in tree_flat:
            tree_flat.append(to_level)
            unused_levels.remove(to_level)

        if to_level.name == "CABIN_INTERIOR_A":
            cabin_interior_b = unused_levels.pop(unused_levels.index("CABIN_INTERIOR_B"))
            to_level.connected_levels.append(cabin_interior_b)
            tree_flat.append(cabin_interior_b)
        elif to_level.name == "CABIN_INTERIOR_B":
            cabin_interior_a = unused_levels.pop(unused_levels.index("CABIN_INTERIOR_A"))
            to_level.connected_levels.append(cabin_interior_a)
            tree_flat.append(cabin_interior_a)
        elif to_level.name == "WELL_2":
            to_level.connected_levels.append(sewer_start)
            tree_flat.append(sewer_start)
            transition = connect_one_way(sewer_start, unfinished_levels, current_collectibles)
            transitions.append(transition)
        elif to_level.one_way:
            transition = connect_one_way(to_level, unfinished_levels, current_collectibles)
            transitions.append(transition)

        
        if to_level in unfinished_levels and len(to_level.unused_entrances) == 0:
            unfinished_levels.remove(to_level)

        transitions.append(Transition(from_entrance, to_entrance))
    
    with open("config.txt", "w", encoding="UTF-8") as f:
        for transition in transitions:
            f.write(str(transition))
    
    print("Done.")

    
def connect_one_way(level: Level, unfinished_levels: List[Level], current_collectibles: CollectibleInfo) -> Transition:
    """
    Connect the other end of a one way level back to the tree.
    """
    from_entrance = level.connect_from_random(current_collectibles)

    valid_levels = [l for l in unfinished_levels if l.num_exits() > 0]
    try:
        to_level = random.choice(valid_levels)
        to_entrance = to_level.connect_to_random()
    except:
        print("Unreachable entrance.")
        to_level = level
        to_entrance = from_entrance

    if to_level not in level.connected_levels:
        level.connected_levels.append(to_level)

    if level in unfinished_levels and len(level.unused_entrances) == 0:
        unfinished_levels.remove(level)
    if to_level in unfinished_levels and len(to_level.unused_entrances) == 0:
        unfinished_levels.remove(to_level)
    
    return Transition(from_entrance, to_entrance)


if __name__ == "__main__":
    main()