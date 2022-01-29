from __future__ import annotations

from dataclasses import dataclass
from os import system
from typing import List
from eveapi.item import Item

from eveapi.recipe import Recipe

from . import api_request

ORDER_TYPE_SELL = "sell"
ORDER_TYPE_BUY  = "buy"

BROKERS_FEE = 0.01

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
    def __init__(self, region_code: int, system_id: int = None, sell_order_tax: float = 0.08):
        self.region_code = region_code
        self.system_id = system_id
        self.sell_order_tax = sell_order_tax

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

    def get_buy_price(self, item: Item, amount: int = 1) -> float:
        """ Get the buy price for the item (buy from sell order), including tax. """
        order_type: str = ORDER_TYPE_SELL

        orders = self.get_order_list(item.type_id, order_type)
        if len(orders) == 0:
            # No sell order for this item exists...
            return 0

        amount_remaining = amount
        cost_sum = 0
        for order in orders:
            if order.volume_remain > amount_remaining:
                # The order can fill the remaining amount
                p = cost_sum + order.price * amount_remaining
                print(f"Buy {amount} {item.name} for {p:,.2f} ISK")
                return p
            else:
                # Buy everything from this order than continue 
                # with the next one
                print("Remaining in order:", order.volume_remain)
                print("For price:", order.price)
                print("Amount before:", amount_remaining)
                cost_sum += order.price * order.volume_remain
                amount_remaining -= order.volume_remain
                print("Amount after:", amount_remaining)
                last_price = order.price
        
        # Check that all items could be purchased
        if amount_remaining > 0:
            print(
                f"WARNING: Not enough {item.name} on the market for this recipe. "
                f"Missing {amount_remaining} items."
            )
            # assume the highest price for the rest of the items
            return last_price * amount_remaining

    def get_sell_price(self, item: Item, amount: int = 1) -> float:
        """ Get the sell price for the item (sell with sell order), including tax.
        Asumes that the target sell price is the minimum sell order. 
        """
        sell_orders = self.get_order_list(item.type_id, ORDER_TYPE_SELL)
        if len(sell_orders) == 0:
            # No sell order for this item exists...
            return 0
        return sell_orders[0].price * amount * (1 - self.sell_order_tax - BROKERS_FEE)