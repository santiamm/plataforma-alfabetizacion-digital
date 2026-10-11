# Auditoría del flujo: registro → login → lección → progreso → certificado

Alcance: revisión de lectura (no se modificó código) de `backend/app.py`, `backend/seed.py`, `frontend/js/main.js`, `frontend/leccion.html`, `frontend/ejercicio.html`, `frontend/certificado.html` y `frontend/dashboard.html`.

Escala de gravedad: **alta** (afecta la validez del resultado o la seguridad), **media** (afecta la experiencia o la consistencia), **baja** (mejora menor o documentación).

## 1. Resumen de hallazgos

| ID | Etapa | Hallazgo | Archivo:línea | Gravedad |
|----|-------|----------|---------------|----------|
| H1 | Certificado | La página del certificado no valida nada en el servidor; se abre con cualquier token | `certificado.html:146-177` | Alta |
| H2 | Certificado | La condición de emisión solo se calcula en el frontend | `main.js:178-199` | Alta |
| H3 | Progreso | `POST /progreso` no valida `estudio_id` | `app.py:127-140` | Alta |
| H4 | Progreso | `POST /progreso` permite registros duplicados e infla el puntaje | `app.py:133`, `app.py:157` | Alta |
| H5 | Lección | Las lecciones y ejercicios no coinciden con los módulos de `seed.py` | `leccion.html:103-381`, `ejercicio.html:112-183`, `seed.py:9-43` | Alta |
| H6 | Ejercicio | El frontend no revisa si el progreso se guardó | `ejercicio.html:260-274` | Media |
| H7 | Ejercicio | Una sola pregunta por módulo, sin nota ni límite de intentos | `ejercicio.html:112-183` | Media |
| H8 | Login/Registro | CORS abierto a cualquier origen y clave JWT de respaldo en el código | `app.py:13`, `app.py:15` | Media |
| H9 | Lección | Bloque 7 de `main.js` anidado por error dentro de otro manejador (código duplicado e inalcanzable) | `main.js:346-486` | Media |
| H10 | Accesibilidad | `accesibilidad.js` solo se carga en el panel; las demás páginas no tienen alto contraste ni A+/A- unificados | `dashboard.html:126`, resto de páginas | Media |
| H11 | Registro | El correo se guarda como teléfono si no hay teléfono | `app.py:63-64` | Baja |
| H12 | Login | El cliente envía el mismo valor como `correo` y `telefono` | `main.js:94` | Baja |
| H13 | Certificado | Sin nombre guardado se muestra el id numérico del token | `certificado.html:165` | Baja |
| H14 | Certificado | Texto fijo "7 módulos" y fecha del navegador, sin código verificable | `certificado.html:99`, `certificado.html:175` | Baja |
| H15 | Ejercicio | Falta el cierre `</body></html>` | `ejercicio.html:276` | Baja |
| H16 | Documentación | La documentación del proyecto indica 5 módulos y 5 páginas con accesibilidad; el código tiene 7 módulos | `seed.py:9-43` | Baja |

## 2. Detalle por etapa

### 2.1 Registro
- **Qué hace:** el formulario envía nombre, apellido, correo, teléfono y contraseña a `POST /registro` (`main.js:37-73`). El backend valida campos obligatorios, duplicados de teléfono y de correo, y guarda la contraseña con hash de Werkzeug (`app.py:45-80`).
- **Fallos:**
  - Si no hay teléfono se usa el correo como teléfono (`app.py:63-64`); la columna es de 20 caracteres y es poco coherente con el modelo. *Baja.*
  - No hay validación de formato de correo, teléfono ni longitud mínima de contraseña. *Baja.*

### 2.2 Login
- **Qué hace:** `POST /login` busca por teléfono o correo, verifica el hash y devuelve un JWT con el id como texto (`app.py:86-112`). El cliente guarda `token`, `usuario_nombre` y `usuario_id` en `localStorage` (`main.js:105-113`).
- **Fallos:**
  - CORS con `origins: "*"` y clave JWT de respaldo fija en el código (`app.py:13`, `app.py:15`). Para producción deben restringirse. *Media.*
  - El cliente manda el mismo valor en `correo` y `telefono` (`main.js:94`); funciona, pero es redundante. *Baja.*
  - No hay límite de intentos fallidos. *Baja.*

### 2.3 Lección
- **Qué hace:** el panel pide los módulos a `GET /estudios` (`main.js:152`) y enlaza a `leccion.html?id=N`. La lección se pinta desde un diccionario escrito en la propia página (`leccion.html:103-381`).
- **Fallos:**
  - **Contenido desalineado (H5, alta):** `seed.py` define 7 módulos de seguridad digital (Wi-Fi y datos móviles, redes sociales, WhatsApp, phishing, vishing, contraseñas, descargas). Las lecciones y ejercicios tratan otros temas (ratón y teclado, navegación, claves, trámites, WhatsApp, banca móvil, descargas). Solo el módulo 7 coincide. El título que ve el usuario en el panel no corresponde con lo que aprende al abrir la lección.
  - **Código duplicado (H9, media):** en `main.js:346-486` el bloque "7. Carga dinámica de contenido" quedó dentro del `forEach` del bloque 6, por llaves mal cerradas. Nunca se ejecuta de forma útil y repite lo que ya hace `leccion.html`. Ninguna página que carga `main.js` incluye esos elementos.
  - **Accesibilidad (H10, media):** `accesibilidad.js` solo se carga en `dashboard.html:126`. Lección, ejercicio y certificado traen su propio A+/A- (solo en la lección) y no ofrecen alto contraste.
  - Un `id` fuera de rango en la URL muestra el módulo 1 sin aviso. *Baja.*

