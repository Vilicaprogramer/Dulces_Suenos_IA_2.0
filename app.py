# ==============================================================================
# PROYECTO DE DESARROLLO DE APLICACIONES WEB (DAW)
# PROYECTO: Dulces Sueños AI 2.0 - Generador de Cuentos Infantiles con IA
# ARCHIVO: app.py (Servidor Backend en Python con Flask y SQLAlchemy)
# ==============================================================================

# Importamos las librerías necesarias del sistema y de Python
import os
import io
import re
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from fpdf import FPDF

# Importamos los componentes del framework Flask
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file

# Importamos el ORM SQLAlchemy para interactuar con la base de datos
from flask_sqlalchemy import SQLAlchemy

# Importamos las herramientas de gestión de sesiones de usuario
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Importamos las funciones de seguridad para encriptar contraseñas
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------------------------------------------------------------------
# 1. CARGA DE CONFIGURACIÓN Y VARIABLES DE ENTORNO
# ------------------------------------------------------------------------------

# Cargamos las variables privadas definidas en el archivo .env (claves de API, etc.)
load_dotenv()

# Inicializamos la aplicación principal de Flask
app = Flask(__name__)

# Clave secreta para firmar las cookies de sesión y mensajes flash
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_secreta_provisoria_dulces_suenos_2026')

# Establecemos el tiempo máximo de inactividad de la sesión (30 minutos)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Conexión a la base de datos (SQLite en local o PostgreSQL en Neon si existe DATABASE_URL)
url_base_datos = os.getenv('DATABASE_URL')
if not url_base_datos:
    url_base_datos = 'sqlite:///base_datos_dulces_suenos.db'
elif url_base_datos.startswith('postgres://'):
    url_base_datos = url_base_datos.replace('postgres://', 'postgresql+psycopg://', 1)
