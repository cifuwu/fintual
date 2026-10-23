"""Una forma de probar el rebalanceo ingresando los datos por consola."""

from decimal import Decimal, InvalidOperation

from portfolio import Portfolio, Stock


def read_decimal(
    prompt: str, *, positive: bool = False, maximum: Decimal | None = None
) -> Decimal:
    """Pide un número y vuelve a preguntar si hay algo que corregir."""
    while True:
        try:
            value = Decimal(input(prompt).strip().replace(",", "."))
        except InvalidOperation:
            print("Ingresa un número válido, por ejemplo 10.5.")
            continue

        if not value.is_finite():
            print("Ingresa un número finito.")
        elif value < 0 or (positive and value == 0):
            limit = "mayor que cero" if positive else "mayor o igual a cero"
            print(f"Ingresa un número {limit}.")
        elif maximum is not None and value > maximum:
            print(f"Ingresa un número menor o igual a {maximum}.")
        else:
            return value


def read_stocks() -> list[Stock]:
    """Pide las acciones. Usa cantidad cero para una que quieras empezar a comprar."""
    stocks = []
    symbols = set()
    print("\nIngresa las acciones. Usa cantidad 0 si todavía no tienes una acción.")

    while True:
        symbol = input("\nSímbolo de la acción (Enter para terminar): ").strip().upper()
        if not symbol:
            if stocks:
                return stocks
            print("Ingresa al menos una acción.")
            continue
        if symbol in symbols:
            print("Ese símbolo ya fue ingresado. Usa una sola posición por acción.")
            continue

        quantity = read_decimal("Cantidad actual de acciones: ")
        price = read_decimal("Último precio por acción: ", positive=True)
        stocks.append(Stock(symbol, quantity, price))
        symbols.add(symbol)


def read_allocations(stocks: list[Stock]) -> dict[str, Decimal]:
    """Pide los porcentajes y los pasa a proporciones: por ejemplo, de 40% a 0.4."""
    while True:
        print("\nIngresa los porcentajes objetivo. Deben sumar 100.")
        print("Usa 0 para vender completamente una posición.")
        allocations = {}
        for stock in stocks:
            percentage = read_decimal(
                f"Porcentaje objetivo de {stock.symbol}: ", maximum=Decimal("100")
            )
            allocations[stock.symbol] = percentage / Decimal("100")

        total = sum(allocations.values(), Decimal("0"))
        if total == Decimal("1"):
            return allocations
        print(f"Los porcentajes suman {total * 100:f}%. Deben sumar 100%.")
        print("Vuelve a ingresar la distribución objetivo.")


def show_results(portfolio: Portfolio) -> None:
    """Muestra lo que tenemos y qué habría que comprar o vender."""
    total_value = sum(
        (stock.quantity * stock.current_price() for stock in portfolio.stocks),
        Decimal("0"),
    )
    print(f"\nValor total del portafolio: {total_value:.2f}")
    print("\nPosiciones actuales:")
    for stock in portfolio.stocks:
        percentage = portfolio.allocations.get(stock.symbol, Decimal("0")) * 100
        print(
            f"{stock.symbol}: {stock.quantity:f} acciones, "
            f"precio {stock.current_price():f}, objetivo {percentage:f}%."
        )

    trades = portfolio.rebalance()
    if not trades:
        if total_value == 0:
            print("\nEl portafolio tiene valor cero. No hay operaciones que realizar.")
        else:
            print("\nEl portafolio ya está balanceado. No se requieren operaciones.")
        return

    print("\nOperaciones sugeridas:")
    for stock in portfolio.stocks:
        quantity = trades.get(stock.symbol, Decimal("0"))
        if quantity != 0:
            action = "Comprar" if quantity > 0 else "Vender"
            amount = abs(quantity) * stock.current_price()
            print(
                f"{action} {abs(quantity):f} acciones de {stock.symbol} "
                f"por un monto de {amount:.2f}."
            )
    print("Las operaciones son una simulación; las posiciones no se modifican.")


def main() -> None:
    print("Prueba de rebalanceo de portafolio")
    print("Puedes usar punto o coma decimal, sin separadores de miles.")

    while True:
        stocks = read_stocks()
        allocations = read_allocations(stocks)
        show_results(Portfolio(stocks, allocations))

        answer = input("\nEscribe s para probar otro portafolio o Enter para salir: ")
        if answer.strip().lower() not in ("s", "si", "sí"):
            break


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrueba finalizada.")
