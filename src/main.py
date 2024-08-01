from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from src.dataset_loader import DatasetLoader 


from src.worker import run_get_association_task

from pydantic import BaseModel


class InputToAssociate(BaseModel):
    idco45: str
    importo_tot: float


app = FastAPI()

@app.post("/get_association", status_code=201)
def run_get_association(input_to_associate: InputToAssociate):
    task = run_get_association_task.delay(input_to_associate.idco45, input_to_associate.importo_tot)
    return JSONResponse({"task_id": task.id})

