import psycopg2
from psycopg2 import sql

# conn = psycopg2.connect(host="postgres", port="5432", database="connectorlib", user="connectorlib", password="connectorlib")
conn = psycopg2.connect(host="localhost", port="5432", database="connectorlib", user="connectorlib", password="connectorlib")
cur = conn.cursor()

if __name__ == "__main__":
    cur.execute("""
        SELECT s.nspname as schema_name, t.relname as table_name
        FROM pg_class t 
        JOIN pg_namespace s ON s.oid = t.relnamespace
        WHERE t.relkind = 'r'
        AND s.nspname !~ '^pg_' 
        AND s.nspname != 'information_schema'
        ORDER BY 1, 2;
    """)

    for schema, table in cur.fetchall():
        print(f"Dropping {schema}.{table}")
        cur.execute(sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(sql.Identifier(schema), sql.Identifier(table)))

    with open("config/setup.sql", "r") as f:
        cur.execute(f.read().strip())

    print("Created new tables and relations")

    try:
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
