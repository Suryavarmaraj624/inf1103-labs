from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """
    Strategy pattern: the shared interface for every discount.
    Responsibility: turn an order total into a discounted total.

    Order only ever calls apply(). It never checks which strategy it has,
    so a new discount is a new class, and Order does not change (OCP).
    """

    @abstractmethod
    def apply(self, total: float) -> float:
        """
        Input:  total (float), the order total before discount
        Output: the total after this discount
        """
        pass

    def describe(self) -> str:
        """Output: a short label for printing. Subclasses may override it."""
        return type(self).__name__


class NoDiscount(DiscountStrategy):
    """Returns the total unchanged. Used when an order has no discount."""

    def apply(self, total: float) -> float:
        return total

    def describe(self) -> str:
        return "No discount"


class PercentageDiscount(DiscountStrategy):
    """Takes a percentage off, e.g. PercentageDiscount(10) takes 10% off."""

    def __init__(self, percent: float) -> None:
        if percent < 0 or percent > 100:
            raise ValueError("Percentage must be between 0 and 100.")
        self.__percent: float = percent

    def apply(self, total: float) -> float:
        return total * (1 - self.__percent / 100)

    def describe(self) -> str:
        return f"{self.__percent:g}% off"


class BulkDiscount(DiscountStrategy):
    """
    Takes a fixed amount off any total at or above a threshold,
    e.g. BulkDiscount(200, 20) takes 20 off any total of 200 or more.
    """

    def __init__(self, threshold: float, amount: float) -> None:
        if threshold < 0 or amount < 0:
            raise ValueError("Threshold and amount cannot be negative.")
        self.__threshold: float = threshold
        self.__amount: float = amount

    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return max(total - self.__amount, 0.0)
        return total

    def describe(self) -> str:
        return f"${self.__amount:.2f} off orders of ${self.__threshold:.2f} or more"

class StudentDiscount(DiscountStrategy):
    RATE: float = 0.05

    def apply(self, total: float) -> float:
        return total * (1 - StudentDiscount.RATE)

    def describe(self) -> str:
        return "Student discount (5% off)"