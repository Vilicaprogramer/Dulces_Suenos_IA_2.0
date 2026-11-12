// ==============================================================================
// PROYECTO DE DESARROLLO DE APLICACIONES WEB (DAW)
// PROYECTO: Dulces Sueños AI 2.0
// ARCHIVO: static/js/main.js (Lógica Frontend en JavaScript Vanilla)
// ==============================================================================

document.addEventListener("DOMContentLoaded", function () {
    crear_cielo_de_estrellas_animadas();
    controlar_pantalla_de_bienvenida();
    iniciar_selector_de_personajes_rapidos();
    iniciar_formulario_creador_de_cuentos();
    configurar_eventos_globales_modales();
    iniciar_control_responsive_movil();
});

// ==============================================================================
// 1. FONDO DE ESTRELLAS Y SPLASH SCREEN
// ==============================================================================
function crear_cielo_de_estrellas_animadas() {
    const contenedor_estrellas = document.getElementById("fondo-estrellas-fijo");
    if (!contenedor_estrellas) return;

    const total_estrellas_a_crear = 85;
    for (let indice = 0; indice < total_estrellas_a_crear; indice++) {
        const elemento_estrella = document.createElement("div");
        elemento_estrella.classList.add("estrella-brillante");

        const x = Math.random() * 100;
        const y = Math.random() * 100;
        const tam = Math.random() * 3 + 1;
        const duracion = Math.random() * 3 + 1.5;
        const retardo = Math.random() * 3;

        elemento_estrella.style.left = x + "%";
        elemento_estrella.style.top = y + "%";
        elemento_estrella.style.width = tam + "px";
        elemento_estrella.style.height = tam + "px";
        elemento_estrella.style.setProperty("--duracion", duracion + "s");
        elemento_estrella.style.animationDelay = retardo + "s";

        contenedor_estrellas.appendChild(elemento_estrella);
    }
}

function controlar_pantalla_de_bienvenida() {
    const pantalla_bienvenida = document.getElementById("pantalla-bienvenida");
    if (pantalla_bienvenida) {
        setTimeout(function () {
            pantalla_bienvenida.style.opacity = "0";
            setTimeout(function () {
                pantalla_bienvenida.style.visibility = "hidden";
            }, 1200);
        }, 3800);
    }
}

// ==============================================================================
// 2. MODALES Y FORMULARIOS
// ==============================================================================
function abrir_ventana_modal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "flex";
    }
}

function cerrar_ventana_modal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "none";
    }
}

function configurar_eventos_globales_modales() {
    window.addEventListener("click", function (evento) {
        if (evento.target.classList.contains("modal-fondo") && evento.target.id !== "modal-carga") {
            evento.target.style.display = "none";
        }
    });

    window.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            document.querySelectorAll(".modal-fondo").forEach(function (modal) {
                if (modal.id !== "modal-carga") {
                    modal.style.display = "none";
                }
            });
        }
    });
}

function alternarFormularioCreacion() {
    const contenedor = document.getElementById("contenedor-formulario-crear");
    if (contenedor) {
        if (contenedor.style.display === "none" || contenedor.style.display === "") {
            contenedor.style.display = "block";
            contenedor.scrollIntoView({ behavior: 'smooth' });
        } else {
            contenedor.style.display = "none";
        }
    }
}

function iniciar_selector_de_personajes_rapidos() {
    const botones = document.querySelectorAll(".btn-personaje");
    const campo = document.getElementById("nombre_personaje");
    if (botones.length === 0 || !campo) return;

    botones.forEach(function (boton) {
        boton.addEventListener("click", function () {
            let nombre = boton.getAttribute("data-personaje") || boton.textContent.trim();
            campo.value = nombre;
            botones.forEach(b => b.classList.remove("activo"));
            boton.classList.add("activo");
        });
    });
}

// ==============================================================================
// 3. LECTOR DE LIBROS CON PAGINACIÓN INTERACTIVA
// ==============================================================================
let paginasDelCuentoActual = [];
let indicePaginaActual = 0;

function abrirCuentoEnLibro(titulo, texto) {
    const elemento_titulo = document.getElementById("libro-titulo-cuento");
    if (elemento_titulo) {
        elemento_titulo.textContent = titulo;
    }

    const lineas = texto.split("\n");
    let parrafos = [];
    for (let i = 0; i < lineas.length; i++) {
        let p = lineas[i].trim();
        if (p.length > 0) {
            parrafos.push("<p>" + p + "</p>");
        }
    }

    paginasDelCuentoActual = [];
    let parrafosPorPagina = 2;
    for (let i = 0; i < parrafos.length; i += parrafosPorPagina) {
        paginasDelCuentoActual.push(parrafos.slice(i, i + parrafosPorPagina).join(""));
    }

    if (paginasDelCuentoActual.length === 0) {
        paginasDelCuentoActual = ["<p>El cuento está vacío.</p>"];
    }

    indicePaginaActual = 0;
    actualizarVistaPaginaLibro();
    abrir_ventana_modal("visor-libro");
}

/**
 * Paginación interactiva con animación 3D de volteo de hoja (Emil Kowalski).
 * Memoria Técnica Nivel FP DAW:
 * En lugar de alternar instantáneamente el contenido HTML, aplicamos una clase
 * CSS con transformación rotateY() en el eje vertical Z=0. A mitad de la
 * rotación (180ms), cuando el elemento alcanza el punto ciego de ángulo,
 * se actualiza el texto de la página, completando el retorno fluido a 0 grados.
 */
