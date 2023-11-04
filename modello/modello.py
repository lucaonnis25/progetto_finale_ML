import json
import sqlite3
import numpy as np
import pandas as pd
from fastapi import HTTPException
from pypmml import Model
import requests


class Predict:

    def __init__(self, sqlite_db):
        self.sqlite_db = sqlite_db

    def predict_data(self, url, table_name):
        try:
            df = pd.read_csv(url, encoding='UTF-8', sep=";")
            df.columns = df.columns.str.replace(' ', '_')

            colonne_da_eliminare = ['density', 'volatile_acidity', 'total_sulfur_dioxide']
            for col in colonne_da_eliminare:
                if col in df.columns:
                    df = df.drop(col, axis=1)

            model = Model.fromFile('modello/wine_quality.pmml')
            y_pred = model.predict(df)
            y_pred = np.round(y_pred)
            real_quality = df['quality']

            df_db = pd.concat([real_quality, y_pred], axis=1)
            json_output = df_db.to_json(orient="records")
            json_output_object = json.loads(json_output)

            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            column_names = list(json_output_object[0].keys())
            for record in json_output_object:
                cursor.execute(f"INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}) VALUES (?, ?)",
                               (record[column_names[0]], record[column_names[1]]))

            conn.commit()
            conn.close()

            return json_output_object

        except Exception as e:
            raise Exception(f"Si è verificato un errore durante la previsione: {str(e)}")


