import csv

from inventory import Inventory
from product_factory import ProductFactory
from supplier import Supplier


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    """
    Reads products from a CSV file, creates each one through ProductFactory
    and adds it to the inventory. Every product is linked to the given supplier.

    Expected header: product_type,product_id,name,price,stock_quantity

    try / except / else / finally:
    - except FileNotFoundError: the file is missing, report it, do not crash
    - else: the file opened, so read the rows. Each row has its own
            try / except ValueError, so one bad row is reported and skipped
            and loading carries on with the next row
    - finally: always runs, whether the file opened or not
    """
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row (None if the file is empty)

            for line_number, row in enumerate(reader, start=2):
                if not row:  # skip blank lines
                    continue
                try:
                    if len(row) != 5:
                        raise ValueError(f"expected 5 values, found {len(row)}")

                    product_type, product_id, name, price, stock = row
                    product = ProductFactory.create(
                        product_type, product_id.strip(), name.strip(),
                        float(price), int(stock), supplier,
                    )
                except ValueError as error:
                    print(f"Skipped row {line_number} {row}: {error}")
                    continue

                if inventory.add_product(product):
                    loaded += 1
                else:
                    print(f"Skipped row {line_number}: product ID "
                          f"'{product.get_product_id()}' already exists.")

        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")