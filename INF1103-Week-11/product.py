from abc import ABC, abstractmethod

from supplier import Supplier


class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier) -> None:
        # Validation: the Product owns these rules, so it checks them itself.
        # Every subclass passes through here via super().__init__(), so no
        # subclass can skip them (LSP).
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        Product.__validate_stock(stock)

        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        self.__supplier: Supplier = supplier

    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    @staticmethod
    def __validate_stock(stock: int) -> None:
        if not isinstance(stock, int) or stock < 0:
            raise ValueError("Stock quantity cannot be negative.")

    def update_stock(self, quantity: int) -> None:
        Product.__validate_stock(quantity)
        self.__stock = quantity

    def display_information(self) -> None:
       
        print(
            f"ID: {self.__product_id} | Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | Stock: {self.__stock}"
        )
        print(
            f"    Supplier: {self.__supplier.get_name()} "
            f"({self.__supplier.get_supplier_id()})"
        )

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """
        Output: a message explaining how this product is fulfilled.
        Every subclass must provide its own implementation.
        """
        pass