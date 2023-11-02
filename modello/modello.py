import numpy as np
import pandas as pd
from fastapi import HTTPException
from pypmml import Model
import requests

class Predict:

    def __init__(self, sqlite_db):
        self.sqlite_db = sqlite_db

    def predict_and_save(self, data: dict):
        try:
            url = data.get("url")
            df = pd.read_csv(url, encoding='UTF-8', sep=";")
            # sostituisco gli spazi bianchi tra i nomi delle colonne con un _ perché potrebbero dare problemi con il db
            df.columns = df.columns.str.replace(' ', '_')
            #print(df)
            colonne_da_eliminare = ['density', 'volatile_acidity', 'total_sulfur_dioxide']
            for col in colonne_da_eliminare:
                if col in df.columns:
                    df = df.drop(col, axis=1)
            print(df)
            model = Model.fromFile('modello/wine_quality.pmml')
            y_pred = model.predict(df)
            # arrotondo l'output del modello visto che nel dataset originale i valori erano interi
            y_pred = np.round(y_pred)
            print(y_pred)
            real_quality = df['quality']
            print(f'real quality{real_quality}')
            # creo il df da inserire nel db
            df_db = pd.concat([real_quality, y_pred], axis=1)
            print(df_db)
            json_output = df_db.to_json(orient="records")
            print(json_output)

            #creazione della tabella vuota per inserire i risultati
            url_tabella_vuota = "http://localhost:8000/crea_tabella_vuota"
            json_tabella = {
                "table_name": "risultati_modello",
                "column_name": ["quality", "predicted_quality"]
            }
            requests.post(url_tabella_vuota, json=json_tabella)

            # Effettuare la richiesta POST per inserire i dati nel database
            url_inserimento = "http://localhost:8000/inserisci"
            json_dati = {
                "table_name": "risultati_modello",
                "data": json_output
            }
            response = requests.post(url_inserimento, json=json_dati)

            if response.status_code == 200:
                print("Dati inseriti nel database con successo.")
            else:
                print(f"Si è verificato un errore durante la richiesta: {response.text}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Si è verificato un errore durante l'elaborazione: {str(e)}")

