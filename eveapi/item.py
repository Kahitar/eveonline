from dataclasses import dataclass


@dataclass
class Item:
    name: str
    type_id: int

    def __hash__(self) -> int:
        return self.type_id