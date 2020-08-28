import sqlite3

connection = sqlite3.connect('main.db')
cursor = connection.cursor()

tables = [
    "CREATE TABLE users (id int, username text, password text, \
serial text, email text, prof int, name text, is_active boolean)",
    "CREATE TABLE orders (id int, proficiency int, task_text text, \
cnc text, device_type int, is_done boolean, time text)",
    "CREATE TABLE devices (id int, device_type int)",
    "CREATE TABLE device_types (id int, prof int, description text)"
    ]
for table in tables:
    cursor.execute(table)

user = (1, 'mise', 'some hash', '321670', 'mikhaylow@mirea.ru', 3,
        'Михайлов С.Р.', True)
user_insert = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
cursor.execute(user_insert, user)

orders = [
    (1, 2, 'task1.html', '', 1, False, '01:00:00'),
    (2, 2, 'task2.html', 'program2.cnc', 2, False, '01:15:00')
]
order_insert = "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)"
cursor.executemany(order_insert, orders)

devices = [
    (1, 1),
    (2, 1),
    (3, 2)
]
device_insert = "INSERT INTO devices VALUES (?, ?)"
cursor.executemany(device_insert, devices)

device_types = [
    (1, 1, "name without cnc"),
    (2, 3, "name with cnc")
]
type_insert = "INSERT INTO device_types VALUES (?, ?, ?)"
cursor.executemany(type_insert, device_types)

connection.commit()

select_user = "SELECT * FROM users"  # where serial = {}"
x = (cursor.execute(select_user))
for y in x: print(y)

connection.close()
