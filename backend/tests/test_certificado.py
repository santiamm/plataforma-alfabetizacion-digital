from datetime import date

import pytest
from app import app, db, Estudio, Progreso, Intento


def _completar(cliente, cabeceras, estudio_id):
    db.session.add(Intento(usuario_id=1, estudio_id=estudio_id, leccion=1, pregunta=1, opcion="A", correcta=True))
    db.session.commit()
    cliente.post('/progreso', json={"estudio_id": estudio_id}, headers=cabeceras)


@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(Estudio(titulo="Modulo 1", descripcion="Prueba", puntos_recompensa=10))
        db.session.add(Estudio(titulo="Modulo 2", descripcion="Prueba", puntos_recompensa=10))
        db.session.commit()

        cliente = app.test_client()
        cliente.post('/registro', json={
            "nombre": "Jose",
            "apellido": "Perez Gomez",
            "telefono": "3120000000",
            "password": "mypassword"
        })

        yield cliente

        db.session.remove()
        db.drop_all()


@pytest.fixture
def cabeceras(cliente):
    respuesta = cliente.post('/login', json={"telefono": "3120000000", "password": "mypassword"})
    return {"Authorization": f"Bearer {respuesta.get_json()['access_token']}"}


def test_certificado_sin_token(cliente):
    respuesta = cliente.get('/certificado')

    assert respuesta.status_code == 401


def test_certificado_sin_modulos_completados(cliente, cabeceras):
    respuesta = cliente.get('/certificado', headers=cabeceras)

    assert respuesta.status_code == 403
    assert "2 módulo" in respuesta.get_json()["mensaje"]
    assert respuesta.get_json()["faltan"] == 2


def test_certificado_base_sin_modulos(cliente, cabeceras):
    Estudio.query.delete()
    db.session.commit()

    respuesta = cliente.get('/certificado', headers=cabeceras)

    assert respuesta.status_code == 403
    assert "mensaje" in respuesta.get_json()


def test_certificado_incompleto(cliente, cabeceras):
    _completar(cliente, cabeceras, 1)

    respuesta = cliente.get('/certificado', headers=cabeceras)

    assert respuesta.status_code == 403
    assert "1 módulo" in respuesta.get_json()["mensaje"]
    assert respuesta.get_json()["faltan"] == 1


@pytest.mark.parametrize("ruta", ['/certificado', '/api/certificado'])
def test_certificado_completo(cliente, cabeceras, ruta):
    _completar(cliente, cabeceras, 1)
    _completar(cliente, cabeceras, 2)
    assert Progreso.query.count() == 2

    respuesta = cliente.get(ruta, headers=cabeceras)

    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["nombre"] == "Jose Perez Gomez"
    assert datos["fecha_emision"] == date.today().isoformat()
    assert datos["total_modulos"] == 2
