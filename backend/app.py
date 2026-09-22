from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

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
        return jsonify({"mensaje": "Login exitoso"}), 200
        
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

if __name__ == '__main__':
    app.run(debug=True)