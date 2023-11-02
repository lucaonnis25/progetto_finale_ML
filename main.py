import sqlite3
from fastapi import FastAPI, HTTPException
from DB.data_utils import DataUtils
from modello.modello import Predict
import pandas as pd
from pypmml import Model

app = FastAPI()
sqlite_db = 'dbML.sqlite'

@app.get("/")
async def root():
    return {"message": "Hello World"}

# GET
# passare json con table_name : nome tabella desiderata
@app.post("/get")
async def get_data_json(json_data: dict):
    try:
        table_name = json_data.get("table_name", "")

        utils = DataUtils(sqlite_db)
        data = utils.get_data(table_name)
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


# CREATE
@app.post("/crea_con_dati")
async def create_table_with_data(json_data: dict):
    try:
        # estrazione dei dati contenuti nel json
        table_name = json_data.get("table_name", "")
        data = json_data.get("data", [])

        utils = DataUtils(sqlite_db)
        utils.create_table_with_data(data, table_name)

        return {"message": "tabella con dati salvata nel database con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crea_tabella_vuota")
async def create_empty_table(json_data: dict):
    try:
        table_name = json_data.get("table_name", "")
        column_name = json_data.get("column_name", [])

        utils = DataUtils(sqlite_db)
        utils.create_empty_table(column_name, table_name)
        return {"message": f"tabella {table_name} creata con successo"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# INSERT
@app.post("/inserisci")
async def insert_json_into_table(json_data: dict):
    try:
        # estrazione dei dati contenuti nel json
        table_name = json_data.get("table_name", "")
        data = json_data.get("data", [])

        utils = DataUtils(sqlite_db)

        utils.insert_data_from_json(data, table_name)

        return {"message": "dati inseriti nel database con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#DELETE
@app.delete("/delete")
async def delete_data_from_table(json_data: dict):
    try:
        table_name = json_data.get("table_name", "")
        data = json_data.get("data", [])

        utils = DataUtils(sqlite_db)

        utils.delete_data(data, table_name)

        return {"message": "dati eliminati con successo."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#UPDATE
@app.put("/update")
async def update_data(json_data: dict):
    try:
        table_name = json_data.get('table_name')
        condition_column = json_data.get('condition_column')
        condition_value = json_data.get('condition_value')
        new_value = json_data.get('new_value')
        condition_id = json_data.get('condition_id')

        utils = DataUtils(sqlite_db)
        utils.update_table(table_name, new_value, condition_column, condition_value, condition_id)

        return {"message": f"aggiornamento della tabella '{table_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Si è verificato un errore: {str(e)}")

# TEST DEL MODELLO
@app.post("/predict")
async def predict(json_data:dict):
    try:
        url = json_data.get('url')
        df = pd.read_csv(url)
        model = Model.fromFile('modello/wine_quality.pmml')
        y_pred = model.predict(df)
        print(y_pred)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Si è verificato un errore durante l'elaborazione: {str(e)}")


