import unittest

from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from supplier import Supplier


class TestProductValidation(unittest.TestCase):

    def setUp(self) -> None:
        self.supplier = Supplier("S001", "TechSource", "sales@techsource.com")

    def test_price_of_zero_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            PhysicalProduct("P001", "Lamp", 0.0, 10, self.supplier, 1.0)
        self.assertEqual(str(caught.exception), "Price must be greater than zero.")

    def test_negative_price_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PhysicalProduct("P001", "Lamp", -5.0, 10, self.supplier, 1.0)

    def test_negative_stock_rejected_on_creation(self) -> None:
        with self.assertRaises(ValueError) as caught:
            PhysicalProduct("P001", "Lamp", 25.0, -1, self.supplier, 1.0)
        self.assertEqual(str(caught.exception), "Stock quantity cannot be negative.")

    def test_zero_stock_allowed(self) -> None:
        product = PhysicalProduct("P001", "Lamp", 25.0, 0, self.supplier, 1.0)
        self.assertEqual(product.get_stock(), 0)

    def test_negative_stock_rejected_on_update_and_stock_unchanged(self) -> None:
        product = PhysicalProduct("P001", "Lamp", 25.0, 10, self.supplier, 1.0)
        with self.assertRaises(ValueError):
            product.update_stock(-3)
        self.assertEqual(product.get_stock(), 10)

    def test_digital_product_follows_the_same_rules(self) -> None:
        # LSP: a subclass may not skip or weaken the rules its parent sets
        with self.assertRaises(ValueError):
            DigitalProduct("D001", "Editor", 0.0, 10, self.supplier, 450.0)
        with self.assertRaises(ValueError):
            DigitalProduct("D001", "Editor", 49.9, -1, self.supplier, 450.0)

    def test_inventory_update_stock_passes_the_error_up(self) -> None:
        inventory = Inventory()
        inventory.add_product(PhysicalProduct("P001", "Lamp", 25.0, 10, self.supplier, 1.0))
        with self.assertRaises(ValueError):
            inventory.update_stock("P001", -1)
        self.assertFalse(inventory.update_stock("NOPE", 5))
        self.assertTrue(inventory.update_stock("P001", 5))


class TestOrderLineValidation(unittest.TestCase):

    def setUp(self) -> None:
        supplier = Supplier("S001", "TechSource", "sales@techsource.com")
        self.lamp = PhysicalProduct("P001", "Lamp", 25.0, 10, supplier, 1.0)

    def test_zero_quantity_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            OrderLine(self.lamp, 0)
        self.assertEqual(str(caught.exception), "Quantity must be greater than zero.")

    def test_negative_quantity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            OrderLine(self.lamp, -2)

    def test_order_does_not_keep_a_rejected_line(self) -> None:
        order = Order("O001")
        with self.assertRaises(ValueError):
            order.add_order_line(self.lamp, 0)
        self.assertEqual(order.get_order_lines(), [])

    def test_valid_quantity_accepted(self) -> None:
        order = Order("O001")
        order.add_order_line(self.lamp, 2)
        self.assertAlmostEqual(order.calculate_total(), 50.0)


if __name__ == "__main__":
    unittest.main()