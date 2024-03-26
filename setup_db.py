import psycopg2

# Informationen zum PostgreSQL-Docker-Container
host = 'db'  # Ersetzen Sie durch 'localhost', wenn Sie nicht Docker verwenden.
port = 5432
user = 'test'
password = 'test'
database = 'pa_vcid_db'  # Ersetzen Sie durch den gewünschten Datenbanknamen

# Verbindung zu PostgreSQL
connection = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)
connection.autocommit = True

# Erstellen eines Cursor-Objekts zur Interaktion mit der Datenbank
cursor = connection.cursor()

# Erstellen Sie die Datenbank
cursor.execute(f"COMMIT;")
try:
    cursor.execute(f"CREATE DATABASE {database};")
    print(f"Database '{database}' has been created and is ready for use.")
except psycopg2.errors.DuplicateDatabase:
    print(f"Database '{database}' already exists. Continuing...")

# Schliessen des Cursors und der Verbindung
cursor.close()
connection.close()

# Verbindung zur neuen Datenbank herstellen
connection = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database,
)
connection.autocommit = True

# Erstellen eines Cursor-Objekts zur Interaktion mit der Datenbank
cursor = connection.cursor()

# Alle Tabellen loeschen, wenn sie existieren
cursor.execute("""
    DROP TABLE IF EXISTS "user" CASCADE;
    DROP TABLE IF EXISTS "post" CASCADE;
    DROP TABLE IF EXISTS "comment" CASCADE;
    DROP TABLE IF EXISTS "like" CASCADE;
    DROP TABLE IF EXISTS "friendship" CASCADE;
""")

# Benutzertabelle erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS "user" (
        id SERIAL PRIMARY KEY,
        username VARCHAR(20) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password VARCHAR(60) NOT NULL
    );
""")

# Post-Tabelle erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS "post" (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        user_id INTEGER REFERENCES "user" (id) NOT NULL
    );
""")

# Tabelle Kommentar erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS "comment" (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        post_id INTEGER REFERENCES post (id) NOT NULL
    );
""")

# Like-Tabelle erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS "like" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        post_id INTEGER REFERENCES post (id) NOT NULL
    );
""")

# Freundschaftstabelle erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS "friendship" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user" (id) NOT NULL,
        friend_id INTEGER REFERENCES "user" (id) NOT NULL
    );
""")

# 10 Benutzer anlegen, Testbenutzer
cursor.execute("""
    INSERT INTO "user" (username, email, password) VALUES
        ('john', 'test@mail.com', '$2b$12$AtulTqJa7NCO3HYH9qS4iebUTveVLVk1a/YbZpyXx6mfYnlYt9opW'),
        ('test1', 'test1@mail.com', '$2b$12$3ytO5zthedKdLyY5ZVVQ6.iM6XTbrY9phcmvMK0vKcxHTSt0O8TDG'),
        ('test2', 'test2@mail.com', '$2b$12$2fxVnhUB9234Rt8igOSFPeeI0A2.r1uLl15ALt4x89yS3SSIZqrHu'),
        ('test3', 'test3@mail.com', '$2b$12$i1v2C47ZUIZphUcH.gOGQ.aYNjOs/Aexug/EsinxwCR4SsaCK9wdS'),
        ('test4', 'test4@mail.com', '$2b$12$TVjEuvBG1iSa90XxgsA7LePibrECeYjJxYtmjhoq9ynXlfnLWVw5C')
        """)


# Freundschaften schliessen
cursor.execute("""
    INSERT INTO "friendship" (user_id, friend_id) VALUES
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (3, 4),
        (4, 5)
        """)

# Einige Beitraege erstellen
cursor.execute("""
    INSERT INTO "post" (content, user_id) VALUES
        ('Hello World!', 1),
        ('This is a test post.', 2),
        ('This is another test post.', 3)
        """)

# Einige Likes erzeugen
cursor.execute("""
    INSERT INTO "like" (user_id, post_id) VALUES
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 1),
        (2, 2),
        (3, 1),
        (4, 1),
        (4, 2),
        (4, 3)
        """)

# Erstellen Sie einige Kommentare
cursor.execute("""
    INSERT INTO "comment" (content, user_id, post_id) VALUES
        ('Hello Stranger!', 1, 1),
        ('What a wonderful world!', 2, 1),
        ('Greetings everyone.', 4, 1),
        ('(╯°□°)╯︵ ┻━┻', 1, 2),
        ('┬─┬ノ( º _ ºノ)', 3, 2)
        """)

print("Database tables have been created.")
# Schliessen des Cursors und der Verbindung
cursor.close()
connection.close()
