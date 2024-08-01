from association_algorithm import AssociationAlgorithm
from dataset_loader import DatasetLoader
from metrics_associati import MetricsAssociati
import pandas as pd


mandati_associati_path = "../data/03158_ASSOCIATI_13_05_24.xls"
mandati_non_associati_path = "../data/03158_NON_ASSOCIATI_13_05_24.xls"
enti_path = "../data/03158_IBAN_ENTI_13_05_24.xls"
pratiche_path = "../data/03158_pratiche_17_05_2024.csv"

dataset_loader = DatasetLoader(mandati_associati_path, mandati_non_associati_path, enti_path, pratiche_path)
association_algorithm = AssociationAlgorithm()
all_combinations = association_algorithm.get_list_all_combinations_for_metric(dataset_loader.mandati_associati, dataset_loader.iban_to_idente, dataset_loader.pratiche)

mandati_associati = pd.read_excel(mandati_associati_path)
metrics_associati = MetricsAssociati(all_combinations, mandati_associati)
metrics_associati.get_associati_metrics()