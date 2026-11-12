# Bibliotecas
import os
from typing import List, Optional
import requests

# Configuración
URL_API = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# Comunicación con la API
def llamar(metodo: str, ruta: str, datos: Optional[dict] = None):
    respuesta = requests.request(metodo, URL_API + ruta, json=datos, timeout=5)
    if respuesta.status_code >= 400:
        detalle = respuesta.json().get("detail", respuesta.text)
        if isinstance(detalle, list):
            detalle = "; ".join(f"{'.'.join(str(c) for c in e['loc'][1:])}: {e['msg']}" for e in detalle)
        print(f"  Error {respuesta.status_code}: {detalle}")
        return None
    return respuesta.json() if respuesta.content else True


def elegir(elementos: List[dict], describir) -> Optional[dict]:
    if not elementos:
        print("  No hay elementos para elegir")
        return None
    for numero, elemento in enumerate(elementos, start=1):
        print(f"  {numero}. {describir(elemento)}")
    opcion = input("  Número: ").strip()
    if not opcion.isdigit() or not 1 <= int(opcion) <= len(elementos):
        print("  Opción no válida")
        return None
    return elementos[int(opcion) - 1]


def describir_usuario(u: dict) -> str:
    return f"{u['nombre']} <{u['email']}>" + (" (admin)" if u["es_admin"] else "")


def describir_producto(p: dict) -> str:
    extra = ""
    if p["tipo"] == "electronico":
        extra = f", garantía {p['meses_garantia']} meses"
    elif p["tipo"] == "ropa":
        extra = f", talla {p['talla']}, {p['color']}"
    return f"{p['nombre']} [{p['tipo']}] {p['precio']:.2f}€ (stock {p['stock']}{extra})"


# Opciones del menú
def crear_usuario() -> None:
    tipo = input("  Tipo (cliente/administrador): ").strip()
    datos = {"nombre": input("  Nombre: ").strip(), "email": input("  Email: ").strip(), "tipo": tipo}
    if tipo == "cliente":
        datos["direccion_postal"] = input("  Dirección postal: ").strip()
    usuario = llamar("POST", "/usuarios", datos)
    if usuario:
        print(f"  Creado: {describir_usuario(usuario)}")


def listar_usuarios() -> None:
    usuarios = llamar("GET", "/usuarios") or []
    for u in usuarios:
        print(f"  - {describir_usuario(u)}")
    if not usuarios:
        print("  No hay usuarios")


def crear_producto() -> None:
    tipo = input("  Tipo (generico/electronico/ropa): ").strip()
    try:
        datos = {
            "tipo": tipo,
            "nombre": input("  Nombre: ").strip(),
            "precio": float(input("  Precio: ")),
            "stock": int(input("  Stock: ")),
        }
        if tipo == "electronico":
            datos["meses_garantia"] = int(input("  Meses de garantía: "))
    except ValueError:
        print("  Precio, stock y garantía tienen que ser números")
        return
    if tipo == "ropa":
        datos["talla"] = input("  Talla: ").strip()
        datos["color"] = input("  Color: ").strip()
    producto = llamar("POST", "/productos", datos)
    if producto:
        print(f"  Creado: {describir_producto(producto)}")


def listar_productos() -> None:
    productos = llamar("GET", "/productos") or []
    for p in productos:
        print(f"  - {describir_producto(p)}")
    if not productos:
        print("  No hay productos")


def eliminar_producto() -> None:
    producto = elegir(llamar("GET", "/productos") or [], describir_producto)
    if producto and llamar("DELETE", f"/productos/{producto['id']}"):
        print(f"  Eliminado: {producto['nombre']}")


