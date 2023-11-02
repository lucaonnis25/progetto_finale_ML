import sqlite3
from fastapi import FastAPI, HTTPException
from DB.data_utils import DataUtils
from modello.modello import Predict
import requests
# inizializzazione fast_api
app = FastAPI()
sqlite_db = 'dbML.sqlite'

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

@app.post("/risultati_modello")
async def insert_json_model(json_data: dict):
    try:
        # estrazione dei dati contenuti nel json
        table_name = json_data.get("table_name", "")
        data = json_data.get("data", [])

        utils = DataUtils(sqlite_db)

        utils.insert_risultati_modello(data, table_name)

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
async def predict(data: dict):
    try:
        url = data.get("url")
        predict = Predict(sqlite_db)
        json_model_data = predict.predict_data(url)
        print(json_model_data)

        json_dati = {
            "table_name": "risultati_modello",
            "data": [{"quality":5,"predicted_quality":5.0},{"quality":5,"predicted_quality":5.0}]
        }
        response = requests.post("http://127.0.0.1:8000/risultati_modello", json=json_dati)

        if response.status_code == 200:
            return {"message": "Dati inseriti nel database con successo."}
        else:
            return {"message": "Si è verificato un errore durante l'inserimento nel database."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Si è verificato un errore durante l'elaborazione: {str(e)}")


