"""
Randomizer for FEZ.
"""

import argparse
from datetime import datetime
import hashlib
import json
import os
import random
from typing import List, Tuple

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
        timestamp_as_bytes = datetime.now().microsecond.to_bytes(4, "big")
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
        if removed_levels == 6:
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

    transitions = []

    output_str = ""

    current_collectibles = CollectibleInfo(anti_cubes=1)

    new_transitions, current_collectibles = populate_hubs(levels, tree_flat, current_collectibles)
    transitions += new_transitions

    # The unused levels so far.
    unused_levels = [l for l in levels if l not in tree_flat]

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
            if from_entrance.locked:
                to_level.is_behind_key = True
                to_level.key_door_source = from_level.name
            elif from_level.is_behind_key:
                to_level.is_behind_key = True
                to_level.key_door_source = from_level.key_door_source
            if to_level not in tree_flat:
                current_collectibles += to_level.collectibles
                if to_level.collectibles.keys > 0 and to_level.is_behind_key:
                    print(f"Key placed behind key door (source door in {to_level.key_door_source})")
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


def populate_hubs(levels: List[Level], tree_flat: List[Level],
                  collectibles: CollectibleInfo) -> Tuple[List[Transition], CollectibleInfo]:
    """
    Populate a skeleton graph connecting all hubs.
    """
    gomez_house = tree_flat[tree_flat.index("GOMEZ_HOUSE")]

    new_collectibles = collectibles

    transitions = []
    new_transitions, new_collectibles = connect_to_hub(gomez_house, levels, tree_flat, new_collectibles)
    transitions += new_transitions

    hub_names = ["NATURE_HUB", "INDUSTRIAL_HUB", "SEWER_HUB", "ZU_CITY_RUINS", "GRAVEYARD_GATE"]
    for _ in range(4):
        from_hub = random.choice([l for l in tree_flat if l.name in hub_names])
        new_transitions, new_collectibles = connect_to_hub(from_hub, levels, tree_flat, new_collectibles)
        transitions += new_transitions
        
    
    return transitions, new_collectibles


def connect_to_hub(from_level: Level, levels: List[Level], tree_flat: List[Level],
                   collectibles: CollectibleInfo) -> Tuple[List[Transition], CollectibleInfo]:
    """
    Connect this level to a random remaining hub using 3-8 levels in the process.
    
    Rules:
    - No one-way levels
    - No entrances that require any collectibles, or that are considered one-way.
    """
    assert(from_level in tree_flat)
    # Get a list of all the hubs that haven't bee used yet.
    unused_levels = [l for l in levels if l not in tree_flat]
    hub_names = ["NATURE_HUB", "INDUSTRIAL_HUB", "SEWER_HUB", "ZU_CITY_RUINS", "GRAVEYARD_GATE"]
    unused_hubs = [l for l in unused_levels if l.name in hub_names]
    assert(len(unused_hubs) > 0)

    # Choose a random hub and remove it from the list.
    hub = random.choice(unused_hubs)
    unused_levels.remove(hub)

    valid_levels = [l for l in unused_levels if l.num_exits() > 1 and not l.one_way and l.name not in hub_names]

    num_rooms = random.randrange(3, 9)

    last_level = from_level

    transitions = []

    for idx in range(num_rooms):
        from_entrance = last_level.connect_two_way()
        if idx == num_rooms - 1:
            to_level = hub
        else:
            to_level = random.choice(valid_levels)
        collectibles += to_level.collectibles
        last_level.connected_levels.append(to_level)
        tree_flat.append(to_level)
        if to_level in valid_levels:
            valid_levels.remove(to_level)
        to_entrance = to_level.connect_two_way()
        transitions.append(Transition(from_entrance, to_entrance))
        last_level = to_level

    return transitions, collectibles

if __name__ == "__main__":
    main()