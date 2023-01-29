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
    locked: bool = False
    cubes_required: int = 0

    def can_exit(self):
        """Do not allow exiting from locked doors."""
        return (not self.locked) and (self.cubes_required == 0)


@dataclass
class Transition:
    """Class for storing information about level transitions."""
    source: Entrance
    dest: Entrance

