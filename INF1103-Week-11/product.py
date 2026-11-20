from abc import ABC, abstractmethod
from supplier import Supplier

class Product(ABC):

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier) -> None:
        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        self.__supplier: Supplier = supplier

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def update_stock(self, quantity):
        
        if not isinstance(quantity, int) or quantity < 0:
            return False

        self.__stock = quantity
        return True

    def display_information(self):
        print(
            f"ID: {self.__product_id} | Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | Stock: {self.__stock}"
        )

        print(
            f"    Supplier: {self.__supplier.get_name()} "
            f"({self.__supplier.get_supplier_id()})"
        )

    @abstractmethod
    def get_fulfilment_info(self):
        pass