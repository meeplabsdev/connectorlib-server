import psycopg2

# conn = psycopg2.connect(host="postgres", port="5432", database="connectorlib", user="connectorlib", password="connectorlib")
conn = psycopg2.connect(host="localhost", port="5432", database="connectorlib", user="connectorlib", password="connectorlib")
cur = conn.cursor()

if __name__ == "__main__":
    with open("config/connectorlib.sql", "r") as f:
        cur.execute(f.read().strip())

    try:
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
