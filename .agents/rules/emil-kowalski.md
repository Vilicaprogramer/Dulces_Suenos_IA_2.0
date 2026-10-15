# Pautas de Animación y Microinteracciones - Emil Kowalski

Este documento codifica los principios y reglas de ingeniería de interacción de **Emil Kowalski** (creador de *Sonner*, pionero en diseño de interacción de alta fidelidad). En este proyecto se aplican estrictamente utilizando **CSS3 nativo y JavaScript Vanilla (ES6)**.

---

## 1. Filosofía Central

1. **El buen gusto se entrena:** El diseño refinado no es cuestión de suerte ni de opiniones arbitrarias. Es una observación meticulosa de por qué las mejores interfaces se sienten fluidas y humanas.
2. **Los detalles invisibles se acumulan:** Los usuarios no perciben conscientemente cada milisegundo de animación o curva bezier; perciben la armonía total (*"como mil voces apenas audibles cantando perfectamente afinadas"*).
3. **La belleza es una ventaja competitiva:** En un mundo donde todo software "funciona", la experiencia táctil, la respuesta inmediata y el acabado artesanal diferencian el producto.

---

## 2. Árbol de Decisión de Animación (The Animation Decision Framework)

Antes de escribir cualquier línea de animación o transición, responde a estas tres preguntas:

### ¿Debe animarse este elemento? (Regla de Frecuencia)
Evalúa cuántas veces al día interactúa el usuario con este elemento:

| Frecuencia | Decisión | Ejemplo en el Proyecto |
| :--- | :--- | :--- |
| **100+ veces/día** | **Cero animación. Prohibido.** | Atajos de teclado, navegación directa rápida, toggles repetitivos. |
| **Decenas de veces/día** | **Reducir al mínimo (100–160ms)** | Efectos hover sutiles, botones de acción inmediata, tarjetas de selección. |
| **Ocasional** | **Animación estándar (150–250ms)** | Modales, cajones laterales, alertas/toasts, cambio de capítulo del cuento. |
| **Rara / Primera vez** | **Deleite / Celebración (300–600ms)** | Guardar un nuevo cuento con éxito, felicitación de buenas noches, logros. |

> **Regla de Oro:** **NUNCA animes acciones iniciadas por teclado.** El teclado exige inmediatez absoluta; animarlo introduce latencia artificial que desconecta al usuario de la acción.

---

## 3. Curvas de Aceleración (Easing) y Tiempos

### Curvas Prohibidas y Permitidas
- **PROHIBIDO:** Usar `ease-in` en cualquier elemento de interfaz. El `ease-in` arranca lento, lo que genera una sensación de retardo y pesadez en el momento crítico donde el ojo del usuario está observando.
- **PROHIBIDO:** Usar `transition: all`. Siempre declara explícitamente las propiedades animadas (`transition: transform 160ms var(--ease-out), opacity 160ms var(--ease-out)`).
- **PROHIBIDO:** Las curvas predeterminadas del navegador (`ease`, `ease-out` nativo plano) carecen de fuerza. Emplea curvas personalizadas `cubic-bezier`.

### Variables CSS del Sistema (Tokens Obligatorios)
Definidas en `:root` para todo el proyecto:

```css
:root {
    /* Curva de desaceleración fuerte: entradas, despliegues y respuestas inmediatas */
    --ease-out: cubic-bezier(0.23, 1, 0.32, 1);

    /* Curva orgánica fluida: movimientos de un punto A a B dentro de la pantalla */
    --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);

    /* Curva estilo iOS/cajón suave: modales, hojas emergentes y acordeones */
    --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);

    /* Curva elástica/resorte calibrada para feedback táctil */
    --ease-spring: cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Duraciones Estándar de la UI (Límite máximo: 300ms)
- **Feedback táctil en botones / clics:** `100ms – 160ms`
- **Tooltips y pequeños popovers:** `125ms – 200ms`
- **Desplegables, menús contextuales y selects:** `150ms – 220ms`
- **Modales, overlays y paneles laterales:** `200ms – 300ms`

---

## 4. Reglas Críticas de Componentes (Kowalski Principles)

### A. Feedback Táctil en Botones y Controles
Todo elemento pulsable debe acusar recibo inmediatamente al usuario mediante `:active`:
```css
.btn-magico, .tarjeta-interactiva {
    transition: transform 160ms var(--ease-out), background-color 160ms ease, box-shadow 160ms ease;
}

