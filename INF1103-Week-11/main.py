import json

from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from discount_strategy import (BulkDiscount, DiscountStrategy, NoDiscount,
                               PercentageDiscount, StudentDiscount)
from inventory import Inventory
from order import Order
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from product_loader import load_products
from supplier import Supplier

FILENAME = "inventory.json"


def get_valid_stock(prompt: str) -> int:
    """
    Keeps asking until the user enters a whole number that is 0 or more.
    int() raises ValueError for text such as "abc" or "2.5", so that is caught
    and the user is asked again (we never continue with incomplete data).
    """
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a number that is 0 or more.")
                continue
            return value
        except ValueError:
            print("Please enter a whole number, e.g. 5")


def get_positive_float(prompt: str) -> float:
    """
    Keeps asking until the user enters a number greater than zero (e.g. a price).
    float() raises ValueError for text such as "abc": caught, ask again.
    """
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_valid_decimal(prompt: str, label: str) -> float:
    """
    Keeps asking until the user enters a number that is 0 or more
    (weight, download size...). label is used in the messages.
    """
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print(f"The {label} cannot be negative.")
                continue
            return value
        except ValueError:
            print(f"Please enter a valid {label}, e.g. 1.5")


def record_to_supplier(record: dict) -> Supplier:
    """
    Builds a Supplier from one saved record.
    Raises: KeyError if a field is missing
    """
    return Supplier(record["id"], record["name"], record["email"])


def record_to_product(record: dict, suppliers: dict[str, Supplier]) -> Product:
    """
    Builds the correct Product subclass from one saved record, linking it to
    the existing Supplier object named by the record's "supplier_id".
    Input:  record (dict), suppliers (dict of supplier_id -> Supplier)
    Output: a Product created by ProductFactory
    Raises: KeyError / TypeError / ValueError if the record is malformed,
            refers to a supplier that does not exist, has an unknown type,
            or breaks a Product validation rule
    """
    supplier = suppliers[record["supplier_id"]]

    # Creation goes through the factory: main.py no longer decides which class
    return ProductFactory.create(
        record["type"],
        record["id"],
        record["name"],
        float(record["price"]),
        int(record["stock"]),
        supplier,
        weight=float(record.get("weight", 0.0)),
        download_size=float(record.get("download_size", 0.0)),
    )


def supplier_to_record(supplier: Supplier) -> dict:
    return {
        "id": supplier.get_supplier_id(),
        "name": supplier.get_name(),
        "email": supplier.get_contact_email(),
    }


def product_to_record(product: Product) -> dict:
    """
    Turns a Product object into a dictionary that can be saved as JSON.
    The supplier is saved as just its ID: suppliers are stored once, in their
    own list, so every product from the same supplier shares one Supplier.
    """
    record = {
        "id": product.get_product_id(),
        "name": product.get_name(),
        "price": product.get_price(),
        "stock": product.get_stock(),
        "supplier_id": product.get_supplier().get_supplier_id(),
    }

    if isinstance(product, PhysicalProduct):
        record["type"] = "physical"
        record["weight"] = product.get_weight()
    elif isinstance(product, DigitalProduct):
        record["type"] = "digital"
        record["download_size"] = product.get_download_size()

    return record


def load_inventory(filename: str = FILENAME) -> tuple[Inventory, dict[str, Supplier]]:
    """
    Loads suppliers and products from a JSON file.
    Suppliers are loaded first so products can be linked to them.
    Input:  filename (str)
    Output: (Inventory, suppliers dict). Both are empty if the file is
            missing or unreadable.
    """
    inventory = Inventory()
    suppliers: dict[str, Supplier] = {}

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"{filename} not found. Starting with an empty inventory.")
        return inventory, suppliers
    except json.JSONDecodeError:
        print(f"Warning: {filename} is not valid JSON. Starting with an empty inventory.")
        return inventory, suppliers

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("suppliers"), list)
        or not isinstance(data.get("products"), list)
    ):
        print(f"Warning: {filename} has an unexpected format. Starting with an empty inventory.")
        return inventory, suppliers

    for record in data["suppliers"]:
        try:
            supplier = record_to_supplier(record)
        except (KeyError, TypeError):
            print("Warning: skipped a malformed supplier record.")
            continue
        suppliers[supplier.get_supplier_id()] = supplier

    for record in data["products"]:
        try:
            product = record_to_product(record, suppliers)
        except (KeyError, TypeError, ValueError):
            print("Warning: skipped a malformed product record.")
            continue
        inventory.add_product(product)

    print("Inventory loaded successfully.")
    return inventory, suppliers


