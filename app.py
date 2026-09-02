
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

VERSION = "v1.1.0"

# Base de datos en memoria
BASE_DATOS = {
    "clientes": ["Ana Torres", "Carlos Mendoza"],
    "pedidos": [
        {
            "id": 1,
            "codigo": "ORD-2026-8921",
            "cliente": "Ana Torres",
            "producto": "Laptop Gamer Nova Pro",
            "cantidad": 2,
            "precio_unitario": 1500.00,
            "descuento": 10,
            "monto_final": 2700.00,
            "estado": "Confirmado"
        },
        {
            "id": 2,
            "codigo": "ORD-2026-8922",
            "cliente": "Carlos Mendoza",
            "producto": "Monitor 27 UltraSlim",
            "cantidad": 1,
            "precio_unitario": 850.00,
            "descuento": 0,
            "monto_final": 850.00,
            "estado": "Confirmado"
        }
    ]
}

# ---------------------------------------------------------------------------
# Lógica de Negocio
# ---------------------------------------------------------------------------

def calcular_total(cantidad, precio_unitario):
    """
    Calcula el total. Valida que ambos parámetros sean numéricos ANTES
    de compararlos, para no depender de que el llamador ya los haya
    convertido correctamente (defensa en profundidad).
    """
    if isinstance(cantidad, str) or isinstance(precio_unitario, str):
        raise TypeError(
            "calcular_total espera valores numéricos (int/float), no str. "
            "Convierta los datos antes de invocar esta función."
        )
    if cantidad < 0 or precio_unitario < 0:
        raise ValueError("Cantidad y precio unitario deben ser valores no negativos.")
    return cantidad * precio_unitario

def aplicar_descuento(total, porcentaje):
    if isinstance(total, str) or isinstance(porcentaje, str):
        raise TypeError("aplicar_descuento espera valores numéricos (int/float), no str.")
    if not (0 <= porcentaje <= 100):
        raise ValueError("El porcentaje de descuento debe estar entre 0 y 100.")
    return total - (total * porcentaje / 100)

def validar_codigo_pedido(codigo):
    return isinstance(codigo, str) and codigo.startswith("ORD-")

def registrar_cliente(nombre):
    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        raise ValueError("El nombre del cliente no puede estar vacío.")
    if nombre_limpio not in BASE_DATOS["clientes"]:
        BASE_DATOS["clientes"].append(nombre_limpio)
    return len(BASE_DATOS["clientes"])

def registrar_venta(codigo, cliente, producto, cantidad, precio_unitario, descuento=0):
    """
    Registra una nueva venta. Todos los valores numéricos que lleguen
    como texto (por ejemplo desde un formulario HTML o un JSON del
    frontend) se castean explícitamente aquí, ANTES de tocar la lógica
    de negocio. Este es el punto único de "saneamiento" de datos.
    """
    if not validar_codigo_pedido(codigo):
        raise ValueError("Código inválido. Debe iniciar con ORD-")

    if not cliente or not str(cliente).strip():
        raise ValueError("El cliente es obligatorio.")
    if not producto or not str(producto).strip():
        raise ValueError("El producto es obligatorio.")

    # --- Casteo defensivo de tipos ---
    try:
        cantidad = int(cantidad)
        precio_unitario = float(precio_unitario)
        descuento = float(descuento) if descuento not in (None, "") else 0.0
    except (TypeError, ValueError):
        raise ValueError(
            "Cantidad, precio unitario y descuento deben ser valores numéricos válidos."
        )

    subtotal = calcular_total(cantidad, precio_unitario)
    monto_final = aplicar_descuento(subtotal, descuento)

    nuevo_id = max([p["id"] for p in BASE_DATOS["pedidos"]], default=0) + 1
    nuevo_pedido = {
        "id": nuevo_id,
        "codigo": codigo,
        "cliente": cliente,
        "producto": producto,
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "descuento": descuento,
        "monto_final": monto_final,
        "estado": "Confirmado"
    }

    BASE_DATOS["pedidos"].append(nuevo_pedido)
    registrar_cliente(cliente)
    return nuevo_pedido

def actualizar_pedido(pedido_id, cantidad=None, precio_unitario=None, descuento=None, estado=None):
    for p in BASE_DATOS["pedidos"]:
        if p["id"] == pedido_id:
            try:
                if cantidad is not None:
                    p["cantidad"] = int(cantidad)
                if precio_unitario is not None:
                    p["precio_unitario"] = float(precio_unitario)
                if descuento is not None:
                    p["descuento"] = float(descuento)
                if estado is not None:
                    p["estado"] = str(estado)
            except (TypeError, ValueError):
                raise ValueError("Cantidad, precio unitario y descuento deben ser numéricos.")

            subtotal = calcular_total(p["cantidad"], p["precio_unitario"])
            p["monto_final"] = aplicar_descuento(subtotal, p["descuento"])
            return p
    return None