.btn-magico:active, .tarjeta-interactiva:active {
    transform: scale(0.97);
}
```

### B. Prohibido Animar desde `scale(0)`
En el mundo real nada brota de la nada infinita. Animar desde `scale(0)` parece artificial.
- **Siempre inicia en escala sutil:** Inicia desde `scale(0.95)` o `scale(0.96)` combinado con `opacity: 0`:
```css
/* CORRECTO */
.elemento-entrante {
    opacity: 0;
    transform: scale(0.95) translateY(6px);
    transition: opacity 200ms var(--ease-out), transform 200ms var(--ease-out);
}
.elemento-entrante.visible {
    opacity: 1;
    transform: scale(1) translateY(0);
}
```

### C. Origen de Transformación Consciente (`transform-origin`)
- Desplegables, tooltips y ventanas emergentes deben nacer y escalar **desde el botón o gatillo que los activó** (arriba a la izquierda, arriba al centro, etc.).
- **Excepción:** Los modales centrados en pantalla mantienen `transform-origin: center`.

### D. Tiempos Asimétricos (Entrada vs. Salida)
- Cuando el usuario decide una acción reflexiva (ej. mantener pulsado para borrar), el avance es lento y deliberado.
- Al soltar o cancelar, la respuesta del sistema debe ser instantánea y enérgica:
```css
/* Salida / Liberación rápida */
.overlay-confirmacion {
    transition: opacity 150ms var(--ease-out);
}
```

### E. Desenfoque como Puente en Transiciones de Estado (`filter: blur`)
Cuando se alterna entre dos estados o vistas de un contenedor y el fundido plano genera un choque visual brusco, añade un micro-desenfoque transitorio (`filter: blur(2px)`):
```css
.contenedor-transicion {
    transition: opacity 180ms var(--ease-out), filter 180ms var(--ease-out);
}
.contenedor-transicion.cambiando {
    opacity: 0;
    filter: blur(2px);
}
```

### F. Cascada / Stagger en Listas de Elementos
Al cargar tarjetas o listados de cuentos, desfasa sutilmente la aparición (30ms a 50ms por ítem). Nunca hagas esperar al usuario:
```css
.tarjeta-cuento {
    opacity: 0;
    transform: translateY(12px);
    animation: aparecerCuento 280ms var(--ease-out) forwards;
}
.tarjeta-cuento:nth-child(1) { animation-delay: 0ms; }
.tarjeta-cuento:nth-child(2) { animation-delay: 40ms; }
.tarjeta-cuento:nth-child(3) { animation-delay: 80ms; }
.tarjeta-cuento:nth-child(4) { animation-delay: 120ms; }

@keyframes aparecerCuento {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

---

## 5. Rendimiento y Aceleración por Hardware

1. **Propiedades seguras para la GPU:** Anima exclusivamente `transform` y `opacity` (y excepcionalmente `clip-path`).
2. **Prohibido animar propiedades de maquetación:** NUNCA animes `width`, `height`, `top`, `left`, `margin` ni `padding`, pues provocan reflujos (*layout thrashing*) continuos y caídas de fotogramas.
3. **Transiciones CSS antes que Keyframes en UI dinámica:** Las transiciones CSS se pueden interrumpir en cualquier punto del recorrido y redirigirse suavemente; los `@keyframes` se reinician bruscamente a cero si se interrumpe la animación.

---

## 6. Accesibilidad y Filtro de Dispositivos Táctiles

### Reducción de Movimiento Obligatoria
En dispositivos con preferencia de movimiento reducido activada, no eliminamos el feedback; sustituimos el desplazamiento por un desvanecimiento suave de opacidad:
```css
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.15s !important;
        scroll-behavior: auto !important;
    }
    .tarjeta-cuento, .btn-magico, .elemento-entrante {
        transform: none !important;
    }
}
```

### Protección de Hover en Pantallas Táctiles
En móviles, el estado `:hover` se dispara erráticamente al pulsar con el dedo. Protege los efectos hover:
```css
@media (hover: hover) and (pointer: fine) {
    .btn-magico:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 215, 0, 0.25);
    }
}
```

---

## 7. Tabla de Autoevaluación (Revisión Kowalski)

| Antes (Práctica Deficiente) | Después (Estándar Emil Kowalski) | Motivo |
| :--- | :--- | :--- |
| `transition: all 0.3s ease` | `transition: transform 180ms var(--ease-out), opacity 180ms var(--ease-out)` | Evita recalcular todas las propiedades y usa una curva intencional y rápida. |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0;` | En el mundo real ningún objeto surge de la nada absoluta. |
| `transition: 0.5s ease-in` | `transition: 200ms var(--ease-out)` | `ease-in` hace que la UI se sienta lenta y perezosa al reaccionar. |
| Sin respuesta al hacer clic | `:active { transform: scale(0.97); }` | Confirma hápticamente al usuario que el sistema recibió su acción. |
| Animación de entrada de 600ms | Animación de 180ms a 240ms | La UI debe sentirse ágil; las animaciones no deben hacer perder tiempo. |
