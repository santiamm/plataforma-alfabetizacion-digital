import pytest
from app import app, db, Usuario, Estudio, Pregunta, Progreso, Intento


@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(Estudio(titulo="Modulo 1", descripcion="Prueba", puntos_recompensa=50))
        db.session.add(Estudio(titulo="Modulo 2", descripcion="Prueba", puntos_recompensa=50))
        for estudio_id in (1, 2):
            db.session.add(Pregunta(
                estudio_id=estudio_id, leccion=1, pregunta=1, opcion_correcta="A",
                explicacion_correcta="Bien hecho.", pista="Piensa de nuevo.",
                explicaciones_incorrectas={"B": "B no sirve.", "C": "C tampoco."}
            ))
        for nombre, telefono in (("Don Jose", "3120000000"), ("Dona Ana", "3130000000")):
            usuario = Usuario(nombre=nombre, telefono=telefono)
            usuario.set_password("mypassword")
            db.session.add(usuario)
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def _cabeceras(cliente, telefono):
    respuesta = cliente.post('/login', json={"telefono": telefono, "password": "mypassword"})
    return {"Authorization": f"Bearer {respuesta.get_json()['access_token']}"}


@pytest.fixture
def cabeceras(cliente):
    return _cabeceras(cliente, "3120000000")


VALIDO = {"estudio_id": 1, "leccion": 1, "pregunta": 1, "opcion": "B"}


@pytest.mark.parametrize("ruta", ['/intentos', '/api/intentos'])
def test_intento_fallido(cliente, cabeceras, ruta):
    respuesta = cliente.post(ruta, json=VALIDO, headers=cabeceras)

    assert respuesta.status_code == 201
    assert respuesta.get_json() == {"correcta": False, "explicacion": "B no sirve.", "pista": "Piensa de nuevo."}
    intento = Intento.query.one()
    assert (intento.estudio_id, intento.leccion, intento.pregunta) == (1, 1, 1)
    assert intento.opcion == "B"
    assert intento.correcta is False
    assert intento.fecha is not None


def test_intento_acertado_sin_pista(cliente, cabeceras):
    respuesta = cliente.post('/intentos', json={**VALIDO, "opcion": "A"}, headers=cabeceras)

    assert respuesta.status_code == 201
    assert respuesta.get_json() == {"correcta": True, "explicacion": "Bien hecho."}
    assert Intento.query.one().correcta is True


def test_intento_no_se_puede_falsear(cliente, cabeceras):
    respuesta = cliente.post('/intentos', json={**VALIDO, "opcion": "B", "correcta": True}, headers=cabeceras)

    assert respuesta.get_json()["correcta"] is False
    assert Intento.query.one().correcta is False


@pytest.mark.parametrize("opcion", ["A", "B"])
def test_respuesta_nunca_revela_la_opcion_correcta(cliente, cabeceras, opcion):
    respuesta = cliente.post('/intentos', json={**VALIDO, "opcion": opcion}, headers=cabeceras)

    assert "opcion_correcta" not in respuesta.get_json()


@pytest.mark.parametrize("campo,valor", [
    ("estudio_id", None), ("estudio_id", "1"), ("estudio_id", True), ("estudio_id", 0),
    ("leccion", None), ("leccion", 0), ("leccion", 1.5),
    ("pregunta", None), ("pregunta", -1), ("pregunta", "1"),
    ("opcion", None), ("opcion", ""), ("opcion", "   "), ("opcion", "ABCDEF"), ("opcion", 1),
])
def test_intento_datos_invalidos(cliente, cabeceras, campo, valor):
    cuerpo = {**VALIDO, campo: valor}
    respuesta = cliente.post('/intentos', json=cuerpo, headers=cabeceras)

    assert respuesta.status_code == 400
    assert "mensaje" in respuesta.get_json()
    assert Intento.query.count() == 0


def test_intento_sin_cuerpo(cliente, cabeceras):
    respuesta = cliente.post('/intentos', json={}, headers=cabeceras)

    assert respuesta.status_code == 400
    assert Intento.query.count() == 0


def test_intento_opcion_inexistente(cliente, cabeceras):
    respuesta = cliente.post('/intentos', json={**VALIDO, "opcion": "D"}, headers=cabeceras)

    assert respuesta.status_code == 400
    assert "mensaje" in respuesta.get_json()
    assert Intento.query.count() == 0


def test_intento_modulo_inexistente(cliente, cabeceras):
    respuesta = cliente.post('/intentos', json={**VALIDO, "estudio_id": 99}, headers=cabeceras)

    assert respuesta.status_code == 404
    assert "módulo" in respuesta.get_json()["mensaje"]
    assert Intento.query.count() == 0


@pytest.mark.parametrize("campo", ["leccion", "pregunta"])
def test_intento_pregunta_inexistente(cliente, cabeceras, campo):
    respuesta = cliente.post('/intentos', json={**VALIDO, campo: 2}, headers=cabeceras)

    assert respuesta.status_code == 404
    assert "pregunta" in respuesta.get_json()["mensaje"]
    assert Intento.query.count() == 0


def test_intento_sin_token(cliente):
    respuesta = cliente.post('/intentos', json=VALIDO)

    assert respuesta.status_code == 401
    assert Intento.query.count() == 0


def test_listar_intentos_sin_token(cliente):
    assert cliente.get('/intentos').status_code == 401


def test_varios_intentos_misma_pregunta_se_guardan_todos(cliente, cabeceras):
    cliente.post('/intentos', json=VALIDO, headers=cabeceras)
    cliente.post('/intentos', json={**VALIDO, "opcion": "A"}, headers=cabeceras)

    respuesta = cliente.get('/intentos', headers=cabeceras)
    intentos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert [i["correcta"] for i in intentos] == [False, True]
    assert [i["opcion"] for i in intentos] == ["B", "A"]


def test_listar_solo_intentos_propios(cliente, cabeceras):
    cliente.post('/intentos', json=VALIDO, headers=cabeceras)
    otras = _cabeceras(cliente, "3130000000")
    cliente.post('/intentos', json={**VALIDO, "opcion": "C"}, headers=otras)

    propios = cliente.get('/api/intentos', headers=cabeceras).get_json()

    assert len(propios) == 1
    assert propios[0]["opcion"] == "B"


def test_listar_filtra_por_modulo(cliente, cabeceras):
    cliente.post('/intentos', json=VALIDO, headers=cabeceras)
    cliente.post('/intentos', json={**VALIDO, "estudio_id": 2}, headers=cabeceras)

    filtrados = cliente.get('/intentos?estudio_id=2', headers=cabeceras).get_json()

    assert len(filtrados) == 1
    assert filtrados[0]["estudio_id"] == 2


def test_intento_no_crea_progreso_ni_puntos(cliente, cabeceras):
    cliente.post('/intentos', json={**VALIDO, "opcion": "A"}, headers=cabeceras)

    assert Progreso.query.count() == 0
    assert cliente.get('/perfil', headers=cabeceras).get_json()["puntos_totales"] == 0
