from app.database import obtener_conexion

def obtener_todos():
    conexion = obtener_conexion()
    filas = conexion.execute(" SELECT * FROM productos").fetchall() #fetchall significa dame todas las filas del resultado
    conexion.close()
    return [dict(fila)for fila in filas ] #convierte cada fila en un diccionario, para que FastAPI la pueda devolver como JSON

#funcion cumple solamente para buscar si el ID existe o no y que no este repetido 
def obtener_por_id(id):
    conexion = obtener_conexion()
    fila = conexion.execute(" SELECT * FROM productos WHERE id = ?",(id,)).fetchone()  #fetchone() significa “dame una fila, o None si no hay
    conexion.close()
    if fila is None:
        return None
    else:
        return dict(fila)
    
#funcion para insertar datos 
def crear(nombre, sku, stock, precio):
    conexion = obtener_conexion()
    cursor = conexion.execute("INSERT INTO productos (nombre, sku, stock, precio) VALUES (?,?,?,?)",
    (nombre,sku,stock,precio))
    conexion.commit()
    nuevo_id = cursor.lastrowid  #lastrowid es “¿qué id le tocó al que acabo de insertar?
    conexion.close()
    return obtener_por_id(nuevo_id)

#funcion que sirve cuando haya un error con el sku repetido pueda seguir su funcion 
def crear(nombre, sku, stock, precio):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute("INSERT INTO productos (nombre, sku, stock, precio) VALUES (?,?,?,?)",
        (nombre,sku,stock,precio))
        conexion.commit()
        nuevo_id = cursor.lastrowid
    finally:
        conexion.close()
    return obtener_por_id(nuevo_id)


def obtener_por_sku(sku):
    conexion = obtener_conexion()
    fila = conexion.execute("SELECT * FROM productos WHERE sku = ?",(sku,)).fetchone()
    conexion.close()
    if fila is None:
        return None
    else:
        return dict(fila)

def obtener_stock_bajo(stock):
    conexion = obtener_conexion()
    filas = conexion.execute("SELECT * FROM productos WHERE stock < ?",(stock,)).fetchall()
    conexion.close()
    return [dict(fila)for fila in filas ]

def actualizar(nombre, sku, stock, precio,id):
    conexion = obtener_conexion()
    try:
        conexion.execute("UPDATE productos SET nombre = ?, sku = ?, stock = ?, precio = ? WHERE id = ?",
        (nombre,sku,stock,precio,id))
        conexion.commit() 
    finally:
        conexion.close()
    return obtener_por_id(id)

def eliminar(id):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute("DELETE FROM productos WHERE id = ?",(id,))
        conexion.commit()
        borradas = cursor.rowcount #cuantas filas borro 
    finally:
        conexion.close()
    return borradas
