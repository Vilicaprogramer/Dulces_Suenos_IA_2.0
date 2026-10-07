// ==============================================================================
// PROYECTO DE DESARROLLO DE APLICACIONES WEB (DAW)
// PROYECTO: Dulces Sueños AI 2.0
// ARCHIVO: static/js/main.js (Lógica Frontend en JavaScript Vanilla)
// ==============================================================================

// Esperamos a que todo el árbol DOM esté completamente cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Generamos el fondo dinámico de estrellas parpadeantes
    crear_cielo_de_estrellas_animadas();

    // 2. Controlamos el temporizador para ocultar la pantalla de bienvenida (Splash Screen)
    controlar_pantalla_de_bienvenida();

    // 3. Activamos la funcionalidad de los botones píldora para seleccionar personajes rápidos
    iniciar_selector_de_personajes_rapidos();

    // 4. Conectamos el evento submit del formulario para generar cuentos mediante Fetch API
    iniciar_formulario_creador_de_cuentos();

    // 5. Configuramos los eventos globales para las ventanas modales (tecla Escape y clic fuera)
    configurar_eventos_globales_modales();

});


// ==============================================================================
// 1. FUNCIÓN PARA GENERAR ESTRELLAS PARPADEANTES DINÁMICAMENTE
// ==============================================================================
function crear_cielo_de_estrellas_animadas() {
    // Obtenemos el elemento contenedor que ocupa el fondo fijo de la pantalla
    const contenedor_estrellas = document.getElementById("fondo-estrellas-fijo");
    
    // Si el contenedor no existe en el HTML, salimos de la función para evitar errores
    if (!contenedor_estrellas) {
        return;
    }

    // Definimos la cantidad de estrellas que queremos crear en el cielo
    const total_estrellas_a_crear = 85;

    // Mediante un bucle for tradicional, creamos cada una de las estrellas
    for (let indice = 0; indice < total_estrellas_a_crear; indice++) {
        const elemento_estrella = document.createElement("div");
        elemento_estrella.classList.add("estrella-brillante");

        // Calculamos posiciones horizontales y verticales aleatorias en porcentaje (0% a 100%)
        const posicion_horizontal_x = Math.random() * 100;
        const posicion_vertical_y = Math.random() * 100;

        // Calculamos un tamaño aleatorio entre 1 píxel y 4 píxeles
        const tamano_estrella = Math.random() * 3 + 1;

        // Calculamos la duración y el retardo de la animación para que no parpadeen a la vez
        const duracion_animacion = Math.random() * 3 + 1.5; // Entre 1.5 y 4.5 segundos
        const retardo_animacion = Math.random() * 3;        // Hasta 3 segundos de desfase

        // Aplicamos los estilos calculados directamente a la estrella
        elemento_estrella.style.left = posicion_horizontal_x + "%";
        elemento_estrella.style.top = posicion_vertical_y + "%";
        elemento_estrella.style.width = tamano_estrella + "px";
        elemento_estrella.style.height = tamano_estrella + "px";
        elemento_estrella.style.setProperty("--duracion", duracion_animacion + "s");
        elemento_estrella.style.animationDelay = retardo_animacion + "s";

        // Insertamos la nueva estrella dentro del contenedor del fondo
        contenedor_estrellas.appendChild(elemento_estrella);
    }
}


// ==============================================================================
// 2. FUNCIÓN PARA LA PANTALLA DE BIENVENIDA (SPLASH SCREEN)
// ==============================================================================
function controlar_pantalla_de_bienvenida() {
    const pantalla_bienvenida = document.getElementById("pantalla-bienvenida");
    
    // Si el elemento existe, programamos su desvanecimiento suave tras la animación inicial
    if (pantalla_bienvenida) {
        // Esperamos 3.8 segundos para que la estrella 3D termine su vuelo
        setTimeout(function () {
            // Iniciamos la transición de opacidad a 0
            pantalla_bienvenida.style.opacity = "0";
            
            // Tras 1.2 segundos adicionales (duración de la transición CSS), lo ocultamos por completo
            setTimeout(function () {
                pantalla_bienvenida.style.visibility = "hidden";
            }, 1200);
        }, 3800);
    }
}


// ==============================================================================
// 3. FUNCIONES PARA EL CONTROL DE VENTANAS MODALES
// ==============================================================================

// Función global que abre una ventana modal dado su identificador ID
function abrir_ventana_modal(identificador_modal) {
    const ventana_modal = document.getElementById(identificador_modal);
    if (ventana_modal) {
        ventana_modal.style.display = "flex";
    }
}

// Función global que oculta una ventana modal dado su identificador ID
function cerrar_ventana_modal(identificador_modal) {
    const ventana_modal = document.getElementById(identificador_modal);
    if (ventana_modal) {
        ventana_modal.style.display = "none";
    }
}

// Configura los eventos para cerrar modales al hacer clic fuera o pulsar la tecla Escape
function configurar_eventos_globales_modales() {
    // Si el usuario hace clic sobre el fondo oscuro de la modal (fuera del recuadro blanco)
    window.addEventListener("click", function (evento) {
        if (evento.target.classList.contains("modal-fondo")) {
            evento.target.style.display = "none";
        }
    });

    // Si el usuario pulsa la tecla Escape (ESC) en el teclado
    window.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            const todas_las_modales = document.querySelectorAll(".modal-fondo");
            todas_las_modales.forEach(function (modal_individual) {
                modal_individual.style.display = "none";
            });
        }
    });
}