elif url_base_datos.startswith('postgresql://'):
    url_base_datos = url_base_datos.replace('postgresql://', 'postgresql+psycopg://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = url_base_datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Evita errores de conexión cerrada cuando Neon entra en reposo
if url_base_datos.startswith('postgresql'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
# Recuperamos la clave secreta de la API de Google Gemini desde las variables de entorno
CLAVE_API_GEMINI = os.getenv('GEMINI_API_KEY')

# Inicializamos el objeto SQLAlchemy vinculado a nuestra app
db = SQLAlchemy(app)

# Configuramos el gestor de sesiones de Flask-Login
gestor_login = LoginManager(app)
# Si un usuario intenta acceder a una ruta protegida sin iniciar sesión, se le redirige a la página principal
gestor_login.login_view = 'pagina_inicio'


# ==============================================================================
# 2. DEFINICIÓN DE MODELOS DE BASE DE DATOS (TABLAS SQL CON ORM)
# ==============================================================================

class TipoCuenta(db.Model):
    """
    Tabla 'tipos_cuenta': Representa los planes de suscripción disponibles.
    Planes: Free (5 cuentos), Premium (20 cuentos), Ilimitado (-1 cuentos).
    """
    __tablename__ = 'tipos_cuenta'
    
    id_tipo = db.Column(db.Integer, primary_key=True)
    nombre_plan = db.Column(db.String(50), nullable=False)
    limite_cuentos = db.Column(db.Integer, nullable=False)


class Usuario(UserMixin, db.Model):
    """
    Tabla 'usuarios': Almacena las cuentas de los usuarios registrados.
    Hereda de UserMixin para que Flask-Login gestione el estado de autenticación.
    """
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    correo_electronico = db.Column(db.String(120), unique=True, nullable=False)
    contrasena_encriptada = db.Column(db.String(255), nullable=True)
    # Columna 'nombre_completo' para guardar el nombre o apodo del usuario
    nombre_completo = db.Column(db.String(100), nullable=True)
    id_google = db.Column(db.String(255), unique=True, nullable=True)
    
    # Clave foránea que relaciona al usuario con un plan de suscripción
    id_tipo_cuenta = db.Column(db.Integer, db.ForeignKey('tipos_cuenta.id_tipo'), default=1)
    
    # Relaciones ORM para navegar entre tablas fácilmente
    plan_suscripcion = db.relationship('TipoCuenta', backref='usuarios_inscritos')
    mis_cuentos = db.relationship('Cuento', backref='creador_cuento', lazy=True)

    # Método obligatorio de Flask-Login para obtener el identificador único del usuario
    def get_id(self):
        return str(self.id_usuario)


class Cuento(db.Model):
    """
    Tabla 'cuentos': Guarda los cuentos generados por cada usuario con la IA.
    """
    __tablename__ = 'cuentos'
    
    id_cuento = db.Column(db.Integer, primary_key=True)
    id_usuario_dueno = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    titulo_cuento = db.Column(db.String(200), nullable=False)
    texto_cuento = db.Column(db.Text, nullable=False)
    nombre_personaje = db.Column(db.String(100))
    grupo_edad = db.Column(db.String(50))
    valor_moral = db.Column(db.String(100))
    tematica = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    # Campo booleano para borrado lógico (True = visible en la estantería del usuario)
    visible_biblioteca = db.Column(db.Boolean, default=True, nullable=False)


# Función que utiliza Flask-Login para recargar el objeto de usuario desde la sesión
@gestor_login.user_loader
def cargar_usuario_por_id(id_del_usuario):
    # Usamos db.session.get() para cumplir con el estándar moderno de SQLAlchemy
    return db.session.get(Usuario, int(id_del_usuario))


# ==============================================================================
# 3. CONTROLADORES Y RUTAS DE LA APLICACIÓN WEB
# ==============================================================================

# Interceptor: Se ejecuta ANTES de cualquier ruta para reiniciar el reloj de inactividad
@app.before_request
def actualizar_tiempo_sesion():
    if current_user.is_authenticated:
        # Marcamos la sesión como permanente para que respete el PERMANENT_SESSION_LIFETIME
        session.permanent = True
        # Indicamos que la sesión ha sido modificada, lo que reinicia el contador a 60 minutos
        session.modified = True
        
# Ruta 1: Página principal (Landing pública o Panel de creación si el usuario ya inició sesión)
@app.route('/')
def pagina_inicio():
    lista_de_cuentos_del_usuario = []
    
    # Comprobamos si el usuario actual ha iniciado sesión
    if current_user.is_authenticated:
        # Obtenemos SOLO sus cuentos visibles en la biblioteca ordenados por fecha de creación descendente
        lista_de_cuentos_del_usuario = Cuento.query.filter_by(
            id_usuario_dueno=current_user.id_usuario,
            visible_biblioteca=True
        ).order_by(Cuento.fecha_creacion.desc()).all()
    
    return render_template('index.html', mis_cuentos=lista_de_cuentos_del_usuario)


# Ruta 2: Proceso de registro de una nueva cuenta
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    # Recogemos los datos enviados desde el formulario HTML de registro
    nombre_introducido = request.form.get('nombre_usuario', '').strip()
    correo_introducido = request.form.get('correo_usuario', '').strip()
    clave_introducida = request.form.get('clave_usuario', '')
    
    # Validamos que el usuario haya escrito su nombre
    if not nombre_introducido:
        flash('Por favor, introduce tu nombre para registrarte.')
        return redirect(url_for('pagina_inicio'))

    # Validamos que se haya introducido un correo electrónico
    if not correo_introducido:
        flash('Por favor, introduce una dirección de correo electrónico válida.')
        return redirect(url_for('pagina_inicio'))

    # Validamos que se haya introducido una contraseña
    if not clave_introducida:
        flash('Por favor, introduce una contraseña para tu cuenta.')
        return redirect(url_for('pagina_inicio'))

    # Comprobamos si ya existe una cuenta con este correo en la base de datos
    usuario_existente = Usuario.query.filter_by(correo_electronico=correo_introducido).first()
    if usuario_existente:
        flash('Este correo electrónico ya está registrado. Por favor, inicia sesión.')
        return redirect(url_for('pagina_inicio'))
        
    # Encriptamos la contraseña utilizando el algoritmo PBKDF2 con SHA-256
    clave_encriptada_segura = generate_password_hash(clave_introducida, method='pbkdf2:sha256')
    
    # Creamos la nueva instancia de usuario con el plan gratuito (ID 1) y su nombre completo asignado
    nuevo_usuario = Usuario(
        correo_electronico=correo_introducido,
        nombre_completo=nombre_introducido,
        contrasena_encriptada=clave_encriptada_segura,
        id_tipo_cuenta=1
    )
    
    # Guardamos el nuevo usuario en la base de datos
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    # Iniciamos sesión automáticamente para mejorar la experiencia del usuario
    login_user(nuevo_usuario)
    flash(f'¡Registro completado con éxito! Bienvenido a Dulces Sueños, {nombre_introducido}.')
    return redirect(url_for('pagina_inicio'))


# Ruta 3: Proceso de inicio de sesión (Login tradicional)
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    # Recogemos las credenciales enviadas desde el formulario HTML de login
    correo_introducido = request.form.get('correo_login')
    clave_introducida = request.form.get('clave_login')
    
    # Buscamos al usuario en la base de datos por su correo
    usuario_encontrado = Usuario.query.filter_by(correo_electronico=correo_introducido).first()
    
    # Verificamos si el usuario existe y si la contraseña coincide con el hash almacenado
    if usuario_encontrado and check_password_hash(usuario_encontrado.contrasena_encriptada, clave_introducida):
        login_user(usuario_encontrado)
        flash('¡Bienvenido de nuevo!')
        return redirect(url_for('pagina_inicio'))
    else:
        flash('Correo electrónico o contraseña incorrectos.')
        return redirect(url_for('pagina_inicio'))


# Ruta 4: Endpoint asíncrono para generar cuentos infantiles llamando a la API de Google Gemini
@app.route('/generar-cuento', methods=['POST'])
@login_required
def generar_cuento():
    # 1. Recuperamos los datos enviados por la petición (en formato JSON desde JavaScript)
    datos_recibidos = request.get_json(silent=True)
    if not datos_recibidos:
        datos_recibidos = request.form
    
    tema_solicitado = datos_recibidos.get('tema_cuento', 'una aventura mágica')
    personaje_solicitado = datos_recibidos.get('nombre_personaje', 'un valiente amiguito')
    tono_solicitado = datos_recibidos.get('tono_cuento', 'dulce')

    # 2. Comprobamos el límite de cuentos permitidos según el plan de suscripción del usuario
    if current_user.plan_suscripcion:
        limite_del_plan = current_user.plan_suscripcion.limite_cuentos
    else:
        limite_del_plan = 5
    
    # Si el límite es distinto de -1 (donde -1 significa ilimitado)
    if limite_del_plan != -1:
        # Calculamos el primer día del mes actual para contar los cuentos generados este mes
        inicio_del_mes_actual = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        cantidad_cuentos_mes = Cuento.query.filter(
            Cuento.id_usuario_dueno == current_user.id_usuario,
            Cuento.fecha_creacion >= inicio_del_mes_actual
        ).count()

        # Si ya alcanzó el límite, devolvemos un código de estado HTTP 403 (Prohibido)
        if cantidad_cuentos_mes >= limite_del_plan:
            mensaje_error_limite = f"Has alcanzado el límite de {limite_del_plan} cuentos este mes. ¡Actualiza tu plan para crear más!"
            return jsonify({
                "status": "error", 
                "message": mensaje_error_limite
            }), 403

    # 3. Construimos el texto del Prompt que le enviaremos al modelo de lenguaje
    frase_rechazo_seguridad = "Lo siento, ese tema no es apropiado para un cuento de Dulces Sueños. ¿Por qué no probamos con una historia de magia o animales?"

    prompt_texto = f"""
    Eres un escritor experto en literatura infantil y cuentacuentos profesional en castellano para la plataforma Dulces Sueños AI.
    Tu misión es redactar una historia maravillosa, cálida, enriquecedora y educativa, ideal para leer antes de dormir a niños de entre 4 y 10 años.

    ================================================================================
    REGLA INQUEBRANTABLE DE SEGURIDAD INFANTIL Y PROTOCOLO DE RECHAZO (CRÍTICO):
    ================================================================================
    Queda TERMINANTEMENTE PROHIBIDO incluir cualquier mención, alusión directa o indirecta, metáfora o insinuación sobre:
    - Sexualidad, erotismo o contenido para adultos.
    - Drogas, estupefacientes, tabaco, alcohol o sustancias ilícitas.
    - Muerte, suicidio, duelo traumático o autolesiones.
    - Violencia física o verbal, agresión, sangre, peleas o armas de cualquier tipo.
    - Acoso, intimidación, crueldad o comportamientos destructivos.
    - Terror, monstruos aterradores, pesadillas, gore o situaciones de pánico o miedo extremo.

    Si el tema solicitado ("{tema_solicitado}") o el nombre del personaje ("{personaje_solicitado}") contiene o insinúa CUALQUIERA de estos temas prohibidos, NO ESCRIBAS NINGÚN CUENTO, NO PIDAS DISCULPAS ADICIONALES Y NO AGREGUES TÍTULO NI EXPLICACIONES. Responde ÚNICA Y EXCLUSIVAMENTE con esta frase exacta:
    "{frase_rechazo_seguridad}"

    ================================================================================
    DIRECTRICES DE LONGITUD Y ESTRUCTURA (CUENTO LARGO Y DETALLADO):
    ================================================================================
    Si los parámetros son completamente seguros, debes generar un cuento extenso, inmersivo y pausado:
    1. TIEMPO DE LECTURA: Diseñado para una lectura en voz alta pausada de 8 a 10 minutos.
    2. EXTENSIÓN: Debe tener OBLIGATORIAMAMENTE entre 8 y 10 párrafos amplios y muy desarrollados.
    3. DETALLE Y RIQUEZA DESCRIPTIVA: No hagas resúmenes rápidos ni historias cortas. Describe con detalle inmersivo los entornos (colores, aromas, sonidos nocturnos, la luz de las estrellas), las emociones de los personajes, sus reflexiones y su interacción con el entorno.
    4. DIÁLOGOS VIVOS: Incluye diálogos tiernos y entretenidos entre los personajes que aporten dinamismo y aprendizaje a la narración.
    5. FINAL RELAJANTE: Concluye la historia de forma dulce, sosegada y reconfortante, invitando suavemente al niño al descanso y al sueño reparador.

    ================================================================================
    PARÁMETROS DEL CUENTO:
    ================================================================================
    - Protagonista: {personaje_solicitado}
    - Tema central: {tema_solicitado}
    - Tono o estilo: {tono_solicitado}

    ================================================================================
    FORMATO ESTRICTO DE RESPUESTA:
    ================================================================================
    - Línea 1 (obligatoria): Debe comenzar exactamente con "Título: [Nombre creativo y mágico del cuento]".
    - Salto de línea.
    - A partir de la línea 2: El cuerpo del cuento estructurado en al menos 8 a 10 párrafos claramente separados entre sí.
    """

    # 4. Preparamos los datos y la URL para la petición HTTP POST a la API REST de Gemini
    url_api_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={CLAVE_API_GEMINI}"
    cuerpo_peticion_api = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_texto}
                ]
            }
        ]
    }

    try:
        # Mostramos en la consola del servidor el estado de la clave antes de hacer la petición
        if CLAVE_API_GEMINI:
            print("INFO: Iniciando llamada a la API de Gemini con clave configurada.")
        else:
            print("ADVERTENCIA: No se encontró la variable GEMINI_API_KEY en el entorno.")
        
        # Realizamos la petición HTTP a los servidores de Google
        respuesta_servidor = requests.post(url_api_gemini, json=cuerpo_peticion_api, timeout=60)
        datos_json_respuesta = respuesta_servidor.json()
        
        # Verificamos si Google respondió con un código de error
        if respuesta_servidor.status_code != 200:
            mensaje_detalle_error = datos_json_respuesta.get('error', {}).get('message', 'Error desconocido')
            return jsonify({
                "status": "error", 
                "message": f"Error en el servicio de IA: {mensaje_detalle_error}"
            }), 500

        # Extraemos el texto generado por el modelo
        texto_generado_por_ia = datos_json_respuesta['candidates'][0]['content']['parts'][0]['text'].strip()

        # Comprobamos si la IA activó el protocolo de rechazo por seguridad infantil
        if "no es apropiado para un cuento de Dulces Sueños" in texto_generado_por_ia or "Lo siento, ese tema no es apropiado" in texto_generado_por_ia:
            return jsonify({
                "status": "error", 
                "message": texto_generado_por_ia
            }), 400

        # Separamos el título del cuento del resto de párrafos
        lineas_del_texto = texto_generado_por_ia.strip().split('\n')
        if len(lineas_del_texto) > 0 and 'Título:' in lineas_del_texto[0]:
            titulo_del_cuento = lineas_del_texto[0].replace('Título:', '').replace('*', '').strip()
            cuerpo_del_cuento = '\n'.join(lineas_del_texto[1:]).strip()
        else:
            titulo_del_cuento = f"El cuento de {personaje_solicitado}"
            cuerpo_del_cuento = texto_generado_por_ia.strip()

    except Exception as error_capturado:
        # Si ocurre un fallo de red o excepción inesperada, lo registramos y avisamos al cliente
        print("ERROR: Ocurrió un error al procesar el cuento:", str(error_capturado))
        return jsonify({
            "status": "error", 
            "message": f"Error interno del servidor: {str(error_capturado)}"
        }), 500
        
    # 5. Guardamos el cuento recién generado en la base de datos
    nuevo_cuento_creado = Cuento(
        id_usuario_dueno=current_user.id_usuario,
        titulo_cuento=titulo_del_cuento,
        texto_cuento=cuerpo_del_cuento,
        nombre_personaje=personaje_solicitado,
        tematica=tema_solicitado,
        valor_moral=tono_solicitado
    )
    
    db.session.add(nuevo_cuento_creado)
    db.session.commit()

    # 6. Devolvemos la respuesta exitosa en formato JSON para que el navegador la pinte
    return jsonify({
        "status": "success",
        "titulo": titulo_del_cuento,
        "cuento": cuerpo_del_cuento
    }), 200