# ---------------------------------------------------------------------------
# Renderizado de Interfaz Web
# ---------------------------------------------------------------------------

def construir_html():
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>NovaTech S.A.C. - Dashboard Interactivo -</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f1f5f9; margin: 0; padding: 25px; color: #334155; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 20px; }}
        h1 {{ font-size: 24px; color: #0f172a; margin: 0; }}
        .grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .card {{ background: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 20px; }}
        .form-group {{ margin-bottom: 12px; }}
        label {{ display: block; font-size: 12px; font-weight: bold; margin-bottom: 4px; color: #475569; }}
        input, select {{ width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; }}
        button {{ background: #2563eb; color: white; border: none; padding: 10px 15px; border-radius: 4px; font-weight: bold; cursor: pointer; width: 100%; }}
        button:hover {{ background: #1d4ed8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f8fafc; color: #475569; }}
        .btn-edit {{ background: #f59e0b; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 11px; }}
        #mensajeError {{ display: none; background: #fee2e2; color: #b91c1c; padding: 10px; border-radius: 4px; margin-bottom: 10px; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Comercial NovaTech S.A.C. - Operations & Analytics </h1>
            <span>Versión: <strong>{VERSION}</strong></span>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Ventas por Producto (S/) </h3>
                <canvas id="ventasChart" height="120"></canvas>
            </div>

            <div class="card">
                <h3>Registrar Nueva Venta</h3>
                <div id="mensajeError"></div>
                <form id="formVenta">
                    <div class="form-group"><label>Código</label><input type="text" id="codigo" value="ORD-2026-9000" required></div>
                    <div class="form-group"><label>Cliente</label><input type="text" id="cliente" required></div>
                    <div class="form-group"><label>Producto</label><input type="text" id="producto" required></div>
                    <div style="display:flex; gap: 8px;">
                        <div class="form-group"><label>Cant.</label><input type="number" id="cantidad" value="1" min="1" required></div>
                        <div class="form-group"><label>Precio</label><input type="number" step="0.01" id="precio" value="100.00" min="0" required></div>
                        <div class="form-group"><label>Desc %</label><input type="number" id="descuento" value="0" min="0" max="100"></div>
                    </div>
                    <button type="submit">Guardar Pedido</button>
                </form>
            </div>
        </div>

        <div class="card">
            <h3>Listado General de Pedidos</h3>
            <table id="tablaPedidos">
                <thead>
                    <tr>
                        <th>ID</th><th>Código</th><th>Cliente</th><th>Producto</th><th>Cant.</th><th>P. Unit.</th><th>Desc %</th><th>Monto Total</th><th>Acciones</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <script>
        let chartInstance = null;

        async function cargarDatos() {{
            const res = await fetch('/api/pedidos');
            const data = await res.json();

            const tbody = document.querySelector('#tablaPedidos tbody');
            tbody.innerHTML = '';

            const prodTotales = {{}};

            data.pedidos.forEach(p => {{
                tbody.innerHTML += `
                    <tr>
                        <td>${{p.id}}</td>
                        <td>${{p.codigo}}</td>
                        <td>${{p.cliente}}</td>
                        <td>${{p.producto}}</td>
                        <td>${{p.cantidad}}</td>
                        <td>S/ ${{p.precio_unitario.toFixed(2)}}</td>
                        <td>${{p.descuento}}%</td>
                        <td><strong>S/ ${{p.monto_final.toFixed(2)}}</strong></td>
                        <td><button class="btn-edit" onclick="editarPedido(${{p.id}}, ${{p.cantidad}})">Modificar Cantidad</button></td>
                    </tr>
                `;

                prodTotales[p.producto] = (prodTotales[p.producto] || 0) + p.monto_final;
            }});

            renderGrafico(Object.keys(prodTotales), Object.values(prodTotales));
        }}

        function renderGrafico(labels, values) {{
            const ctx = document.getElementById('ventasChart').getContext('2d');
            if (chartInstance) chartInstance.destroy();

            chartInstance = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{ label: 'Total Ventas (S/)', data: values, backgroundColor: '#2563eb' }}]
                }},
                options: {{ responsive: true }}
            }});
        }}

        function mostrarError(msg) {{
            const el = document.getElementById('mensajeError');
            el.textContent = msg;
            el.style.display = 'block';
            setTimeout(() => {{ el.style.display = 'none'; }}, 4000);
        }}

        document.getElementById('formVenta').addEventListener('submit', async (e) => {{
            e.preventDefault();

            // Se castean los valores numéricos en el propio frontend
            // como buena práctica adicional (defensa en capas), aunque
            // el backend ya no depende de esto para funcionar.
            const payload = {{
                codigo: document.getElementById('codigo').value,
                cliente: document.getElementById('cliente').value,
                producto: document.getElementById('producto').value,
                cantidad: Number(document.getElementById('cantidad').value),
                precio_unitario: Number(document.getElementById('precio').value),
                descuento: Number(document.getElementById('descuento').value)
            }};

            const res = await fetch('/api/pedidos', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(payload)
            }});

            if (!res.ok) {{
                const err = await res.json();
                mostrarError(err.error || 'No se pudo registrar la venta.');
                return;
            }}

            e.target.reset();
            document.getElementById('codigo').value = 'ORD-2026-9000';
            cargarDatos();
        }});

        async function editarPedido(id, cantActual) {{
            const nuevaCant = prompt("Ingrese la nueva cantidad para el pedido ID " + id, cantActual);
            if (nuevaCant !== null) {{
                const res = await fetch('/api/pedidos', {{
                    method: 'PUT',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ id: id, cantidad: Number(nuevaCant) }})
                }});
                if (!res.ok) {{
                    const err = await res.json();
                    mostrarError(err.error || 'No se pudo actualizar el pedido.');
                    return;
                }}
                cargarDatos();
            }}
        }}

        cargarDatos();
    </script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Controlador Servidor HTTP
