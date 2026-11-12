from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProductoBase(BaseModel):
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    meses_garantia: int | None = None
    talla: str | None = None
    color: str | None = None


class ProductoCreate(ProductoBase):
    pass


class ProductoRead(ProductoBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
