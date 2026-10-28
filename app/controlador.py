from fastapi import APIRouter

from app import servicio
from app.esquemas import ProductoEntrada, MovimientoEntrada

router = APIRouter(prefix="/productos", tags=["Productos"]) #todas las rutas de este mesero empiezan con /productos. Así no lo repites.


@router.get("/{id}")  #@router.get("/{id}") → la ruta queda /productos/5. El {id} es un hueco en la dirección, y FastAPI te lo pasa como parámetro.
def obtener(id: int):
    return servicio.obtener_producto(id)

@router.post("", status_code=201)
def crear(datos: ProductoEntrada):
    return servicio.crear_producto(datos.nombre, datos.sku, datos.stock, datos.precio)

@router.post("/{id}/movimientos",status_code=200)
def registrar_movimiento(id:int, datos: MovimientoEntrada):
    return servicio.registrar_movimiento(id, datos.tipo, datos.cantidad)

@router.get("")
def listar(stockBajo: bool = False):
    return servicio.listar_productos(stockBajo)

@router.put("/{id}", status_code=200)
def actualizar_producto(id: int, datos:ProductoEntrada):
    return servicio.actualizar_producto(id, datos.nombre, datos.sku, datos.stock, datos.precio)

@router.delete("/{id}", status_code=204)
def eliminar(id:int):
    servicio.eliminar_producto(id)