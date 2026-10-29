# Prueba Técnica – Desarrollador Junior – DISAN

**Candidato:** Jhon Ramírez

Este repositorio contiene la solución completa de la prueba técnica:

| Parte | Componente                     | Ubicación                                                                   |
| ----- | ------------------------------ | --------------------------------------------------------------------------- |
| 1     | Lógica y algoritmos            | [Ver Parte 1](#parte-1-lógica-y-algoritmos)                                 |
| 2     | Bases de datos y SQL           | [Ver Parte 2](#parte-2-bases-de-datos-y-sql)                                |
| 3     | API REST de inventario         | [Ver Parte 3](#parte-3-api-rest-de-inventario) (código en `app/` y `test/`) |
| 4     | Revisión de código             | [Ver Parte 4](#parte-4-revisión-de-código)                                  |
| 5     | Conceptos y preguntas abiertas | [Ver Parte 5](#parte-5-conceptos-y-preguntas-abiertas)                      |

---

## Parte 1: Lógica y algoritmos

### L-1: Dos números cuya suma es igual a `n`

```python
def dos_suma(numeros, n):
    vistos = set()
    for num in numeros:
        falta = n - num
        if falta in vistos:
            return (falta, num)
        vistos.add(num)
    return None
```

**Justificación de la complejidad O(n):** la lista se recorre una sola vez.
En cada paso se calcula cuánto falta para llegar a `n` y se busca ese valor
en un `set`, operación que cuesta O(1). Total: n × O(1) = **O(n)**.
Si se usara una lista para guardar los vistos, cada búsqueda costaría O(n)
y el total sería O(n²).

Ejemplos:

```python
dos_suma([3, 8, 2, 5], 10)   # (8, 2)
dos_suma([1, 2, 3], 100)     # None
```

### L-2: Paréntesis, corchetes y llaves balanceados

```python
def esta_balanceada(cadena):
    pares = {")": "(", "]": "[", "}": "{"}
    pila = []
    for simbolo in cadena:
        if simbolo not in pares:
            pila.append(simbolo)
        else:
            if len(pila) == 0:
                return False
            sacado = pila.pop()
            if sacado != pares[simbolo]:
                return False
    return len(pila) == 0
```

Se usa una **pila**: el último símbolo que se abre debe ser el primero en
cerrarse. Al terminar, la cadena es válida solo si la pila quedó vacía.

**Complejidad O(n):** se recorre la cadena una vez y `append` / `pop` cuestan O(1).

**Supuesto:** la cadena contiene únicamente `( ) [ ] { }`.

```python
esta_balanceada("{[()]}")   # True
esta_balanceada("{[(])}")   # False
esta_balanceada("((")       # False
esta_balanceada(")")        # False
```

### L-3: Top 3 clientes por cantidad

```python
def top_clientes(pedidos):
    libreta = {}
    for pedido in pedidos:
        cliente = pedido["cliente"]
        cantidad = pedido["cantidad"]
        libreta[cliente] = libreta.get(cliente, 0) + cantidad
    ordenados = sorted(libreta.items(), key=lambda x: x[1], reverse=True)
    return ordenados[:3]
```

Se agrupa con un diccionario (cliente → cantidad total) y se ordena con
`sorted`, que es parte de Python (no es una librería externa).

**Complejidad:** O(n) para agrupar los n pedidos + O(k log k) para ordenar
los k clientes distintos.

```python
pedidos = [
    {"cliente": "Ana",  "producto": "Arroz", "cantidad": 5},
    {"cliente": "Luis", "producto": "Leche", "cantidad": 2},
    {"cliente": "Ana",  "producto": "Pan",   "cantidad": 3},
    {"cliente": "Sofi", "producto": "Cafe",  "cantidad": 7},
    {"cliente": "Luis", "producto": "Huevo", "cantidad": 4},
    {"cliente": "Pepe", "producto": "Sal",   "cantidad": 1},
]
top_clientes(pedidos)   # [('Ana', 8), ('Sofi', 7), ('Luis', 6)]
```

---

## Parte 2: Bases de datos y SQL

Esquema de referencia: `Clientes`, `Pedidos`, `DetallePedido`, `Productos`.

### SQL-1: Total vendido por ciudad durante el último mes

```sql
-- Interpreto "último mes" como el mes calendario anterior
-- (si hoy es octubre: del 1 al 30 de septiembre).
-- Si se quisieran los últimos 30 días:
--   WHERE p.fecha >= date('now', '-30 days')
-- Uso Pedidos.total; por eso no uno DetallePedido
-- (duplicaría el total del pedido por cada producto).
-- La columna fecha queda sin funciones para poder usar el índice.

SELECT c.ciudad, SUM(p.total) AS total_vendido
FROM Clientes c
JOIN Pedidos p ON p.cliente_id = c.id
WHERE p.fecha >= date('now', 'start of month', '-1 month')
  AND p.fecha <  date('now', 'start of month')
GROUP BY c.ciudad;
```

### SQL-2: Clientes que no han realizado ningún pedido

```sql
SELECT c.nombre
FROM Clientes c
LEFT JOIN Pedidos p ON p.cliente_id = c.id
WHERE p.id IS NULL;
```

### SQL-3: Top 5 productos más vendidos por categoría

```sql
-- Interpreto "más vendidos" como unidades vendidas.
-- Si se quisiera por ingresos: SUM(cantidad * precio).

WITH ventas AS (
    SELECT pr.id, pr.nombre, pr.categoria,
           SUM(d.cantidad) AS unidades
    FROM Productos pr
    JOIN DetallePedido d ON d.producto_id = pr.id
    GROUP BY pr.id, pr.nombre, pr.categoria
),
ranking AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY categoria
                              ORDER BY unidades DESC) AS puesto
    FROM ventas
)
SELECT categoria, nombre, unidades, puesto
FROM ranking
WHERE puesto <= 5;
```

### SQL-4: Optimización de `YEAR(fecha)`

**Causa:** al aplicar `YEAR()` sobre la columna `fecha`, la base de datos debe
calcular el año de cada fila una por una, aunque exista un índice. El índice
está ordenado por la fecha completa, no por el resultado de `YEAR()`, así que
no se puede usar. Con millones de registros esto produce un escaneo completo
de la tabla.

**Solución:**

1. Crear un índice sobre `fecha`.
2. Reemplazar `YEAR()` por un rango, para que el índice pueda saltar directo
   al inicio de 2026.
3. Seleccionar solo las columnas necesarias en vez de `*`.

```sql
CREATE INDEX idx_pedidos_fecha ON Pedidos(fecha);

SELECT id, cliente_id, fecha, total
FROM Pedidos
WHERE fecha >= '2026-01-01' AND fecha < '2027-01-01';
```

Se usa `< '2027-01-01'` en lugar de `<= '2026-12-31'` para incluir los
registros del 31 de diciembre que tengan hora.

### SQL-5: Conceptos

**INNER JOIN vs LEFT JOIN:** `INNER JOIN` devuelve solo las filas que tienen
coincidencia en ambas tablas. `LEFT JOIN` devuelve todas las filas de la tabla
izquierda; si no tienen coincidencia, las columnas de la tabla derecha quedan
en `NULL`. Ejemplo: un cliente sin pedidos no aparece con `INNER JOIN`, pero
sí con `LEFT JOIN`.

**GROUP BY vs HAVING:** `GROUP BY` agrupa las filas que tienen el mismo valor
en una sola fila por grupo, para aplicar funciones como `SUM` o `COUNT`.
`HAVING` filtra esos grupos después de agrupar. La diferencia con `WHERE` es
que `WHERE` filtra filas antes de agrupar, por eso no puede usar `SUM`;
`HAVING` sí puede.

---

## Parte 3: API REST de inventario

API para la gestión del inventario de productos de una empresa distribuidora.
Permite crear, consultar, actualizar y eliminar productos, registrar entradas
y salidas de stock, y consultar los productos con stock bajo.

### Tecnologías

- Python 3.13
- FastAPI (framework web y validación con Pydantic)
- SQLite (módulo `sqlite3` incluido en Python)
- Pytest (pruebas unitarias)

### Requisitos

- Python 3.10 o superior
- Git

### Instalación

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

### Ejecución

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs

La base de datos `inventario.db` se crea automáticamente al iniciar la aplicación.

### Pruebas

```bash
python -m pytest -v
```

Las pruebas usan una base de datos temporal, por lo que no modifican los datos
de `inventario.db`. Cubren:

- Una entrada aumenta el stock.
- Una salida que dejaría el stock en negativo se rechaza y el stock no cambia.
- No se permiten SKU duplicados, sin importar mayúsculas o minúsculas.

### Endpoints

| Método | Ruta                          | Descripción                            | Respuestas         |
| ------ | ----------------------------- | -------------------------------------- | ------------------ |
| GET    | `/productos`                  | Lista todos los productos              | 200                |
| GET    | `/productos?stockBajo=true`   | Lista productos con stock menor a 10   | 200                |
| GET    | `/productos/{id}`             | Obtiene un producto                    | 200, 404           |
| POST   | `/productos`                  | Crea un producto                       | 201, 409, 422      |
| PUT    | `/productos/{id}`             | Actualiza un producto                  | 200, 404, 409, 422 |
| DELETE | `/productos/{id}`             | Elimina un producto                    | 204, 404           |
| POST   | `/productos/{id}/movimientos` | Registra una entrada o salida de stock | 200, 404, 409, 422 |

**Ejemplo: crear un producto**

```json
POST /productos
{
  "nombre": "Arroz",
  "sku": "ARZ-500G",
  "stock": 20,
  "precio": 3500
}
```

**Ejemplo: registrar un movimiento**

```json
POST /productos/1/movimientos
{
  "tipo": "salida",
  "cantidad": 5
}
```

`tipo` acepta únicamente `"entrada"` o `"salida"`.

### Reglas de negocio y decisiones

- **Stock no negativo:** una salida que dejaría el stock en negativo se rechaza
  con **409 Conflict**. Se eligió 409 porque la petición es válida, pero entra
  en conflicto con el estado actual del recurso (no hay unidades suficientes).
  En ese caso el stock no se modifica.
- **SKU único:** no pueden existir dos productos con el mismo SKU (409).
  El SKU se normaliza (se quitan espacios y se pasa a mayúsculas), por lo que
  `"lch-001"` y `"LCH-001"` se consideran el mismo.
- **Stock bajo:** un producto con menos de 10 unidades. El límite está definido
  en la constante `LIMITE_STOCK_BAJO` del servicio.
- **Validaciones de entrada:** el nombre y el SKU son obligatorios, el stock no
  puede ser negativo (por defecto 0), el precio debe ser mayor a 0 y la cantidad
  de un movimiento debe ser mayor a 0. Los datos inválidos responden 422.
- **Errores consistentes:** todas las respuestas de error usan el formato:

  ```json
  { "error": "mensaje descriptivo" }
  ```

  Los errores de validación incluyen además el campo `detalles`.

- **Seguridad:** todas las consultas SQL usan parámetros (`?`) para prevenir
  inyección SQL.
- **Conexiones seguras:** las operaciones que modifican datos usan
  `try / finally` para cerrar siempre la conexión, incluso si ocurre un error.

### Estructura del proyecto

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

---

## Parte 4: Revisión de código

> **Nota:** no recibí el fragmento de código de esta parte. Para demostrar el
> criterio, elaboré un fragmento de ejemplo con las cinco deficiencias indicadas
> (R-1 a R-5) y lo analicé.

### Fragmento analizado

```python
import sqlite3

def registrar_usuario(conexion, datos):
    nombre = datos["nombre"]
    correo = datos["correo"]
    password = datos["password"]
    conexion.execute(
        "INSERT INTO usuarios (nombre, correo, password) VALUES ('"
        + nombre + "', '" + correo + "', '" + password + "')"
    )
    conexion.commit()


def buscar_usuario(conexion, correo):
    try:
        cursor = conexion.execute(
            "SELECT * FROM usuarios WHERE correo = '" + correo + "'"
        )
        return cursor.fetchone()
    except:
        pass


def correos_repetidos(correos):
    repetidos = []
    for i in range(len(correos)):
        for j in range(len(correos)):
            if i != j and correos[i] == correos[j]:
                if correos[i] not in repetidos:
                    repetidos.append(correos[i])
    return repetidos


def calcular_descuento(conexion, correo):
    usuario = buscar_usuario(conexion, correo)
    return usuario["compras"] * 0.1
```

### Problema 1 (R-1): Inyección SQL

- **Dónde:** `registrar_usuario` y `buscar_usuario`, al armar el SQL.
- **Qué está mal:** el SQL se construye concatenando con `+` los datos que
  escribe el usuario.
- **Por qué es peligroso:** la base de datos no puede distinguir entre la orden
  del programador y el texto del usuario. Si alguien escribe código SQL como
  nombre, por ejemplo `Pepe'); DROP TABLE usuarios; --`, ese código se ejecuta
  y puede leer, modificar o borrar datos.
- **Corrección:** usar consultas parametrizadas, donde los valores van separados
  del SQL y se tratan siempre como datos:

  ```python
  conexion.execute(
      "INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)",
      (nombre, correo, password_hash)
  )
  conexion.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
  ```

### Problema 2 (R-2): Variables usadas sin validación

- **Dónde:** `registrar_usuario` (`datos["nombre"]`, `datos["correo"]`,
  `datos["password"]`) y `calcular_descuento` (`usuario["compras"]`).
- **Qué está mal:** se usan los valores sin revisar que existan o que sean válidos.
- **Por qué es peligroso:**
  - Si a `datos` le falta una llave, el programa falla con `KeyError`.
  - Si llega un correo vacío o mal escrito, se guarda igual y la base de datos
    queda con información inválida.
  - Si `buscar_usuario` no encuentra el correo, devuelve `None`, y
    `usuario["compras"]` falla con `TypeError`.
- **Corrección:**
  - Validar los datos de entrada antes de usarlos, por ejemplo con un modelo de
    Pydantic (campos obligatorios, correo con formato válido, contraseña con
    longitud mínima).
  - En `calcular_descuento`, verificar que el usuario exista:

    ```python
    if usuario is None:
        raise UsuarioNoEncontrado(f"No existe el usuario {correo}")
    ```

### Problema 3 (R-3): Ciclo ineficiente

- **Dónde:** `correos_repetidos`.
- **Qué está mal:** tiene dos `for` anidados que comparan cada correo con todos
  los demás, además de buscar en una lista con `not in`.
- **Por qué es peligroso:** la complejidad es O(n²). Con 1.000 correos son cerca
  de un millón de comparaciones; con millones de registros la función se vuelve
  inutilizable.
- **Corrección:** recorrer la lista una sola vez usando `set`, donde buscar
  cuesta O(1). La complejidad baja a O(n):

  ```python
  def correos_repetidos(correos):
      vistos = set()
      repetidos = set()
      for correo in correos:
          if correo in vistos:
              repetidos.add(correo)
          else:
              vistos.add(correo)
      return list(repetidos)
  ```

### Problema 4 (R-4): Manejo de excepciones vacío

- **Dónde:** `buscar_usuario`, en el bloque `except: pass`.
- **Qué está mal:** el `except` atrapa cualquier error y no hace nada con él.
  El error se oculta y la función devuelve `None` como si todo estuviera bien.
- **Por qué es peligroso:** nadie se entera de que algo falló. El programa termina
  fallando en otro lugar (por ejemplo, en `calcular_descuento`) con un mensaje
  que no tiene relación con la causa real, lo que dificulta mucho encontrar el
  error. Además, un `except` sin tipo atrapa todos los errores, incluso los que
  no se esperaban.
- **Corrección:**
  - Atrapar solo el error esperado: `except sqlite3.Error`.
  - Registrar el error en un log para poder revisarlo.
  - Volver a lanzarlo, o lanzar un error con un mensaje claro, para que quien
    llamó la función sepa que algo falló.

### Problema 5 (R-5): Contraseña almacenada en texto plano

- **Dónde:** `registrar_usuario`, al guardar `password`.
- **Qué está mal:** la contraseña se guarda tal como la escribió el usuario.
- **Por qué es peligroso:** si alguien obtiene acceso a la base de datos, puede
  leer todas las contraseñas. Como muchas personas repiten contraseñas, el
  atacante podría entrar a sus correos, bancos u otros servicios.
- **Corrección:** guardar un hash de la contraseña con un algoritmo seguro como
  bcrypt. El hash no se puede revertir; para iniciar sesión se calcula el hash
  de lo que escribe el usuario y se compara con el guardado:

  ```python
  hash_guardado = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
  bcrypt.checkpw(intento.encode(), hash_guardado)
  ```

---

## Parte 5: Conceptos y preguntas abiertas

### C-1: Inyección de dependencias

Es una forma de diseñar el código en la que un componente recibe desde afuera
los objetos que necesita (sus dependencias), en lugar de crearlos él mismo.

Sirve para que el código quede menos acoplado: se puede cambiar una dependencia
(por ejemplo, la base de datos) sin modificar el componente, y facilita las
pruebas, porque se puede entregar una versión falsa o temporal.

**En mi proyecto:** el servicio importa el repositorio directamente, por lo que
está acoplado. Para las pruebas tuve que usar `monkeypatch` y reemplazar la base
de datos real por una temporal. Con inyección de dependencias (por ejemplo,
`Depends` de FastAPI) bastaría con pasarle al servicio un repositorio de prueba.

### C-2: GET, POST, PUT y PATCH

| Método | Uso                                                         | Idempotente | Ejemplo                                     |
| ------ | ----------------------------------------------------------- | ----------- | ------------------------------------------- |
| GET    | Consultar información sin modificarla                       | Sí          | `GET /productos/2`                          |
| POST   | Crear un recurso nuevo                                      | No          | `POST /productos`                           |
| PUT    | Reemplazar un recurso completo (se envían todos los campos) | Sí          | `PUT /productos/2`                          |
| PATCH  | Modificar solo algunos campos                               | Depende     | `PATCH /productos/2` con `{"precio": 5000}` |

Una operación es idempotente si ejecutarla una o varias veces produce el mismo
resultado. **En mi proyecto** uso `POST` para los movimientos de stock, porque
cada envío debe registrar un movimiento nuevo: enviarlo dos veces suma dos veces.

### C-3: Conflictos en Git

Un conflicto ocurre cuando dos ramas modifican las mismas líneas de un mismo
archivo de forma distinta, y Git no puede decidir automáticamente qué versión
conservar. Aparece al combinar cambios con `git merge` o `git pull`.

Git marca el archivo así:

```
<<<<<<< HEAD
(mi versión)
=======
(la otra versión)
>>>>>>> otra-rama
```

**Procedimiento para resolverlo:**

1. Identificar los archivos en conflicto (`git status`).
2. Decidir qué versión queda: la mía, la otra o una combinación de ambas.
3. Borrar las marcas `<<<<<<<`, `=======` y `>>>>>>>`.
4. Probar que el código siga funcionando.
5. `git add <archivo>`
6. `git commit`

**En mi proyecto:** al subirlo a GitHub creé el repositorio vacío, sin README,
para evitar un conflicto con el README que ya tenía en mi computador.

### C-4: Un error complejo que resolví

Al registrar salidas de stock en la API, el sistema guardó un stock de **-87**.
Revisé el servicio y encontré que la validación comparaba el stock **anterior**
en vez del **nuevo stock calculado**, así que una salida mayor al stock pasaba
la validación.

**Proceso de depuración:**

1. Reproduje el error registrando una salida de 100 unidades sobre un producto con 13.
2. Seguí el código línea por línea con esos valores y vi que la condición
   revisaba `producto["stock"]` en lugar de `nuevo_stock`.
3. Corregí la condición para validar `nuevo_stock`.
4. Escribí una prueba unitaria que intenta una salida mayor al stock y verifica
   que se rechace y que el stock no cambie.
5. Comprobé que la prueba falla si vuelvo a introducir el error, y que pasa con
   la corrección.

Durante el desarrollo también detecté que el sistema aceptaba el mismo SKU en
mayúsculas y minúsculas (`"LCH-001"` y `"lch-001"`). Lo resolví normalizando el
SKU en el servicio y agregué una prueba para ese caso.
