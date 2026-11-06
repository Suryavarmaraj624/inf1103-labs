import json
import os

from inventory import Inventory
from product import Product
 
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
 
 
def get_valid_price(prompt):
    
    entry = input(prompt).strip()
 
    digits = entry[1:] if entry.startswith("-") else entry
    if not digits.replace(".", "", 1).isdigit():
        print(f"Error: '{entry}' is not a valid price. Entry rejected.")
        return None
 
    price = float(entry)
 
    if price < 0:
        print(f"Error: Negative price ({price}) is not allowed. Entry rejected.")
        return None
 
    return price
 
 
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
            product = Product(
                record["id"], record["name"], float(record["price"]), int(record["stock"])
            )
        except (KeyError, TypeError, ValueError):
            print("Warning: skipped a malformed product record.")
            continue
        inventory.add_product(product)
 
    print("Inventory loaded successfully.")
    return inventory
 
 
def save_inventory(inventory, filename=FILENAME):
    
    records = []
    for product in inventory.get_products():
        records.append(
            {
                "id": product.get_product_id(),
                "name": product.get_name(),
                "price": product.get_price(),
                "stock": product.get_stock(),
            }
        )
 
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
    product_id = input("Product ID: ").strip().upper()
    name = input("Product Name: ").strip()
 
    if product_id == "" or name == "":
        print("Error: Product ID and Name cannot be empty. Entry rejected.")
        return
 
    price = get_valid_price("Price: ")
    if price is None:
        return
 
    stock = get_valid_stock("Stock Quantity: ")
    if stock is None:
        return
 
    product = Product(product_id, name, price, stock)
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
    print(f"ID: {product.get_product_id()}")
    print(f"Name: {product.get_name()}")
    print(f"Price: ${product.get_price():.2f}")
    print(f"Stock: {product.get_stock()}")
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