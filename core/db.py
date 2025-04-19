import mysql.connector
import numpy as np

def connect_db():
    return mysql.connector.connect(
        host="MySQL-8.2",
        port=3306,
        user="root",
        password="",
        database="faceid"
    )

def insert_person(first_name, last_name, username, phone, telegram, whatsapp):
    # Добавляем префиксы, если нужно
    telegram = f"@{telegram}" if telegram and not telegram.startswith("@") else telegram
    whatsapp = f"https://wa.me/{whatsapp}" if whatsapp and not whatsapp.startswith("http") else whatsapp

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO people (first_name, last_name, username, phone, telegram, whatsapp)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (first_name, last_name, username, phone, telegram, whatsapp))

    conn.commit()
    person_id = cursor.lastrowid
    conn.close()
    return person_id



def insert_photo(person_id, photo_blob, face_encoding):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO photos (person_id, photo, face_encoding)
        VALUES (%s, %s, %s)
    ''', (person_id, photo_blob, face_encoding.tobytes()))

    conn.commit()
    conn.close()

def get_all_photos():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.first_name, p.last_name, p.username, p.phone, p.telegram, p.whatsapp, ph.face_encoding
        FROM people p
        JOIN photos ph ON p.id = ph.person_id
    ''')
    people_photos = cursor.fetchall()
    conn.close()
    return people_photos


def get_person_by_username(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, first_name, last_name FROM people WHERE username = %s', (username,))
    result = cursor.fetchone()
    conn.close()
    return result  # Вернёт (id, first_name, last_name) или None

def get_person_by_username_full(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM people WHERE username = %s', (username,))
    result = cursor.fetchone()
    conn.close()
    return result


def update_person(username, first_name, last_name, phone, telegram, whatsapp):
    telegram = f"@{telegram}" if telegram and not telegram.startswith("@") else telegram
    whatsapp = f"https://wa.me/{whatsapp}" if whatsapp and not whatsapp.startswith("http") else whatsapp

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE people
        SET first_name=%s, last_name=%s, phone=%s, telegram=%s, whatsapp=%s
        WHERE username=%s
    ''', (first_name, last_name, phone, telegram, whatsapp, username))

    conn.commit()
    conn.close()

def update_single_field(username, field, value):
    if field == "telegram" and not value.startswith("@"):
        value = f"@{value}"
    if field == "whatsapp" and not value.startswith("http"):
        value = f"https://wa.me/{value}"

    conn = connect_db()
    cursor = conn.cursor()
    query = f"UPDATE people SET {field} = %s WHERE username = %s"
    cursor.execute(query, (value, username))
    conn.commit()
    conn.close()