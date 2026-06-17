import psycopg2
import sys

# URL del superusuario para configurar la BD (ejecutado desde el contenedor)
ADMIN_DB_URL = "postgresql://postgres:password@db:5432/tesis_db"

def setup_rls():
    try:
        conn = psycopg2.connect(ADMIN_DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("1. Creando usuario app_user...")
        try:
            cursor.execute("CREATE USER app_user WITH PASSWORD 'app_password';")
        except psycopg2.errors.DuplicateObject:
            print("  app_user ya existe.")
            pass
            
        print("2. Asignando permisos...")
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE tesis_db TO app_user;")
        cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;")
        cursor.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;")
        cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;")
        cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;")
        
        # Las tablas con RLS estricto basado en user_id
        tables_user_id = ["skin_profiles", "analyses", "routines", "skin_checks"]
        
        print("3. Configurando políticas RLS en tablas de usuario...")
        for t in tables_user_id:
            print(f"  Aplicando a {t}...")
            cursor.execute(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"DROP POLICY IF EXISTS tenant_policy ON {t};")
            cursor.execute(f"""
                CREATE POLICY tenant_policy ON {t}
                FOR ALL
                USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer);
            """)
            
        print("4. Configurando política para routine_steps (vía routines)...")
        cursor.execute("ALTER TABLE routine_steps ENABLE ROW LEVEL SECURITY;")
        cursor.execute("ALTER TABLE routine_steps FORCE ROW LEVEL SECURITY;")
        cursor.execute("DROP POLICY IF EXISTS tenant_policy ON routine_steps;")
        cursor.execute("""
            CREATE POLICY tenant_policy ON routine_steps
            FOR ALL
            USING (routine_id IN (
                SELECT id FROM routines 
                WHERE user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer
            ));
        """)
        
        print("5. Configurando política para users (solo actualización)...")
        # El login y registro necesitan que SELECT e INSERT no tengan RLS,
        # Pero podemos bloquear UPDATE y DELETE para que un usuario no cambie a otro
        cursor.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
        cursor.execute("ALTER TABLE users FORCE ROW LEVEL SECURITY;")
        cursor.execute("DROP POLICY IF EXISTS tenant_policy_select ON users;")
        cursor.execute("DROP POLICY IF EXISTS tenant_policy_insert ON users;")
        cursor.execute("DROP POLICY IF EXISTS tenant_policy_update ON users;")
        cursor.execute("DROP POLICY IF EXISTS tenant_policy_delete ON users;")
        
        cursor.execute("CREATE POLICY tenant_policy_select ON users FOR SELECT USING (true);")
        cursor.execute("CREATE POLICY tenant_policy_insert ON users FOR INSERT WITH CHECK (true);")
        cursor.execute("""
            CREATE POLICY tenant_policy_update ON users
            FOR UPDATE
            USING (id = NULLIF(current_setting('app.current_user_id', true), '')::integer);
        """)
        cursor.execute("""
            CREATE POLICY tenant_policy_delete ON users
            FOR DELETE
            USING (id = NULLIF(current_setting('app.current_user_id', true), '')::integer);
        """)

        print("\n✅ RLS configurado correctamente!")
        
    except Exception as e:
        print(f"❌ Error configurando RLS: {e}", file=sys.stderr)
        
if __name__ == "__main__":
    setup_rls()
