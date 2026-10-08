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


def search_product(inventory, product_id):
    for product in inventory:
        if product["id"] == product_id:
            return product
    return None


def add_product(inventory, product_id, name, price, stock):
    if search_product(inventory, product_id) is not None:
        return False

    inventory.append({"id": product_id, "name": name, "price": price, "stock": stock})
    return True


def update_stock(inventory, product_id, new_stock):
    product = search_product(inventory, product_id)
    if product is None:
        return False

    product["stock"] = new_stock
    return True

def display_all(inventory):
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

def main():
    inventory = [
        {"id": "P001", "name": "Laptop", "price": 1200.00, "stock": 15},
        {"id": "P002", "name": "Mouse", "price": 25.50, "stock": 40},
        {"id": "P003", "name": "Keyboard", "price": 45.00, "stock": 25},
    ]
    print(search_product(inventory, "P002"))      # the Mouse dictionary
    print(search_product(inventory, "P999"))      # None
    print(add_product(inventory, "P004", "Monitor", 299.99, 10))   # True
    print(add_product(inventory, "P004", "Monitor", 299.99, 10))   # False (duplicate)
    print(update_stock(inventory, "P002", 50))    # True
    display_all(inventory)                        # Mouse stock 50, Monitor listed


if __name__ == "__main__":
    main()