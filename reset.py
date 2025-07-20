import psycopg2
from psycopg2 import sql

if __name__ == "__main__":
    conn = psycopg2.connect("user=connectorlib password=connectorlib dbname=connectorlib")
    cur = conn.cursor()

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

    print("Creating new tables and relations")
    with open("config.sql", "r") as f:
        cur.execute(f.read().strip())

    try:
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise e
