from product import Product


class OrderLine:
    def __init__(self, product: Product, quantity: int) -> None:
        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def display_line(self) -> None:
        print(
            f"{self.__product.get_product_id()} | {self.__product.get_name()} | "
            f"Qty: {self.__quantity} | Subtotal: ${self.calculate_subtotal():.2f}"
        )