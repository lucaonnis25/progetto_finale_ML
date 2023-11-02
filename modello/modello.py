import numpy as np
import pandas as pd
from fastapi import HTTPException
from pypmml import Model
import requests

class Predict:

    def __init__(self, sqlite_db):
        self.sqlite_db = sqlite_db

    def predict_data(self, url):
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

            return json_output

        except Exception as e:
            raise Exception(f"Si è verificato un errore durante la previsione: {str(e)}")
