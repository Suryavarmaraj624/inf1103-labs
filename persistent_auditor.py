def get_valid_input():
    entry = input("Enter stock quantity (or 'quit' to finish): ").strip()

    if entry.lower() == "quit":
        return "quit"

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


def main():
    orders = load_inventory()

    print("Current Orders:\n")
    for order_id, product, quantity in orders:
        print(f"{order_id}, {product}, {quantity}")
    print()

    # keep the rest of main() as it was in modular_auditor.py for now —
    # don't touch the loop yet, just verify loading works first


if __name__ == "__main__":
    main()