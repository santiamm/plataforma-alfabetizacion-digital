from app import app, db, Usuario

def test_crear_usuario():
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        #usuario prueba
        nuevo_usuario = Usuario(nombre="Ludmila", telefono="3001234567", password="123")
        db.session.add(nuevo_usuario)
        db.session.commit()

        #verificar guardado
        usuario_guardado = Usuario.query.first()
        assert usuario_guardado.nombre == "Ludmila"