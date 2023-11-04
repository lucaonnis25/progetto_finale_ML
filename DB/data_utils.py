import sqlite3
import pandas as pd
import json
from fastapi import HTTPException
from watchfiles.cli import logger
import re

# Classe per interazione con db
class DataUtils:
    # inizializzo la classe passando il db da utilizzare
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

# utilizzo questa funzione per importare i dataset che hanno già dei dati al loro interno
    def create_table_with_data(self, data, table_name):
        try:
            if not self.valid_input_table(table_name):
                error_message = f"Il nome della tabella {table_name} contiene caratteri speciali. Impossibile creare la tabella."
                print(f"Il nome della tabella {table_name} contiene caratteri speciali. Impossibile creare la tabella.")
                raise ValueError(error_message)

            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()

            column_names = list(data[0].keys())
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER,
                    {column_names[0]} REAL,
                    {column_names[1]} REAL,
                    {column_names[2]} REAL,
                    {column_names[3]} REAL,
                    {column_names[4]} REAL,
                    {column_names[5]} REAL,
                    {column_names[6]} REAL,
                    {column_names[7]} REAL,
                    {column_names[8]} REAL,
                    {column_names[9]} REAL,
                    {column_names[10]} REAL,
                    {column_names[11]} REAL,
                    CONSTRAINT pk_{table_name} PRIMARY KEY (id)
                )
            ''')
            for record in data:
                cursor.execute(
                    f'INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}, {column_names[2]}, {column_names[3]}, {column_names[4]}, {column_names[5]}, {column_names[6]}, {column_names[7]}, {column_names[8]}, {column_names[9]}, {column_names[10]}, {column_names[11]}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)',
                    (record[column_names[0]], record[column_names[1]], record[column_names[2]],
                     record[column_names[3]], record[column_names[4]], record[column_names[5]], record[column_names[6]],
                     record[column_names[7]], record[column_names[8]], record[column_names[9]], record[column_names[10]],
                     record[column_names[11]])
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

            for col in column_name:
                query += f', {col} REAL'
            query += ')'
            cursor.execute(query)

            conn.commit()
            conn.close()

        except Exception as e:
            error_message = f"Si è verificato un errore: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

# funzione per inserire dati in una tabella esistente
    def insert_data_from_json(self, data, table_name):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            if data:
                column_names = list(data[0].keys())
                cursor = conn.cursor()
                for record in data:
                    cursor.execute(
                    f'INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}, {column_names[2]}, {column_names[3]}, {column_names[4]}, {column_names[5]}, {column_names[6]}, {column_names[7]}, {column_names[8]}, {column_names[9]}, {column_names[10]}, {column_names[11]}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)',
                    (record[column_names[0]], record[column_names[1]], record[column_names[2]],
                     record[column_names[3]], record[column_names[4]], record[column_names[5]], record[column_names[6]],
                     record[column_names[7]], record[column_names[8]], record[column_names[9]], record[column_names[10]],
                     record[column_names[11]])

                        )

                conn.commit()
                conn.close()

                print(f'Dati inseriti con successo nella tabella {table_name}')
        except Exception as e:
            error_message = f"Si è verificato un errore: {str(e)}"
            print(error_message)
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    def insert_risultati_modello(self, data, table_name):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            column_names = list(data[0].keys())
            for record in data:
                cursor.execute(f"INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}) VALUES (?, ?)",
                               (record[column_names[0]], record[column_names[1]]))

            conn.commit()
            conn.close()

            return {"message": "Dati inseriti nel database con successo."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    def delete_data(self, data, table_name):
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()

            for record in data:
                id_value = record.get("id")
                cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (id_value,))

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
