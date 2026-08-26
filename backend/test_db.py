from app import app, db, Usuario, Estudio, Progreso

def test_crear_usuario():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        nuevo_usuario = Usuario(nombre="Ludmila", telefono="3001234567", password="123")
        db.session.add(nuevo_usuario)
        db.session.commit()
        assert Usuario.query.first().nombre == "Ludmila"

def test_crear_estudio():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        nuevo_estudio = Estudio(titulo="Fraudes en YouTube", descripcion="Identificarlos", puntos_recompensa=10)
        db.session.add(nuevo_estudio)
        db.session.commit()
        assert Estudio.query.first().titulo == "Fraudes en YouTube"

def test_registrar_progreso():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        nuevo_progreso = Progreso(usuario_id=1, estudio_id=1, completado=True)
        db.session.add(nuevo_progreso)
        db.session.commit()
        assert Progreso.query.first().completado == True