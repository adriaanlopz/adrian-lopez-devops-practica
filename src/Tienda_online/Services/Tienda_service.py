# Bibliotecas
from typing import Dict, List, Tuple
from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Administrador, Cliente, Usuario

# Clases
class TiendaService:

    def __init__(self) -> None:
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    def registrar_usuario(self, tipo: str, nombre: str, email: str, direccion_postal: str = "") -> Usuario:
        if tipo == "cliente":
            usuario: Usuario = Cliente(nombre, email, direccion_postal)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError(f"Tipo de usuario desconocido: {tipo}")
        self.usuarios[usuario.id] = usuario
        return usuario

    def anadir_producto(
        self,
        categoria: str,
        nombre: str,
        precio: float,
        stock: int,
        meses_garantia: int = 0,
        talla: str = "",
        color: str = "",
    ) -> Producto:
        if categoria == "electronico":
            producto: Producto = ProductoElectronico(nombre, precio, stock, meses_garantia)
        elif categoria == "ropa":
            producto = ProductoRopa(nombre, precio, stock, talla, color)
        elif categoria == "generico":
            producto = Producto(nombre, precio, stock)
        else:
            raise ValueError(f"Categoría desconocida: {categoria}")
        self.productos[producto.id] = producto
        return producto

    def eliminar_producto(self, producto_id: str) -> None:
        if producto_id not in self.productos:
            raise ValueError(f"No existe el producto {producto_id}")
        del self.productos[producto_id]

    def listar_productos(self) -> List[Producto]:
        return list(self.productos.values())

    def realizar_pedido(self, cliente_id: str, lineas: List[Tuple[str, int]]) -> Pedido:
        cliente = self.usuarios.get(cliente_id)
        if not isinstance(cliente, Cliente):
            raise ValueError(f"No existe el cliente {cliente_id}")

        cantidades: Dict[str, int] = {}
        for producto_id, cantidad in lineas:
            if producto_id not in self.productos:
                raise ValueError(f"No existe el producto {producto_id}")
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor que 0")
            cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

        lineas_pedido = [(self.productos[pid], cantidad) for pid, cantidad in cantidades.items()]
        for producto, cantidad in lineas_pedido:
            if not producto.hay_stock(cantidad):
                raise ValueError(f"Stock insuficiente de {producto.nombre}")

        for producto, cantidad in lineas_pedido:
            producto.actualizar_stock(-cantidad)
        pedido = Pedido(cliente, lineas_pedido)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, cliente_id: str) -> List[Pedido]:
        return sorted((p for p in self.pedidos if p.cliente.id == cliente_id), key=lambda p: p.fecha)
