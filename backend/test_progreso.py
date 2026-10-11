import pytest
from app import app, db, Usuario, Estudio, Progreso


@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(Estudio(titulo="Modulo 1", descripcion="Prueba", puntos_recompensa=50))
        usuario = Usuario(nombre="Don Jose", telefono="3120000000")
        usuario.set_password("mypassword")
        db.session.add(usuario)
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


@pytest.fixture
def cabeceras(cliente):
    respuesta = cliente.post('/login', json={"telefono": "3120000000", "password": "mypassword"})
    return {"Authorization": f"Bearer {respuesta.get_json()['access_token']}"}


@pytest.mark.parametrize("ruta", ['/progreso', '/api/progreso'])
def test_progreso_exito(cliente, cabeceras, ruta):
    respuesta = cliente.post(ruta, json={"estudio_id": 1}, headers=cabeceras)

    assert respuesta.status_code == 201
    assert Progreso.query.count() == 1


@pytest.mark.parametrize("cuerpo", [{}, {"estudio_id": None}, {"estudio_id": "1"}, {"estudio_id": True}, {"estudio_id": 1.5}])
def test_progreso_estudio_id_invalido(cliente, cabeceras, cuerpo):
    respuesta = cliente.post('/progreso', json=cuerpo, headers=cabeceras)

    assert respuesta.status_code == 400
    assert "mensaje" in respuesta.get_json()
    assert Progreso.query.count() == 0


def test_progreso_estudio_inexistente(cliente, cabeceras):
    respuesta = cliente.post('/progreso', json={"estudio_id": 99}, headers=cabeceras)

    assert respuesta.status_code == 404
    assert "mensaje" in respuesta.get_json()
    assert Progreso.query.count() == 0


def test_progreso_duplicado_no_suma_puntos(cliente, cabeceras):
    cliente.post('/progreso', json={"estudio_id": 1}, headers=cabeceras)
    respuesta = cliente.post('/progreso', json={"estudio_id": 1}, headers=cabeceras)

    assert respuesta.status_code == 200
    assert "ya completado" in respuesta.get_json()["mensaje"]
    assert Progreso.query.count() == 1
    perfil = cliente.get('/perfil', headers=cabeceras)
    assert perfil.get_json()["puntos_totales"] == 50


def test_progreso_sin_token(cliente):
    respuesta = cliente.post('/progreso', json={"estudio_id": 1})

    assert respuesta.status_code == 401
    assert Progreso.query.count() == 0
