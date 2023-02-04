"""
Class for storing information about level transitions.
"""

from dataclasses import dataclass

from collectible_info import CollectibleInfo
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

    def can_enter(self, current_collectibles: CollectibleInfo):
        """Return whether or not this entrance can be accessed."""
        if self.locked:
            return current_collectibles.keys > 0
        if self.cubes_required > 0:
            return current_collectibles.total_cubes() >= self.cubes_required
        if self.is_underwater:
            return current_collectibles.water_lower
        if self.needs_owls:
            return current_collectibles.owls == 4
        return True


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
        if self.dest.level == "CABIN_INTERIOR_A":
            output += "CABIN_INTERIOR_B\n"
        elif self.dest.level == "CABIN_INTERIOR_B":
            output += "CABIN_INTERIOR_A\n"
        else:
            output += self.dest.level + '\n'
        output += str(self.dest.volume_id) + '\n'
        output += self.dest.viewpoint + '\n\n'
        # Dest -> Source transition
        output += self.dest.level + '\n'
        output += self.dest.original_destination + '\n'
        if self.source.level == "CABIN_INTERIOR_A":
            output += "CABIN_INTERIOR_B\n"
        elif self.source.level == "CABIN_INTERIOR_B":
            output += "CABIN_INTERIOR_A\n"
        else:
            output += self.source.level + '\n'
        output += str(self.source.volume_id) + '\n'
        output += self.source.viewpoint + '\n\n'
        return output

