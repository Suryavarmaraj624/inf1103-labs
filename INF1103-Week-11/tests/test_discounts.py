import inspect
import io
import tokenize
import unittest

import order as order_module
from discount_strategy import (BulkDiscount, DiscountStrategy, NoDiscount,
                               PercentageDiscount, StudentDiscount)
from order import Order
from physical_product import PhysicalProduct
from supplier import Supplier


def make_order_worth_250(discount: DiscountStrategy | None = None) -> Order:
    """An order whose lines add up to exactly 250.00."""
    supplier = Supplier("S001", "TechSource", "sales@techsource.com")
    chair = PhysicalProduct("P001", "Chair", 100.00, 10, supplier, 7.5)
    lamp = PhysicalProduct("P002", "Lamp", 50.00, 10, supplier, 1.0)
    order = Order("O001", discount)
    order.add_order_line(chair, 2)  # 200.00
    order.add_order_line(lamp, 1)   #  50.00
    return order


class TestStrategies(unittest.TestCase):

    def test_discount_strategy_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            DiscountStrategy()  # type: ignore[abstract]

    def test_no_discount_returns_total_unchanged(self) -> None:
        self.assertAlmostEqual(NoDiscount().apply(250.0), 250.0)

    def test_percentage_discount(self) -> None:
        self.assertAlmostEqual(PercentageDiscount(10).apply(250.0), 225.0)

    def test_bulk_discount_at_and_above_threshold(self) -> None:
        bulk = BulkDiscount(200, 20)
        self.assertAlmostEqual(bulk.apply(200.0), 180.0)
        self.assertAlmostEqual(bulk.apply(250.0), 230.0)

    def test_bulk_discount_below_threshold(self) -> None:
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(199.99), 199.99)

    def test_student_discount(self) -> None:
        self.assertAlmostEqual(StudentDiscount().apply(250.0), 237.5)

    def test_invalid_percentage_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PercentageDiscount(150)


class TestOrderUsesStrategy(unittest.TestCase):

    def test_default_strategy_is_no_discount(self) -> None:
        order = make_order_worth_250()
        self.assertIsInstance(order.get_discount(), NoDiscount)
        self.assertAlmostEqual(order.calculate_total(), 250.0)

    def test_each_order_gets_its_own_default(self) -> None:
        self.assertIsNot(Order("A").get_discount(), Order("B").get_discount())

    def test_total_goes_through_the_strategy(self) -> None:
        order = make_order_worth_250(BulkDiscount(200, 20))
        self.assertAlmostEqual(order.calculate_subtotal(), 250.0)
        self.assertAlmostEqual(order.calculate_total(), 230.0)

    def test_set_discount_changes_strategy_on_existing_order(self) -> None:
        order = make_order_worth_250(BulkDiscount(200, 20))
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225.0)

    def test_two_orders_can_share_one_strategy(self) -> None:
        shared = PercentageDiscount(10)
        first = make_order_worth_250(shared)
        second = make_order_worth_250(shared)
        self.assertIs(first.get_discount(), second.get_discount())
        self.assertAlmostEqual(first.calculate_total(), second.calculate_total())

    def test_new_strategy_works_without_changing_order(self) -> None:
        # A brand-new strategy defined only inside this test. Order has never
        # heard of it, yet works with it: open for extension, closed for change.
        class HalfPrice(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total / 2

        order = make_order_worth_250(HalfPrice())
        self.assertAlmostEqual(order.calculate_total(), 125.0)

    def test_order_has_no_discount_if_elif_logic(self) -> None:
        # Look at the code words only (tokenize skips comments and docstrings
        # are STRING tokens), so the word "elif" in a docstring does not count
        source = inspect.getsource(order_module)
        words = {tok.string for tok in tokenize.generate_tokens(io.StringIO(source).readline)
                 if tok.type == tokenize.NAME}
        self.assertNotIn("elif", words)
        for name in ("PercentageDiscount", "BulkDiscount", "StudentDiscount",
                     "discount_type", "isinstance"):
            self.assertNotIn(name, words, f"Order mentions {name}")
        self.assertIn("self.__discount.apply(", inspect.getsource(Order.calculate_total))


if __name__ == "__main__":
    unittest.main()