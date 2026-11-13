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
// 3. LECTOR DE LIBROS CON PAGINACIÓN DINÁMICA POR ALTURA REAL
// ==============================================================================
let paginasDelCuentoActual = [];
let indicePaginaActual = 0;
let tituloCuentoActual = "";
let textoCuentoActual = "";
let cuentoRecienCreado = false;

function abrirCuentoEnLibro(titulo, texto, esNuevo = false) {
    tituloCuentoActual = titulo;
    textoCuentoActual = texto;
    cuentoRecienCreado = esNuevo;

    const elemento_titulo = document.getElementById("libro-titulo-cuento");
    if (elemento_titulo) {
        elemento_titulo.textContent = titulo;
    }

    // 1. Abrimos el modal ANTES de paginar para que #libro-cuerpo-cuento tenga ancho y alto reales
    abrir_ventana_modal("visor-libro");

    // 2. Calculamos las páginas exactas que caben en la altura visible del contenedor
    paginasDelCuentoActual = paginarTextoPorAlturaReal(texto);

    if (paginasDelCuentoActual.length === 0) {
        paginasDelCuentoActual = ["<p class='primer-parrafo-cuento'>El cuento está vacío.</p>"];
    }

    indicePaginaActual = 0;
    actualizarVistaPaginaLibro();
}

/**
 * Reparte el cuento en páginas reales midiendo scrollHeight vs clientHeight
 * para que ninguna línea quede cortada ni se pierdan palabras al pasar página.
 */
function paginarTextoPorAlturaReal(texto) {
    const cuerpo = document.getElementById("libro-cuerpo-cuento");
    if (!cuerpo) return [];

    // Altura máxima disponible dentro del contenedor del libro (con margen de seguridad)
    const alturaMaxima = cuerpo.clientHeight - 8;
    if (alturaMaxima <= 40) {
        // Fallback si el contenedor aún no tiene dimensiones calculadas
        return texto
            .split("\n")
            .map(l => l.trim())
            .filter(l => l.length > 0)
            .map((p, idx) => `<p class="${idx === 0 ? 'primer-parrafo-cuento' : ''}">${p}</p>`);
    }

    // Creamos un clon invisible con exactamente el mismo ancho, tipografía y columnas que el visor
    const medidor = document.createElement("div");
    const estilos = window.getComputedStyle(cuerpo);
    medidor.style.position = "absolute";
    medidor.style.visibility = "hidden";
    medidor.style.pointerEvents = "none";
    medidor.style.width = cuerpo.clientWidth + "px";
    medidor.style.height = alturaMaxima + "px";
    medidor.style.fontFamily = estilos.fontFamily;
    medidor.style.fontSize = estilos.fontSize;
    medidor.style.lineHeight = estilos.lineHeight;
    medidor.style.padding = estilos.padding;
    medidor.style.boxSizing = estilos.boxSizing;
    medidor.style.columnCount = estilos.columnCount;
    medidor.style.columnGap = estilos.columnGap;
    medidor.style.overflow = "hidden";
    cuerpo.parentElement.appendChild(medidor);

    const parrafosOriginales = texto
        .split("\n")
        .map(l => l.trim())
        .filter(l => l.length > 0);

    const paginas = [];
    let htmlPaginaActual = "";
    let esPrimerParrafoDelCuento = true;

    for (let i = 0; i < parrafosOriginales.length; i++) {
        const palabras = parrafosOriginales[i].split(/\s+/);
        let idxPalabra = 0;

        while (idxPalabra < palabras.length) {
            const claseInicial = esPrimerParrafoDelCuento ? ' class="primer-parrafo-cuento"' : '';
            let bloqueEnConstruccion = "";
            let palabrasQueCaben = 0;

            // Añadimos palabra a palabra hasta llenar la altura exacta de la página
            for (let j = idxPalabra; j < palabras.length; j++) {
                const candidato = bloqueEnConstruccion
                    ? bloqueEnConstruccion + " " + palabras[j]
                    : palabras[j];
                medidor.innerHTML = htmlPaginaActual + `<p${claseInicial}>${candidato}</p>`;

                // Comprobamos desbordamiento tanto vertical como horizontal (por si usa column-count: 2)
                if (medidor.scrollHeight <= alturaMaxima && medidor.scrollWidth <= cuerpo.clientWidth + 2) {
                    bloqueEnConstruccion = candidato;
                    palabrasQueCaben++;
                } else {
                    break;
                }
            }

            if (palabrasQueCaben === 0) {
                // La página actual ya está llena: la guardamos y abrimos una nueva página
                if (htmlPaginaActual.trim().length > 0) {
                    paginas.push(htmlPaginaActual);
                    htmlPaginaActual = "";
                } else {
                    // Seguridad por si una palabra suelta fuese más ancha que la caja
                    htmlPaginaActual += `<p${claseInicial}>${palabras[idxPalabra]}</p>`;
                    idxPalabra++;
                    esPrimerParrafoDelCuento = false;
                }
            } else {
                htmlPaginaActual += `<p${claseInicial}>${bloqueEnConstruccion}</p>`;
                idxPalabra += palabrasQueCaben;
                esPrimerParrafoDelCuento = false;

                // Si aún quedan palabras de este mismo párrafo, cerramos página y seguimos en la siguiente
                if (idxPalabra < palabras.length) {
                    paginas.push(htmlPaginaActual);
                    htmlPaginaActual = "";
                }
            }
        }
    }

    if (htmlPaginaActual.trim().length > 0) {
        paginas.push(htmlPaginaActual);
    }

    medidor.remove();
    return paginas;
}