# Ruta 5: Borrado lógico de un cuento perteneciente al usuario logueado
@app.route('/borrar-cuento/<int:id_cuento>', methods=['POST'])
@login_required
def borrar_cuento(id_cuento):
    cuento_a_borrar = Cuento.query.filter_by(
        id_cuento=id_cuento, 
        id_usuario_dueno=current_user.id_usuario
    ).first()
    
    if cuento_a_borrar:
        # En lugar de borrar físicamente el registro (db.session.delete), realizamos un borrado lógico
        # asignando visible_biblioteca = False. De este modo el cuento no aparece en la biblioteca,
        # pero la cuota mensual de cuentos creados se mantiene intacta para evitar abusos.
        cuento_a_borrar.visible_biblioteca = False
        db.session.commit()
        flash('Cuento retirado de tu biblioteca personal.')
        
    return redirect(url_for('pagina_inicio'))


# Función auxiliar para sanear texto antes de pasarlo a FPDF (evita errores con comillas tipográficas o emojis)
def limpiar_texto_para_pdf(texto_original):
    """
    Sustituye comillas curvas, guiones largos y retira emojis para que las fuentes
    estándar de FPDF no lancen error de codificación, respetando tildes y la letra eñe.
    """
    if not texto_original:
        return ""
    reemplazos_caracteres = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...', '«': '"', '»': '"'
    }
    for caracter_origen, caracter_destino in reemplazos_caracteres.items():
        texto_original = texto_original.replace(caracter_origen, caracter_destino)
    # Codificamos a latin-1 ignorando caracteres especiales incompatibles con la fuente
    return texto_original.encode('latin-1', 'ignore').decode('latin-1')


