from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)

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