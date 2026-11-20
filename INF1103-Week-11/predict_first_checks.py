from discount_strategy import BulkDiscount, PercentageDiscount, StudentDiscount
from inventory import Inventory
from main import get_positive_float
from order import Order
from product_factory import ProductFactory
from product_loader import load_products
from supplier import Supplier


def heading(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def check_strategy() -> None:
    heading("2.3 / 2.4  STRATEGY")
    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    chair = ProductFactory.create("physical", "P001", "Chair", 100.00, 10, supplier, weight=7.5)
    lamp = ProductFactory.create("physical", "P002", "Lamp", 50.00, 10, supplier, weight=1.0)

    order = Order("O001", BulkDiscount(200, 20))
    order.add_order_line(chair, 2)
    order.add_order_line(lamp, 1)
    print("Lines add up to:", order.calculate_subtotal())
    print("With BulkDiscount(200, 20):", order.calculate_total())

    order.set_discount(PercentageDiscount(10))
    print("After set_discount(PercentageDiscount(10)):", order.calculate_total())

    order.set_discount(StudentDiscount())  # the 4th strategy: Order unchanged
    print("After set_discount(StudentDiscount()):", order.calculate_total())

    shared = PercentageDiscount(10)
    order_a = Order("A", shared)
    order_b = Order("B", shared)
    print("Two orders sharing ONE PercentageDiscount object:",
          order_a.get_discount() is order_b.get_discount())


def check_factory() -> None:
    heading("3.2  FACTORY WITH AN UNKNOWN TYPE")
    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    try:
        ProductFactory.create("service", "S001", "Installation", 30.00, 5, supplier)
    except ValueError as error:
        print(f"Caught {type(error).__name__}: {error}")
    # To see what happens when NOTHING catches it, type this in a Python shell:
    #   ProductFactory.create("service", "S001", "Installation", 30.0, 5, supplier)


def check_input() -> None:
    heading("5.1  get_positive_float  (type: abc, then -5, then 12.50)")
    value = get_positive_float("Price: ")
    print("Returned:", value)


def check_loading() -> None:
    heading("5.2  load_products('products.csv')")
    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    inventory = Inventory()  # empty, so no IDs clash with inventory.json
    load_products("products.csv", inventory, supplier)

    heading("5.2  load_products with a file that does not exist")
    load_products("missing_products.csv", Inventory(), supplier)


if __name__ == "__main__":
    check_strategy()
    check_factory()
    check_input()
    check_loading()