// ==============================================================================
// 4. CONTROL DEL SELECTOR DE PERSONAJES RÁPIDOS (BOTONES PÍLDORA)
// ==============================================================================
function iniciar_selector_de_personajes_rapidos() {
    const botones_de_personajes = document.querySelectorAll(".btn-personaje");
    const campo_nombre_personaje = document.getElementById("nombre_personaje");

    // Verificamos que existan tanto los botones como el input antes de continuar
    if (botones_de_personajes.length === 0 || !campo_nombre_personaje) {
        return;
    }

    // Añadimos el evento clic a cada botón píldora
    botones_de_personajes.forEach(function (boton_individual) {
        boton_individual.addEventListener("click", function () {
            // Obtenemos el nombre asignado al personaje desde el atributo data-personaje
            let nombre_personaje_seleccionado = boton_individual.getAttribute("data-personaje");
            if (!nombre_personaje_seleccionado) {
                nombre_personaje_seleccionado = boton_individual.textContent.trim();
            }

            // Asignamos el nombre al campo de texto del formulario
            campo_nombre_personaje.value = nombre_personaje_seleccionado;

            // Retiramos la clase 'activo' de todos los botones para que solo uno brille
            botones_de_personajes.forEach(function (boton_a_limpiar) {
                boton_a_limpiar.classList.remove("activo");
            });

            // Añadimos la clase 'activo' al botón en el que acabamos de hacer clic
            boton_individual.classList.add("activo");
        });
    });

    // Si el usuario decide escribir manualmente en el input, actualizamos el botón activo
    campo_nombre_personaje.addEventListener("input", function () {
        const texto_escrito_por_usuario = campo_nombre_personaje.value.trim().toLowerCase();

        botones_de_personajes.forEach(function (boton_individual) {
            let nombre_del_boton = boton_individual.getAttribute("data-personaje");
            if (!nombre_del_boton) {
                nombre_del_boton = boton_individual.textContent;
            }
            nombre_del_boton = nombre_del_boton.trim().toLowerCase();

            // Si coincide exactamente, lo marcamos como activo; de lo contrario, lo desmarcamos
            if (texto_escrito_por_usuario === nombre_del_boton) {
                boton_individual.classList.add("activo");
            } else {
                boton_individual.classList.remove("activo");
            }
        });
    });
}


// ==============================================================================
// 5. GENERACIÓN ASÍNCRONA DE CUENTOS CON FETCH API
// ==============================================================================
function iniciar_formulario_creador_de_cuentos() {
    const formulario_creador = document.querySelector(".formulario-creador");
    if (!formulario_creador) {
        return;
    }

    const boton_enviar_formulario = formulario_creador.querySelector("button[type='submit']");

    formulario_creador.addEventListener("submit", async function (evento_submit) {
        // 1. Prevenimos el comportamiento por defecto del formulario para que no recargue la página
        evento_submit.preventDefault();

        // 2. Guardamos el texto original del botón y mostramos un estado de carga al usuario
        let texto_original_del_boton = "";
        if (boton_enviar_formulario) {
            texto_original_del_boton = boton_enviar_formulario.innerHTML;
            boton_enviar_formulario.innerHTML = "✨ Las estrellas están escribiendo tu historia... ✨";
            boton_enviar_formulario.disabled = true;
        }

        // 3. Obtenemos los valores de los campos del formulario con valores por defecto seguros
        const campo_tema = document.getElementById("tema_cuento");
        const campo_personaje = document.getElementById("nombre_personaje");
        const campo_tono = document.getElementById("tono_cuento");

        let valor_tema = "una aventura mágica";
        if (campo_tema && campo_tema.value.trim() !== "") {
            valor_tema = campo_tema.value.trim();
        }

        let valor_personaje = "un amiguito";
        if (campo_personaje && campo_personaje.value.trim() !== "") {
            valor_personaje = campo_personaje.value.trim();
        }

        let valor_tono = "dulce";
        if (campo_tono && campo_tono.value !== "") {
            valor_tono = campo_tono.value;
        }

        // 4. Estructuramos el objeto JavaScript con los datos a enviar en formato JSON
        const paquete_datos_a_enviar = {
            tema_cuento: valor_tema,
            nombre_personaje: valor_personaje,
            tono_cuento: valor_tono
        };

        try {
            // 5. Realizamos la petición HTTP POST asíncrona hacia el backend de Flask
            const respuesta_del_servidor = await fetch("/generar-cuento", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(paquete_datos_a_enviar)
            });

            // Convertimos la respuesta recibida en un objeto JSON
            const datos_json_recibidos = await respuesta_del_servidor.json();

            // Si el servidor respondió con un código 200 (OK)
            if (respuesta_del_servidor.ok) {
                alert("¡Cuento generado con éxito!\n\n" + datos_json_recibidos.titulo + "\n\n" + datos_json_recibidos.cuento);
            } else {
                // Si el servidor devolvió un error (ej. límite de cuentos alcanzado)
                alert("Aviso del servidor: " + datos_json_recibidos.message);
            }

        } catch (error_de_red) {
            // Si hubo un problema de conexión con el servidor
            alert("Hubo un problema de conexión al comunicar con el servidor.");
        } finally {
            // 6. Restauramos el botón a su estado original tanto si hubo éxito como si hubo error
            if (boton_enviar_formulario) {
                boton_enviar_formulario.innerHTML = texto_original_del_boton;
                boton_enviar_formulario.disabled = false;
            }
        }
    });
}