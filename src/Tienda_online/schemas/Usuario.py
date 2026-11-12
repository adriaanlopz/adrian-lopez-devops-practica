from typing import Literal

from pydantic import BaseModel, ConfigDict


class UsuarioBase(BaseModel):
    nombre: str
    email: str


class UsuarioCreate(UsuarioBase):
    tipo: Literal["cliente", "administrador"]
    direccion_postal: str | None = None


class UsuarioRead(UsuarioBase):
    id: str
    es_admin: bool

    model_config = ConfigDict(from_attributes=True)
