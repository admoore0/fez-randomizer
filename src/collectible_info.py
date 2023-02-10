from dataclasses import dataclass

@dataclass(unsafe_hash=True)
class CollectibleInfo:
    golden_cubes: int = 0
    anti_cubes: int = 0
    heart_pieces: int = 0
    bits: int = 0
    keys: int = 0
    owls: int = 0
    water_lower: bool = False
    other: str = ""

    def __bool__(self):
        return not (self.golden_cubes == 0 and self.anti_cubes == 0 and self.heart_pieces == 0 and self.bits == 0
                    and self.keys == 0 and self.owls == 0 and self.water_lower == False and self.other == "")

    def __not__(self):
        return not bool(self)

    def __add__(self, other: object) -> 'CollectibleInfo':
        if not isinstance(other, CollectibleInfo):
            return NotImplemented
        else:
            return CollectibleInfo(
                golden_cubes=self.golden_cubes+other.golden_cubes,
                anti_cubes=self.anti_cubes+other.anti_cubes,
                heart_pieces=self.heart_pieces+other.heart_pieces,
                bits=self.bits+other.bits,
                keys=self.keys+other.keys,
                owls=self.owls+other.owls,
                water_lower=self.water_lower or other.water_lower,
                other=self.other + ", " + other.other
            )
    
    def total_cubes(self) -> int:
        return self.golden_cubes + self.anti_cubes + self.bits // 8
