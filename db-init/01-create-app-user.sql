-- Crear usuario app_user con contraseña app_password
CREATE USER app_user WITH PASSWORD 'app_password';

-- Dar todos los privilegios sobre la base de datos tesis_db
GRANT ALL PRIVILEGES ON DATABASE tesis_db TO app_user;

-- Conectar a la base de datos tesis_db para dar permisos sobre el schema
\c tesis_db

-- Dar permisos sobre el schema public
GRANT ALL ON SCHEMA public TO app_user;

-- Dar permisos sobre todas las tablas existentes y futuras
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;

-- Dar permisos sobre todas las secuencias existentes y futuras
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
