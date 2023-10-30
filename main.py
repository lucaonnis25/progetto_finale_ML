import sqlite3
from fastapi import FastAPI, HTTPException
from DB.data_utils import DataUtils

app = FastAPI()
sqlite_db = 'dbML.sqlite'

@app.get("/")
async def root():
    return {"message": "Hello World"}

# CREATE
@app.post("/crea_con_dati")
async def create_table_with_data(json_data: dict):
    try:
        # estrazione dati da json
        table_name = json_data.get("table_name", "")
        data = json_data.get("data", [])

        utils = DataUtils(sqlite_db)
        utils.create_table_with_data(data, table_name)

        return {"message": "Tabella con dati salvati nel database con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crea_vuoto")
async def create_empty_table(json_data: dict):
    try:
        table_name = json_data.get("table_name", "")
        column_name = json_data.get("column_name", [])

        utils = DataUtils(sqlite_db)
        utils.create_empty_table(column_name, table_name)
        return {"message": f"Tabella {table_name} creata con successo"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# INSERT
@app.post("/inserisci")
async def insert_json_into_table(json_data: dict):
    try:
        # estrazione dati da json
        table_name = json_data.get("table_name", "")
        data = json_data.get("data", [])

        utils = DataUtils(sqlite_db)

        utils.insert_data_from_json(data, table_name)

        return {"message": "Dati JSON inseriti nel database con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
