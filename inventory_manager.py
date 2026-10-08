import json
import os

FILENAME = "inventory.json"


def get_valid_stock(prompt):
    """
    Prompts for a stock quantity and validates it.
    Input:  prompt (str)
    Output: a valid non-negative int, or None (invalid entry)
    """
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
    """
    Prompts for a price and validates it.
    Input:  prompt (str)
    Output: a valid non-negative float, or None (invalid entry)
    """
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


def search_product(inventory, product_id):
    """
    Looks for a product by ID.
    Input:  inventory (list of dicts), product_id (str)
    Output: the product dictionary if found, otherwise None
    """
    for product in inventory:
        if product["id"] == product_id:
            return product
    return None


def add_product(inventory, product_id, name, price, stock):
    """
    Adds a new product to the inventory list.
    Input:  inventory (list of dicts), product_id (str), name (str),
            price (float), stock (int)
    Output: True if added, False if the product ID already exists
    """
    if search_product(inventory, product_id) is not None:
        return False

    inventory.append({"id": product_id, "name": name, "price": price, "stock": stock})
    return True


def update_stock(inventory, product_id, new_stock):
    """
    Sets a new stock quantity for an existing product.
    Input:  inventory (list of dicts), product_id (str), new_stock (int)
    Output: True if updated, False if the product doesn't exist
    """
    product = search_product(inventory, product_id)
    if product is None:
        return False

    product["stock"] = new_stock
    return True


def display_all(inventory):
    """
    Prints every product in the inventory.
    Input:  inventory (list of dicts)
    Output: none (prints to screen)
    """
    print("Current Inventory")
    print("-" * 48)
    if not inventory:
        print("No products in inventory.")
    for product in inventory:
        print(
            f"ID: {product['id']} | Name: {product['name']} | "
            f"Price: ${product['price']:.2f} | Stock: {product['stock']}"
        )
    print("-" * 48)


def load_inventory(filename=FILENAME):
    """
    Loads the inventory from a JSON file if it exists.
    Input:  filename (str)
    Output: list of product dicts. Returns [] if the file is missing
            or isn't valid JSON -- no error is raised.
    """
    if not os.path.exists(filename):
        print(f"{filename} not found. Starting with an empty inventory.")
        return []

    print(f"{filename} found.")

    try:
        with open(filename, "r") as f:
            inventory = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {filename} is not valid JSON. Starting with an empty inventory.")
        return []

    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory, filename=FILENAME):
    """
    Saves the inventory list to a JSON file.
    Input:  inventory (list of dicts), filename (str)
    Output: none (writes to file)
    """
    with open(filename, "w") as f:
        json.dump(inventory, f, indent=4)


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

    if add_product(inventory, product_id, name, price, stock):
        print("Product added successfully!")
    else:
        print(f"Error: Product ID '{product_id}' already exists. Entry rejected.")


def prompt_update_stock(inventory):
    print("Update Stock")
    product_id = input("Enter Product ID: ").strip().upper()

    product = search_product(inventory, product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found:")
    print(f"Name: {product['name']}")
    print(f"Current Stock: {product['stock']}")

    new_stock = get_valid_stock("New Stock Quantity: ")
    if new_stock is None:
        return

    update_stock(inventory, product_id, new_stock)
    print("Stock updated successfully!")


def prompt_search_product(inventory):
    print("Search Product")
    product_id = input("Enter Product ID: ").strip().upper()

    product = search_product(inventory, product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found")
    print("-" * 48)
    print(f"ID: {product['id']}")
    print(f"Name: {product['name']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Stock: {product['stock']}")
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
            display_all(inventory)
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