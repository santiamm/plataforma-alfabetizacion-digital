import pytest
from app import app, db, Usuario, Estudio, Pregunta, Progreso, Intento


@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(Estudio(titulo="Modulo 1", descripcion="Prueba", puntos_recompensa=50))
        db.session.add(Pregunta(
            estudio_id=1, leccion=1, pregunta=1, opcion_correcta="A",
            explicacion_correcta="Bien hecho.", pista="Piensa de nuevo.",
            explicaciones_incorrectas={"B": "B no sirve."}
        ))
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


def _acierto(estudio_id=1, correcta=True):
    db.session.add(Intento(usuario_id=1, estudio_id=estudio_id, leccion=1, pregunta=1, opcion="A", correcta=correcta))
    db.session.commit()


@pytest.mark.parametrize("ruta", ['/progreso', '/api/progreso'])
def test_progreso_exito(cliente, cabeceras, ruta):
    _acierto()
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


def test_progreso_sin_intentos_da_403(cliente, cabeceras):
    respuesta = cliente.post('/progreso', json={"estudio_id": 1}, headers=cabeceras)

    assert respuesta.status_code == 403
    assert "responder correctamente" in respuesta.get_json()["mensaje"]
    assert Progreso.query.count() == 0


def test_progreso_con_solo_intento_fallido_da_403(cliente, cabeceras):
    _acierto(correcta=False)
    respuesta = cliente.post('/progreso', json={"estudio_id": 1}, headers=cabeceras)

    assert respuesta.status_code == 403
    assert Progreso.query.count() == 0


def test_progreso_acertando_por_la_api(cliente, cabeceras):
    acierto = cliente.post('/intentos', json={"estudio_id": 1, "leccion": 1, "pregunta": 1, "opcion": "A"}, headers=cabeceras)
    respuesta = cliente.post('/progreso', json={"estudio_id": 1}, headers=cabeceras)

    assert acierto.get_json()["correcta"] is True
    assert respuesta.status_code == 201
    assert Progreso.query.count() == 1


def test_progreso_duplicado_no_suma_puntos(cliente, cabeceras):
    _acierto()
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
