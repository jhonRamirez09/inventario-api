from fastapi import FastAPI
from app.database import crear_tablas


crear_tablas()
app = FastAPI()



@app.get("/")
def inicio():
    return {"mensaje": "API de inventario funcionando"}