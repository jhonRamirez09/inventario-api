from app import repositorio

class ProductoNoEncontrado(Exception):
    pass

class SkuDuplicado(Exception):
    pass

class StockInsuficiente(Exception):
    pass

def obtener_producto(id):
    producto = repositorio.obtener_por_id(id)
    if producto is None:
        raise ProductoNoEncontrado(f"No existe el producto con id {id}")
    return producto

def crear_producto(nombre,sku,stock,precio):
    producto = repositorio.obtener_por_sku(sku)
    if producto is None:
        producto = repositorio.crear(nombre,sku,stock,precio)
    else:
       raise SkuDuplicado(f"Sku ya existe, intenta con otro {sku}")
    return producto

def registrar_movimiento(id,tipo,cantidad):
    producto = obtener_producto(id) 
    if tipo == "entrada":
        nuevo_stock = producto["stock"] + cantidad
    elif tipo == "salida":
        nuevo_stock = producto["stock"] - cantidad
    if nuevo_stock < 0:
        raise StockInsuficiente(f"Stock insuficiente: disponible {producto['stock']}, solicitado {cantidad}")
    return repositorio.actualizar_stock(id,nuevo_stock)

LIMITE_STOCK_BAJO = 10
def listar_productos(stock_bajo):
    if stock_bajo is True:
        return repositorio.obtener_stock_bajo(LIMITE_STOCK_BAJO)
    else:
        return repositorio.obtener_todos()

def eliminar_producto(id):
    borradas = repositorio.eliminar(id)
    if borradas == 0:
       raise ProductoNoEncontrado(f"No existe el producto con id {id}")

def actualizar_producto(id, nombre, sku, stock, precio):
    obtener_producto(id)
    encontrado = repositorio.obtener_por_sku(sku)
    if encontrado is not None and encontrado["id"] != id:
        raise SkuDuplicado(f"Sku ya existe, intenta con otro {sku}")
    return repositorio.actualizar(id, nombre, sku, stock, precio)