import ast
import contextlib
import io
import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from inventory import Inventory
from main import get_positive_float, get_valid_stock
from product_loader import load_products
from supplier import Supplier

PROJECT = pathlib.Path(__file__).resolve().parent.parent

SAMPLE_CSV = """product_type,product_id,name,price,stock_quantity
physical,P001,Desk Lamp,25.00,10
digital,D001,Photo Editor,49.90,100
service,S001,Installation,30.00,5
physical,P002,Office Chair,abc,3
physical,P003,Monitor Stand,39.50,7
"""


def run_and_capture(function, *args) -> tuple[object, str]:
    """Runs a function and returns (its result, everything it printed)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = function(*args)
    return result, buffer.getvalue()


class TestUserInput(unittest.TestCase):

    def test_get_positive_float_asks_again_until_valid(self) -> None:
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]) as fake:
            value, printed = run_and_capture(get_positive_float, "Price: ")
        self.assertEqual(value, 12.5)
        self.assertEqual(fake.call_count, 3)
        self.assertEqual(printed.splitlines(), [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])

    def test_get_valid_stock_asks_again_until_valid(self) -> None:
        with patch("builtins.input", side_effect=["ten", "2.5", "-1", "7"]) as fake:
            value, _ = run_and_capture(get_valid_stock, "Stock: ")
        self.assertEqual(value, 7)
        self.assertEqual(fake.call_count, 4)


class TestLoadProducts(unittest.TestCase):

    def setUp(self) -> None:
        self.supplier = Supplier("S001", "TechSource", "sales@techsource.com")
        self.inventory = Inventory()
        self.folder = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.folder.name, "products.csv")
        with open(self.csv_path, "w", newline="") as f:
            f.write(SAMPLE_CSV)

    def tearDown(self) -> None:
        self.folder.cleanup()

    def test_bad_rows_skipped_and_valid_rows_loaded(self) -> None:
        _, printed = run_and_capture(load_products, self.csv_path,
                                     self.inventory, self.supplier)
        ids = [p.get_product_id() for p in self.inventory.get_products()]
        self.assertEqual(ids, ["P001", "D001", "P003"])
        lines = printed.splitlines()
        self.assertIn("Unknown product type: service", lines[0])
        self.assertIn("could not convert string to float: 'abc'", lines[1])
        self.assertEqual(lines[2:], ["3 products loaded.", "Load attempt finished."])

    def test_missing_file_handled_gracefully(self) -> None:
        missing = os.path.join(self.folder.name, "no_such_file.csv")
        _, printed = run_and_capture(load_products, missing,
                                     self.inventory, self.supplier)
        self.assertEqual(printed.splitlines(), [
            f"Products file not found: {missing}",
            "Load attempt finished.",
        ])
        self.assertEqual(self.inventory.get_products(), [])

    def test_duplicate_id_reported_not_loaded_twice(self) -> None:
        run_and_capture(load_products, self.csv_path, self.inventory, self.supplier)
        _, printed = run_and_capture(load_products, self.csv_path,
                                     self.inventory, self.supplier)
        self.assertEqual(len(self.inventory.get_products()), 3)
        self.assertIn("0 products loaded.", printed)


class TestSpecificExceptions(unittest.TestCase):
    """Every except clause in the project must name a specific exception."""

    def test_no_bare_or_catch_all_except(self) -> None:
        problems = []
        for path in PROJECT.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                names = []
                if node.type is None:
                    names = ["(bare except)"]
                elif isinstance(node.type, ast.Name):
                    names = [node.type.id]
                elif isinstance(node.type, ast.Tuple):
                    names = [e.id for e in node.type.elts if isinstance(e, ast.Name)]
                for name in names:
                    if name in ("(bare except)", "Exception", "BaseException"):
                        problems.append(f"{path.name} line {node.lineno}: {name}")
        self.assertEqual(problems, [], "Too-general except: " + ", ".join(problems))


if __name__ == "__main__":
    unittest.main()