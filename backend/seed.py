from app import app, db, Estudio

def poblar_base_datos():
    with app.app_context():
        db.drop_all()
        db.create_all()

        cursos = [
            Estudio(
                titulo="Modulo 1: Conexiones Seguras y Datos Moviles",
                descripcion="Por que no debes conectarte a redes Wi-Fi gratuitas en parques o cafes. Aprende a usar tus datos moviles como la opcion mas segura fuera de casa.",
                puntos_recompensa=50
            ),
            Estudio(
                titulo="Modulo 2: Uso Seguro de Redes Sociales",
                descripcion="Identifica anuncios engañosos, aprende a rechazar solicitudes de desconocidos y controla que contenido (fotos, viajes) es seguro compartir.",
                puntos_recompensa=70
            ),
            Estudio(
                titulo="Modulo 3: WhatsApp libre de Spam y Estafas",
                descripcion="Descubre como bloquear numeros desconocidos, empresas falsas y como detener la difusion de cadenas o noticias falsas.",
                puntos_recompensa=60
            ),
            Estudio(
                titulo="Modulo 4: Enlaces Peligrosos (Phishing)",
                descripcion="Reconoce mensajes de texto o correos que fingen ser empresas reales (como supermercados o envios) para que no caigas en la trampa.",
                puntos_recompensa=100
            ),
            Estudio(
                titulo="Modulo 5: Llamadas Fraudulentas (Vishing)",
                descripcion="Como actuar ante llamadas urgentes de supuestos familiares o premios falsos. Regla principal: no dar informacion y llamar directo al familiar.",
                puntos_recompensa=100
            ),
            Estudio(
                titulo="Modulo 6: Gestión Inteligente de Contraseñas",
                descripcion="Aprende a usar un gestor de contraseñas y la importancia de tener el correo de un familiar de confianza (hijo/nieto) como respaldo para recuperar tus cuentas.",
                puntos_recompensa=120
            ),
            Estudio(
                titulo="Modulo 7: Descargas Seguras de Aplicaciones",
                descripcion="Evita instalar aplicaciones que prometen limpiar tu celular o regalar cosas. Aprende a usar unicamente la tienda oficial de tu telefono.",
                puntos_recompensa=90
            )
        ]

        db.session.add_all(cursos)
        db.session.commit()
        print("Base de datos poblada exitosamente con el curriculo ajustado y detallado.")

if __name__ == '__main__':
    poblar_base_datos()