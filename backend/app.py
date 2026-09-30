import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Reemplaza la línea: CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'clave_respaldo_uts_2026')
db = SQLAlchemy(app)
jwt = JWTManager(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=True)
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

# RUTA REGISTRO (soporta /registro y /api/registro)
@app.route('/registro', methods=['POST'])
@app.route('/api/registro', methods=['POST'])
def registro():
    datos = request.get_json() or {}
    
    # Soporta nombre + apellido o nombre completo
    nombre_raw = datos.get('nombre', '').strip()
    apellido_raw = datos.get('apellido', '').strip()
    nombre_completo = f"{nombre_raw} {apellido_raw}".strip() if apellido_raw else nombre_raw
    
    telefono = datos.get('telefono', '').strip()
    correo = datos.get('correo', '').strip()
    password = datos.get('password', '').strip()

    if not nombre_completo or not password:
        return jsonify({"mensaje": "Nombre y contraseña son obligatorios."}), 400

    # Si no ingresó teléfono pero sí correo, usamos el correo como identificador
    if not telefono:
        telefono = correo

    if not telefono:
        return jsonify({"mensaje": "Debes ingresar al menos un teléfono o un correo."}), 400

    if Usuario.query.filter_by(telefono=telefono).first():
        return jsonify({"mensaje": "El teléfono o usuario ya está registrado."}), 400

    if correo and Usuario.query.filter_by(correo=correo).first():
        return jsonify({"mensaje": "El correo ya está registrado."}), 400

    nuevo_usuario = Usuario(nombre=nombre_completo, telefono=telefono, correo=correo if correo else None)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario registrado con éxito"}), 201

# RUTA LOGIN (soporta /login y /api/login)
@app.route('/login', methods=['POST'])
@app.route('/api/login', methods=['POST'])
def login():
    datos = request.get_json() or {}
    identificador = (datos.get('correo') or datos.get('telefono') or datos.get('identificador') or '').strip()
    password = datos.get('password', '').strip()

    if not identificador or not password:
        return jsonify({"mensaje": "Ingresa tu correo o teléfono y tu contraseña."}), 400

    # Busca coincidencia por correo o por teléfono
    usuario = Usuario.query.filter(
        (Usuario.telefono == identificador) | (Usuario.correo == identificador)
    ).first()

    if usuario and usuario.check_password(password):
        token_acceso = create_access_token(identity=str(usuario.id))
        return jsonify({
            "mensaje": "Login exitoso",
            "access_token": token_acceso,
            "nombre": usuario.nombre,
            "id_usuario": usuario.id,
            "telefono": usuario.telefono,
            "correo": usuario.correo
        }), 200

    return jsonify({"mensaje": "Correo, teléfono o contraseña incorrectos."}), 401

@app.route('/estudios', methods=['GET'])
@app.route('/api/estudios', methods=['GET'])
def obtener_estudios():
    estudios = Estudio.query.all()
    return jsonify([
        {
            "id": e.id,
            "titulo": e.titulo,
            "descripcion": e.descripcion,
            "puntos_recompensa": e.puntos_recompensa
        } for e in estudios
    ]), 200

@app.route('/progreso', methods=['POST'])
@app.route('/api/progreso', methods=['POST'])
@jwt_required()
def registrar_progreso():
    usuario_id_actual = get_jwt_identity()
    datos = request.get_json() or {}
    nuevo = Progreso(
        usuario_id=int(usuario_id_actual),
        estudio_id=datos.get('estudio_id'),
        completado=True
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"mensaje": "Progreso guardado correctamente"}), 201

@app.route('/progreso', methods=['GET'])
@app.route('/api/progreso', methods=['GET'])
@jwt_required()
def obtener_progreso():
    usuario_id_actual = get_jwt_identity()
    progresos = Progreso.query.filter_by(usuario_id=int(usuario_id_actual)).all()
    return jsonify([{"id": p.id, "estudio_id": p.estudio_id, "completado": p.completado} for p in progresos]), 200

@app.route('/perfil', methods=['GET'])
@app.route('/api/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil():
    usuario_id_actual = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id_actual))
    progresos = Progreso.query.filter_by(usuario_id=usuario.id, completado=True).all()
    puntos = sum((Estudio.query.get(p.estudio_id).puntos_recompensa for p in progresos if Estudio.query.get(p.estudio_id)), 0)

    return jsonify({
        "nombre": usuario.nombre,
        "telefono": usuario.telefono,
        "correo": usuario.correo,
        "puntos_totales": puntos
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)