import sys
import os
import sqlite3
from flask import Flask
import json

SQL_PATH = './res/create-db.sql'  # Путь к файлу со схемой базы данных
SOURCE_DB_PATH = './res/animal.db'  # Путь конвертируемой базы


def update_dictionary(destination, table_name, value):
    cursor = destination.cursor()

    # Запрашиваем данные из словаря
    cursor.execute(f'SELECT id FROM {table_name} WHERE name="{value}"')
    row = cursor.fetchone()

    if row:
        # Если запись есть, возвращаем id
        return row['id']

    # Запрашивает число всех записей
    cursor.execute(f'SELECT count(*) as rows_count FROM {table_name}')
    row = cursor.fetchone()

    # Создаём новую запись
    new_id = int(row["rows_count"]) + 1  # Новый id
    cursor.execute(f'INSERT INTO {table_name} VALUES({new_id}, "{value}")')

    return new_id


def text_or_null(value, default_value='NULL'):
    return f'"{value}"' if value is not None else default_value


def push_row(destination, row):

    # Проверяем словари
    animal_type_id = update_dictionary(destination, 'animal_types', row['animal_type'])
    primary_color_id = update_dictionary(destination, 'colors', row['color1'])
    secondary_color_id = update_dictionary(destination, 'colors', row['color2'])
    outcome_subtype_id = update_dictionary(destination, 'outcome_subtypes', row['outcome_subtype'])
    outcome_type_id = update_dictionary(destination, 'outcome_types', row['outcome_type'])
    breed_id = update_dictionary(destination, 'breeds', row['breed'])

    # Обычные записи
    name = row['name']
    date_of_birth = row['date_of_birth']
    age_upon_outcome = row['age_upon_outcome']
    animal_id = row['animal_id']
    outcome_date = f'{row["outcome_year"]}-{str(row["outcome_month"]).rjust(2, "0")}-00'

    # Делаем новую запись
    cursor = destination.cursor()
    query = f"""
        REPLACE INTO animals (
            animal_type,
            primary_color,
            secondary_color,
            outcome_subtype,
            outcome_type,
            breed,
            name,
            date_of_birth,
            age_upon_outcome,
            id,
            outcome_date
        ) VALUES (
            {animal_type_id},
            {primary_color_id},
            {secondary_color_id},
            {outcome_subtype_id},
            {outcome_type_id},
            {breed_id},
            {text_or_null(name)},
            "{date_of_birth}",
            "{age_upon_outcome}",
            "{animal_id}",
            "{outcome_date}"
        )
    """

    try:
        cursor.execute(query)

        return True
    except sqlite3.Error:
        return False


def convert_db(source_path, destination_path):
    with sqlite3.connect(destination_path) as destination:
        destination.row_factory = sqlite3.Row

        with open(SQL_PATH, mode='r') as f:
            # Выполняем инициирующий скрипт
            destination.executescript(f.read())
            destination.commit()

        with sqlite3.connect(source_path) as source:
            # Наполняем новую базу, построчно

            source.row_factory = sqlite3.Row
            cursor_source = source.cursor()

            cursor_source.execute('Select * FROM animals')
            rows = cursor_source.fetchall()

            errors = 0

            for row in rows:
                if not push_row(destination, row):
                    errors += 1

            return len(rows) != errors


def start_server(database_path):
    app = Flask('__main__')

    @app.route('/<index>')
    def index_view(index):
        with sqlite3.connect(database_path) as database:
            database.row_factory = sqlite3.Row
            cursor = database.cursor()

            query = f"""
                SELECT
                    animals.name,
                    animals.date_of_birth,
                    animals.age_upon_outcome,
                    animals.id,
                    animals.outcome_date,
                    animal_types.name AS animal_type,
                    outcome_types.name AS outcome_type,
                    outcome_subtypes.name AS outcome_subtype,
                    breeds.name AS breed,
                    C1.name AS primary_color,
                    C2.name AS secondary_color
                FROM
                    animals,
                    animal_types,
                    outcome_types,
                    outcome_subtypes,
                    breeds
                    JOIN colors AS C1
                        ON animals.primary_color = C1.id
                    JOIN colors AS C2
                        ON animals.secondary_color = C2.id
                WHERE
                    animals.id="{index}"
                    AND animals.animal_type = animal_types.id
                    AND animals.outcome_type = outcome_types.id
                    AND animals.outcome_subtype = outcome_subtypes.id
                    AND animals.breed = breeds.id
            """
            cursor.execute(query)

            return json.dumps(dict(cursor.fetchone()))

    app.run(debug=True)


def run(source_path, destination_path):

    if not source_path or not os.path.isfile(source_path):
        # Проверяем наличие конвертируемой базы
        print(f'File {source_path} not found')
        return

    database_path = None

    if destination_path:
        # Если указан destination_db, конвертируем

        if os.path.isfile(destination_path):
            # Проверяем на существование базы назначения
            print(f'File {destination_path} is exists and will be updated')

        print('Converting...')

        if not convert_db(source_path, destination_path):
            # Если конвертировать не удалось, завершаем приложение
            print()
            return

        print('Converting...ok')

        database_path = destination_path
    else:
        # Если указан только source_db, то открываем его без конвертирования

        database_path = source_path

    # Запускаем Flask
    start_server(database_path)


if __name__ == '__main__':
    print('Start arguments: [source] [destination]')
    print('             or: [destination] for open existing database')

    if len(sys.argv) <= 1:
        # Запускаем с параметрами по умолчанию, для отладки
        run(SOURCE_DB_PATH, f'{SOURCE_DB_PATH}.converted.db')
    else:
        run(
            sys.argv[1],
            sys.argv[2] if len(sys.argv) > 2 else None
        )
