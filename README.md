# API de Inventario

API REST para la gestión del inventario de productos de una empresa distribuidora.
Permite crear, consultar, actualizar y eliminar productos, registrar entradas y
salidas de stock, y consultar los productos con stock bajo.

## Tecnologías

- Python 3.13
- FastAPI (framework web y validación con Pydantic)
- SQLite (módulo `sqlite3` incluido en Python)
- Pytest (pruebas unitarias)

## Requisitos

- Python 3.10 o superior
- Git

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/jhonRamirez09/inventario-api.git
   cd inventario-api
   ```

2. Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   ```

   Windows:

   ```bash
   venv\Scripts\activate
   ```

   Mac / Linux:

   ```bash
   source venv/bin/activate
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs

La base de datos `inventario.db` se crea automáticamente al iniciar la aplicación.

## Pruebas

```bash
python -m pytest -v
```

Las pruebas usan una base de datos temporal, por lo que no modifican
los datos de `inventario.db`.

## Endpoints

| Método | Ruta                          | Descripción                            | Respuestas         |
| ------ | ----------------------------- | -------------------------------------- | ------------------ |
| GET    | `/productos`                  | Lista todos los productos              | 200                |
| GET    | `/productos?stockBajo=true`   | Lista productos con stock menor a 10   | 200                |
| GET    | `/productos/{id}`             | Obtiene un producto                    | 200, 404           |
| POST   | `/productos`                  | Crea un producto                       | 201, 409, 422      |
| PUT    | `/productos/{id}`             | Actualiza un producto                  | 200, 404, 409, 422 |
| DELETE | `/productos/{id}`             | Elimina un producto                    | 204, 404           |
| POST   | `/productos/{id}/movimientos` | Registra una entrada o salida de stock | 200, 404, 409, 422 |

### Ejemplo: crear un producto

```json
POST /productos
{
  "nombre": "Arroz",
  "sku": "ARZ-500G",
  "stock": 20,
  "precio": 3500
}
```

### Ejemplo: registrar un movimiento

```json
POST /productos/1/movimientos
{
  "tipo": "salida",
  "cantidad": 5
}
```

`tipo` acepta únicamente `"entrada"` o `"salida"`.

## Reglas de negocio y decisiones

- **Stock no negativo:** una salida que dejaría el stock en negativo se rechaza
  con **409 Conflict**. Se eligió 409 porque la petición es válida, pero entra
  en conflicto con el estado actual del recurso (no hay unidades suficientes).
  En ese caso el stock no se modifica.
- **SKU único:** no pueden existir dos productos con el mismo SKU (409).
  El SKU se normaliza (se quitan espacios y se pasa a mayúsculas), por lo que
  `"lch-001"` y `"LCH-001"` se consideran el mismo.
- **Stock bajo:** se considera stock bajo un producto con menos de 10 unidades.
  El límite está definido en la constante `LIMITE_STOCK_BAJO` del servicio.
- **Validaciones de entrada:** el nombre y el SKU son obligatorios, el stock
  no puede ser negativo (por defecto 0), el precio debe ser mayor a 0 y la
  cantidad de un movimiento debe ser mayor a 0. Los datos inválidos responden 422.
- **Errores consistentes:** todas las respuestas de error usan el formato:

  ```json
  { "error": "mensaje descriptivo" }
  ```

  Los errores de validación incluyen además el campo `detalles`.

- **Seguridad:** todas las consultas SQL usan parámetros (`?`) para prevenir
  inyección SQL.

## Estructura del proyecto

```
inventario-api/
├── app/
│   ├── main.py          # Punto de entrada y manejo centralizado de errores
│   ├── controlador.py   # Capa de controlador: endpoints HTTP
│   ├── esquemas.py      # Validación de datos de entrada (Pydantic)
│   ├── servicio.py      # Capa de servicio: reglas de negocio
│   ├── repositorio.py   # Capa de repositorio: acceso a la base de datos
│   └── database.py      # Conexión a SQLite y creación de tablas
├── test/
│   ├── conftest.py      # Base de datos temporal para cada prueba
│   └── test_servicio.py # Pruebas unitarias de las reglas de negocio
├── requirements.txt
└── README.md
```

El controlador recibe las peticiones y las delega al servicio; el servicio
aplica las reglas de negocio y usa el repositorio, que es la única capa que
accede a la base de datos.
