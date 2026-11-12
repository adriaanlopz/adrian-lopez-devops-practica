# Bibliotecas 
import uuid
from datetime import datetime
from typing import List, Tuple

from models.Producto import Producto
from models.Usuario import Cliente

# Clase
class Pedido:

    def __init__(self, cliente: Cliente, lineas: List[Tuple[Producto, int]]) -> None:
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.lineas: List[Tuple[Producto, int]] = lineas
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        return sum(producto.precio * cantidad for producto, cantidad in self.lineas)

    @property
    def cliente_id(self) -> str:
        return self.cliente.id

    @property
    def total(self) -> float:
        return round(self.calcular_total(), 2)

    @property
    def items(self) -> List[dict]:
        return [
            {"producto_id": producto.id, "nombre": producto.nombre, "precio": producto.precio, "cantidad": cantidad}
            for producto, cantidad in self.lineas
        ]

    def __str__(self) -> str:
        detalle = ", ".join(f"{cantidad}x {producto.nombre}" for producto, cantidad in self.lineas)
        return (
            f"Pedido [{self.id[:8]}] de {self.cliente.nombre} ({self.fecha:%Y-%m-%d %H:%M}) - "
            f"{detalle} - Total: {self.calcular_total():.2f}€"
        )
