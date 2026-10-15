# Pautas de Buen Gusto y Diseño Visual Premium - Taste & High-End Visual Design

Este documento recoge los criterios de **Taste Frontend**, **High-End Visual Design** y **GPT-Taste** aplicados con maestría a **Dulces Sueños AI 2.0** con **CSS3 puro y HTML5 semántico**.

---

## 1. Disciplina Anti-Clichés de IA (Anti-Default Discipline)

Los modelos de IA tienden por defecto a repetir patrones estéticos predecibles y genéricos. En este proyecto queda **expresamente prohibido**:
1. **El gradiente violeta genérico "AI Purple"** sobre fondo negro puro (`#000000`). En su lugar, usamos fondos nocturnos oscuros con matices orgánicos de azul cobalto profundo (`#0a0b1c`, `#0e1026`) y toques de estrellas y magia infantil.
2. **Las 3 tarjetas idénticas y simétricas en fila** como único recurso de diseño. Crea ritmo asimétrico, tarjetas bento destacadas o flujos alternados.
3. **Titulares eternos de 5 o 6 líneas.** Los encabezados principales (`h1`, `h2`) deben respirar en contenedores amplios (`max-width: 800px - 1100px`) y tener un máximo estricto de 2 a 3 líneas con tipografía escalada mediante `clamp()`.
4. **Tarjetas planas sin profundidad** o sombras toscas sin desenfoque difuso.
5. **Iconos o emojis sueltos sin contenedor ni escala.** Los iconos deben estar integrados en cápsulas o acompañados de micro-envoltorios estructurados.

---

## 2. Los Tres Diales de Configuración Visual (The Three Dials)

Cada vista de la aplicación debe concebirse ajustando estos tres diales:

- **Varianza de Diseño (`DESIGN_VARIANCE: 8/10`):** Rompe la monotonía geométrica. Combina cuadrículas asimétricas (Bento grids), tamaños de tarjetas proporcionales a su importancia y jerarquía visual nítida.
- **Intensidad de Movimiento (`MOTION_INTENSITY: 6/10`):** Movimiento con masa física real, amortiguado y elástico cuando procede. Animaciones orgánicas (estrellas parpadeantes con micro-flotación, botones reactivos).
- **Densidad Visual (`VISUAL_DENSITY: 4/10`):** Espaciado amplio (*Macro-Whitespace*). Deja respirar a cada sección con separaciones generosas (`padding: 4rem 1.5rem` a `6rem 2rem`). Nunca amontones información.

---

## 3. Arquitectura "Double-Bezel" (Doppelrand / Carcasa Maquinada)

Para elevar tarjetas y contenedores clave a una categoría visual de alta gama, utiliza la arquitectura de **doble envolvente física concéntrica**:

```html
<!-- Estructura HTML Semántica -->
<article class="tarjeta-shell">
    <div class="tarjeta-core">
        <header class="tarjeta-encabezado">...</header>
        <div class="tarjeta-contenido">...</div>
    </div>
</article>
```

```css
/* Carcasa Exterior (Shell) */
.tarjeta-shell {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 28px;
    padding: 8px; /* Separación milimétrica constante */
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6);
    transition: transform 220ms var(--ease-out), border-color 220ms ease;
}

/* Núcleo Interior (Core) */
.tarjeta-core {
    background: linear-gradient(145deg, rgba(26, 28, 56, 0.85) 0%, rgba(14, 16, 38, 0.95) 100%);
    /* El radio interior es matemáticamente concéntrico: R_exterior - padding */
    border-radius: calc(28px - 8px);
    padding: 1.75rem;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.12); /* Brillo superior biselado */
}
```

---

## 4. Glassmorphism Nocturno de Alta Precisión

Para el tono de **Dulces Sueños AI 2.0**, el acabado translúcido debe evocar una ventana a una noche mágica y soñadora, no un simple fondo borroso:

