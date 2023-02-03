"""
Class for storing information about levels.
"""

from dataclasses import dataclass

import random

from typing import Any, Dict, List, Optional, Union

from entrance import Entrance, Transition

@dataclass
class CollectibleInfo:
    golden_cubes: int = 0
    anti_cubes: int = 0
    heart_pieces: int = 0
    bits: int = 0
    keys: int = 0
    owls: int = 0
    other: str = ""


class Level:
    """
    Class for storing information about levels.
    """

    def __init__(self, name: str, collectibles: CollectibleInfo, entrances: List[Entrance],
                 one_way: bool = False) -> None:
        self.name = name
        self.collectibles = collectibles
        self.entrances = entrances
        self.unused_entrances = entrances
        self.unreachable_entrances: List[Entrance] = []
        self.connected_levels: List[Level] = []
        self.one_way = one_way

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Level):
            raise NotImplementedError
        return other.name == self.name

    def contains(self, level: Union['Level', str], visited: List['Level'] = []) -> bool:
        if self in visited:
            return False
        if isinstance(level, str):
            if level == self.name:
                return True
        else:
            if level == self:
                return True
        for connected_level in self.connected_levels:
            if connected_level.contains(level, visited + [self]):
                return True
        return False
    
    def connect_from_random(self) -> Entrance:
        """
        Start a connection from a random choice of one of this level's entrances. This also removes this entrance from
        the level's unused entrance list.

        :return: The entrance selected.
        """
        if not self.unused_entrances:
            raise ValueError("Level has no unused entrances.")
        entrance = random.choice(self.unused_entrances)
        self.unused_entrances.remove(entrance)
        return entrance

    def connect_to_random(self) -> Entrance:
        """
        End a connection at a 'random' choice of this level's nodes. For some rooms where travel is only permitted one
        way, we must choose the 'starting' entrance for that level.

        :return: The entrance selected.
        """
        if not self.unused_entrances:
            raise ValueError("Level has no unused entrances.")
        if self.name in ["OBSERVATORY", "LAVA_XXX", "WELL_B/SEWER_START"]:
            entrance = self.unused_entrances[0]
        else:
            valid_entrances = [e for e in self.unused_entrances if e.can_exit()]
            if len(valid_entrances) == 0:
                print("Warning: could not find a valid entrance for this level, player will emerge from locked door.")
                entrance = random.choice(self.unused_entrances)
            else:
                entrance = random.choice(valid_entrances)
        self.unused_entrances.remove(entrance)
        return entrance

    def pprint(self, depth: int = 0, visited: List['Level'] = []) -> str:
        """
        Get a tree visualization of the levels connections.
        
        :param depth: How many layers into the tree this level is.
        :param visited: A list of visited nodes.
        """
        prefix = ("| " * depth) + "|-"
        if self in visited:
            # Use a star to indicate that this level'c connections are defined elsewhere.
            return prefix + self.name + "*\n"
        else:
            output = prefix + self.name + "\n"
            for level in self.connected_levels:
                other_levels_in_group = [l for l in self.connected_levels if l.name != level.name]
                output += level.pprint(depth + 1, visited + other_levels_in_group + [self])
            return output

    def num_exits(self) -> int:
        open_exits = [e for e in self.unused_entrances if e.can_exit()]
        return len(open_exits)

    def get_nearest_entrance(self) -> Optional[Entrance]:
        if len(self.unused_entrances) >= 1:
            output = random.choice(self.unused_entrances)
            self.unused_entrances.remove(output)
            return output
        elif len(self.connected_levels) >= 1:
            for level in self.connected_levels:
                entrance = level.get_nearest_entrance()
                if entrance:
                    return entrance
        else:
            return None

    def next_leaf(self) -> Optional['Level']:
        return Level.next_leaf_bfs([self])

    @staticmethod
    def next_leaf_bfs(levels: List['Level']) -> Optional['Level']:
        next_layer = []
        for level in levels:
            if level.unused_entrances:
                return level
            for connected_level in level.connected_levels:
                if connected_level not in levels:
                    next_layer += [connected_level]
        if len(next_layer) == 0:
            return None
        return Level.next_leaf_bfs(next_layer)


    def total_unused_entrances(self, visited: List['Level'] = []) -> int:
        output = len(self.unused_entrances)
        for level in self.connected_levels:
            if level not in visited:
                output += level.total_unused_entrances(visited + [self])
        return output

    @classmethod
    def load_from_json(cls, json: Dict[str, Any]):
        name = json.get("name", "")
        collectibles = CollectibleInfo(**json.get("collectibles", {}))
        if name == "WELL_B/SEWER_START":
            # Do some logic to account for different level_names.
            entrance_level = ""
        else:
            entrance_level = name
        entrances = [Entrance(level=entrance_level, **args) for args in json.get("entrances", [])]
        one_way = json.get("one_way", False)
        return cls(name, collectibles, entrances, one_way)