# Ruta 6: Descargar un cuento en formato PDF maquetado para lectura infantil
@app.route('/descargar-cuento/<int:id_cuento>')
@login_required
def descargar_cuento(id_cuento):
    # Buscamos el cuento verificando que pertenezca al usuario actualmente autenticado
    cuento_a_descargar = Cuento.query.filter_by(
        id_cuento=id_cuento,
        id_usuario_dueno=current_user.id_usuario
    ).first()

    # Si no existe o pertenece a otro usuario, redirigimos a la página de inicio
    if not cuento_a_descargar:
        flash('El cuento solicitado no existe o no tienes permiso para descargarlo.')
        return redirect(url_for('pagina_inicio'))

    # Clase personalizada que hereda de FPDF para gestionar encabezado y pie de página
    class CuentoInfantilPDF(FPDF):
        def header(self):
            # Encabezado sutil con el nombre de la plataforma
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(140, 145, 170)
            self.cell(0, 8, 'Dulces Sueños AI - Cuentos Mágicos Infantiles', align='C', new_x='LMARGIN', new_y='NEXT')
            self.ln(4)

        def footer(self):
            # Pie de página situado a 15 mm del borde inferior
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 165)
            texto_pie = f"Página {self.page_no()} | Creado con magia en Dulces Sueños AI"
            self.cell(0, 10, texto_pie, align='C')

    # Inicializamos el documento en formato A4 vertical
    pdf = CuentoInfantilPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Márgenes amplios y cómodos: 22 mm en los laterales y 20 mm arriba y abajo
    pdf.set_margins(left=22, top=20, right=22)
    pdf.add_page()

    # Título del cuento grande, centrado y destacado en color azul marino nocturno
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(24, 28, 64)
    titulo_limpio = limpiar_texto_para_pdf(cuento_a_descargar.titulo_cuento)
    pdf.multi_cell(0, 10, titulo_limpio, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    # Subtítulo con el nombre del protagonista si está disponible
    if cuento_a_descargar.nombre_personaje:
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(180, 130, 40) # Tono dorado cálido
        personaje_limpio = limpiar_texto_para_pdf(cuento_a_descargar.nombre_personaje)
        texto_subtitulo = f"Una aventura mágica protagonizada por {personaje_limpio}"
        pdf.cell(0, 8, texto_subtitulo, align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(4)

    # Línea divisoria decorativa suave en la cabecera
    pdf.set_draw_color(225, 215, 185)
    pdf.set_line_width(0.4)
    x_inicial = 40
    x_final = pdf.w - 40
    y_linea = pdf.get_y()
    pdf.line(x_inicial, y_linea, x_final, y_linea)
    pdf.ln(8)

    # Cuerpo del cuento con tipografía legible de 13 pt e interlineado cómodo (8.5 mm)
    pdf.set_font('Helvetica', '', 13)
    pdf.set_text_color(45, 45, 55) # Tinta oscura para máxima nitidez

    # Dividimos el texto del cuento en párrafos
    parrafos_del_cuento = cuento_a_descargar.texto_cuento.split('\n')
    for parrafo in parrafos_del_cuento:
        parrafo_procesado = limpiar_texto_para_pdf(parrafo.strip())
        if parrafo_procesado:
            # Alineamos de forma justificada y dejamos espacio de 4 mm entre párrafos
            pdf.multi_cell(0, 8.5, parrafo_procesado, align='J', new_x='LMARGIN', new_y='NEXT')
            pdf.ln(4)

    # Guardamos el archivo PDF generado en un buffer de memoria BytesIO
    buffer_memoria_pdf = io.BytesIO()
    pdf.output(buffer_memoria_pdf)
    buffer_memoria_pdf.seek(0)

    # Creamos un nombre de archivo seguro a partir del título del cuento
    nombre_limpio_archivo = re.sub(r'[^\w\s-]', '', cuento_a_descargar.titulo_cuento.lower())
    nombre_limpio_archivo = re.sub(r'[-\s]+', '_', nombre_limpio_archivo).strip('_')
    if not nombre_limpio_archivo:
        nombre_limpio_archivo = 'cuento_dulces_suenos'
    nombre_final_pdf = f"{nombre_limpio_archivo}.pdf"

    # Enviamos el archivo directamente al navegador para su descarga
    return send_file(
        buffer_memoria_pdf,
        as_attachment=True,
        download_name=nombre_final_pdf,
        mimetype='application/pdf'
    )


# Ruta 7: Cierre de la sesión activa
@app.route('/logout')
@login_required
def cerrar_sesion():
    logout_user()
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('pagina_inicio'))


# ==============================================================================
# 4. INICIALIZACIÓN DE LA BASE DE DATOS Y ARRANQUE DEL SERVIDOR
# ==============================================================================

with app.app_context():
    # Creamos las tablas en la base de datos si todavía no existen
    db.create_all()
    
    # Comprobación de seguridad para añadir la columna 'visible_biblioteca' si no existe aún
    # Permite migración automática sin perder cuentos existentes en SQLite o PostgreSQL (Neon)
    try:
        db.session.execute(db.text("ALTER TABLE cuentos ADD COLUMN IF NOT EXISTS visible_biblioteca BOOLEAN DEFAULT TRUE;"))
        db.session.commit()
    except Exception:
        db.session.rollback()
        try:
            # En SQLite estándar donde 'IF NOT EXISTS' no se admita en ADD COLUMN
            db.session.execute(db.text("ALTER TABLE cuentos ADD COLUMN visible_biblioteca BOOLEAN DEFAULT TRUE;"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # Comprobación de seguridad para añadir la columna 'nombre' a la tabla 'usuarios' si no existe aún
    # Permite migración automática sin perder cuentas de usuario existentes en SQLite o PostgreSQL (Neon)
    try:
        db.session.execute(db.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);"))
        db.session.commit()
    except Exception:
        db.session.rollback()
        try:
            # En SQLite estándar donde 'IF NOT EXISTS' no se admita en ADD COLUMN
            db.session.execute(db.text("ALTER TABLE usuarios ADD COLUMN nombre VARCHAR(100);"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # Insertamos los 3 planes de suscripción base si la tabla está vacía
    plan_inicial_existente = db.session.get(TipoCuenta, 1)
    if not plan_inicial_existente:
        plan_free = TipoCuenta(id_tipo=1, nombre_plan='Free', limite_cuentos=5)
        plan_premium = TipoCuenta(id_tipo=2, nombre_plan='Premium', limite_cuentos=20)
        plan_ilimitado = TipoCuenta(id_tipo=3, nombre_plan='Ilimitado', limite_cuentos=-1)
        
        db.session.add_all([plan_free, plan_premium, plan_ilimitado])
        db.session.commit()
        print("INFO: Planes de suscripción creados en la base de datos.")

    # Creamos una cuenta de Administrador por defecto si no existe
    administrador_existente = Usuario.query.filter_by(correo_electronico='admin@dulcessuenos.ai').first()
    if not administrador_existente:
        clave_admin_encriptada = generate_password_hash('DulcesSuenos@I1982', method='pbkdf2:sha256')
        cuenta_administrador = Usuario(
            correo_electronico='admin@dulcessuenos.ai',
            nombre='Administrador',
            nombre_completo='Administrador Root',
            contrasena_encriptada=clave_admin_encriptada,
            id_tipo_cuenta=3
        )
        db.session.add(cuenta_administrador)
        db.session.commit()
        print("INFO: Usuario Administrador creado: admin@dulcessuenos.ai")

if __name__ == '__main__':
    # Arrancamos el servidor de desarrollo de Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
