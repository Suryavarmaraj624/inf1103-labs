import ast
import pathlib
import unittest

from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from supplier import Supplier

PROJECT = pathlib.Path(__file__).resolve().parent.parent


class TestProductFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.supplier = Supplier("S001", "TechSource", "sales@techsource.com")

    def test_creates_physical_product(self) -> None:
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10,
                                        self.supplier, weight=1.2)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertIsInstance(product, Product)
        assert isinstance(product, PhysicalProduct)  # tells mypy the real type
        self.assertAlmostEqual(product.get_weight(), 1.2)

    def test_creates_digital_product(self) -> None:
        product = ProductFactory.create("digital", "D001", "Photo Editor", 49.9, 100,
                                        self.supplier, download_size=450.0)
        self.assertIsInstance(product, DigitalProduct)
        assert isinstance(product, DigitalProduct)
        self.assertAlmostEqual(product.get_download_size(), 450.0)

    def test_type_is_not_case_sensitive(self) -> None:
        product = ProductFactory.create(" Physical ", "P001", "Lamp", 25.0, 10,
                                        self.supplier)
        self.assertIsInstance(product, PhysicalProduct)

    def test_unknown_type_raises_clear_value_error(self) -> None:
        with self.assertRaises(ValueError) as caught:
            ProductFactory.create("service", "S001", "Installation", 30.0, 5,
                                  self.supplier)
        self.assertEqual(str(caught.exception), "Unknown product type: service")

    def test_factory_still_applies_product_validation(self) -> None:
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P001", "Lamp", 0.0, 10, self.supplier)


class TestProductsCreatedThroughFactory(unittest.TestCase):
    """Only product_factory.py may call PhysicalProduct(...) / DigitalProduct(...)."""

    def test_no_direct_creation_outside_the_factory(self) -> None:
        allowed = {"product_factory.py", "test_relationships.py",
                   "predict_first_checks.py"}
        offenders = []
        for path in PROJECT.glob("*.py"):
            if path.name in allowed:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id in ("PhysicalProduct", "DigitalProduct")):
                    offenders.append(f"{path.name} line {node.lineno}")
        self.assertEqual(offenders, [], "Direct creation found: " + ", ".join(offenders))


if __name__ == "__main__":
    unittest.main()