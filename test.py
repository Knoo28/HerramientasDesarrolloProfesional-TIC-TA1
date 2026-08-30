import copy
import unittest

import app
from app import (
    calcular_total,
    aplicar_descuento,
    validar_codigo_pedido,
    registrar_venta,
    actualizar_pedido,
    VERSION,
)


# ---------------------------------------------------------------------------
# Pruebas base de lógica de negocio
# ---------------------------------------------------------------------------

class TestLogicaNegocioNovaTech(unittest.TestCase):

    def test_1_calcular_total_correcto(self):
        """Test 1: El total debe ser igual a cantidad * precio_unitario."""
        resultado = calcular_total(2, 1500.00)
        self.assertEqual(resultado, 3000.00)

    def test_2_aplicar_descuento_correcto(self):
        """Test 2: El descuento debe restarse correctamente del total."""
        total = 3000.00
        resultado = aplicar_descuento(total, 10)  # 10% de descuento
        self.assertEqual(resultado, 2700.00)

    def test_3_validar_codigo_pedido_valido(self):
        """Test 3: Un código que inicia con 'ORD-' debe ser válido."""
        codigo = "ORD-2026-8921"
        self.assertTrue(validar_codigo_pedido(codigo))

    def test_4_validar_codigo_pedido_invalido(self):
        """Test 4: Un código que NO inicia con 'ORD-' debe ser inválido (False)."""
        codigo = "XYZ-2026-8921"
        self.assertFalse(validar_codigo_pedido(codigo))

    def test_5_version_correcta(self):
        """Test 5: La constante VERSION debe ser exactamente 'v1.1.0'."""
        self.assertEqual(VERSION, "v1.1.0")


class TestRegresionTiposStrInt(unittest.TestCase):

    def setUp(self):
        """
        Aísla cada test: BASE_DATOS es estado global en memoria, y
        registrar_venta/actualizar_pedido lo mutan. Sin este aislamiento,
        el orden de ejecución de los tests podría afectar sus resultados
        (ej. ids autoincrementales, o clientes duplicados).
        """
        self._backup = copy.deepcopy(app.BASE_DATOS)

    def tearDown(self):
        app.BASE_DATOS.clear()
        app.BASE_DATOS.update(self._backup)

    def test_calcular_total_rechaza_strings_con_typeerror_explicito(self):
        """
        calcular_total debe fallar con un TypeError claro y controlado
        si recibe strings, en vez de fallar de forma críptica en la
        comparación `cantidad < 0`.
        """
        with self.assertRaises(TypeError):
            calcular_total("3", "120.50")

    def test_aplicar_descuento_rechaza_strings_con_typeerror_explicito(self):
        with self.assertRaises(TypeError):
            aplicar_descuento("3000", "10")

    def test_registrar_venta_castea_strings_numericos_correctamente(self):
        """
        Caso de regresión principal: registrar_venta debe aceptar
        cantidad/precio_unitario/descuento como strings (tal como llegan
        desde un formulario HTML o un JSON sin tipado) y convertirlos
        internamente, en vez de propagar un TypeError al handler HTTP.
        """
        pedido = registrar_venta(
            codigo="ORD-2026-9000",
            cliente="Luis Rojas",
            producto="Teclado Mecánico",
            cantidad="3",              # string, como llega del formulario
            precio_unitario="120.50",  # string
            descuento="5",             # string
        )

        self.assertIsInstance(pedido["cantidad"], int)
        self.assertIsInstance(pedido["precio_unitario"], float)
        self.assertIsInstance(pedido["descuento"], float)
        self.assertEqual(pedido["cantidad"], 3)
        self.assertEqual(pedido["precio_unitario"], 120.50)
        # 3 * 120.50 = 361.50; con 5% de descuento -> 343.425
        self.assertAlmostEqual(pedido["monto_final"], 343.425, places=3)

    def test_registrar_venta_con_valores_no_numericos_lanza_valueerror_controlado(self):
        """
        Si el valor ni siquiera es convertible a número (ej. "abc"),
        debe lanzar ValueError (manejable como HTTP 400), no un
        TypeError sin controlar que tumbe el servidor.
        """
        with self.assertRaises(ValueError):
            registrar_venta(
                codigo="ORD-2026-9001",
                cliente="Test",
                producto="Test",
                cantidad="abc",
                precio_unitario="10",
            )

    def test_registrar_venta_con_codigo_invalido_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            registrar_venta(
                codigo="XYZ-1",
                cliente="Test",
                producto="Test",
                cantidad="1",
                precio_unitario="10",
            )

    def test_registrar_venta_descuento_vacio_por_defecto_cero(self):
        """
        El frontend puede enviar descuento como "" (campo vacío). Debe
        tratarse como 0, no como error de casteo.
        """
        pedido = registrar_venta(
            codigo="ORD-2026-9002",
            cliente="Test",
            producto="Test",
            cantidad="1",
            precio_unitario="100",
            descuento="",
        )
        self.assertEqual(pedido["descuento"], 0.0)
        self.assertEqual(pedido["monto_final"], 100.0)

    def test_actualizar_pedido_castea_strings_numericos(self):
        """
        actualizar_pedido (usado por el endpoint PUT, ej. al modificar
        la cantidad desde el dashboard) también debe aceptar strings.
        """
        pedido_actualizado = actualizar_pedido(pedido_id=1, cantidad="5")

        self.assertIsNotNone(pedido_actualizado)
        self.assertIsInstance(pedido_actualizado["cantidad"], int)
        self.assertEqual(pedido_actualizado["cantidad"], 5)

    def test_actualizar_pedido_con_valor_no_numerico_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            actualizar_pedido(pedido_id=1, cantidad="no-es-un-numero")


if __name__ == "__main__":
    unittest.main()