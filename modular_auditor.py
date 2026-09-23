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

def main():
    total_inventory = 0
    failed_entries = 0

    print("Smart Inventory Auditor")

    while True:
        result = get_valid_input()

        if result == "quit":
            break

        if result is None:
            failed_entries += 1
            continue

        quantity = result
        total_inventory = process_delivery(total_inventory, quantity)
        tax = calculate_tax(quantity)
        print(f"Accepted. Delivery: {quantity} | Tax: {tax:.2f} | Current inventory total: {total_inventory}")

        if total_inventory > 500:
            print(f"ALERT: Overstock! Inventory ({total_inventory}) exceeds 500 units.")
            break

    print("\n--- Final Report ---")
    print(f"Total Units Processed: {total_inventory}")
    print(f"Number of Failed/Rejected Entries: {failed_entries}")


if __name__ == "__main__":
    main()