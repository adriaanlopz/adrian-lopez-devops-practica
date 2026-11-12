from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PedidoItemCreate(BaseModel):
    producto_id: str
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    cliente_id: str
    items: list[PedidoItemCreate] = Field(min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre: str
    precio: float
    cantidad: int


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente_id: str
    total: float
    items: list[PedidoItemRead]

    model_config = ConfigDict(from_attributes=True)
