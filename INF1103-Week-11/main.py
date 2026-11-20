import json
import os

from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier
from product_factory import ProductFactory

FILENAME = "inventory.json"


def get_valid_stock(prompt: str) -> int | None:
    entry = input(prompt).strip()

    digits = entry[1:] if entry.startswith("-") else entry
    if not digits.isdigit():
        print(f"Error: '{entry}' is not a valid number. Entry rejected.")
        return None

    stock = int(entry)

    if stock < 0:
        print(f"Error: Negative quantity ({stock}) is not allowed. Entry rejected.")
        return None

    return stock


def get_valid_decimal(prompt: str, label: str) -> float | None:
    entry = input(prompt).strip()

    digits = entry[1:] if entry.startswith("-") else entry
    if not digits.replace(".", "", 1).isdigit():
        print(f"Error: '{entry}' is not a valid {label}. Entry rejected.")
        return None

    value = float(entry)

    if value < 0:
        print(f"Error: Negative {label} ({value}) is not allowed. Entry rejected.")
        return None

    return value


def record_to_supplier(record: dict) -> Supplier:
    return Supplier(record["id"], record["name"], record["email"])


def record_to_product(record: dict, suppliers: dict[str, Supplier]) -> Product:
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
    inventory = Inventory()
    suppliers: dict[str, Supplier] = {}

    if not os.path.exists(filename):
        print(f"{filename} not found. Starting with an empty inventory.")
        return inventory, suppliers

    print(f"{filename} found.")

    try:
        with open(filename, "r") as f:
            data = json.load(f)
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
                   filename: str = FILENAME) -> None:
    data = {
        "suppliers": [supplier_to_record(s) for s in suppliers.values()],
        "products": [product_to_record(p) for p in inventory.get_products()],
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def display_menu() -> None:
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Add Supplier")
    print("6. Create Order")
    print("7. Save Inventory")
    print("8. Exit")
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

    price = get_valid_decimal("Price: ", "price")
    if price is None:
        return

    stock = get_valid_stock("Stock Quantity: ")
    if stock is None:
        return

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
        entered = get_valid_decimal("Weight (kg): ", "weight")
        if entered is None:
            return
        weight = entered
    else:
        kind = "digital"
        entered = get_valid_decimal("Download Size (MB): ", "download size")
        if entered is None:
            return
        download_size = entered

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
    if new_stock is None:
        return

    inventory.update_stock(product_id, new_stock)
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


def prompt_create_order(inventory: Inventory) -> None:
    print("Create Order")
    order_id = input("Order ID: ").strip().upper()

    if order_id == "":
        print("Error: Order ID cannot be empty. Entry rejected.")
        return

    order = Order(order_id)

    while True:
        product_id = input("Product ID to add (or 'done' to finish): ").strip().upper()

        if product_id == "DONE":
            break

        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found.")
            continue

        quantity = get_valid_stock("Quantity: ")
        if quantity is None:
            continue

        if order.add_order_line(product, quantity):
            print(f"Added {quantity} x {product.get_name()} to the order.")
        else:
            print("Error: Quantity must be at least 1. Entry rejected.")

    print()
    order.display_order()


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
            save_inventory(inventory, suppliers)
            print(f"Inventory saved successfully to {FILENAME}.")
        elif option == "8":
            print("Saving inventory before exit...")
            save_inventory(inventory, suppliers)
            print("Inventory saved successfully.")
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    main()