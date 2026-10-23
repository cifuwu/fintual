"""Qué comprar y vender para llegar a la distribución que buscamos."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Stock:
    """Una acción: cuántas tenemos y cuál es el último precio que recibimos."""

    symbol: str
    quantity: Decimal
    price: Decimal

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("Stock symbol must not be empty")
        if not self.quantity.is_finite() or self.quantity < 0:
            raise ValueError("Stock quantity must be finite and non-negative")
        if not self.price.is_finite() or self.price <= 0:
            raise ValueError("Stock price must be finite and positive")

    def current_price(self) -> Decimal:
        """Devuelve el precio que recibimos al crear esta posición."""
        return self.price


class Portfolio:
    """Las acciones que tenemos y cómo queremos repartir el valor entre ellas."""

    def __init__(
        self, stocks: list[Stock], allocations: dict[str, Decimal]
    ) -> None:
        self.stocks = tuple(stocks)
        self.allocations = dict(allocations)

        symbols = {stock.symbol for stock in self.stocks}
        if len(symbols) != len(self.stocks):
            raise ValueError("Stock symbols must be unique")

        unknown_symbols = self.allocations.keys() - symbols
        if unknown_symbols:
            raise ValueError(
                "Missing stock prices for: " + ", ".join(sorted(unknown_symbols))
            )

        for weight in self.allocations.values():
            if not weight.is_finite() or not 0 <= weight <= 1:
                raise ValueError(
                    "Allocation weights must be finite and between 0 and 1"
                )

        if sum(self.allocations.values(), Decimal("0")) != Decimal("1"):
            raise ValueError("Allocation weights must sum to 1")

    def rebalance(self) -> dict[str, Decimal]:
        """Calcula cuánto comprar (+) o vender (-) de cada acción.

        Comparamos cuánto queremos tener invertido con cuánto tenemos ahora.
        Dividimos esa diferencia por el precio para pasar de dinero a acciones.
        """
        current_values = {
            stock.symbol: stock.quantity * stock.current_price()
            for stock in self.stocks
        }
        total_value = sum(current_values.values(), Decimal("0"))
        trades = {}

        for stock in self.stocks:
            weight = self.allocations.get(stock.symbol, Decimal("0"))
            target_value = total_value * weight
            value_difference = target_value - current_values[stock.symbol]
            quantity_to_trade = value_difference / stock.current_price()

            if quantity_to_trade != 0:
                trades[stock.symbol] = quantity_to_trade

        return trades
