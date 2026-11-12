# Bibliotecas
import uuid

# Clases
class Usuario:

    def __init__(self, nombre: str, email: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        return False

    @property
    def es_admin(self) -> bool:
        return self.is_admin()

    def __str__(self) -> str:
        return f"[{self.id[:8]}] {self.nombre} ({self.email})"


class Cliente(Usuario):

    def __init__(self, nombre: str, email: str, direccion_postal: str) -> None:
        super().__init__(nombre, email)
        self.direccion_postal: str = direccion_postal

    def __str__(self) -> str:
        return f"{super().__str__()} | Dirección: {self.direccion_postal}"


class Administrador(Usuario):

    def is_admin(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"{super().__str__()} | Administrador"
