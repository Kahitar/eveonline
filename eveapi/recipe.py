from __future__ import annotations
from typing import List, Dict

import json
from .item import Item

class UnknownRecipe(ValueError):
    def __init__(self, recipe_name: str):
        super().__init__(f"Unknown recipe {recipe_name}")

class Recipe:
    def __init__(self, name: str):
        recipe_data: dict = self._from_database(name)
        self.product = Item(recipe_data['name'], recipe_data['type_id'])
        self.ingredients: Dict[Item, int] = {
            Item("unknown_item_name", item['type_id']): item['amount']
                for item in recipe_data['ingredients']
        }

    def _from_database(self, name: str) -> dict:
        recipes = None
        with open("database/recipes.json") as f:
            recipes = json.loads(f.read())

        if recipes is None:
            raise UnknownRecipe(name)

        for recipe in recipes:
            if "name" in recipe and name == recipe['name']:
                return recipe
        raise UnknownRecipe(name)