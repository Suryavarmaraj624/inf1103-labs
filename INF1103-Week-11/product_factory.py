from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


class ProductFactory:
    """
    Factory pattern: the ONE place that decides which Product subclass to build.
    The rest of the program asks the factory for a Product and never imports
    PhysicalProduct or DigitalProduct itself.

    The factory creates products but does not store them (UML: a dashed
    «creates» dependency to Product, not an association).

    Trade-off: adding a new product type still means editing create() here,
    so the factory itself is not closed for modification (OCP). That is
    accepted because it is now one place instead of several.
    """

    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier,
               weight: float = 0.0, download_size: float = 0.0) -> Product:
        """
        Input:  product_type ("physical" or "digital", any case), the common
                product values, plus the extra value the chosen type needs:
                weight (kg) for physical, download_size (MB) for digital.
                The extras default to 0.0, e.g. when a CSV file has no column.
        Output: a Product (really a PhysicalProduct or DigitalProduct)
        Raises: ValueError for an unknown type, or (from Product) an invalid
                price or stock quantity
        """
        kind = product_type.strip().lower()

        if kind == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity,
                                   supplier, weight)
        elif kind == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity,
                                  supplier, download_size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")