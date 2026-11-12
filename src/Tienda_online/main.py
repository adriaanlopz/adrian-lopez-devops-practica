from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from models.Usuario import Cliente
from schemas.Pedido import PedidoCreate, PedidoRead
from schemas.Producto import ProductoCreate, ProductoRead
from schemas.Usuario import UsuarioCreate, UsuarioRead
from Services.Tienda_service import TiendaService

app = FastAPI(title="Tienda online")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

tienda = TiendaService()


def get_tienda():
    return tienda


@app.get("/", include_in_schema=False)
def inicio():
    return RedirectResponse("/docs")


@app.post("/usuarios", response_model=UsuarioRead, status_code=201)
def alta_usuario(usuario: UsuarioCreate, servicio: TiendaService = Depends(get_tienda)):
    if usuario.tipo == "cliente" and not usuario.direccion_postal:
        raise HTTPException(status_code=400, detail="Un cliente necesita dirección postal")
    return servicio.registrar_usuario(usuario.tipo, usuario.nombre, usuario.email, usuario.direccion_postal or "")


@app.get("/usuarios", response_model=list[UsuarioRead])
def lista_usuarios(servicio: TiendaService = Depends(get_tienda)):
    return list(servicio.usuarios.values())


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def ficha_usuario(usuario_id: str, servicio: TiendaService = Depends(get_tienda)):
    usuario = servicio.usuarios.get(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.post("/productos", response_model=ProductoRead, status_code=201)
def alta_producto(producto: ProductoCreate, servicio: TiendaService = Depends(get_tienda)):
    if producto.tipo == "electronico" and producto.meses_garantia is None:
        raise HTTPException(status_code=400, detail="Un producto electrónico necesita meses_garantia")
    if producto.tipo == "ropa" and (not producto.talla or not producto.color):
        raise HTTPException(status_code=400, detail="Un producto de ropa necesita talla y color")
    return servicio.anadir_producto(
        producto.tipo,
        producto.nombre,
        producto.precio,
        producto.stock,
        meses_garantia=producto.meses_garantia or 0,
        talla=producto.talla or "",
        color=producto.color or "",
    )


@app.get("/productos", response_model=list[ProductoRead])
def lista_productos(servicio: TiendaService = Depends(get_tienda)):
    return servicio.listar_productos()


@app.get("/productos/{producto_id}", response_model=ProductoRead)
def ficha_producto(producto_id: str, servicio: TiendaService = Depends(get_tienda)):
    producto = servicio.productos.get(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@app.delete("/productos/{producto_id}")
def baja_producto(producto_id: str, servicio: TiendaService = Depends(get_tienda)):
    if producto_id not in servicio.productos:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    servicio.eliminar_producto(producto_id)
    return {"message": f"Producto {producto_id} dado de baja"}


@app.post("/pedidos", response_model=PedidoRead, status_code=201)
def alta_pedido(pedido: PedidoCreate, servicio: TiendaService = Depends(get_tienda)):
    if not isinstance(servicio.usuarios.get(pedido.cliente_id), Cliente):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for item in pedido.items:
        producto = servicio.productos.get(item.producto_id)
        if producto is None:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")
        if not producto.hay_stock(item.cantidad):
            raise HTTPException(status_code=400, detail=f"Stock insuficiente de {producto.nombre}")
    try:
        return servicio.realizar_pedido(pedido.cliente_id, [(i.producto_id, i.cantidad) for i in pedido.items])
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[PedidoRead])
def historial_cliente(cliente_id: str, servicio: TiendaService = Depends(get_tienda)):
    if cliente_id not in servicio.usuarios:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return servicio.listar_pedidos_usuario(cliente_id)
