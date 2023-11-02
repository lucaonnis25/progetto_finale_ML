import pandas as pd
from pypmml import Model

class Predict:
    def __init__(self, sqlite_db):
        self.sqlite_db = sqlite_db
    def predict(self, url):
        df = pd.read_csv(url)
        model = Model.fromFile('modello/wine_quality.pmml')
        y_pred = model.predict(df)

        print(y_pred)