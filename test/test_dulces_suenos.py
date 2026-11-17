import os
import sys
import unittest
from datetime import timedelta
from unittest.mock import patch, MagicMock

# Añadimos la carpeta raíz del proyecto al path para poder importar app.py sin errores
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

# Configuramos variables de entorno de prueba ANTES de importar app.py
# Así nos aseguramos de que NUNCA se conecte a Neon ni toque el .db real
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'clave_secreta_solo_para_tests_unitarios'
os.environ['GEMINI_API_KEY'] = 'clave_falsa_de_prueba_gemini'

from app import app, db, TipoCuenta, Usuario, Cuento
from werkzeug.security import check_password_hash


class PruebasDulcesSuenosAI(unittest.TestCase):
    """
    Batería de pruebas unitarias y de integración basada en la Matriz RFTP (Punto 5.6).
    Utiliza una base de datos SQLite temporal en memoria RAM (:memory:) para que
    ninguna inserción o borrado afecte a los datos reales de desarrollo o producción.
    """

    def setUp(self):
        """
        Este método se ejecuta automáticamente ANTES de cada test individual.
        Prepara una aplicación limpia y una base de datos vacía en memoria.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False

        # Creamos un cliente de pruebas para simular peticiones HTTP (GET y POST)
        self.cliente = app.test_client()

        # Creamos el contexto de aplicación y reiniciamos las tablas desde cero en RAM
        self.contexto_app = app.app_context()
        self.contexto_app.push()
        db.session.remove()
        db.drop_all()
        db.create_all()

        # Insertamos los 3 planes básicos necesarios para que funcionen los registros
        plan_free = TipoCuenta(id_tipo=1, nombre_plan='Free', limite_cuentos=5)
        plan_premium = TipoCuenta(id_tipo=2, nombre_plan='Premium', limite_cuentos=20)
        plan_ilimitado = TipoCuenta(id_tipo=3, nombre_plan='Ilimitado', limite_cuentos=-1)
        db.session.add_all([plan_free, plan_premium, plan_ilimitado])
        db.session.commit()

    def tearDown(self):
        """
        Este método se ejecuta automáticamente DESPUÉS de cada test.
        Borra todas las tablas en memoria para que cada prueba sea 100 % independiente.
        """
        db.session.remove()
        db.drop_all()
        self.contexto_app.pop()

    # =========================================================================
    # BLOQUE A: PRUEBAS DE AUTENTICACIÓN, CONTROL DE ACCESOS Y SESIÓN (R01)
    # =========================================================================

    def test_R01F01T01P01_cifrado_contrasena_en_bd(self):
        """R01F01T01P01: Verifica que la contraseña se guarda cifrada con PBKDF2-SHA256 y no en texto plano."""
        self.cliente.post('/registro', data={
            'nombre_usuario': 'Familia García',
            'correo_usuario': 'familia.garcia@ejemplo.es',
            'clave_usuario': 'SuenosSeguros2026!'
        }, follow_redirects=True)

        usuario_bd = Usuario.query.filter_by(correo_electronico='familia.garcia@ejemplo.es').first()
        self.assertIsNotNone(usuario_bd, "El usuario debería haberse guardado en la BD.")
        self.assertNotEqual(usuario_bd.contrasena_encriptada, 'SuenosSeguros2026!')
        self.assertTrue(usuario_bd.contrasena_encriptada.startswith('pbkdf2:sha256:'))
        self.assertTrue(check_password_hash(usuario_bd.contrasena_encriptada, 'SuenosSeguros2026!'))

    def test_R01F01T02P01_registro_usuario_y_saludo_personalizado(self):
        """R01F01T02P01: Comprueba el alta en plan Free, guardado de nombre_completo y saludo en cabecera."""
        respuesta = self.cliente.post('/registro', data={
            'nombre_usuario': 'Laura Martínez',
            'correo_usuario': 'laura@ejemplo.es',
            'clave_usuario': 'ClaveValida2026'
        }, follow_redirects=True)

        self.assertEqual(respuesta.status_code, 200)
        html_respuesta = respuesta.data.decode('utf-8')

        # Verificamos datos en base de datos
        usuario_laura = Usuario.query.filter_by(correo_electronico='laura@ejemplo.es').first()
        self.assertIsNotNone(usuario_laura)
        self.assertEqual(usuario_laura.nombre_completo, 'Laura Martínez')
        self.assertEqual(usuario_laura.id_tipo_cuenta, 1)  # Plan Free por defecto

        # Verificamos que la interfaz saluda por su nombre
        self.assertIn('Hola, Laura Martínez', html_respuesta)

    def test_R01F02T01P01_login_credenciales_validas_e_invalidas(self):
        """R01F02T01P01: Valida rechazo con contraseña errónea y acceso correcto con contraseña válida."""
        # Registramos primero a Laura y cerramos sesión
        self.cliente.post('/registro', data={
            'nombre_usuario': 'Laura Martínez',
            'correo_usuario': 'laura@ejemplo.es',
            'clave_usuario': 'ClaveValida2026'
        })
        self.cliente.get('/logout')

        # (a) Intento con contraseña errónea
        resp_error = self.cliente.post('/login', data={
            'correo_login': 'laura@ejemplo.es',
            'clave_login': 'ClaveFalsa123'
        }, follow_redirects=True)
        html_error = resp_error.data.decode('utf-8')
        self.assertNotIn('Hola, Laura Martínez', html_error)

        # (b) Intento con contraseña correcta
        resp_ok = self.cliente.post('/login', data={
            'correo_login': 'laura@ejemplo.es',
            'clave_login': 'ClaveValida2026'
        }, follow_redirects=True)
        html_ok = resp_ok.data.decode('utf-8')
        self.assertIn('Hola, Laura Martínez', html_ok)

    def test_R01F02T02P01_expiracion_sesion_inactividad_60_minutos(self):
        """R01F02T02P01: Comprueba que PERMANENT_SESSION_LIFETIME está configurado a 60 minutos."""
        self.assertEqual(app.config['PERMANENT_SESSION_LIFETIME'], timedelta(minutes=60))

        # Registramos e iniciamos sesión para activar @app.before_request
        self.cliente.post('/registro', data={
            'nombre_usuario': 'Laura Martínez',
            'correo_usuario': 'laura@ejemplo.es',
            'clave_usuario': 'ClaveValida2026'
        })
        self.cliente.get('/')
        with self.cliente.session_transaction() as sesion_actual:
            self.assertTrue(sesion_actual.permanent)

    # =========================================================================
    # BLOQUE B: PRUEBAS DE IA, SEGURIDAD INFANTIL Y CUOTAS (R02 Y R03)
    # =========================================================================

    @patch('app.requests.post')
    def test_R02F01T01P01_y_T02P01_generacion_cuento_ia_y_estructura(self, mock_post_gemini):
        """R02F01T01P01 / T02P01: Simula respuesta de Gemini 2.5 Flash, valida estructura limpia y guardado."""
        self.cliente.post('/registro', data={
            'nombre_usuario': 'Padre Prueba',
            'correo_usuario': 'padre@ejemplo.es',
            'clave_usuario': 'Password123'
        })

        # Simulamos una respuesta exitosa de la API de Google Gemini (8 párrafos sin Markdown)
        cuento_simulado = (
            "Título: El viaje espacial de Pipo en su bañera\n\n"
            + "\n\n".join([f"Párrafo número {i} de la aventura tranquila de Pipo hacia las estrellas." for i in range(1, 9)])
        )
        respuesta_falsa = MagicMock()
        respuesta_falsa.status_code = 200
        respuesta_falsa.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": cuento_simulado}]}}]
        }
        mock_post_gemini.return_value = respuesta_falsa

        # Enviamos la petición AJAX al endpoint /generar-cuento
        respuesta = self.cliente.post('/generar-cuento', json={
            'nombre_personaje': 'Pipo',
            'tema_cuento': 'Viaje en bañera espacial',
            'tono_cuento': 'Dulce'
        })

        self.assertEqual(respuesta.status_code, 200)
        datos_json = respuesta.get_json()
        self.assertIn('El viaje espacial de Pipo', datos_json['titulo'])
        self.assertNotIn('#', datos_json['cuento'])
        self.assertNotIn('**', datos_json['cuento'])

        # Comprobamos que se ha guardado en la base de datos
        cuento_guardado = Cuento.query.first()
        self.assertIsNotNone(cuento_guardado)
        self.assertTrue(cuento_guardado.visible_biblioteca)

    @patch('app.requests.post')
    def test_R02F02T01P01_bloqueo_contenido_no_apto_guardrail(self, mock_post_gemini):
        """R02F02T01P01 / T02P01: Verifica que CONTENIDO_NO_APTO devuelve HTTP 400 y no guarda nada en BD."""
        self.cliente.post('/registro', data={
            'nombre_usuario': 'Padre Prueba',
            'correo_usuario': 'padre@ejemplo.es',
            'clave_usuario': 'Password123'
        })

        # Simulamos que Gemini activa el protocolo de seguridad infantil
        respuesta_bloqueo = MagicMock()
        respuesta_bloqueo.status_code = 200
        respuesta_bloqueo.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Lo siento, ese tema no es apropiado para un cuento de Dulces Sueños. ¿Por qué no probamos con una historia de magia o animales?"}]}}]
        }
        mock_post_gemini.return_value = respuesta_bloqueo

        respuesta = self.cliente.post('/generar-cuento', json={
            'nombre_personaje': 'Zombi',
            'tema_cuento': 'Guerra espacial con explosiones y monstruos',
            'tono_cuento': 'Aventurero'
        })

        self.assertEqual(respuesta.status_code, 400)
        # Verificamos que CERO cuentos se guardaron en la base de datos
        self.assertEqual(Cuento.query.count(), 0)

    @patch('app.requests.post')
    def test_R03F01T01P01_control_limite_mensual_plan_free(self, mock_post_gemini):
        """R03F01T01P01 / T02P01: Comprueba el bloqueo HTTP 403 al intentar crear el 6.º cuento en plan Free."""
        self.cliente.post('/registro', data={
            'nombre_usuario': 'Usuario Free',
            'correo_usuario': 'free@dulcessuenos.ai',
            'clave_usuario': 'Password123'
        })
        usuario = Usuario.query.filter_by(correo_electronico='free@dulcessuenos.ai').first()

        # Insertamos 5 cuentos creados este mismo mes (mezclando visibles y borrados lógicamente)
        for i in range(1, 6):
            cuento = Cuento(
                id_usuario_dueno=usuario.id_usuario,
                titulo_cuento=f'Cuento {i}',
                texto_cuento='Texto de prueba tranquilo.',
                visible_biblioteca=(i % 2 == 0)
            )
            db.session.add(cuento)
        db.session.commit()

        # Intentamos generar el 6.º cuento
        respuesta = self.cliente.post('/generar-cuento', json={
            'nombre_personaje': 'Luna',
            'tema_cuento': 'El bosque de las luciérnagas',
            'tono_cuento': 'Sueño tranquilo'
        })

        self.assertEqual(respuesta.status_code, 403)
        # Confirmamos que ni siquiera se llamó a la API externa de Gemini
        mock_post_gemini.assert_not_called()

    # =========================================================================
    # BLOQUE C: BIBLIOTECA, PDF, BORRADO LÓGICO Y ACCESIBILIDAD (R04, R05, R06)
    # =========================================================================

    def test_R04_y_R06_estructura_html_lector_3d_y_accesibilidad(self):
        """R04 / R06: Verifica que la plantilla renderiza el lector 3D, controles de teclado y atributos ARIA."""
        respuesta = self.cliente.get('/')
        self.assertEqual(respuesta.status_code, 200)
        html = respuesta.data.decode('utf-8')

        # Comprobamos presencia del visor 3D y controles de paginación
        self.assertIn('id="visor-libro"', html)
        self.assertIn('id="indicador-paginas"', html)
        self.assertIn('aria-label', html)

    def test_R05F01T01P01_descarga_pdf_y_borrado_logico_biblioteca(self):
        """R05F01T01P01 / T02P01: Prueba descarga directa en PDF y borrado lógico (visible_biblioteca=False)."""
        self.cliente.post('/registro', data={
            'nombre_usuario': 'Lectora Prueba',
            'correo_usuario': 'lectora@ejemplo.es',
            'clave_usuario': 'Password123'
        })
        usuario = Usuario.query.filter_by(correo_electronico='lectora@ejemplo.es').first()

        # Creamos un cuento de prueba con tildes y eñes para validar fpdf2
        cuento = Cuento(
            id_usuario_dueno=usuario.id_usuario,
            titulo_cuento='El sueño mágico de Ñoño',
            texto_cuento='Había una vez un niño muy soñador.\n\nY colorín colorado, este cuento se ha acabado.'
        )
        db.session.add(cuento)
        db.session.commit()
        id_cuento = cuento.id_cuento

        # (a) Probamos la descarga en PDF (/descargar-cuento/<id>)
        resp_pdf = self.cliente.get(f'/descargar-cuento/{id_cuento}')
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(resp_pdf.mimetype, 'application/pdf')
        self.assertTrue(resp_pdf.data.startswith(b'%PDF-'))

        # (b) Probamos el borrado lógico (/borrar-cuento/<id>)
        resp_borrar = self.cliente.post(f'/borrar-cuento/{id_cuento}', follow_redirects=True)
        self.assertEqual(resp_borrar.status_code, 200)

        # El libro desaparece de la vista HTML de la estantería...
        html_estanteria = resp_borrar.data.decode('utf-8')
        self.assertNotIn('El sueño mágico de Ñoño', html_estanteria)

        # ...pero sigue existiendo en la base de datos con visible_biblioteca = False
        cuento_en_bd = db.session.get(Cuento, id_cuento)
        self.assertIsNotNone(cuento_en_bd)
        self.assertFalse(cuento_en_bd.visible_biblioteca)


if __name__ == '__main__':
    unittest.main(verbosity=2)