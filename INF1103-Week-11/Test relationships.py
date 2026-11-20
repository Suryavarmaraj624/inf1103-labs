"""
Lab 8 test script: demonstrates association, aggregation, composition,
type hints, LSP and polymorphism.

Run from the project folder:  python test_relationships.py
"""
import typing

from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


def heading(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------- Section 2
def test_association() -> None:
    heading("SECTION 2: ASSOCIATION (Supplier and Product)")

    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    laptop = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.2)
    editor = DigitalProduct("D001", "Photo Editor", 79.99, 100, supplier, 450.0)

    print("Supplier shown through each Product:")
    laptop.get_supplier().display_information()
    editor.get_supplier().display_information()
    print("Both products share the SAME Supplier object:",
          laptop.get_supplier() is editor.get_supplier())

    # --- Predict first: what happens to the products after this line? ---
    del supplier

    print("\nAfter 'del supplier':")
    laptop.display_information()
    editor.display_information()
    laptop.get_supplier().display_information()


# ---------------------------------------------------------------- Section 3
def test_aggregation() -> None:
    heading("SECTION 3: AGGREGATION (Inventory and Product)")

    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    mouse = PhysicalProduct("P002", "Mouse", 25.50, 40, supplier, 0.1)
    print("Product created BEFORE any inventory exists:", mouse.get_name())

    inventory_a = Inventory()
    inventory_b = Inventory()

    inventory_a.add_product(mouse)
    print("Inventory A has the mouse:", inventory_a.find_product("P002") is mouse)

    # --- Predict first: will the mouse still work after this removal? ---
    inventory_a.remove_product("P002")

    print("\nAfter removing from Inventory A:")
    print("Inventory A find_product('P002'):", inventory_a.find_product("P002"))
    print("The mouse object still works:")
    mouse.display_information()
    print("update_stock(55) on the removed product:", mouse.update_stock(55),
          "-> stock is now", mouse.get_stock())

    inventory_b.add_product(mouse)
    print("\nSame object added to Inventory B:",
          inventory_b.find_product("P002") is mouse)

    inventory_b.remove_product("P002")
    print("Inventory B emptied. The product still exists:", mouse.get_name())


# ---------------------------------------------------------------- Section 4
def test_composition() -> None:
    heading("SECTION 4: COMPOSITION (Order and OrderLine)")

    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    laptop = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.2)
    editor = DigitalProduct("D001", "Photo Editor", 79.99, 100, supplier, 450.0)

    order_1 = Order("O001")
    order_1.add_order_line(laptop, 2)
    order_1.add_order_line(editor, 1)
    order_1.display_order()

    # --- Predict first: same product in two orders. How many OrderLine
    #     objects and how many Product objects exist? ---
    order_2 = Order("O002")
    order_2.add_order_line(laptop, 1)

    line_in_order_1 = order_1.get_order_lines()[0]
    line_in_order_2 = order_2.get_order_lines()[0]

    print("\nSame product in two orders:")
    print("The two OrderLines are the same object?", line_in_order_1 is line_in_order_2)
    print("Their Products are the same object?",
          line_in_order_1.get_product() is line_in_order_2.get_product())
    print("id(line 1) =", id(line_in_order_1), "| id(line 2) =", id(line_in_order_2))
    print("id(product via line 1) =", id(line_in_order_1.get_product()),
          "| id(product via line 2) =", id(line_in_order_2.get_product()))

    print("\nRemoving the laptop line from Order 1 (the Order manages its lines):")
    order_1.remove_order_line("P001")
    order_1.display_order()
    print("The laptop Product itself is untouched:", laptop.get_name())
    print("Order 2 still has its own line:", len(order_2.get_order_lines()), "line(s)")


# ---------------------------------------------------------------- Section 5
def test_type_hints() -> None:
    heading("SECTION 5: TYPE HINTS EVIDENCE")

    print("Product.__init__:", typing.get_type_hints(Product.__init__))
    print("Inventory.find_product:", typing.get_type_hints(Inventory.find_product))
    print("Inventory.add_product:", typing.get_type_hints(Inventory.add_product))
    print("Order.add_order_line:", typing.get_type_hints(Order.add_order_line))
    print("OrderLine.calculate_subtotal:",
          typing.get_type_hints(OrderLine.calculate_subtotal))
    print("Order.calculate_total:", typing.get_type_hints(Order.calculate_total))


# ---------------------------------------------------------------- Section 6
def show_product_details(product: Product) -> None:
    """Works with ANY Product: uses only what the Product abstraction promises."""
    product.display_information()
    print(product.get_fulfilment_info())


def test_lsp() -> None:
    heading("SECTION 6: LISKOV SUBSTITUTION PRINCIPLE")

    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    laptop = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.2)
    editor = DigitalProduct("D001", "Photo Editor", 79.99, 100, supplier, 450.0)

    print("show_product_details() with a PhysicalProduct:")
    show_product_details(laptop)
    print("\nshow_product_details() with a DigitalProduct:")
    show_product_details(editor)

    inventory = Inventory()
    print("\nBoth types added to one Inventory:",
          inventory.add_product(laptop), inventory.add_product(editor))
    print("\nNormal Inventory operations on both types:")
    print("find_product P001:", inventory.find_product("P001") is laptop)
    print("find_product D001:", inventory.find_product("D001") is editor)
    print("update_stock via Inventory:",
          inventory.update_stock("P001", 30), inventory.update_stock("D001", 200))
    inventory.display_all()
    print("remove_product D001:", inventory.remove_product("D001"))

    print("\nThe expectation Product sets for update_stock():")
    print("  valid quantity accepted  -> the stock changes")
    print("  invalid quantity rejected -> returns False, stock unchanged")
    for product in (laptop, editor):
        before = product.get_stock()
        accepted = product.update_stock(before + 5)
        rejected = product.update_stock(-1)
        print(f"  {product.get_name()}: update_stock({before + 5}) -> {accepted}, "
              f"update_stock(-1) -> {rejected}, stock now {product.get_stock()}")


# ---------------------------------------------------------------- Section 7
def test_polymorphism() -> None:
    heading("SECTION 7: POLYMORPHISM")

    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.2))
    inventory.add_product(DigitalProduct("D001", "Photo Editor", 79.99, 100, supplier, 450.0))

    # --- Predict first: what will get_fulfilment_info() print for each? ---
    # One loop, one common type, no isinstance().
    for product in inventory.get_products():
        product.display_information()
        print(product.get_fulfilment_info())
        print()

def test_edge_cases() -> None:
    heading("EDGE CASES")

    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    laptop = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.2)
    inventory = Inventory()
    order = Order("O001")

    print("Add product:", inventory.add_product(laptop))
    print("Add duplicate ID:", inventory.add_product(laptop))
    print("Find unknown ID:", inventory.find_product("P999"))
    print("Remove unknown ID:", inventory.remove_product("P999"))
    print("Update unknown ID:", inventory.update_stock("P999", 5))
    print("Rejected stock update:", laptop.update_stock(-5), "-> stock still", laptop.get_stock())
    print("Order quantity 0:", order.add_order_line(laptop, 0))
    print("Order quantity -3:", order.add_order_line(laptop, -3))
    print("Remove unknown line:", order.remove_order_line("P999"))
    print("Empty order total:", order.calculate_total())


if __name__ == "__main__":
    test_association()
    test_aggregation()
    test_composition()
    test_type_hints()
    test_lsp()
    test_polymorphism()
    test_edge_cases()