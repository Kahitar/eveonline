from __future__ import annotations

from dataclasses import dataclass
from os import system
from typing import List

from eveapi.recipe import Recipe

from . import api_request

ORDER_TYPE_SELL = "sell"
ORDER_TYPE_BUY  = "buy"

@dataclass
class Order:
    is_buy_order: bool
    location_id: int
    order_id: int
    price: int
    system_id: int
    type_id: int
    volume_remain: int
    volume_total: int

    @staticmethod
    def from_json(json: dict) -> Order:
        return Order(
            is_buy_order=json['is_buy_order'],
            location_id=json['location_id'],
            order_id=json['order_id'],
            price=json['price'],
            system_id=json['system_id'],
            type_id=json['type_id'],
            volume_remain=json['volume_remain'],
            volume_total=json['volume_total'],
        )


class Market:
    def __init__(self, region_code: int, system_id: int = None):
        self.region_code = region_code
        self.system_id = system_id

    def get_order_list(self, type_id: int, order_type: str) -> List[Order]:
        query_args = api_request.build_query_args(
            datasource="tranquility",
            order_type=order_type,
            page=1,
            type_id=type_id,
        )
        resp = api_request.get(f"markets/{self.region_code}/orders/{query_args}")
        orders: List[Order] = []
        for order_json in api_request.response_to_json(resp):
            order = Order.from_json(order_json)
            if self.system_id is not None:
                if self.system_id != order.system_id:
                    # Don't add this order to the list
                    continue
            orders.append(order)
        return sorted(orders, key=lambda o: o.price)

    def get_ingredients_cost(self, recipe: Recipe):
        order_type: str = ORDER_TYPE_SELL

        cost_sum = 0
        for item, amount in recipe.ingredients.items():
            orders = self.get_order_list(item.type_id, order_type)
            amount_remaining = amount
            for order in orders:
                if order.volume_remain > amount_remaining:
                    # The order can fill the remaining amount
                    cost_sum += order.price * amount_remaining
                    amount_remaining = 0
                    break
                else:
                    # Buy everything from this order than continue 
                    # with the next one
                    cost_sum += order.price * order.volume_remain
                    amount_remaining -= order.volume_remain
                    last_price = order.price
            
            # Check that all items could be purchased
            if amount_remaining > 0:
                print(
                    f"WARNING: Not enough {item.name} on the market for this recipe. "
                    f"Missing {amount_remaining} items."
                )
                # assume the highest price for the rest of the items
                cost_sum += last_price * amount_remaining

        return cost_sum
