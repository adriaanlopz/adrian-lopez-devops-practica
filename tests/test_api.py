import pytest
from fastapi.testclient import TestClient

from main import app, get_tienda
from Services.Tienda_service import TiendaService


@pytest.fixture
def cliente_http():
    servicio = TiendaService()
    app.dependency_overrides[get_tienda] = lambda: servicio
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


def crear_cliente(http, nombre="Lucía Martín"):
    datos = {"nombre": nombre, "email": "lucia@correo.es", "tipo": "cliente", "direccion_postal": "Rúa do Franco 12"}
    return http.post("/usuarios", json=datos).json()


def crear_producto(http, stock=5):
    datos = {"tipo": "electronico", "nombre": "Monitor 27''", "precio": 229.0, "stock": stock, "meses_garantia": 36}
    return http.post("/productos", json=datos).json()


def test_health(cliente_http):
    respuesta = cliente_http.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_raiz_redirige_a_docs(cliente_http):
    respuesta = cliente_http.get("/", follow_redirects=False)
    assert respuesta.status_code == 307
    assert respuesta.headers["location"] == "/docs"


def test_alta_y_consulta_de_usuarios(cliente_http):
    cliente = crear_cliente(cliente_http)
    admin = cliente_http.post("/usuarios", json={"nombre": "Admin", "email": "admin@tienda.es", "tipo": "administrador"})
    assert admin.status_code == 201
    assert admin.json()["es_admin"] is True
    assert cliente["es_admin"] is False
    assert cliente_http.get(f"/usuarios/{cliente['id']}").json()["nombre"] == "Lucía Martín"
    assert len(cliente_http.get("/usuarios").json()) == 2


def test_cliente_sin_direccion_da_400(cliente_http):
    respuesta = cliente_http.post("/usuarios", json={"nombre": "Pablo", "email": "pablo@correo.es", "tipo": "cliente"})
    assert respuesta.status_code == 400


def test_tipo_de_usuario_no_valido_da_422(cliente_http):
    respuesta = cliente_http.post("/usuarios", json={"nombre": "X", "email": "x@correo.es", "tipo": "invitado"})
    assert respuesta.status_code == 422


def test_usuario_inexistente_da_404(cliente_http):
    assert cliente_http.get("/usuarios/no-existe").status_code == 404


@pytest.mark.parametrize(
    "datos",
    [
        {"tipo": "electronico", "nombre": "Portátil", "precio": 899.99, "stock": 3},
        {"tipo": "ropa", "nombre": "Camiseta", "precio": 14.95, "stock": 10, "talla": "M"},
    ],
)
def test_producto_sin_atributos_de_su_tipo_da_400(cliente_http, datos):
    assert cliente_http.post("/productos", json=datos).status_code == 400


def test_precio_negativo_da_422(cliente_http):
    datos = {"tipo": "generico", "nombre": "Taza", "precio": -1, "stock": 3}
    assert cliente_http.post("/productos", json=datos).status_code == 422


def test_ciclo_de_vida_de_un_producto(cliente_http):
    producto = crear_producto(cliente_http)
    assert producto["meses_garantia"] == 36
    assert cliente_http.get(f"/productos/{producto['id']}").status_code == 200
    assert len(cliente_http.get("/productos").json()) == 1
    assert cliente_http.delete(f"/productos/{producto['id']}").status_code == 200
    assert cliente_http.get(f"/productos/{producto['id']}").status_code == 404
    assert cliente_http.delete(f"/productos/{producto['id']}").status_code == 404


def test_pedido_descuenta_stock_y_aparece_en_el_historial(cliente_http):
    cliente = crear_cliente(cliente_http)
    producto = crear_producto(cliente_http, stock=5)
    pedido = cliente_http.post(
        "/pedidos", json={"cliente_id": cliente["id"], "items": [{"producto_id": producto["id"], "cantidad": 2}]}
    )
    assert pedido.status_code == 201
    assert pedido.json()["total"] == 458.0
    assert cliente_http.get(f"/productos/{producto['id']}").json()["stock"] == 3
    historial = cliente_http.get(f"/usuarios/{cliente['id']}/pedidos").json()
    assert [p["id"] for p in historial] == [pedido.json()["id"]]


def test_pedido_sin_stock_da_400_y_no_toca_el_stock(cliente_http):
    cliente = crear_cliente(cliente_http)
    producto = crear_producto(cliente_http, stock=1)
    respuesta = cliente_http.post(
        "/pedidos", json={"cliente_id": cliente["id"], "items": [{"producto_id": producto["id"], "cantidad": 2}]}
    )
    assert respuesta.status_code == 400
    assert cliente_http.get(f"/productos/{producto['id']}").json()["stock"] == 1


def test_pedido_de_un_administrador_da_404(cliente_http):
    admin = cliente_http.post("/usuarios", json={"nombre": "Admin", "email": "admin@tienda.es", "tipo": "administrador"}).json()
    producto = crear_producto(cliente_http)
    respuesta = cliente_http.post(
        "/pedidos", json={"cliente_id": admin["id"], "items": [{"producto_id": producto["id"], "cantidad": 1}]}
    )
    assert respuesta.status_code == 404


def test_pedido_con_producto_inexistente_da_404(cliente_http):
    cliente = crear_cliente(cliente_http)
    respuesta = cliente_http.post("/pedidos", json={"cliente_id": cliente["id"], "items": [{"producto_id": "x", "cantidad": 1}]})
    assert respuesta.status_code == 404
