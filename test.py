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
# Pruebas Base de Lógica de Negocio (5 pruebas)
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
        """Test 4: Un código que NO inicia con 'ORD-' debe ser inválido."""
        codigo = "XYZ-2026-8921"
        self.assertFalse(validar_codigo_pedido(codigo))

    def test_5_version_correcta(self):
        """Test 5: La constante VERSION debe ser exactamente 'v1.1.0'."""
        self.assertEqual(VERSION, "v1.1.0")


# ---------------------------------------------------------------------------
# Pruebas de Regresión y Robustez HTTP (3 pruebas)
# ---------------------------------------------------------------------------

class TestRegresionTiposStrInt(unittest.TestCase):

    def setUp(self):
        """Aísla cada test respaldando el estado en memoria de BASE_DATOS."""
        self._backup = copy.deepcopy(app.BASE_DATOS)

    def tearDown(self):
        app.BASE_DATOS.clear()
        app.BASE_DATOS.update(self._backup)

    def test_6_registrar_venta_castea_strings_numericos(self):
        """Test 6: Convierte strings numéricos del formulario HTML a los tipos de datos correctos."""
        pedido = registrar_venta(
            codigo="ORD-2026-9000",
            cliente="Luis Rojas",
            producto="Teclado Mecánico",
            cantidad="3",
            precio_unitario="120.50",
            descuento="5",
        )
        self.assertIsInstance(pedido["cantidad"], int)
        self.assertIsInstance(pedido["precio_unitario"], float)
        self.assertEqual(pedido["cantidad"], 3)
        self.assertAlmostEqual(pedido["monto_final"], 343.425, places=3)

    def test_7_registrar_venta_valores_invalidos_lanza_valueerror(self):
        """Test 7: Retorna ValueError controlado si los datos o códigos no son válidos."""
        with self.assertRaises(ValueError):
            registrar_venta(
                codigo="ORD-2026-9001",
                cliente="Test",
                producto="Test",
                cantidad="abc",
                precio_unitario="10",
            )

    def test_8_actualizar_pedido_castea_strings_numericos(self):
        """Test 8: Permite actualizar las cantidades usando strings enviados desde la API/PUT."""
        pedido_actualizado = actualizar_pedido(pedido_id=1, cantidad="5")
        self.assertIsNotNone(pedido_actualizado)
        self.assertIsInstance(pedido_actualizado["cantidad"], int)
        self.assertEqual(pedido_actualizado["cantidad"], 5)

    def test_9_actualizar_estado_pedido(self):
            """Test 9: Permite actualizar el estado del pedido a 'Entregado' o 'Cancel ado' vía API/PUT."""
            pedido_actualizado = actualizar_pedido(pedido_id=1, estado="Entregado")
            self.assertIsNotNone(pedido_actualizado)
            self.assertEqual(pedido_actualizado["estado"], "Entregado")

    def test_10_codigo_pedido(self):
            """Test 10: Prueba deliberadamente fallida con un código de pedido inválido."""
            codigo = "ORD-2026-9999"
            self.assertTrue(validar_codigo_pedido(codigo))

if __name__ == "__main__":
    unittest.main()