### 2.4 Ejercicio y progreso
- **Qué hace:** `ejercicio.html` muestra una pregunta de opción múltiple por módulo (`ejercicio.html:112-183`). Al acertar, bloquea las opciones, muestra la retroalimentación y llama a `POST /progreso` con `estudio_id` (`ejercicio.html:219-274`). El backend guarda un registro `Progreso` con `completado=True` (`app.py:127-140`).
- **Fallos:**
  - **Sin validar `estudio_id` (H3, alta):** el backend toma `datos.get('estudio_id')` sin comprobar que exista, sea entero y pertenezca a un módulo real. Un valor nulo produce error 500 (columna `NOT NULL`); un valor inexistente (por ejemplo 99) se guarda, porque SQLite no aplica claves foráneas por defecto.
  - **Duplicados (H4, alta):** cada llamada crea una fila nueva (`app.py:133`). `/perfil` suma los puntos de todas las filas (`app.py:157`), por lo que repetir un módulo, o llamar al endpoint varias veces, suma puntos sin límite. El panel oculta el problema con `new Set()` (`main.js:166`), pero el puntaje queda mal.
  - **Sin confirmación (H6, media):** `registrarProgresoBackend` no revisa `res.ok` ni informa si falla (`ejercicio.html:260-274`). Sin token o con error del servidor, el usuario ve "correcto" y no queda guardado nada.
  - **Evaluación mínima (H7, media):** una sola pregunta por módulo, reintentos ilimitados, sin nota ni registro de intentos.
  - Falta el cierre `</body></html>` (H15, baja).

### 2.5 Certificado
- **Qué hace:** el panel muestra el banner de certificado cuando el porcentaje llega al 100 % (`main.js:191-199`). `certificado.html` toma el nombre de `localStorage` y la fecha del navegador, y permite imprimir o guardar en PDF.
- **Condición de emisión actual:** cantidad de `estudio_id` distintos devueltos por `GET /progreso` dividida entre la cantidad de módulos de `GET /estudios`, calculada en el navegador (`main.js:178-181`).
- **Fallos:**
  - **Sin validación del servidor (H1, alta):** `certificado.html` solo comprueba que exista un token en `localStorage` (`certificado.html:147-151`). Cualquiera con sesión puede abrir la URL directamente y obtener el certificado sin haber terminado. No existe endpoint de certificado en el backend.
  - **Condición manipulable (H2, alta):** como `POST /progreso` acepta cualquier `estudio_id` (H3), se pueden registrar ids falsos que cuentan como completados. Además, el cálculo usa el total de módulos devuelto por el servidor, pero cuenta ids sin verificar que correspondan a ellos.
  - Nombre de respaldo: usa `payload.sub`, que es el id numérico (H13, baja).
  - Texto fijo "7 módulos", fecha tomada del navegador y sin código de verificación (H14, baja).

## 3. Evaluaciones, simulaciones y retroalimentación

| Elemento | Estado | Evidencia |
|----------|--------|-----------|
| Evaluaciones | **Parcial.** Una pregunta de opción múltiple por módulo; sin nota, sin evaluación final y sin registro de intentos. | `ejercicio.html:112-183` |
| Simulaciones | **No existen.** No hay escenarios simulados (mensaje fraudulento, llamada sospechosa, pantalla de WhatsApp, etc.). | — |
| Retroalimentación | **Existe.** Mensaje inmediato por acierto y por error, con explicación y colores/íconos. | `ejercicio.html:219-256` |

## 4. Recomendaciones (propuestas, sin implementar)

1. Validar en el backend: `estudio_id` entero y existente en `Estudio`, y evitar duplicados por usuario y módulo (consulta previa o restricción única en la tabla).
2. Crear un endpoint protegido que decida la emisión del certificado en el servidor (todos los módulos completados por el usuario) y que `certificado.html` lo consulte antes de mostrar nada.
3. Alinear el contenido de lecciones y ejercicios con los módulos de `seed.py` (o al revés) y decidir cuál es la fuente del currículo.
4. Mostrar al usuario un aviso cuando falle el guardado del progreso.
5. Corregir el anidamiento del bloque 7 en `main.js` y cargar `accesibilidad.js` en todas las páginas.
6. Antes de producción: restringir CORS, exigir `JWT_SECRET_KEY` en el entorno y evaluar límite de intentos de login.
7. Ampliar evaluaciones (más preguntas, nota mínima) y definir si se incluirán simulaciones.

Cada punto cambia comportamiento o arquitectura, por lo que se presentan como opciones para decidir antes de implementar.
