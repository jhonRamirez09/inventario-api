import sqlite3

DB_NAME = "inventario.db" #nombre de nuestra base de datos

#creamos una funcion para la conexion de la base de datos 

def obtener_conexion():
    conexion = sqlite3.connect(DB_NAME)
    conexion.row_factory = sqlite3.Row   # filas como diccionario
    return conexion

#creamos una funcion para crear las tablas 

def crear_tablas():
    conexion = obtener_conexion()
    conexion.execute('''
        CREATE TABLE IF NOT EXISTS productos(       --créala solo si no existe 
            id INTEGER PRIMARY KEY AUTOINCREMENT,   --id que se numera solo: 1, 2, 3...
            nombre TEXT NOT NULL,                   --texto obligatorio
            sku TEXT NOT NULL UNIQUE,               --no se puede repetir
            stock INTEGER NOT NULL DEFAULT 0,       -- unidades enteras; producto nuevo arranca sin stock
            precio REAL NOT NULL )                  -- obligatorio, con decimales
        '''
    )
    conexion.commit()
    conexion.close()