/**
 * Paginación interactiva con animación 3D de volteo de hoja.
 */
function cambiarPaginaLibro(direccion) {
    let nuevoIndice = indicePaginaActual + direccion;
    if (nuevoIndice >= 0 && nuevoIndice < paginasDelCuentoActual.length) {
        const cuerpo = document.getElementById("libro-cuerpo-cuento");
        if (cuerpo) {
            const claseAnimacion = direccion > 0 ? "efecto-giro-derecha" : "efecto-giro-izquierda";
            cuerpo.classList.remove("efecto-giro-derecha", "efecto-giro-izquierda");
            void cuerpo.offsetWidth;
            cuerpo.classList.add(claseAnimacion);

            setTimeout(function () {
                indicePaginaActual = nuevoIndice;
                actualizarVistaPaginaLibro();
            }, 180);

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
                // Pasamos true para que al cerrar el libro se actualice la estantería con el nuevo cuento
                abrirCuentoEnLibro(resultado.titulo, resultado.cuento, true);
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
// 5. APERTURA DE LIBROS DESDE LA BIBLIOTECA
// ==============================================================================
function abrirCuentoDesdeHTML(elementoTarjeta) {
    try {
        const titulo = elementoTarjeta.querySelector(".titulo-oculto").textContent;
        const texto = elementoTarjeta.querySelector(".texto-oculto").value;

        abrirCuentoEnLibro(titulo, texto, false);
    } catch (error) {
        console.error("Error al abrir el libro:", error);
    }
}

// ==============================================================================
// 6. OPTIMIZACIÓN RESPONSIVE MÓVIL, ORIENTACIÓN Y NAVEGACIÓN POR TECLADO
// ==============================================================================
function iniciar_control_responsive_movil() {
    verificarMarcaAbreviadaHeader();

    let temporizadorResize;
    window.addEventListener("resize", function () {
        verificarMarcaAbreviadaHeader();
        clearTimeout(temporizadorResize);
        temporizadorResize = setTimeout(recalcularPaginasSiVisorAbierto, 200);
    });

    window.addEventListener("orientationchange", function () {
        setTimeout(function () {
            verificarMarcaAbreviadaHeader();
            recalcularPaginasSiVisorAbierto();
        }, 200);
    });

    // Navegación cómoda con flechas del teclado cuando el libro está abierto
    window.addEventListener("keydown", function (evento) {
        const visor = document.getElementById("visor-libro");
        const estaAbierto = visor && (visor.style.display === "flex" || getComputedStyle(visor).display === "flex");
        if (!estaAbierto) return;

        if (evento.key === "ArrowRight") {
            cambiarPaginaLibro(1);
        } else if (evento.key === "ArrowLeft") {
            cambiarPaginaLibro(-1);
        }
    });
}

function recalcularPaginasSiVisorAbierto() {
    const visor = document.getElementById("visor-libro");
    if (visor && (visor.style.display === "flex" || getComputedStyle(visor).display === "flex") && textoCuentoActual) {
        const progresoRelativo = paginasDelCuentoActual.length > 0
            ? indicePaginaActual / paginasDelCuentoActual.length
            : 0;
        paginasDelCuentoActual = paginarTextoPorAlturaReal(textoCuentoActual);
        indicePaginaActual = Math.min(
            Math.floor(progresoRelativo * paginasDelCuentoActual.length),
            Math.max(0, paginasDelCuentoActual.length - 1)
        );
        actualizarVistaPaginaLibro();
    }
}

function verificarMarcaAbreviadaHeader() {
    const header = document.querySelector(".barra-navegacion");
    const logo = document.querySelector(".logotipo-web");
    if (!header || !logo) return;

    const esMovil = window.innerWidth <= 768;
    const desbordaHorizontal = header.scrollWidth > header.clientWidth;

    if (esMovil || desbordaHorizontal) {
        logo.classList.add("usar-marca-corta");
    } else {
        logo.classList.remove("usar-marca-corta");
    }
}
