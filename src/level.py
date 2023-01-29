"""
Class for storing information about levels.
"""

from dataclasses import dataclass

from typing import List

from .entrance import Entrance

@dataclass
class CollectibleInfo:
    golden_cubes: int
    anti_cubes: int
    cube_bits: int
    keys: int
    other: List[str]


class Level:
    """
    Class for storing information about levels.
    """

    def __init__(self, name: str, collectibles: CollectibleInfo, entrances: List[Entrance]) -> None:
        self.name = name
        self.collectibles = collectibles
        self.entrances = entrances
        self.unused_entrances = entrances
        self.unreachable_entrances = []

    def num_exits(self, entrance: Entrance) -> int:
        if entrance not in self.unused_entrances:
            raise ValueError("Entrance in use or not in this level.")
        if self.name == "OBSERVATORY" and entrance.volume_id != 696969:
            # Add bottom node to unreachable entrances.
            return len(self.unused_entrances) - 2
        return len(self.unused_entrances) - 1