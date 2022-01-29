from __future__ import annotations


class UnknownItemError(ValueError):
    pass


class Item:
    def __init__(self, name: str, type_id: int):
        self.name = name
        self.type_id = type_id

    def __hash__(self) -> int:
        return self.type_id

    @staticmethod
    def from_json(json: str) -> Item:
        name = "unknown_item_name"
        if "name" in json:
            name = json['name']
        if not "type_id" in json:
            raise UnknownItemError(f"No type_id given for item {name}.")
        return Item(name, json['type_id'])
        
