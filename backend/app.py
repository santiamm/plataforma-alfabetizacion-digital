from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    # Inicialmente permitimos que esté vacío en memoria, pero la DB exigirá valor
    password = db.Column(db.String(255), nullable=False, default="") 

    def set_password(self, password_texto_plano):
        # Esta es la función clave: toma el texto y guarda el hash
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

if __name__ == '__main__':
    app.run(debug=True)