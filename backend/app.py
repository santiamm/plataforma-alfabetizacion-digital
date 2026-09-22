from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['JWT_SECRET_KEY'] = 'clave_secreta_super_segura_123'
db = SQLAlchemy(app)
jwt = JWTManager(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False, default="")

    def set_password(self, password_texto_plano):
        self.password = generate_password_hash(password_texto_plano)

    def check_password(self, password_texto_plano):
        return check_password_hash(self.password, password_texto_plano)

class Estudio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    puntos_recompensa = db.Column(db.Integer, nullable=False)

class Progreso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    estudio_id = db.Column(db.Integer, db.ForeignKey('estudio.id'), nullable=False)
    completado = db.Column(db.Boolean, default=False)

@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    
    usuario_existente = Usuario.query.filter_by(telefono=datos['telefono']).first()
    if usuario_existente:
        return jsonify({"error": "El telefono ya esta registrado"}), 400

    nuevo_usuario = Usuario(nombre=datos['nombre'], telefono=datos['telefono'])
    nuevo_usuario.set_password(datos['password'])
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado con exito"}), 201

@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    usuario = Usuario.query.filter_by(telefono=datos['telefono']).first()
    
    if usuario and usuario.check_password(datos['password']):
        token_acceso = create_access_token(identity=str(usuario.id))
        return jsonify({"mensaje": "Login exitoso", "access_token": token_acceso}), 200
        
    return jsonify({"error": "Credenciales invalidas"}), 401

@app.route('/estudios', methods=['GET'])
def obtener_estudios():
    estudios = Estudio.query.all()
    lista_estudios = []
    
    for estudio in estudios:
        lista_estudios.append({
            "id": estudio.id,
            "titulo": estudio.titulo,
            "descripcion": estudio.descripcion,
            "puntos_recompensa": estudio.puntos_recompensa
        })
        
    return jsonify(lista_estudios), 200


@app.route('/progreso', methods=['POST'])
@jwt_required()
def registrar_progreso():
    usuario_id_actual = get_jwt_identity()
    datos = request.get_json()
    
    nuevo_progreso = Progreso(
        usuario_id=int(usuario_id_actual),
        estudio_id=datos['estudio_id'],
        completado=True
    )
    
    db.session.add(nuevo_progreso)
    db.session.commit()
    
    return jsonify({"mensaje": "Progreso registrado con exito"}), 201


@app.route('/progreso', methods=['GET'])
@jwt_required()
def obtener_progreso():
    usuario_id_actual = get_jwt_identity()
    progresos = Progreso.query.filter_by(usuario_id=int(usuario_id_actual)).all()
    
    lista_progreso = []
    for p in progresos:
        lista_progreso.append({
            "id": p.id,
            "estudio_id": p.estudio_id,
            "completado": p.completado
        })
        
    return jsonify(lista_progreso), 200


@app.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil():
    usuario_id_actual = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id_actual))
    
    progresos = Progreso.query.filter_by(usuario_id=usuario.id, completado=True).all()
    puntos_totales = 0
    
    for p in progresos:
        estudio = Estudio.query.get(p.estudio_id)
        if estudio:
            puntos_totales += estudio.puntos_recompensa
            
    return jsonify({
        "nombre": usuario.nombre,
        "telefono": usuario.telefono,
        "puntos_totales": puntos_totales
    }), 200


if __name__ == '__main__':
    app.run(debug=True)