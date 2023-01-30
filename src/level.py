"""
Class for storing information about levels.
"""

from dataclasses import dataclass

import random

from typing import Any, Dict, List, Optional

from entrance import Entrance, Transition

@dataclass
class CollectibleInfo:
    golden_cubes: int = 0
    anti_cubes: int = 0
    bits: int = 0
    keys: int = 0
    other: str = ""


class Level:
    """
    Class for storing information about levels.
    """

    def __init__(self, name: str, collectibles: CollectibleInfo, entrances: List[Entrance]) -> None:
        self.name = name
        self.collectibles = collectibles
        self.entrances = entrances
        self.unused_entrances = entrances
        self.unreachable_entrances: List[Entrance] = []
        self.connected_levels: List[Level] = []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Level):
            raise NotImplementedError
        return other.name == self.name

    def num_exits(self, entrance: Entrance) -> int:
        if entrance not in self.unused_entrances:
            raise ValueError("Entrance in use or not in this level.")
        if self.name == "OBSERVATORY" and entrance.volume_id != 696969:
            # Add bottom node to unreachable entrances.
            return len(self.unused_entrances) - 2
        return len(self.unused_entrances) - 1

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
            next_layer += level.connected_levels
        if len(next_layer) == 0:
            return None
        return Level.next_leaf_bfs(next_layer)


    def total_unused_entrances(self) -> int:
        output = len(self.unused_entrances)
        for level in self.connected_levels:
            output += level.total_unused_entrances()
        return output

    @classmethod
    def load_from_json(cls, json: Dict[str, Any]):
        name = json.get("name", "")
        collectibles = CollectibleInfo(**json.get("collectibles", {}))
        entrances = [Entrance(**args) for args in json.get("entrances", [])]
        return cls(name, collectibles, entrances)
