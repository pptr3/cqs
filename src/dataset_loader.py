import re
import pandas as pd

class DatasetLoader():

    def __init__(self, mandati_associati_path, mandati_non_associati_path, enti_path, pratiche_path):
        self.mandati_associati = pd.read_excel(mandati_associati_path)
        self.mandati_associati = self.__uniform_datetime(self.mandati_associati)
        self.mandati_associati = self.__remove_tipo_pagamento(self.mandati_associati).iloc[-1000:, :]

        # NOTE: currently not used because this is going to be used for a single "get association()". Still this is not going to be used in the future
        # as we will get new mandati non associati that need to be associated (we can get either a matrix in input or a single row and we
        # will need to find association for all of them)
        self.mandati_non_associati = pd.read_excel(mandati_non_associati_path)
        self.mandati_non_associati["DTINPUT"] = pd.to_datetime(self.mandati_non_associati["DTINPUT"], format="%d.%m.%Y")

        self.enti = pd.read_excel(enti_path)
        self.enti = self.__uniform_enti_iban(self.enti)

        self.pratiche = pd.read_csv(pratiche_path, delimiter=";", encoding="latin1")
        self.pratiche["DATA_STATO"] = pd.to_datetime(self.pratiche["DATA_STATO"], format="%d/%m/%Y")
        self.pratiche = self.__uniform_pratiche(self.pratiche)

        self.iban_to_idente = self.enti.set_index('IBAN_ACCREDITO')['IDENTE'].to_dict()
    
    def __uniform_datetime(self, dataframe):
        dataframe["DTINPUT"] = pd.to_datetime(dataframe["DTINPUT"], format="%d/%m/%Y")
        return dataframe

    def __uniform_enti_iban(self, enti_dataframe):
        enti_dataframe['IBAN_ACCREDITO'] = enti_dataframe['IBAN_ACCREDITO'].str.replace(r'NOTE.*', '', regex=True)
        return enti_dataframe
    
    def __uniform_pratiche(self, pratiche_dataframe):
        pratiche_dataframe['IMPORTO_RATA'] = pratiche_dataframe['IMPORTO_RATA'].str.replace(',', '.').astype(float)
        pratiche_dataframe['ID_PRATICA'] = pratiche_dataframe['ID_PRATICA'].astype(float)
        return pratiche_dataframe
    
    def __remove_tipo_pagamento(self, associati_dataframe):
        associati_dataframe = associati_dataframe[associati_dataframe['TIPO_PAG'].isin(['Z', 'F', 'A', 'PDR'])].drop_duplicates(subset=['IDCO45', 'DTINPUT'], keep='last')
        return associati_dataframe