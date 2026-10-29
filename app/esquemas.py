from pydantic import BaseModel, Field
from typing import Literal

class ProductoEntrada(BaseModel):
    nombre: str = Field(min_length=1)     #min_length=1   → el texto no puede venir vacío
    sku: str = Field(min_length=1)        #min_length=1   → el texto no puede venir vacío
    stock: int = Field(default=0, ge=0)   #ge = 0 → greater or equal: mayor o igual a 0, default=0→ si no lo mandan, vale 0
    precio: float = Field(gt=0)           #gt= 0 → greater than: mayor que 0 (estricto)
    
    
class MovimientoEntrada(BaseModel):
    tipo: Literal["entrada", "salida"]
    cantidad: int = Field(gt=0)
