from __future__ import annotations
from typing import Dict

import json

from . import market
from .item import Item


PI_TYPE = "pi_type"


class UnknownRecipeError(ValueError):
    def __init__(self, recipe_name: str):
        super().__init__(f"Unknown recipe {recipe_name}")


class Recipe:
    def __init__(self, name: str):
        recipe_data: dict = self._from_database(name)
        self.product = Item(recipe_data['name'], recipe_data['type_id'])
        self.ingredients: Dict[Item, int] = {
            Item.from_json(item): item['amount'] for item in recipe_data['ingredients']
        }

    def _from_database(self, name: str) -> dict:
        recipes = None
        with open("database/recipes.json") as f:
            recipes = json.loads(f.read())

        if recipes is None:
            raise UnknownRecipeError(name)

        for recipe in recipes:
            if "name" in recipe and name == recipe['name']:
                return recipe
        raise UnknownRecipeError(name)

    def get_ingredients_cost(self, _market: market.Market) -> float:
        """ Get the costs of the ingredients of the recipe (buy from sell orders). """
        cost_sum = 0
        for item, amount in self.ingredients.items():
            cost_sum += _market.get_buy_price(item, amount)
        return cost_sum

    def get_product_price(self, _market: market.Market):
        """ Get the price of the product (sell with sell order), including taxes. """
        return _market.get_sell_price(self.product, 1)

    def get_profit(self, _market: market.Market) -> float:
        """ Get the profit when crafting the recipe, including all taxes. """
        return self.get_product_price(_market) - self.get_ingredients_cost(_market)

        