1. **Estructura del Cristal:**
   - Fondo semitransparente oscuro con saturación aumentada:
     `background: rgba(20, 22, 48, 0.65);`
   - Filtro de desenfoque de fondo y saturación:
     `backdrop-filter: blur(16px) saturate(160%);`
     `-webkit-backdrop-filter: blur(16px) saturate(160%);`
   - Borde translúcido con resalte de luz superior:
     `border: 1px solid rgba(255, 255, 255, 0.12);`
     `box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18), 0 16px 36px rgba(0, 0, 0, 0.4);`
2. **Restricción Crucial de Rendimiento:**
   - Aplica `backdrop-filter` **únicamente a elementos fijos o flotantes** (barra de navegación flotante, modales, alertas superpuestas).
   - **NUNCA** apliques `backdrop-filter` indiscriminadamente a decenas de elementos que hacen scroll continuo en una lista larga, ya que fuerza al navegador a recalcular la composición en cada fotograma.

---

## 5. Arquitectura de Botones "Island" y Micro-Contenedores de Iconos

Los botones principales (*Call-to-Action*) son píldoras táctiles con icono integrado en micro-cápsula:

```html
<button class="btn-cta-isla" type="button">
    <span>Comenzar Historia</span>
    <span class="icono-capsula" aria-hidden="true">
        <i class="fas fa-magic"></i>
    </span>
</button>
```

```css
.btn-cta-isla {
    display: inline-flex;
    align-items: center;
    gap: 0.85rem;
    padding: 0.75rem 0.85rem 0.75rem 1.6rem;
    border-radius: 9999px;
    background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%);
    color: #0a0b1c;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    cursor: pointer;
    box-shadow: 0 8px 24px rgba(255, 215, 0, 0.28), inset 0 1px 1px rgba(255, 255, 255, 0.5);
    transition: transform 160ms var(--ease-out), box-shadow 160ms ease;
}

.btn-cta-isla .icono-capsula {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 50%;
    background: rgba(10, 11, 28, 0.15);
    transition: transform 200ms var(--ease-spring);
}

@media (hover: hover) and (pointer: fine) {
    .btn-cta-isla:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(255, 215, 0, 0.38);
    }
    .btn-cta-isla:hover .icono-capsula {
        transform: rotate(12deg) scale(1.08);
    }
}

.btn-cta-isla:active {
    transform: scale(0.97);
}
```

---

## 6. Rejillas Bento "Gapless" y Composición de Cuadrícula

Al diseñar la galería de cuentos, categorías de valores o estadísticas del niño:
1. Usa **CSS Grid con flujo denso:**
   ```css
   .bento-grid {
       display: grid;
       grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
       grid-auto-flow: dense;
       gap: 1.5rem;
   }
   ```
2. **Jerarquía diferenciada:** El cuento destacado o la historia recién creada ocupa 2 columnas (`grid-column: span 2`) en pantallas grandes (`@media (min-width: 992px)`).
3. **Colapso móvil (< 768px):** En pantallas móviles, toda la rejilla colapsa limpiamente a 1 sola columna (`grid-column: span 1`) con ancho 100%, evitando cualquier desborde horizontal.

---

## 7. Jerarquía Tipográfica y Reglas de Maquetación

- **Titulares de alto impacto (`h1`, `h2`):**
  - Ajuste de espaciado entre letras (tracking): `letter-spacing: -0.02em;` para compactar titulares grandes y darles aspecto editorial de revista.
  - Escala fluida mediante `clamp()`:
    ```css
    h1.titulo-principal {
        font-size: clamp(2.2rem, 4.5vw, 3.8rem);
        line-height: 1.15;
        letter-spacing: -0.025em;
    }
    ```
- **Números y métricas (Cuentos leídos, estrellas, minutos):**
  - Usa siempre `font-variant-numeric: tabular-nums;` para que los números mantengan anchura fija y no oscilen al incrementarse o variar.
- **Micro-insignias ("Eyebrow Tags"):**
  - Etiqueta temática sobre el título:
    ```css
    .eyebrow-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(255, 215, 0, 0.12);
        color: var(--color-dorado-estrella);
        border: 1px solid rgba(255, 215, 0, 0.25);
        margin-bottom: 0.75rem;
    }
    ```
