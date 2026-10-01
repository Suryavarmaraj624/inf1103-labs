def get_valid_quantity(prompt="Enter Quantity: "):
    entry = input(prompt).strip()

    if not entry.lstrip("-").isdigit() or entry in ("", "-"):
        print(f"Error: '{entry}' is not a valid number. Entry rejected.")
        return None

    quantity = int(entry)

    if quantity < 0:
        print(f"Error: Negative quantity ({quantity}) is not allowed. Entry rejected.")
        return None

    return quantity


def process_delivery(current_total, new_value):
    return current_total + new_value

def calculate_tax(amount):
    return amount * 0.10

def generate_report(total_units, failed_attempts):
    print("\n--- Final Report ---")
    print(f"Total Deliveries Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")

def load_inventory(filename="inventory.txt"):
    orders = []
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) == 3:
                    order_id, product, quantity = parts
                    orders.append((int(order_id), product.strip(), int(quantity)))
    except FileNotFoundError:
        pass
    return orders


def get_next_order_id(orders):
    if not orders:
        return 1001
    return max(order_id for order_id, _, _ in orders) + 1

def save_inventory(orders, filename="inventory.txt"):
    with open(filename, "w") as f:
        for order_id, product, quantity in orders:
            f.write(f"{order_id},{product},{quantity}\n")

def main():
    orders = load_inventory()
    failed_entries = 0
    total_inventory = sum(quantity for _, _, quantity in orders)
 
    print("Current Orders:\n")
    for order_id, product, quantity in orders:
        print(f"{order_id}, {product}, {quantity}")
    print()
 
    while True:
        product = input("Enter Product Name (or 'quit' to finish): ").strip()
 
        if product.lower() == "quit":
            break
 
        if product == "":
            print("Error: Product name cannot be empty. Entry rejected.")
            failed_entries += 1
            continue
 
        quantity = get_valid_quantity("Enter Quantity: ")
 
        if quantity is None:
            failed_entries += 1
            continue
 
        order_id = get_next_order_id(orders)
        orders.append((order_id, product, quantity))
        total_inventory = process_delivery(total_inventory, quantity)
        tax = calculate_tax(quantity)
 
        print("\nNew Order Added:")
        print(f"{order_id},{product},{quantity}")
        print(f"(Tax on this delivery: {tax:.2f})\n")
 
        if total_inventory > 500:
            print(f"ALERT: Overstock! Inventory ({total_inventory}) exceeds 500 units.")
            break
 
    save_inventory(orders)
    print("Order successfully saved to orders.txt\n")
 
    generate_report(total_inventory, failed_entries)
 
 
if __name__ == "__main__":
    main()