def crear_pedido() -> None:
    clientes = [u for u in llamar("GET", "/usuarios") or [] if not u["es_admin"]]
    print("  Cliente:")
    cliente = elegir(clientes, describir_usuario)
    if not cliente:
        return
    productos = llamar("GET", "/productos") or []
    items = []
    while True:
        print("  Producto (Enter vacío para terminar):")
        for numero, p in enumerate(productos, start=1):
            print(f"  {numero}. {describir_producto(p)}")
        opcion = input("  Número: ").strip()
        if not opcion:
            break
        if not opcion.isdigit() or not 1 <= int(opcion) <= len(productos):
            print("  Opción no válida")
            continue
        cantidad = input("  Cantidad: ").strip()
        if not cantidad.isdigit():
            print("  La cantidad tiene que ser un número")
            continue
        items.append({"producto_id": productos[int(opcion) - 1]["id"], "cantidad": int(cantidad)})
    if not items:
        print("  Pedido cancelado: no tiene productos")
        return
    pedido = llamar("POST", "/pedidos", {"cliente_id": cliente["id"], "items": items})
    if pedido:
        print(f"  Pedido creado para {cliente['nombre']}: total {pedido['total']:.2f}€")


def ver_pedidos() -> None:
    clientes = [u for u in llamar("GET", "/usuarios") or [] if not u["es_admin"]]
    cliente = elegir(clientes, describir_usuario)
    if not cliente:
        return
    pedidos = llamar("GET", f"/usuarios/{cliente['id']}/pedidos") or []
    if not pedidos:
        print(f"  {cliente['nombre']} no tiene pedidos")
    for pedido in pedidos:
        lineas = ", ".join(f"{i['cantidad']}x {i['nombre']}" for i in pedido["items"])
        print(f"  - {pedido['fecha'][:16].replace('T', ' ')} | {lineas} | Total: {pedido['total']:.2f}€")


def cargar_ejemplo() -> None:
    usuarios = [
        {"nombre": "Lucía Martín", "email": "lucia.martin@correo.es", "tipo": "cliente", "direccion_postal": "Rúa do Franco 12, Santiago"},
        {"nombre": "Pablo Ríos", "email": "pablo.rios@correo.es", "tipo": "cliente", "direccion_postal": "Calle Real 45, Ferrol"},
        {"nombre": "Admin Tienda", "email": "admin@tienda.es", "tipo": "administrador"},
    ]
    productos = [
        {"tipo": "electronico", "nombre": "Monitor 27''", "precio": 229.00, "stock": 8, "meses_garantia": 36},
        {"tipo": "ropa", "nombre": "Pantalón vaquero", "precio": 39.90, "stock": 25, "talla": "42", "color": "Negro"},
        {"tipo": "generico", "nombre": "Taza de cerámica", "precio": 7.50, "stock": 40},
    ]
    creados = sum(1 for datos in usuarios if llamar("POST", "/usuarios", datos))
    creados += sum(1 for datos in productos if llamar("POST", "/productos", datos))
    print(f"  Cargados {creados} elementos de ejemplo")


# Menú
OPCIONES = {
    "1": ("Crear usuario", crear_usuario),
    "2": ("Listar usuarios", listar_usuarios),
    "3": ("Crear producto", crear_producto),
    "4": ("Listar productos", listar_productos),
    "5": ("Eliminar producto", eliminar_producto),
    "6": ("Crear pedido", crear_pedido),
    "7": ("Ver pedidos de un cliente", ver_pedidos),
    "8": ("Cargar datos de ejemplo", cargar_ejemplo),
}


def main() -> None:
    print(f"Tienda online · consola de gestión ({URL_API})")
    while True:
        print()
        for clave, (texto, _) in OPCIONES.items():
            print(f"{clave}. {texto}")
        print("0. Salir")
        opcion = input("> ").strip()
        if opcion == "0":
            break
        if opcion not in OPCIONES:
            print("  Opción no válida")
            continue
        try:
            OPCIONES[opcion][1]()
        except requests.ConnectionError:
            print(f"  No se puede conectar con la API en {URL_API}. ¿Está arrancada?")


if __name__ == "__main__":
    main()