def save_inventory(inventory: Inventory, suppliers: dict[str, Supplier],
                   filename: str = FILENAME) -> bool:
    """
    Saves every supplier and every product to a JSON file.
    Input:  inventory (Inventory), suppliers (dict), filename (str)
    Output: True if saved, False if the file could not be written
            (e.g. it is open in another program, or the folder is read-only)
    """
    data = {
        "suppliers": [supplier_to_record(s) for s in suppliers.values()],
        "products": [product_to_record(p) for p in inventory.get_products()],
    }

    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except OSError as error:  # PermissionError is a kind of OSError
        print(f"Error: could not save to {filename} ({error}).")
        return False
    return True


def display_menu() -> None:
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Add Supplier")
    print("6. Create Order")
    print("7. Save Inventory")
    print("8. Load Products from CSV")
    print("9. Exit")
    print("----------------------------")


def prompt_add_supplier(suppliers: dict[str, Supplier]) -> None:
    print("Add New Supplier")
    supplier_id = input("Supplier ID: ").strip().upper()
    name = input("Supplier Name: ").strip()
    email = input("Contact Email: ").strip()

    if supplier_id == "" or name == "" or email == "":
        print("Error: Supplier ID, Name and Email cannot be empty. Entry rejected.")
        return

    if "@" not in email:
        print(f"Error: '{email}' is not a valid email address. Entry rejected.")
        return

    if supplier_id in suppliers:
        print(f"Error: Supplier ID '{supplier_id}' already exists. Entry rejected.")
        return

    suppliers[supplier_id] = Supplier(supplier_id, name, email)
    print("Supplier added successfully!")


def prompt_add_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("Add New Product")

    if not suppliers:
        print("Error: No suppliers exist yet. Add a supplier first (option 5).")
        return

    print("1. Physical Product")
    print("2. Digital Product")
    product_type = input("Choose product type: ").strip()

    if product_type not in ("1", "2"):
        print("Error: Invalid product type. Entry rejected.")
        return

    product_id = input("Product ID: ").strip().upper()
    name = input("Product Name: ").strip()

    if product_id == "" or name == "":
        print("Error: Product ID and Name cannot be empty. Entry rejected.")
        return

    price = get_positive_float("Price: ")
    stock = get_valid_stock("Stock Quantity: ")

    print("Available Suppliers:")
    for supplier in suppliers.values():
        supplier.display_information()

    supplier_id = input("Supplier ID: ").strip().upper()
    if supplier_id not in suppliers:
        print(f"Error: Supplier '{supplier_id}' not found. Entry rejected.")
        return
    supplier = suppliers[supplier_id]

    weight = 0.0
    download_size = 0.0
    if product_type == "1":
        kind = "physical"
        weight = get_valid_decimal("Weight (kg): ", "weight")
    else:
        kind = "digital"
        download_size = get_valid_decimal("Download Size (MB): ", "download size")

    try:
        product = ProductFactory.create(kind, product_id, name, price, stock,
                                        supplier, weight=weight,
                                        download_size=download_size)
    except ValueError as error:
        print(f"Error: {error} Entry rejected.")
        return

    if inventory.add_product(product):
        print("Product added successfully!")
    else:
        print(f"Error: Product ID '{product_id}' already exists. Entry rejected.")


