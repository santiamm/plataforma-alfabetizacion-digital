import os
from datetime import date, datetime, timezone
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
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
    __table_args__ = (db.UniqueConstraint('usuario_id', 'estudio_id', name='uq_progreso_usuario_estudio'),)
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    estudio_id = db.Column(db.Integer, db.ForeignKey('estudio.id'), nullable=False)
    completado = db.Column(db.Boolean, default=False)

class Pregunta(db.Model):
    __table_args__ = (db.UniqueConstraint('estudio_id', 'leccion', 'pregunta', name='uq_pregunta_estudio_leccion_pregunta'),)
    id = db.Column(db.Integer, primary_key=True)
    estudio_id = db.Column(db.Integer, db.ForeignKey('estudio.id'), nullable=False)
    leccion = db.Column(db.Integer, nullable=False)
    pregunta = db.Column(db.Integer, nullable=False)
    opcion_correcta = db.Column(db.String(5), nullable=False)
    explicacion_correcta = db.Column(db.Text, nullable=False)
    pista = db.Column(db.Text, nullable=False)
    explicaciones_incorrectas = db.Column(db.JSON, nullable=False)

class Intento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    estudio_id = db.Column(db.Integer, db.ForeignKey('estudio.id'), nullable=False)
    leccion = db.Column(db.Integer, nullable=False)
    pregunta = db.Column(db.Integer, nullable=False)
    opcion = db.Column(db.String(5), nullable=False)
    correcta = db.Column(db.Boolean, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

@app.route('/registro', methods=['POST'])
@app.route('/api/registro', methods=['POST'])
def registro():
    datos = request.get_json() or {}

    nombre_raw = datos.get('nombre', '').strip()
    apellido_raw = datos.get('apellido', '').strip()
    nombre_completo = f"{nombre_raw} {apellido_raw}".strip() if apellido_raw else nombre_raw

    telefono = datos.get('telefono', '').strip()
    correo = datos.get('correo', '').strip()
    password = datos.get('password', '').strip()

    if not nombre_completo or not password:
        return jsonify({"mensaje": "Nombre y contraseña son obligatorios."}), 400

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

@app.route('/', methods=['GET'])
def index():
    return {"status": "API del proyecto funcionando correctamente"}
@app.route('/login', methods=['POST'])
@app.route('/api/login', methods=['POST'])
def login():
    datos = request.get_json() or {}
    identificador = (datos.get('correo') or datos.get('telefono') or datos.get('identificador') or '').strip()
    password = datos.get('password', '').strip()

    if not identificador or not password:
        return jsonify({"mensaje": "Ingresa tu correo o teléfono y tu contraseña."}), 400

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
    datos = request.get_json(silent=True) or {}
    estudio_id = datos.get('estudio_id')

    if not isinstance(estudio_id, int) or isinstance(estudio_id, bool):
        return jsonify({"mensaje": "estudio_id es obligatorio y debe ser un número entero."}), 400

    if not db.session.get(Estudio, estudio_id):
        return jsonify({"mensaje": "El módulo indicado no existe."}), 404

    usuario_id = int(usuario_id_actual)
    ya_completado = Progreso.query.filter_by(usuario_id=usuario_id, estudio_id=estudio_id).first()
    if ya_completado:
        return jsonify({"mensaje": "Módulo ya completado."}), 200

    if not Intento.query.filter_by(usuario_id=usuario_id, estudio_id=estudio_id, correcta=True).first():
        return jsonify({"mensaje": "Primero debes responder correctamente el ejercicio de este módulo."}), 403

    db.session.add(Progreso(usuario_id=usuario_id, estudio_id=estudio_id, completado=True))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"mensaje": "Módulo ya completado."}), 200
    return jsonify({"mensaje": "Progreso guardado correctamente"}), 201

@app.route('/progreso', methods=['GET'])
@app.route('/api/progreso', methods=['GET'])
@jwt_required()
def obtener_progreso():
    usuario_id_actual = get_jwt_identity()
    progresos = Progreso.query.filter_by(usuario_id=int(usuario_id_actual)).all()
    return jsonify([{"id": p.id, "estudio_id": p.estudio_id, "completado": p.completado} for p in progresos]), 200

def _es_entero_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= 1

@app.route('/intentos', methods=['POST'])
@app.route('/api/intentos', methods=['POST'])
@jwt_required()
def registrar_intento():
    datos = request.get_json(silent=True) or {}
    estudio_id = datos.get('estudio_id')
    leccion = datos.get('leccion')
    pregunta = datos.get('pregunta')
    opcion = datos.get('opcion')

    if not all(_es_entero_positivo(v) for v in (estudio_id, leccion, pregunta)):
        return jsonify({"mensaje": "estudio_id, leccion y pregunta son obligatorios y deben ser enteros desde 1."}), 400

    if not isinstance(opcion, str) or not 1 <= len(opcion.strip()) <= 5:
        return jsonify({"mensaje": "opcion es obligatoria y debe ser un texto de 1 a 5 caracteres."}), 400
    opcion = opcion.strip()

    if not db.session.get(Estudio, estudio_id):
        return jsonify({"mensaje": "El módulo indicado no existe."}), 404

    banco = Pregunta.query.filter_by(estudio_id=estudio_id, leccion=leccion, pregunta=pregunta).first()
    if not banco:
        return jsonify({"mensaje": "La pregunta indicada no existe."}), 404

    correcta = opcion == banco.opcion_correcta
    if not correcta and opcion not in banco.explicaciones_incorrectas:
        return jsonify({"mensaje": "Esa opción no existe en esta pregunta."}), 400

    db.session.add(Intento(
        usuario_id=int(get_jwt_identity()), estudio_id=estudio_id, leccion=leccion,
        pregunta=pregunta, opcion=opcion, correcta=correcta
    ))
    db.session.commit()

    if correcta:
        return jsonify({"correcta": True, "explicacion": banco.explicacion_correcta}), 201
    return jsonify({
        "correcta": False,
        "explicacion": banco.explicaciones_incorrectas[opcion],
        "pista": banco.pista
    }), 201

@app.route('/intentos', methods=['GET'])
@app.route('/api/intentos', methods=['GET'])
@jwt_required()
def obtener_intentos():
    consulta = Intento.query.filter_by(usuario_id=int(get_jwt_identity()))
    estudio_id = request.args.get('estudio_id', type=int)
    if estudio_id is not None:
        consulta = consulta.filter_by(estudio_id=estudio_id)
    intentos = consulta.order_by(Intento.id).all()
    return jsonify([
        {
            "id": i.id, "estudio_id": i.estudio_id, "leccion": i.leccion, "pregunta": i.pregunta,
            "opcion": i.opcion, "correcta": i.correcta, "fecha": i.fecha.isoformat()
        } for i in intentos
    ]), 200

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

@app.route('/certificado', methods=['GET'])
@app.route('/api/certificado', methods=['GET'])
@jwt_required()
def obtener_certificado():
    usuario = db.session.get(Usuario, int(get_jwt_identity()))
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    ids_modulos = {e.id for e in Estudio.query.all()}
    if not ids_modulos:
        return jsonify({"mensaje": "Aún no hay módulos disponibles."}), 403

    completados = {
        p.estudio_id for p in Progreso.query.filter_by(usuario_id=usuario.id, completado=True).all()
        if p.estudio_id in ids_modulos
    }
    faltan = len(ids_modulos) - len(completados)
    if faltan > 0:
        return jsonify({"mensaje": f"Te faltan {faltan} módulo(s) para obtener el certificado."}), 403

    return jsonify({
        "nombre": usuario.nombre,
        "fecha_emision": date.today().isoformat()
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)