from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import crear_tablas
from app.controlador import router
from app.servicio import ProductoNoEncontrado, SkuDuplicado, StockInsuficiente

crear_tablas()

app = FastAPI(title="API de Inventario")
app.include_router(router)


@app.exception_handler(ProductoNoEncontrado)
def manejar_no_encontrado(request: Request, exc: ProductoNoEncontrado):
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(SkuDuplicado)
def manejar_sku_duplicado(request: Request, exc: SkuDuplicado):
    return JSONResponse(status_code=409, content={"error": str(exc)})

@app.exception_handler(StockInsuficiente)
def manejar_stock_insuficiente(request:Request, exc:StockInsuficiente):
    return JSONResponse(status_code=409, content={"error": str(exc)})
