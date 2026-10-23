"""Pruebas para revisar los cálculos y los datos que aceptamos."""

import unittest
from decimal import Decimal

from portfolio import Portfolio, Stock


class StockTests(unittest.TestCase):
    def test_current_price_returns_supplied_price(self):
        stock = Stock("META", Decimal("2"), Decimal("150.25"))

        self.assertEqual(stock.current_price(), Decimal("150.25"))

    def test_rejects_empty_symbols(self):
        for symbol in ("", "   "):
            with self.subTest(symbol=symbol), self.assertRaises(ValueError):
                Stock(symbol, Decimal("1"), Decimal("100"))

    def test_rejects_invalid_quantities(self):
        for quantity in ("-1", "NaN", "sNaN", "Infinity", "-Infinity"):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                Stock("META", Decimal(quantity), Decimal("100"))

    def test_rejects_invalid_prices(self):
        for price in ("0", "-1", "NaN", "sNaN", "Infinity", "-Infinity"):
            with self.subTest(price=price), self.assertRaises(ValueError):
                Stock("META", Decimal("1"), Decimal(price))


class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.stocks = [
            Stock("META", Decimal("8"), Decimal("100")),
            Stock("AAPL", Decimal("1"), Decimal("200")),
        ]
        self.allocations = {"META": Decimal("0.4"), "AAPL": Decimal("0.6")}

    def test_rebalance_returns_buys_and_sells(self):
        portfolio = Portfolio(self.stocks, self.allocations)

        self.assertEqual(
            portfolio.rebalance(), {"META": Decimal("-4"), "AAPL": Decimal("2")}
        )

    def test_balanced_portfolio_returns_no_trades(self):
        stocks = [
            Stock("META", Decimal("4"), Decimal("100")),
            Stock("AAPL", Decimal("3"), Decimal("200")),
        ]

        self.assertEqual(Portfolio(stocks, self.allocations).rebalance(), {})

    def test_buys_new_stock_and_sells_stock_without_allocation(self):
        stocks = self.stocks + [Stock("GOOG", Decimal("0"), Decimal("50"))]
        allocations = {"AAPL": Decimal("0.5"), "GOOG": Decimal("0.5")}

        self.assertEqual(
            Portfolio(stocks, allocations).rebalance(),
            {"META": Decimal("-8"), "AAPL": Decimal("1.5"), "GOOG": Decimal("10")},
        )

    def test_zero_allocation_sells_entire_position(self):
        allocations = {"META": Decimal("0"), "AAPL": Decimal("1")}

        self.assertEqual(
            Portfolio(self.stocks, allocations).rebalance(),
            {"META": Decimal("-8"), "AAPL": Decimal("4")},
        )

    def test_supports_fractional_shares(self):
        stocks = [
            Stock("META", Decimal("1"), Decimal("100")),
            Stock("AAPL", Decimal("1"), Decimal("200")),
        ]
        allocations = {"META": Decimal("0.5"), "AAPL": Decimal("0.5")}

        self.assertEqual(
            Portfolio(stocks, allocations).rebalance(),
            {"META": Decimal("0.5"), "AAPL": Decimal("-0.25")},
        )

    def test_zero_value_portfolio_returns_no_trades(self):
        stocks = [
            Stock("META", Decimal("0"), Decimal("100")),
            Stock("AAPL", Decimal("0"), Decimal("200")),
        ]

        self.assertEqual(Portfolio(stocks, self.allocations).rebalance(), {})

    def test_rebalance_does_not_change_positions_or_allocations(self):
        portfolio = Portfolio(self.stocks, self.allocations)
        original_stocks = portfolio.stocks
        original_allocations = portfolio.allocations.copy()

        first_trades = portfolio.rebalance()

        self.assertEqual(portfolio.stocks, original_stocks)
        self.assertEqual(portfolio.allocations, original_allocations)
        self.assertEqual(portfolio.rebalance(), first_trades)

    def test_trades_preserve_value_and_reach_target_allocation(self):
        stocks = [
            Stock("META", Decimal("1"), Decimal("3")),
            Stock("AAPL", Decimal("1"), Decimal("7")),
        ]
        allocations = {"META": Decimal("0.5"), "AAPL": Decimal("0.5")}
        trades = Portfolio(stocks, allocations).rebalance()

        self.assertEqual(trades["META"], Decimal("0.6666666666666666666666666667"))
        self.assertEqual(trades["AAPL"], Decimal("-0.2857142857142857142857142857"))

        # Algunas divisiones no terminan, así que dejamos un pequeño margen.
        tolerance = Decimal("1e-24")
        final_values = {
            stock.symbol: (stock.quantity + trades[stock.symbol]) * stock.price
            for stock in stocks
        }
        self.assertLessEqual(abs(sum(final_values.values()) - Decimal("10")), tolerance)
        for symbol, value in final_values.items():
            with self.subTest(symbol=symbol):
                self.assertLessEqual(abs(value - Decimal("5")), tolerance)

    def test_rejects_duplicate_symbols(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            Portfolio(self.stocks + [self.stocks[0]], self.allocations)

    def test_rejects_allocations_without_a_stock_price(self):
        with self.assertRaisesRegex(ValueError, "GOOG"):
            Portfolio(self.stocks, {"GOOG": Decimal("1")})

    def test_rejects_invalid_weights(self):
        for weight in ("-0.1", "1.1", "NaN", "sNaN", "Infinity", "-Infinity"):
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                Portfolio(self.stocks, {"META": Decimal(weight)})

    def test_rejects_allocations_that_do_not_sum_to_one(self):
        for allocations in (
            {},
            {"META": Decimal("0.4"), "AAPL": Decimal("0.5")},
            {"META": Decimal("0.6"), "AAPL": Decimal("0.6")},
        ):
            with self.subTest(allocations=allocations):
                with self.assertRaisesRegex(ValueError, "sum to 1"):
                    Portfolio(self.stocks, allocations)


if __name__ == "__main__":
    unittest.main()
