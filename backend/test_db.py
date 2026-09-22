from app import app, db, Usuario, Estudio, Progreso
from werkzeug.security import generate_password_hash

def test_crear_usuario():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        nuevo_usuario = Usuario(nombre="Carmen", telefono="3001234567")
        nuevo_usuario.set_password("123")
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        usuario_guardado = Usuario.query.first()
        assert usuario_guardado.nombre == "Carmen"
        assert usuario_guardado.password != "123"
        assert usuario_guardado.check_password("123") == True

def test_crear_estudio():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        nuevo_estudio = Estudio(titulo="Fraudes en YouTube", descripcion="Identificarlos", puntos_recompensa=10)
        db.session.add(nuevo_estudio)
        db.session.commit()
        
        assert Estudio.query.first().titulo == "Fraudes en YouTube"

def test_registrar_progreso():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        nuevo_progreso = Progreso(usuario_id=1, estudio_id=1, completado=True)
        db.session.add(nuevo_progreso)
        db.session.commit()
        
        assert Progreso.query.first().completado == True

def test_registro_usuario():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    cliente = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()

        respuesta = cliente.post('/registro', json={
            "nombre": "Don Jose",
            "telefono": "3120000000",
            "password": "mypassword"
        })
        
        assert respuesta.status_code == 201
        assert b"Usuario registrado con exito" in respuesta.data

def test_registro_usuario_duplicado():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    cliente = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()

        cliente.post('/registro', json={
            "nombre": "Don Jose",
            "telefono": "3120000000",
            "password": "123"
        })
        
        respuesta_duplicada = cliente.post('/registro', json={
            "nombre": "Dona Maria",
            "telefono": "3120000000",
            "password": "456"
        })
        
        assert respuesta_duplicada.status_code == 400
        assert b"El telefono ya esta registrado" in respuesta_duplicada.data


def test_login_usuario():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    cliente = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()
        
        nuevo_usuario = Usuario(nombre="Don Jose", telefono="3120000000")
        nuevo_usuario.set_password("mypassword")
        db.session.add(nuevo_usuario)
        db.session.commit()

        respuesta_correcta = cliente.post('/login', json={
            "telefono": "3120000000",
            "password": "mypassword"
        })
        
        assert respuesta_correcta.status_code == 200
        datos = respuesta_correcta.get_json()
        assert "access_token" in datos



def test_obtener_estudios():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    cliente = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()
        
        nuevo_estudio = Estudio(titulo="Modulo 1", descripcion="Prueba", puntos_recompensa=10)
        db.session.add(nuevo_estudio)
        db.session.commit()

        respuesta = cliente.get('/estudios')
        
        assert respuesta.status_code == 200
        assert b"Modulo 1" in respuesta.data


def test_registrar_progreso_con_token():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    cliente = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()
        
        nuevo_estudio = Estudio(titulo="Modulo 1", descripcion="Prueba", puntos_recompensa=10)
        db.session.add(nuevo_estudio)
        
        nuevo_usuario = Usuario(nombre="Don Jose", telefono="3120000000")
        nuevo_usuario.set_password("mypassword")
        db.session.add(nuevo_usuario)
        db.session.commit()

        respuesta_login = cliente.post('/login', json={
            "telefono": "3120000000",
            "password": "mypassword"
        })
        token = respuesta_login.get_json()["access_token"]

        respuesta_progreso = cliente.post('/progreso', 
            json={"estudio_id": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert respuesta_progreso.status_code == 201
        assert b"Progreso registrado" in respuesta_progreso.data
        

def test_obtener_progreso_con_token():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    cliente = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()
        
        nuevo_estudio = Estudio(titulo="Modulo 1", descripcion="Prueba", puntos_recompensa=10)
        db.session.add(nuevo_estudio)
        
        nuevo_usuario = Usuario(nombre="Don Jose", telefono="3120000000")
        nuevo_usuario.set_password("mypassword")
        db.session.add(nuevo_usuario)
        db.session.commit()

        respuesta_login = cliente.post('/login', json={
            "telefono": "3120000000",
            "password": "mypassword"
        })
        token = respuesta_login.get_json()["access_token"]

        cliente.post('/progreso', 
            json={"estudio_id": 1},
            headers={"Authorization": f"Bearer {token}"}
        )

        respuesta_obtener = cliente.get('/progreso', headers={"Authorization": f"Bearer {token}"})
        
        assert respuesta_obtener.status_code == 200
        assert b"estudio_id" in respuesta_obtener.data