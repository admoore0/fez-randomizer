"""
Class for storing information about level transitions.
"""

from dataclasses import dataclass


@dataclass
class Entrance:
    """Class for information about a single entrance."""
    level: str
    volume_id: int
    viewpoint: str
    original_destination: str
    locked: bool = False
    is_underwater: bool = False
    needs_owls: bool = False
    needs_switch: bool = False
    cubes_required: int = 0

    def can_exit(self):
        """Do not allow exiting from locked doors."""
        return not (self.locked or self.cubes_required != 0 or self.is_underwater or self.needs_owls or self.needs_switch)


@dataclass
class Transition:
    """Class for storing information about level transitions."""
    source: Entrance
    dest: Entrance

    def __str__(self) -> str:
        output = ""
        # Source -> Dest transition.
        output += self.source.level + '\n'
        output += self.source.original_destination + '\n'
        output += self.dest.level + '\n'
        output += str(self.dest.volume_id) + '\n'
        output += self.dest.viewpoint + '\n\n'
        # Dest -> Source transition
        output += self.dest.level + '\n'
        output += self.dest.original_destination + '\n'
        output += self.source.level + '\n'
        output += str(self.source.volume_id) + '\n'
        output += self.source.viewpoint + '\n\n'
        return output

