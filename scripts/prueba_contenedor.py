import http.client
import json
import sys
import time
import urllib.error
import urllib.request

URL_API = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")


def llamar(metodo, ruta, datos=None):
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    peticion = urllib.request.Request(
        URL_API + ruta, data=cuerpo, method=metodo, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(peticion, timeout=5) as respuesta:
            return respuesta.status, json.loads(respuesta.read() or b"null")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"null")


def esperar_api(segundos=30):
    for _ in range(segundos):
        try:
            if llamar("GET", "/health")[0] == 200:
                return
        except (OSError, http.client.HTTPException):
            pass
        time.sleep(1)
    sys.exit(f"La API no responde en {URL_API}")


def comprobar(descripcion, obtenido, esperado):
    if obtenido != esperado:
        print(f"[FALLO] {descripcion}: se esperaba {esperado} y llegó {obtenido}")
        sys.exit(1)
    print(f"[OK] {descripcion}: {obtenido}")


def main():
    print(f"Probando la API en {URL_API}\n")
    esperar_api()

    codigo, cuerpo = llamar("GET", "/health")
    comprobar("GET /health", (codigo, cuerpo), (200, {"status": "ok"}))

    codigo, cliente = llamar(
        "POST",
        "/usuarios",
        {"nombre": "Lucía Martín", "email": "lucia@correo.es", "tipo": "cliente", "direccion_postal": "Rúa do Franco 12"},
    )
    comprobar("POST /usuarios (cliente)", codigo, 201)

    codigo, _ = llamar("GET", f"/usuarios/{cliente['id']}")
    comprobar("GET /usuarios/{id}", codigo, 200)

    codigo, producto = llamar(
        "POST",
        "/productos",
        {"tipo": "electronico", "nombre": "Monitor 27''", "precio": 229.0, "stock": 5, "meses_garantia": 36},
    )
    comprobar("POST /productos (electrónico)", codigo, 201)

    codigo, productos = llamar("GET", "/productos")
    comprobar("GET /productos incluye el nuevo", any(p["id"] == producto["id"] for p in productos), True)

    linea = {"producto_id": producto["id"], "cantidad": 2}
    codigo, pedido = llamar("POST", "/pedidos", {"cliente_id": cliente["id"], "items": [linea]})
    comprobar("POST /pedidos", codigo, 201)
    comprobar("Total del pedido (2 x 229.0)", pedido["total"], 458.0)

    codigo, ficha = llamar("GET", f"/productos/{producto['id']}")
    comprobar("Stock después del pedido (5 - 2)", ficha["stock"], 3)

    codigo, _ = llamar("POST", "/pedidos", {"cliente_id": cliente["id"], "items": [{**linea, "cantidad": 10}]})
    comprobar("POST /pedidos sin stock suficiente", codigo, 400)

    codigo, historial = llamar("GET", f"/usuarios/{cliente['id']}/pedidos")
    comprobar("GET /usuarios/{id}/pedidos", (codigo, len(historial)), (200, 1))

    codigo, _ = llamar("DELETE", f"/productos/{producto['id']}")
    comprobar("DELETE /productos/{id}", codigo, 200)

    codigo, _ = llamar("GET", f"/productos/{producto['id']}")
    comprobar("GET /productos/{id} tras borrarlo", codigo, 404)

    print("\nTodas las comprobaciones son correctas")


if __name__ == "__main__":
    main()
