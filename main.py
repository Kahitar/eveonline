from eveapi import market
from eveapi.recipe import Recipe

def main():
    forge_market = market.Market(10000002, system_id=30000142)
    recipe = Recipe("Wetware Mainframe")
    cost = forge_market.get_ingredients_cost(recipe)
    print(f"Ingredients cost {recipe.product.name}: {cost:.2f} ISK")

if __name__ == "__main__":
    main()