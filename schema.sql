-- Script de creación de las tablas de la base de datos para Dulces Sueños AI 2.0
-- Creado para ejecutar en PostgreSQL o SQLite

-- 1. Tabla para los tipos de cuenta/suscripción (Free, Premium, Ilimitado)
CREATE TABLE IF NOT EXISTS tipos_cuenta (
    id_tipo SERIAL PRIMARY KEY,
    nombre_plan VARCHAR(50) NOT NULL, -- Nombre comercial del plan
    limite_cuentos INT NOT NULL       -- Número máximo de cuentos al mes (-1 = sin límite)
);

-- Insertamos los 3 planes básicos que vamos a ofrecer
INSERT INTO tipos_cuenta (nombre_plan, limite_cuentos) VALUES 
('Free', 5),
('Premium', 20),
('Ilimitado', -1)
ON CONFLICT DO NOTHING;

-- 2. Tabla para guardar los usuarios registrados
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    correo_electronico VARCHAR(120) UNIQUE NOT NULL,
    contrasena_encriptada VARCHAR(255),               -- Puede ser NULL si entra con Google
    nombre_completo VARCHAR(100),
    id_google VARCHAR(255) UNIQUE,                     -- Identificador si inicia sesión con Google
    id_tipo_cuenta INT DEFAULT 1,                     -- Por defecto todos empiezan en el plan Free (ID 1)
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tipo_cuenta) REFERENCES tipos_cuenta(id_tipo)
);

-- 3. Tabla para guardar el historial de cuentos creados por cada usuario
CREATE TABLE IF NOT EXISTS cuentos (
    id_cuento SERIAL PRIMARY KEY,
    id_usuario_dueno INT NOT NULL,                     -- Relación con la tabla usuarios
    titulo_cuento VARCHAR(200) NOT NULL,
    texto_cuento TEXT NOT NULL,                        -- Contenido completo del cuento
    nombre_personaje VARCHAR(100),
    grupo_edad VARCHAR(50),
    valor_moral VARCHAR(100),
    tematica VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario_dueno) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);