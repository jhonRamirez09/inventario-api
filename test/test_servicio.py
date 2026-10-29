import pytest
from app import servicio
from app.servicio import StockInsuficiente,SkuDuplicado


def test_entrada_aumenta_el_stock():
    producto = servicio.crear_producto("Arroz", "ARZ-001", 10, 3000)
    actualizado = servicio.registrar_movimiento(producto["id"], "entrada", 5)
    assert actualizado["stock"] == 15

def test_salida_que_deja_stock_negativo_se_rechaza():
    producto = servicio.crear_producto("Arroz", "ARZ-001", 10, 3000)

    with pytest.raises(StockInsuficiente):
        servicio.registrar_movimiento(producto["id"], "salida",50)

    despues = servicio.obtener_producto(producto["id"] )
    assert despues["stock"] == 10

def test_sku_duplicado_sin_importar_mayusculas():
    producto = servicio.crear_producto("Arroz", "LCH-001", 10, 3000)

    with pytest.raises(SkuDuplicado):
        servicio.crear_producto("Leche", "lch-001", 10, 3000)
