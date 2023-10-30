import sqlite3
import pandas as pd
import json
from fastapi import HTTPException
from watchfiles.cli import logger
import re

class DataUtils:
    def __init__(self, sqlite_db):
        self.sqlite_db = sqlite_db

    def get_data(self, table_name):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT * FROM {table_name}
            ''')

            column_names = [description[0] for description in cursor.description]
            data = cursor.fetchall()
            conn.close()

            response = []
            for row in data:
                response_row = {}
                for i, column_name in enumerate(column_names):
                    response_row[column_name] = row[i]
                response.append(response_row)

            return response

        except Exception as e:
            error_message = f"Si è verificato un errore: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    def valid_input_table(self, table_name: str):
        pattern = re.compile('[\'!?#]')
        if pattern.search(table_name):
            return False
        return True

    def valid_input_data(self, data):
        pattern = re.compile('[\'!?#]')
        for key, value in data.items():
            if pattern.search(str(key)) or pattern.search(str(value)):
                return False
        return True

    def create_table_with_data(self, data, table_name):
        try:
            if not self.valid_input_table(table_name):
                error_message = f"Il nome della tabella {table_name} contiene caratteri speciali. Impossibile creare la tabella."
                print(f"Il nome della tabella {table_name} contiene caratteri speciali. Impossibile creare la tabella.")
                raise ValueError(error_message)

            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()

            if table_name == "regioni":
                column_names = list(data[0].keys())
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {column_names[0]} INTEGER PRIMARY KEY,
                        {column_names[1]} VARCHAR
                    )
                ''')
                for record in data:
                    cursor.execute(
                        f'INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}) VALUES (?, ?)',
                        (record[column_names[0]], record[column_names[1]])
                    )
            else:
                column_names = list(data[0].keys())
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER,
                        {column_names[0]} INTEGER,
                        {column_names[1]} INTEGER,
                        {column_names[2]} INTEGER,
                        {column_names[3]} INTEGER,
                        CONSTRAINT pk_{table_name} PRIMARY KEY (id),
                        CONSTRAINT fk_{table_name} FOREIGN KEY ({column_names[0]}) REFERENCES regioni(id_regione)
                    )
                ''')
                for record in data:
                    cursor.execute(
                        f'INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}, {column_names[2]}, {column_names[3]}) VALUES (?, ?, ?, ?)',
                        (record[column_names[0]], record[column_names[1]], record[column_names[2]],
                         record[column_names[3]])
                    )

            conn.commit()
            conn.close()

            print(f"Tabella '{table_name}' creata nel database '{self.sqlite_db}' e dati inseriti con successo.")
        except Exception as e:
            error_message = f"Si è verificato un errore: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    def create_empty_table(self, column_name, table_name):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            query = f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY'
            has_region = False
            for col in column_name:
                if col == 'regione':
                    query += f', {col} INTEGER, FOREIGN KEY ({col}) REFERENCES regioni(id_regione)'
                    has_region = True
                else:
                    query += f', {col} INTEGER'
            query += ')'
            cursor.execute(query)

            conn.commit()
            conn.close()
            if has_region:
                print("Chiave esterna per 'regione' aggiunta correttamente.")
        except Exception as e:
            error_message = f"Si è verificato un errore: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    def insert_data_from_json(self, data, table_name):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            if data:
                column_names = list(data[0].keys())
                cursor = conn.cursor()
                for record in data:
                    cursor.execute(
                        f'INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}, {column_names[2]}, {column_names[3]}) VALUES (?, ?, ?, ?)',
                        (
                            record[column_names[0]], record[column_names[1]], record[column_names[2]],
                            record[column_names[3]]
                        ))

                conn.commit()
                conn.close()

                print(f'Dati inseriti con successo nella tabella {table_name}')
        except Exception as e:
            error_message = f"Si è verificato un errore: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    def create_dataframe_from_sql(self, tabella):
        try:
            conn = sqlite3.connect(self.sqlite_db)

            query = input("Inserire la query: ")

            df = pd.read_sql(query, conn)

            conn.close()

            return df
        except Exception as e:
            print(f"Si è verificato un errore: {str(e)}")

    def delete_data(self, data, table_name):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()

            for record in data:
                regione = record.get("Regione")
                anno = record.get("Anno")
                cursor.execute(f"DELETE FROM {table_name} WHERE Regione = ? AND Anno = ?", (regione, anno))

            conn.commit()
            conn.close()

            print(f'Dati eliminati con successo dalla tabella {table_name}')

        except Exception as e:
            error_message = f"Si è verificato un errore: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    def update_table(self, table_name, new_value, condition_column, condition_value, condition_id):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            query = f'''
                UPDATE {table_name}
                SET {condition_column} = ?
                WHERE {condition_id} = ?
            '''
            cursor.execute(query, (new_value, condition_value))

            conn.commit()
            conn.close()

            print(f"Dati nella tabella '{table_name}' aggiornati con successo.")
        except Exception as e:
            error_message = f"Si è verificato un errore durante l'aggiornamento: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)
