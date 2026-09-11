def main():
    total_inventory = 0
    failed_entries = 0

    print("Smart Inventory Auditor")
    print("Enter stock quantity (or type 'quit' to finish):")

    while True:
        entry = input("> ").strip()

        # Exit condition
        if entry.lower() == "quit":
            break

        # Validate that it's a number (allow a leading '-' so we can
        # separately catch negative numbers as a business rule violation)
        if not entry.lstrip("-").isdigit() or entry in ("", "-"):
            print(f"Error: '{entry}' is not a valid number. Entry rejected.")
            failed_entries += 1
            continue

        quantity = int(entry)

        # Business rule: reject negative numbers
        if quantity < 0:
            print(f"Error: Negative quantity ({quantity}) is not allowed. Entry rejected.")
            failed_entries += 1
            continue

        # Valid entry - update running total
        total_inventory += quantity
        print(f"Accepted. Current inventory total: {total_inventory}")

        # Overstock check
        if total_inventory > 500:
            print(f"ALERT: Overstock! Inventory ({total_inventory}) exceeds 500 units.")
            break

    # Final report
    print("\n--- Final Report ---")
    print(f"Total Units Processed: {total_inventory}")
    print(f"Number of Failed/Rejected Entries: {failed_entries}")


if __name__ == "__main__":
    main()