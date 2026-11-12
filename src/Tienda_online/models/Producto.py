# Bibliotecas
import uuid

# Clases
class Producto:

    tipo: str = "generico"

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        if self.stock + cantidad < 0:
            raise ValueError(f"Stock insuficiente de {self.nombre}")
        self.stock += cantidad

    def __str__(self) -> str:
        return f"[{self.id[:8]}] {self.nombre} - {self.precio:.2f}€ (stock: {self.stock})"


class ProductoElectronico(Producto):

    tipo: str = "electronico"

    def __init__(self, nombre: str, precio: float, stock: int, meses_garantia: int) -> None:
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        return f"{super().__str__()} | Garantía: {self.meses_garantia} meses"


class ProductoRopa(Producto):

    tipo: str = "ropa"

    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str) -> None:
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        return f"{super().__str__()} | Talla: {self.talla}, Color: {self.color}"
