from app.database import obtener_conexion

def obtener_todos():
    conexion = obtener_conexion()
    filas = conexion.execute(" SELECT * FROM productos").fetchall() #fetchall significa dame todas las filas del resultado
    conexion.close()
    return [dict(fila)for fila in filas ] #convierte cada fila en un diccionario, para que FastAPI la pueda devolver como JSON

#busca por id 
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