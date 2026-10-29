import pytest
from app import database


@pytest.fixture(autouse=True) #autouse=True → “corre esto antes de todas las pruebas, sin que te lo pidan”
def base_de_datos_de_prueba(tmp_path, monkeypatch):  #tmp_path → pytest te presta una carpeta temporal que se borra sola al terminar.
    monkeypatch.setattr(database, "DB_NAME", str(tmp_path / "prueba.db")) #monkeypatch es una base temporal para que no utilice la verdadera
    database.crear_tablas()