function cambiarPaginaLibro(direccion) {
    let nuevoIndice = indicePaginaActual + direccion;
    if (nuevoIndice >= 0 && nuevoIndice < paginasDelCuentoActual.length) {
        const cuerpo = document.getElementById("libro-cuerpo-cuento");
        if (cuerpo) {
            const claseAnimacion = direccion > 0 ? "efecto-giro-derecha" : "efecto-giro-izquierda";
            cuerpo.classList.remove("efecto-giro-derecha", "efecto-giro-izquierda");
            void cuerpo.offsetWidth; // Forzar reflujo de GPU para reiniciar el ciclo de animación
            cuerpo.classList.add(claseAnimacion);

            // Reemplazo del texto en el cenit del giro
            setTimeout(function () {
                indicePaginaActual = nuevoIndice;
                actualizarVistaPaginaLibro();
            }, 180);

            // Limpieza de clases al terminar la transición
            setTimeout(function () {
                cuerpo.classList.remove("efecto-giro-derecha", "efecto-giro-izquierda");
            }, 380);
        } else {
            indicePaginaActual = nuevoIndice;
            actualizarVistaPaginaLibro();
        }
    }
}

function actualizarVistaPaginaLibro() {
    const cuerpo = document.getElementById("libro-cuerpo-cuento");
    const indicador = document.getElementById("indicador-paginas");

    if (cuerpo && paginasDelCuentoActual.length > 0) {
        cuerpo.innerHTML = paginasDelCuentoActual[indicePaginaActual];
    }

    if (indicador) {
        indicador.textContent = `Página ${indicePaginaActual + 1} de ${paginasDelCuentoActual.length}`;
    }
}

// ==============================================================================
// 4. PETICIÓN ASÍNCRONA PARA GENERAR CUENTOS
// ==============================================================================
function iniciar_formulario_creador_de_cuentos() {
    const formulario = document.querySelector(".formulario-creador");
    if (!formulario) return;

    const boton = formulario.querySelector("button[type='submit']");

    formulario.addEventListener("submit", async function (e) {
        e.preventDefault();

        let textoOriginal = "";
        if (boton) {
            textoOriginal = boton.innerHTML;
            boton.innerHTML = "✨ Las estrellas están escribiendo tu historia... ✨";
            boton.disabled = true;
        }

        const tema = document.getElementById("tema_cuento")?.value.trim() || "una aventura mágica";
        const personaje = document.getElementById("nombre_personaje")?.value.trim() || "un amiguito";
        const tono = document.getElementById("tono_cuento")?.value || "dulce";

        const datos = {
            tema_cuento: tema,
            nombre_personaje: personaje,
            tono_cuento: tono
        };

        const modalCarga = document.getElementById("modal-carga");

        try {
            if (modalCarga) modalCarga.style.display = "flex";

            const respuesta = await fetch("/generar-cuento", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datos)
            });

            const resultado = await respuesta.json();

            if (respuesta.ok) {
                abrirCuentoEnLibro(resultado.titulo, resultado.cuento);
            } else {
                alert("Aviso del servidor: " + resultado.message);
            }
        } catch (error) {
            alert("Hubo un problema de conexión al comunicar con el servidor.");
        } finally {
            if (modalCarga) modalCarga.style.display = "none";
            if (boton) {
                boton.innerHTML = textoOriginal;
                boton.disabled = false;
            }
        }
    });
}

// ==============================================================================
// 5. APERTURA DE LIBROS DESDE LA BIBLIOTECA (MÉTODO INFALIBLE)
// ==============================================================================
function abrirCuentoDesdeHTML(elementoTarjeta) {
    try {
        // Extraemos el texto del textarea oculto, que conserva saltos de línea perfectamente
        const titulo = elementoTarjeta.querySelector(".titulo-oculto").textContent;
        const texto = elementoTarjeta.querySelector(".texto-oculto").value;

        abrirCuentoEnLibro(titulo, texto);
    } catch (error) {
        console.error("Error al abrir el libro:", error);
    }
}

// ==============================================================================
// 6. OPTIMIZACIÓN RESPONSIVE MÓVIL Y ORIENTACIÓN
// ==============================================================================
function iniciar_control_responsive_movil() {
    verificarMarcaAbreviadaHeader();
    window.addEventListener("resize", verificarMarcaAbreviadaHeader);

    // Listener de cambio de orientación para refrescar lectura y marca
    window.addEventListener("orientationchange", function () {
        setTimeout(function () {
            verificarMarcaAbreviadaHeader();
            const visor = document.getElementById("visor-libro");
            if (visor && (visor.style.display === "flex" || getComputedStyle(visor).display === "flex")) {
                actualizarVistaPaginaLibro();
            }
        }, 150);
    });
}

function verificarMarcaAbreviadaHeader() {
    const header = document.querySelector(".barra-navegacion");
    const logo = document.querySelector(".logotipo-web");
    if (!header || !logo) return;

    // Detecta si la pantalla es <= 768px o si el contenido del header desborda el ancho disponible
    const esMovil = window.innerWidth <= 768;
    const desbordaHorizontal = header.scrollWidth > header.clientWidth;

    if (esMovil || desbordaHorizontal) {
        logo.classList.add("usar-marca-corta");
    } else {
        logo.classList.remove("usar-marca-corta");
    }
}
