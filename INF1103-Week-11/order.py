from discount_strategy import DiscountStrategy, NoDiscount
from order_line import OrderLine
from product import Product


class Order:
   
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []
        # None (not NoDiscount()) as the default, so every order gets its own
        # default object instead of all orders sharing one created at import time
        self.__discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def get_order_id(self) -> str:
        return self.__order_id

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.__discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self.__order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id() == product_id:
                self.__order_lines.remove(order_line)
                return True
        return False

    def get_order_lines(self) -> list[OrderLine]:
        return list(self.__order_lines)

    def calculate_subtotal(self) -> float:
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def calculate_total(self) -> float:
        return self.__discount.apply(self.calculate_subtotal())

    def display_order(self) -> None:
        print(f"Order {self.__order_id}")
        print("-" * 48)
        if not self.__order_lines:
            print("No items in this order.")
        for order_line in self.__order_lines:
            order_line.display_line()
        print("-" * 48)
        print(f"Subtotal:    ${self.calculate_subtotal():.2f}")
        print(f"Discount:    {self.__discount.describe()}")
        print(f"Order Total: ${self.calculate_total():.2f}")