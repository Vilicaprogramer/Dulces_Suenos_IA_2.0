# Estándar de Artesanía y Calidad de Producto - Impeccable Craft

Este documento define el listón mínimo de calidad (*Craft Floor*) y la disciplina de pulido de **Impeccable**, adaptada a **Dulces Sueños AI 2.0**. Ninguna pantalla o componente se considera terminado hasta cumplir estos estándares.

---

## 1. El Suelo de Artesanía (The Craft Floor)

Todo componente visual o página debe verificar rigurosamente los siguientes requisitos antes de ser entregado:

### A. Contraste Cromático y Legibilidad (WCAG AA Estricto)
- **Texto general y campos de formulario:** Relación de contraste mínima de **4.5:1**.
- **Texto grande (títulos mayores a 24px) y componentes clave:** Relación mínima de **3:1**.
- **Regla del texto secundario sobre fondos nocturnos:** El texto secundario o de apoyo nunca debe ser un gris neutro apagado (`#888888`), sino un tono tintado a partir de la paleta nocturna (por ejemplo, lila suave `#b3b8d4` o celeste grisáceo `#a0aec0`), garantizando legibilidad y calidez visual.

### B. Profundidad y Elevación Realista
- Las sombras deben tener **desplazamiento vertical** y **desenfoque suave difuso**:
  ```css
  /* Sombra elegante y física */
  box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.45), 0 4px 12px -2px rgba(0, 0, 0, 0.25);
  ```
- Prohibidos los halos de color sin desplazamiento (`0 0 20px #color`) como sustituto de profundidad real.
- Declara la elevación con coherencia: o borde biselado sutil, o sombra difusa, o ambos combinados con armonía.

### C. Superficies del Navegador Tematizadas (Browser Surfaces)
Una aplicación de alto nivel se distingue porque las partes nativas del navegador que la mayoría olvida también están integradas con el diseño:

```css
/* 1. Selección de Texto */
::selection {
    background: rgba(255, 215, 0, 0.35);
    color: #ffffff;
}

/* 2. Barra de Desplazamiento Personalizada */
html {
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.2) rgba(10, 11, 28, 0.95);
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0a0b1c;
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.18);
    border-radius: 9999px;
    border: 2px solid #0a0b1c;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 215, 0, 0.4);
}

/* 3. Anillos de Enfoque Accesibles (Teclado) */
:focus-visible {
    outline: 2px solid var(--color-dorado-estrella);
    outline-offset: 3px;
    border-radius: 4px;
}
:focus:not(:focus-visible) {
    outline: none; /* No ensucia el clic de ratón */
}

/* 4. Color de Cursor de Texto */
input, textarea {
    caret-color: var(--color-dorado-estrella);
}
```

---

## 2. Matriz de Estados Completa (Zero Missing States)

Todo elemento interactivo (botones, inputs, tarjetas de cuentos, desplegables) debe tener diseñados y programados explícitamente sus **8 estados**:

| Estado | Comportamiento Obligatorio |
| :--- | :--- |
| **1. Default** | Estado base de reposo con contraste y jerarquía claros. |
| **2. Hover** | Elevación sutil (`translateY(-2px)`), ajuste de brillo, protegido con `@media (hover: hover)`. |
| **3. Active / Pressed** | Contracción táctil (`transform: scale(0.97)`), acuse de recibo físico instantáneo. |
| **4. Focus-visible** | Anillo de enfoque de alto contraste dorado/celeste para navegación accesible por teclado (`Tab`). |
| **5. Disabled** | `opacity: 0.55`, `cursor: not-allowed`, `pointer-events: none` donde aplique, pero conservando legibilidad del texto. |
| **6. Loading / Espera** | Animación de carga fluida o esqueleto con brillo (*shimmer*). Nunca bloquees la UI sin feedback visible. |
| **7. Error** | Borde en tono de advertencia suave (`#ff76ac` o `#ff4d4d`), mensaje de ayuda contextual que explique la solución. |
| **8. Empty State** | Pantalla vacía con ilustración o icono temático (ej. luna durmiendo), texto cálido y botón de acción para crear el primer elemento. **Prohibido limitarse a "No hay datos".** |

---

## 3. Tesis de Deleite con Propósito (Delight Thesis)

El deleite (*delight*) no consiste en llenar la pantalla de confeti aleatorio ni en ralentizar al usuario con animaciones interminables. Es el carácter del producto revelado en un momento ganado con mérito:

- **Momento Ganado:** El niño finaliza la lectura de un cuento. Se produce un sutil destello de estrellas en la pantalla y una frase cálida: *"¡Qué sueñes con los angelitos! Has ganado 1 estrella estelar"*.
- **Causa y Efecto:** Si el usuario guarda una historia favorita, el corazón o la estrella realiza una micro-vibración elástica reconfortante.
- **Regla de Protección:** El deleite jamás debe impedir que el padre o el niño continúen navegando, ni debe obligar a esperar a que termine una animación para poder pulsar otro botón.

---

## 4. Protocolo de Pulido y Prioridad (Polish Protocol)

Cuando revises o refactorices una funcionalidad existente, sigue este orden estricto de prioridades:

1. **Integridad funcional y accesibilidad:** Tareas completas, sin pérdida de datos, navegación por teclado impecable, contraste WCAG verificado.
2. **Cobertura de estados:** Asegurar que ningún estado (carga, error, vacío, deshabilitado) falte o quede sin estilo.
3. **Jerarquía visual y ritmo espacial:** Alinear márgenes, agrupar elementos relacionados estrechamente y separar secciones generosamente.
4. **Cohesión de movimiento y microinteracciones:** Curvas de aceleración unificadas (`--ease-out`), duraciones inferiores a 300ms, feedback en `:active`.
5. **Limpieza y documentación de código:** Eliminar estilos duplicados, verificar variables semánticas en `:root` y comentar con fines didácticos (FP DAW).

---

## 5. Lista de Verificación Final (Pre-Flight Checklist)

Antes de considerar concluida cualquier tarea visual o de interacción:

- [ ] ¿El texto cumple el contraste 4.5:1 / 3:1 de WCAG AA?
- [ ] ¿Se han personalizado `::selection`, `::-webkit-scrollbar` y `:focus-visible`?
- [ ] ¿Todos los botones y controles reaccionan a `:active` con `scale(0.97)`?
- [ ] ¿Las animaciones usan `transform`/`opacity` con variables `--ease-*` y duran < 300ms?
- [ ] ¿Se respeta `@media (prefers-reduced-motion: reduce)`?
- [ ] ¿Los estados de carga, error y vacío están implementados y acompañados de mensajes útiles?
- [ ] ¿El diseño es 100% responsivo y libre de desbordamientos horizontales en 375px, 768px y 1200px?
