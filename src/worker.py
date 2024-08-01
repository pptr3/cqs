import os
from src.association_algorithm import AssociationAlgorithm
from src.dataset_loader import DatasetLoader 


from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="run_get_association")
def run_get_association_task(idco45, importo_tot):
    mandati_associati_path = "/app/data/03158_ASSOCIATI_13_05_24.xls"
    mandati_non_associati_path = "/app/data/03158_NON_ASSOCIATI_13_05_24.xls"
    enti_path = "/app/data/03158_IBAN_ENTI_13_05_24.xls"
    pratiche_path = "/app/data/03158_pratiche_17_05_2024.csv"
    
    dataset_loader = DatasetLoader(mandati_associati_path, mandati_non_associati_path, enti_path, pratiche_path)
    association, case_type = AssociationAlgorithm().get_associations(idco45, importo_tot, None, None, dataset_loader.iban_to_idente, dataset_loader.pratiche)
    print(association, flush=True)
    print("Caso: ", case_type, flush=True)
    
    return True
