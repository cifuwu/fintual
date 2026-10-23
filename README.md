# Rebalanceo de portafolio

Este proyecto resuelve el ejercicio de Fintual: con las acciones que tenemos y
cómo queremos repartir la inversión, calcula cuánto comprar o vender de cada
una. Todo está hecho con la biblioteca estándar de Python.

## Prueba interactiva

Para probarlo, abre una terminal en la carpeta del proyecto y ejecuta:

```sh
python3 prueba.py
```

El programa va pidiendo el símbolo, cuántas acciones tienes y el último precio
de cada una. Cuando termines la lista, presiona Enter en el símbolo. Después 
pide qué porcentaje quieres tener en cada acción, por ejemplo 40 y 60. Tienen
que sumar 100; si la suma no da, te deja ingresarlos de nuevo.

Puedes usar punto o coma decimal, sin separadores de miles. Si quieres comprar
una acción que todavía no tienes, agrégala con cantidad cero. Si quieres vender
todas las acciones de un símbolo, ponle un porcentaje objetivo de cero.

Al final ves lo que tienes, el valor total y qué habría que comprar o vender.
Si te equivocas en algún dato, te lo vuelve a pedir. También puedes probar otro
caso al terminar o salir con Ctrl+C.

Por ejemplo, ingresa META con cantidad 8 y precio 100, AAPL con cantidad 1 y
precio 200, termina la lista e ingresa los porcentajes 40 y 60. El resultado
será vender 4 acciones de META y comprar 2 de AAPL.

## Un ejemplo desde código

También puedes usar las clases directamente. Prueba este ejemplo desde la misma
carpeta:

```sh
python3 - <<'PY'
from decimal import Decimal
from portfolio import Portfolio, Stock

stocks = [
    Stock("META", quantity=Decimal("8"), price=Decimal("100")),
    Stock("AAPL", quantity=Decimal("1"), price=Decimal("200")),
]
allocations = {"META": Decimal("0.4"), "AAPL": Decimal("0.6")}
portfolio = Portfolio(stocks, allocations)

for symbol, quantity in portfolio.rebalance().items():
    action = "BUY" if quantity > 0 else "SELL"
    print(f"{action} {abs(quantity)} {symbol}")
PY
```

Resultado:

```text
SELL 4.0 META
BUY 2.0 AAPL
```

En este ejemplo tenemos 1.000 invertidos: 800 en META y 200 en AAPL. Para llegar
al 40% en META y 60% en AAPL, hay que vender 400 de META y comprar 400 de AAPL.
Así quedaríamos con 4 acciones de META y 3 de AAPL.

## Cómo funciona

En `Stock` guardamos el símbolo, cuántas acciones tenemos y su último precio.
`current_price()` devuelve ese mismo precio, que ya viene dado al crear el objeto.

En `Portfolio` juntamos esas acciones con la distribución que queremos alcanzar.
Primero sumamos cuánto vale todo. Después, para cada acción, hacemos esta cuenta:

```text
valor objetivo = valor total × proporción objetivo
cantidad a comprar o vender = (valor objetivo − valor actual) / precio actual
```

`rebalance()` devuelve un diccionario con cuánto comprar o vender de cada símbolo.
Un número positivo significa comprar y uno negativo, vender. Si no hay que hacer
nada con una acción, no aparece en el resultado. El método solo hace las cuentas:
no cambia las cantidades que tenemos ni manda órdenes de compra o venta.

Si una acción no aparece en la distribución objetivo, la propuesta será venderla
completa. Para sumar una nueva, basta con agregar un `Stock` con cantidad cero y
su precio. Si ponemos un símbolo en la distribución pero falta su `Stock`, el
programa devuelve un `ValueError`: necesita ese precio para hacer las cuentas.

El cálculo hace dos pasadas por las acciones, así que usa tiempo O(n) y memoria
O(n).

## Algunas decisiones

- Podemos comprar o vender fracciones de acciones. Todos los precios están en
  la misma moneda.
- Usamos `Decimal` desde strings, como `Decimal("0.4")`, para no arrastrar las
  aproximaciones de los `float`.
- Las cantidades pueden ser cero, pero no negativas. Los precios tienen que ser
  mayores que cero. Ambos deben ser números finitos.
- Los símbolos no pueden estar vacíos ni repetidos. Las clases los comparan tal
  como llegan; la prueba de consola los pasa a mayúsculas.
- En el código, las proporciones van de cero a uno y tienen que sumar uno, como
  0.4 y 0.6. No aceptamos una distribución vacía, `NaN` ni infinitos.
- Si todas las cantidades están en cero, no hay nada que comprar o vender.
- Dejamos fuera el efectivo, las comisiones, los impuestos, las ventas en corto
  y los cambios de precio durante el cálculo.

No redondeamos las cantidades a centavos ni a un número fijo de acciones. Usamos
la precisión de `Decimal` de Python, que por defecto es de 28 dígitos. Algunas
divisiones no terminan y pueden dejar diferencias muy pequeñas. Para este
ejercicio calculamos las cantidades teóricas, sin ajustarlas a las reglas de un
bróker.

## Pruebas

```sh
python3 -m unittest -v
```

Las pruebas revisan compras y ventas, casos que ya están balanceados, acciones
nuevas y otras que hay que vender por completo. También cubren fracciones, valor
cero y datos inválidos, y comprueban que el valor total se mantenga dentro de la
precisión decimal y que el cálculo no cambie las posiciones originales.

## Uso de LLMs

Esta solución se hizo con ayuda de Codex. Fintual pide compartir las
conversaciones con LLMs, así que al entregar el repositorio también hay que
adjuntar el enlace o una exportación de esta conversación.
