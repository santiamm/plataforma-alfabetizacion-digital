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