def prompt_update_stock(inventory: Inventory) -> None:
    print("Update Stock")
    product_id = input("Enter Product ID: ").strip().upper()

    product = inventory.find_product(product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}")

    new_stock = get_valid_stock("New Stock Quantity: ")

    try:
        inventory.update_stock(product_id, new_stock)
    except ValueError as error:
        print(f"Error: {error} Stock not changed.")
        return
    print("Stock updated successfully!")


def prompt_search_product(inventory: Inventory) -> None:
    print("Search Product")
    product_id = input("Enter Product ID: ").strip().upper()

    product = inventory.find_product(product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found")
    print("-" * 48)
    product.display_information()
    print(f"Fulfilment: {product.get_fulfilment_info()}")
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")
    print("-" * 48)


def choose_discount() -> DiscountStrategy:
    """
    Asks the user which discount to apply and returns that strategy object.
    The choice between strategies happens here, at the user-interface edge.
    Order itself contains no discount if/elif: it just calls apply().
    """
    print("Discounts:")
    print("1. No discount")
    print("2. Percentage discount")
    print("3. Bulk discount ($20 off orders of $200 or more)")
    print("4. Student discount (5% off)")

    while True:
        choice = input("Choose discount: ").strip()
        if choice == "1":
            return NoDiscount()
        elif choice == "2":
            while True:
                percent = get_positive_float("Percentage off (e.g. 10): ")
                try:
                    return PercentageDiscount(percent)
                except ValueError as error:
                    print(error)
        elif choice == "3":
            return BulkDiscount(200, 20)
        elif choice == "4":
            return StudentDiscount()
        print("Please enter a number from 1 to 4.")


def prompt_create_order(inventory: Inventory) -> None:
    print("Create Order")
    order_id = input("Order ID: ").strip().upper()

    if order_id == "":
        print("Error: Order ID cannot be empty. Entry rejected.")
        return

    order = Order(order_id)  # no strategy given, so it starts with NoDiscount()

    while True:
        product_id = input("Product ID to add (or 'done' to finish): ").strip().upper()

        if product_id == "DONE":
            break

        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found.")
            continue

        quantity = get_valid_stock("Quantity: ")

        try:
            order.add_order_line(product, quantity)
        except ValueError as error:
            print(f"Error: {error} Line not added.")
            continue

        print(f"Added {quantity} x {product.get_name()} to the order.")

    print(f"Subtotal so far: ${order.calculate_subtotal():.2f}")
    order.set_discount(choose_discount())  # swap the strategy on this order

    print()
    order.display_order()


def prompt_load_csv(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("Load Products from CSV")

    if not suppliers:
        print("Error: No suppliers exist yet. Add a supplier first (option 5).")
        return

    path = input("CSV file name [products.csv]: ").strip() or "products.csv"

    print("Available Suppliers:")
    for supplier in suppliers.values():
        supplier.display_information()

    supplier_id = input("Supplier ID for these products: ").strip().upper()
    if supplier_id not in suppliers:
        print(f"Error: Supplier '{supplier_id}' not found. Entry rejected.")
        return

    load_products(path, inventory, suppliers[supplier_id])


def main() -> None:
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)

    inventory, suppliers = load_inventory()

    display_menu()

    while True:
        option = input("Enter option: ").strip()

        if option == "1":
            inventory.display_all()
        elif option == "2":
            prompt_add_product(inventory, suppliers)
        elif option == "3":
            prompt_update_stock(inventory)
        elif option == "4":
            prompt_search_product(inventory)
        elif option == "5":
            prompt_add_supplier(suppliers)
        elif option == "6":
            prompt_create_order(inventory)
        elif option == "7":
            print("Saving inventory...")
            if save_inventory(inventory, suppliers):
                print(f"Inventory saved successfully to {FILENAME}.")
        elif option == "8":
            prompt_load_csv(inventory, suppliers)
        elif option == "9":
            print("Saving inventory before exit...")
            if save_inventory(inventory, suppliers):
                print("Inventory saved successfully.")
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()