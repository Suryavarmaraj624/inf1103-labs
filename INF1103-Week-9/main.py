import json
import os

from inventory import Inventory
from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from can_be_shipped import CanBeShipped

FILENAME = "inventory.json"
 
 
def get_valid_stock(prompt):
   
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
 
 
def get_valid_decimal(prompt, label):
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

def record_to_product(record):
    product_type = record["type"]

    if product_type == "physical":
        return PhysicalProduct(
            record["id"], record["name"], float(record["price"]),
            int(record["stock"]), float(record["weight"]),
        )

    if product_type == "digital":
        return DigitalProduct(
            record["id"], record["name"], float(record["price"]),
            int(record["stock"]), float(record["download_size"]),
        )

    raise ValueError(f"Unknown product type: {product_type}")


def product_to_record(product):
    record = {
        "id": product.get_product_id(),
        "name": product.get_name(),
        "price": product.get_price(),
        "stock": product.get_stock(),
    }

    if isinstance(product, PhysicalProduct):
        record["type"] = "physical"
        record["weight"] = product.get_weight()
    elif isinstance(product, DigitalProduct):
        record["type"] = "digital"
        record["download_size"] = product.get_download_size()

    return record
 
def load_inventory(filename=FILENAME):
    
    inventory = Inventory()
 
    if not os.path.exists(filename):
        print(f"{filename} not found. Starting with an empty inventory.")
        return inventory
 
    print(f"{filename} found.")
 
    try:
        with open(filename, "r") as f:
            records = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {filename} is not valid JSON. Starting with an empty inventory.")
        return inventory
 
    if not isinstance(records, list):
        print(f"Warning: {filename} has an unexpected format. Starting with an empty inventory.")
        return inventory
 
    for record in records:
        try:
            product = record_to_product(record)
        except (KeyError, TypeError, ValueError):
            print("Warning: skipped a malformed product record.")
            continue
        inventory.add_product(product)
 
    print("Inventory loaded successfully.")
    return inventory
 
 
def save_inventory(inventory, filename=FILENAME):
    
    records = []
    for product in inventory.get_products():
        records.append(product_to_record(product))
 
    with open(filename, "w") as f:
        json.dump(records, f, indent=4)
 
 
def display_menu():
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")
 
 
def prompt_add_product(inventory):
    print("Add New Product")
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

    if product_type == "1":
        weight = get_valid_decimal("Weight (kg): ", "weight")
        if weight is None:
            return
        product = PhysicalProduct(product_id, name, price, stock, weight)
    else:
        download_size = get_valid_decimal("Download Size (MB): ", "download size")
        if download_size is None:
            return
        product = DigitalProduct(product_id, name, price, stock, download_size)

    if inventory.add_product(product):
        print("Product added successfully!")
    else:
        print(f"Error: Product ID '{product_id}' already exists. Entry rejected.")
 
def prompt_update_stock(inventory):
    print("Update Stock")
    product_id = input("Enter Product ID: ").strip().upper()
 
    product = inventory.search_product(product_id)
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
 
 
def prompt_search_product(inventory):
    print("Search Product")
    product_id = input("Enter Product ID: ").strip().upper()
 
    product = inventory.search_product(product_id)
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
 
 
def main():
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
 
    inventory = load_inventory()
 
    display_menu()
 
    while True:
        option = input("Enter option: ").strip()
 
        if option == "1":
            inventory.display_all()
        elif option == "2":
            prompt_add_product(inventory)
        elif option == "3":
            prompt_update_stock(inventory)
        elif option == "4":
            prompt_search_product(inventory)
        elif option == "5":
            print("Saving inventory...")
            save_inventory(inventory)
            print(f"Inventory saved successfully to {FILENAME}.")
        elif option == "6":
            print("Saving inventory before exit...")
            save_inventory(inventory)
            print("Inventory saved successfully.")
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()