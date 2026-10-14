import sys
from app import app, db, Usuario, Estudio, Progreso, Intento, Pregunta

USUARIOS = [
    {
        "clave": "nuevo",
        "nombre": "Usuario Nuevo",
        "correo": "nuevo@prueba.com",
        "telefono": "3000000001",
        "password": "Prueba2026*",
        "completo": False,
    },
    {
        "clave": "completo",
        "nombre": "Usuario Completo",
        "correo": "completo@prueba.com",
        "telefono": "3000000002",
        "password": "Prueba2026*",
        "completo": True,
    },
]


def asegurar_usuario(datos):
    usuario = Usuario.query.filter_by(correo=datos["correo"]).first()
    if not usuario:
        usuario = Usuario.query.filter_by(telefono=datos["telefono"]).first()
    if not usuario:
        usuario = Usuario(correo=datos["correo"], telefono=datos["telefono"], nombre=datos["nombre"])
        usuario.set_password(datos["password"])
        db.session.add(usuario)
        db.session.flush()
        return usuario
    usuario.nombre = datos["nombre"]
    usuario.correo = datos["correo"]
    usuario.telefono = datos["telefono"]
    if not usuario.check_password(datos["password"]):
        usuario.set_password(datos["password"])
    return usuario


def dejar_sin_progreso(usuario):
    Progreso.query.filter_by(usuario_id=usuario.id).delete()
    Intento.query.filter_by(usuario_id=usuario.id).delete()


def dejar_completo(usuario, estudios):
    for estudio in estudios:
        banco = Pregunta.query.filter_by(estudio_id=estudio.id, leccion=1, pregunta=1).first()
        if not banco:
            continue
        acierto = Intento.query.filter_by(
            usuario_id=usuario.id, estudio_id=estudio.id, correcta=True
        ).first()
        if not acierto:
            db.session.add(Intento(
                usuario_id=usuario.id, estudio_id=estudio.id, leccion=1, pregunta=1,
                opcion=banco.opcion_correcta, correcta=True
            ))
        progreso = Progreso.query.filter_by(usuario_id=usuario.id, estudio_id=estudio.id).first()
        if not progreso:
            db.session.add(Progreso(usuario_id=usuario.id, estudio_id=estudio.id, completado=True))
        elif not progreso.completado:
            progreso.completado = True


def preparar_usuarios():
    with app.app_context():
        estudios = Estudio.query.order_by(Estudio.id).all()
        if not estudios:
            print("La base no tiene módulos. Corre primero: python seed.py")
            return 1

        for datos in USUARIOS:
            usuario = asegurar_usuario(datos)
            if datos["completo"]:
                dejar_completo(usuario, estudios)
            else:
                dejar_sin_progreso(usuario)
        db.session.commit()

        print("Usuarios de prueba listos:")
        for datos in USUARIOS:
            usuario = Usuario.query.filter_by(correo=datos["correo"]).first()
            completados = Progreso.query.filter_by(usuario_id=usuario.id, completado=True).count()
            print(
                f"- {datos['clave']}: correo {datos['correo']} | teléfono {datos['telefono']} | "
                f"contraseña {datos['password']} | módulos completados {completados}/{len(estudios)}"
            )
        return 0


if __name__ == '__main__':
    sys.exit(preparar_usuarios())