# ---------------------------------------------------------------------------

class NovaTechRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._responder(construir_html(), "text/html; charset=utf-8")
        elif self.path == "/api/pedidos":
            self._responder(json.dumps(BASE_DATOS), "application/json")
        elif self.path == "/health":
            self._responder(json.dumps({"status": "ok", "version": VERSION}), "application/json")
        else:
            self.send_error(404, "Recurso no encontrado")

    def do_POST(self):
        if self.path == "/api/pedidos":
            self._manejar_request_json(self._crear_pedido)
        else:
            self.send_error(404, "Recurso no encontrado")

    def do_PUT(self):
        if self.path == "/api/pedidos":
            self._manejar_request_json(self._editar_pedido)
        else:
            self.send_error(404, "Recurso no encontrado")

    # --- Handlers de negocio, separados del parseo/errores de bajo nivel ---

    def _crear_pedido(self, body):
        nuevo = registrar_venta(
            body["codigo"], body["cliente"], body["producto"],
            body["cantidad"], body["precio_unitario"], body.get("descuento", 0)
        )
        self._responder(json.dumps(nuevo), "application/json", 201)

    def _editar_pedido(self, body):
        pedido_actualizado = actualizar_pedido(
            int(body["id"]),
            cantidad=body.get("cantidad"),
            precio_unitario=body.get("precio_unitario"),
            descuento=body.get("descuento")
        )
        if pedido_actualizado:
            self._responder(json.dumps(pedido_actualizado), "application/json")
        else:
            self._responder(json.dumps({"error": "Pedido no encontrado"}), "application/json", 404)

    # --- Infraestructura común: parseo de JSON y manejo de errores ---

    def _manejar_request_json(self, handler_fn):
        """
        Envuelve cualquier operación POST/PUT que reciba JSON:
        - Parsea el body de forma segura.
        - Captura errores esperados (datos inválidos) -> 400.
        - Captura errores inesperados -> 500, sin tumbar el servidor.
        Esto evita que un TypeError/KeyError/JSONDecodeError deje al
        cliente con la conexión reseteada, como ocurría antes.
        """
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length) if length > 0 else b"{}"
            body = json.loads(raw_body)
            handler_fn(body)
        except KeyError as e:
            self._responder(json.dumps({"error": f"Falta el campo requerido: {e}"}), "application/json", 400)
        except (ValueError, TypeError) as e:
            self._responder(json.dumps({"error": str(e)}), "application/json", 400)
        except json.JSONDecodeError:
            self._responder(json.dumps({"error": "El cuerpo de la petición no es JSON válido."}), "application/json", 400)
        except Exception as e:
            # Última barrera: nunca dejar que una excepción no controlada
            # tumbe el hilo del servidor sin responder al cliente.
            self._responder(json.dumps({"error": "Error interno del servidor.", "detalle": str(e)}), "application/json", 500)

    def _responder(self, contenido, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(contenido.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(contenido.encode("utf-8"))

    def log_message(self, format, *args):
        print("[NovaTech] %s - %s" % (self.address_string(), format % args))


def run(server_class=HTTPServer, handler_class=NovaTechRequestHandler, port=4200):
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    print(f"[NovaTech] Servidor ejecutándose en http://localhost:{port} (versión {VERSION})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[NovaTech] Servidor detenido manualmente.")
        httpd.server_close()

if __name__ == "__main__":
    run()
