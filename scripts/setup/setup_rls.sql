-- 1. Crear usuario app_user (ya creado por db-init, pero asegurar existencia)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
        CREATE USER app_user WITH PASSWORD 'app_password';
    END IF;
END
$$;

-- 2. Asignar permisos
GRANT ALL PRIVILEGES ON DATABASE tesis_db TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;

-- 3. Configurar políticas RLS en tablas de usuario
-- skin_profiles
ALTER TABLE skin_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE skin_profiles FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_policy ON skin_profiles;
CREATE POLICY tenant_policy ON skin_profiles
    FOR ALL
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer);

-- analyses
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_policy ON analyses;
CREATE POLICY tenant_policy ON analyses
    FOR ALL
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer);

-- routines
ALTER TABLE routines ENABLE ROW LEVEL SECURITY;
ALTER TABLE routines FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_policy ON routines;
CREATE POLICY tenant_policy ON routines
    FOR ALL
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer);

-- skin_checks
ALTER TABLE skin_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE skin_checks FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_policy ON skin_checks;
CREATE POLICY tenant_policy ON skin_checks
    FOR ALL
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer);

-- 4. Configurar política para routine_steps (vía routines)
ALTER TABLE routine_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE routine_steps FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_policy ON routine_steps;
CREATE POLICY tenant_policy ON routine_steps
    FOR ALL
    USING (routine_id IN (
        SELECT id FROM routines 
        WHERE user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer
    ));

-- 5. Configurar política para users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_policy_select ON users;
DROP POLICY IF EXISTS tenant_policy_insert ON users;
DROP POLICY IF EXISTS tenant_policy_update ON users;
DROP POLICY IF EXISTS tenant_policy_delete ON users;

CREATE POLICY tenant_policy_select ON users FOR SELECT USING (true);
CREATE POLICY tenant_policy_insert ON users FOR INSERT WITH CHECK (true);
CREATE POLICY tenant_policy_update ON users
    FOR UPDATE
    USING (id = NULLIF(current_setting('app.current_user_id', true), '')::integer);
CREATE POLICY tenant_policy_delete ON users
    FOR DELETE
    USING (id = NULLIF(current_setting('app.current_user_id', true), '')::integer);

COMMIT;
