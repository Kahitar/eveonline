import argparse

from eveapi import market
from eveapi.pi import PIRecipe, PlanetaryProduction
from eveapi.recipe import Recipe

def main():
    forge_market = market.Market(10000002, system_id=30000142)
    # recipe = Recipe("Wetware Mainframe")
    # cost = recipe.get_ingredients_cost(forge_market)
    # sell_order = recipe.get_product_price(forge_market)
    # print(f"Ingredients cost {recipe.product.name}: {cost:,.2f} ISK")
    # print(f"Sell Order: {sell_order:,.2f}")

    # print("=================================================")
    # profit = recipe.get_profit(forge_market)
    # print(f"Profit: {profit:,.2f}")

    print("=================================================")

    pi_recipe = PIRecipe("Fertilizer")
    pi = PlanetaryProduction(0.18, pi_recipe)
    pi_profit = pi.get_overall_profit(forge_market)
    print(f"PI Profit: {pi_profit:,.2f}")

if __name__ == "__main__":
    main()