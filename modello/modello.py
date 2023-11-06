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
            # per l'interazione con il db elimino gli spazi bianchi fra i nomi del df
            df.columns = df.columns.str.replace(' ', '_')

            # effettuo il drop dele colonne non utilizzate dal modello
            colonne_da_eliminare = ['density', 'volatile_acidity', 'total_sulfur_dioxide']
            for col in colonne_da_eliminare:
                if col in df.columns:
                    df = df.drop(col, axis=1)
            # richiamo il modello addestrato
            model = Model.fromFile('modello/wine_quality.pmml')
            y_pred = model.predict(df)
            # ho pensato di arrotondare i valori delle predizioni perché nei dati originali i valori di quality erano interi
            y_pred = np.round(y_pred)
            # estraggo i valori reali della quality dal df letto in partenza
            real_quality = df['quality']
            # creo un df con i dati di quality reali e quelli predetti per averne il confronto
            df_db = pd.concat([real_quality, y_pred], axis=1)
            # conversione in  striga json
            json_output = df_db.to_json(orient="records")
            # conversione in oggetto json
            json_output_object = json.loads(json_output)

            # volevo effettuare questa operazione passando il json dei risultati ad una funzione apposita chiamndo un'altra api ma per qualche motivo che sinceramente non sono riuscito a capire, la richiesta post sembrava andare in timeout e bloccava l'applicativo
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            column_names = list(json_output_object[0].keys())
            # salvataggio nel db
            for record in json_output_object:
                cursor.execute(f"INSERT INTO {table_name} ({column_names[0]}, {column_names[1]}) VALUES (?, ?)",
                               (record[column_names[0]], record[column_names[1]]))

            conn.commit()
            conn.close()
            # ritorno l'oggetto
            return json_output_object

        except Exception as e:
            raise Exception(f"Si è verificato un errore durante la previsione: {str(e)}")


