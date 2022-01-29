# Planetary interaction
from __future__ import annotations

from typing import Dict

from .market import Market
from .item import Item, UnknownItemError
from .recipe import Recipe


class PIItem(Item):
    def __init__(self, name: str, type_id: int, tier: int):
        super().__init__(name, type_id)
        self.tier = tier

    def get_base_cost(self) -> float:
        if self.tier == 0:
            return 5
        if self.tier == 1:
            return 400
        if self.tier == 2:
            return 7_200
        if self.tier == 3:
            return 60_000
        if self.tier == 4:
            return 1_200_000
        # Unknown tier
        return 0

    @staticmethod
    def from_json(json: str) -> PIItem:
        item = Item.from_json(json)
        if "pi_tier" not in json:
            raise UnknownItemError(f"The item {item.name} has no pi tier.")
        return PIItem(item.name, item.type_id, json['pi_tier'])


class PIRecipe(Recipe):
    def __init__(self, name: str):
        recipe_data: dict = self._from_database(name)
        self.product = PIItem.from_json(recipe_data)
        self.ingredients: Dict[PIItem, int] = {
            PIItem.from_json(item): item['amount'] for item in recipe_data['ingredients']
        }


class PlanetaryProduction:
    def __init__(self, pi_tax: float, recipe: PIRecipe):
        self.pi_tax = pi_tax
        self.recipe = recipe
        self.import_items: Dict[PIItem, int] = {}
        self.export_items: Dict[PIItem, int] = {}
        self._add_export_items({recipe.product: 1})
        self._add_import_items(recipe.ingredients)

    def _add_import_items(self, import_items: Dict[PIItem, int]):
        self.import_items.update(import_items)

    def _add_export_items(self, export_items: Dict[PIItem, int]):
        self.export_items.update(export_items)

    def get_export_cost(self, launched_from_command_center: bool = False) -> float:
        cost = 0
        for item, amount in self.export_items.items():
            cost += amount * self.calculate_export_fee(
                item.get_base_cost(), self.pi_tax, launched_from_command_center)
        return cost

    def get_import_cost(self) -> float:
        cost = 0
        for item, amount in self.import_items.items():
            cost += amount * self.calculate_import_fee(item.get_base_cost(), self.pi_tax)
        return cost

    def get_overall_profit(self, market: Market) -> float:
        """ Calculate the overall profit including import, export and buy/sell taxes. """
        recipe_profit = self.recipe.get_profit(market)
        import_cost = self.get_import_cost()
        export_cost = self.get_export_cost()
        print(
            f"Recipe Profit: {recipe_profit:,.2f}\n"
            f"Import Cost: {import_cost:,.2f}\n"
            f"Exprt Cost: {export_cost:,.2f}\n"
        )
        return recipe_profit - import_cost - export_cost

    @staticmethod
    def calculate_export_fee(
        base_cost: int,
        tax_rate: float,
        launched_from_command_center: bool = False
    ) -> float:
        # See https://wiki.eveuniversity.org/Planetary_Industry#Import.2FExport_Formulas
        if launched_from_command_center:
            return base_cost * tax_rate * 1.5
        return base_cost * tax_rate

    @staticmethod
    def calculate_import_fee(base_cost: int, tax_rate: float) -> float:
        # See https://wiki.eveuniversity.org/Planetary_Industry#Import.2FExport_Formulas
        return base_cost * tax_rate * 0.5
