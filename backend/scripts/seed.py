from app import app, db, Estudio, Pregunta

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

        preguntas = [
            ("A",
             "¡Excelente! El botón izquierdo es el principal y sirve para interactuar, seleccionar y confirmar.",
             "Piensa en el botón que tocas con el dedo índice.",
             {"B": "El botón derecho sirve para ver opciones extra, no para seleccionar.",
              "C": "La barra espaciadora está en el teclado y sirve para separar palabras."}),
            ("B",
             "¡Muy bien! En la barra de búsqueda del navegador puedes escribir palabras clave y presionar ENTER.",
             "Piensa en el programa que usas para entrar a internet y en la barra de arriba donde escribes.",
             {"A": "La papelera guarda lo que borras; no sirve para buscar.",
              "C": "La calculadora sirve para hacer cuentas, no para buscar en internet."}),
            ("B",
             "¡Perfecto! Ningún banco ni entidad confiable te pedirá contraseñas personales. Nunca las compartas.",
             "Pregúntate: ¿un banco de verdad te pediría tu clave por teléfono?",
             {"A": "Dar la contraseña con prisa es justo lo que buscan los estafadores.",
              "C": "Escribir la contraseña en un mensaje también la deja en manos de desconocidos."}),
            ("A",
             "¡Correcto! Tu documento de identidad es la llave para consultar turnos, trámites y citas en portales oficiales.",
             "Piensa en el documento que muestras cuando te piden identificarte.",
             {"B": "El recibo de la luz no demuestra quién eres.",
              "C": "Los trámites son personales; los datos de otra persona no te sirven."}),
            ("B",
             "¡Así es! Mantienes presionado el botón del micrófono verde, hablas tu mensaje y al soltarlo se envía.",
             "Busca el dibujo que se usa para hablar, junto a donde escribes.",
             {"A": "Apagar el celular no envía ningún mensaje.",
              "C": "Tocar la pantalla con dos dedos no graba tu voz."}),
            ("A",
             "¡Exacto! Las redes públicas de la calle no están protegidas y pueden comprometer tu dinero o tus claves.",
             "Piensa en una red que cualquier desconocido puede usar sin clave.",
             {"B": "El internet de tu casa tiene clave y lo usan personas de confianza.",
              "C": "Tus datos móviles son solo tuyos."}),
            ("A",
             "¡Excelente! Las tiendas oficiales verifican que las aplicaciones estén libres de amenazas antes de que las instales.",
             "Busca la tienda que ya viene instalada en tu celular.",
             {"B": "Los enlaces de desconocidos pueden traer programas que dañan tu celular.",
              "C": "Esos avisos son trampas para que instales algo dañino."}),
        ]
        for curso, (correcta, explicacion, pista, incorrectas) in zip(cursos, preguntas):
            db.session.add(Pregunta(
                estudio_id=curso.id, leccion=1, pregunta=1, opcion_correcta=correcta,
                explicacion_correcta=explicacion, pista=pista, explicaciones_incorrectas=incorrectas
            ))
        db.session.commit()
        print("Base de datos poblada exitosamente con el curriculo ajustado y detallado.")

if __name__ == '__main__':
    poblar_base_datos()