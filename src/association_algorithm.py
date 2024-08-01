import re

class AssociationAlgorithm():
    
    def __init__(self):
        self.identi_none = 0
        self.iban_none = 0
        self.n_caso1 = 0
        self.n_caso2 = 0
        self.n_caso3 = 0
        self.n_nessuno_dei_tre = 0
        self.association_caso3_does_not_exist = 0
        self.greater_than_20 = 0
        self.iban_banca_sistema = 0
        self.iban_inps = 0

    def get_id_ente(self, iban, iban_to_idente):
        id_ente = iban_to_idente.get(iban, None)
        if id_ente is None:
            self.identi_none += 1
            return None
        return id_ente


    def get_pratiche_by_ente_and_stato(self, id_ente, pratiche, perfezionamento, sinistro, estinte):
        if perfezionamento and not sinistro and not estinte:
            return pratiche[(pratiche['IDENTE'] == id_ente) & (pratiche['STATO'] == "Perfezionamento")]
        elif perfezionamento and sinistro and not estinte:
            return pratiche[(pratiche['IDENTE'] == id_ente) & ((pratiche['STATO'] == "Perfezionamento") | (pratiche['STATO'] == "Sinistro"))]
        elif perfezionamento and sinistro and estinte:
            return pratiche[(pratiche['IDENTE'] == id_ente) & ((pratiche['STATO'] == "Perfezionamento") | (pratiche['STATO'] == "Sinistro") | (pratiche['STATO'] == "Estinta"))]
        else:
            print("THIS SHOULD NOT BE PRINTED MOTHER FUCKER")


    # TODO: sort by DATA STATO just in case 3
    # TODO: we hardcodded 20
    def backtrackig_case3(self, target, id_ente, pratiche, perfezionamento, sinistro, estinte):
        candidates = self.get_pratiche_by_ente_and_stato(id_ente, pratiche, perfezionamento=perfezionamento, sinistro=sinistro, estinte=estinte)
        if len(candidates) > 20: # TODO: to dehardcodde
            return ["greater_than_20"]
        # NOTE: we consider only candiates with len <= 20
        # We cut off IMPORTO_RATA that is greater than the input "target" because if IMPORTO_RATA is greater, we will never be able to find a combination that matches `target` 
        candidates = [(candidates['ID_PRATICA'].iloc[i], candidates['IMPORTO_RATA'].iloc[i]) for i in range(len(candidates)) if candidates['IMPORTO_RATA'].iloc[i] < target]
        ans = []
        def backtrack(idx, currlist):
            nonlocal ans
            if sum([importo for _, importo in currlist]) == target:
                ans.append(currlist.copy())
                return
            if sum([importo for _, importo in currlist]) > target:
                return
            for i in range(idx, len(candidates)):
                currlist.append(candidates[i])
                backtrack(i+1, currlist)
                currlist.pop()
        backtrack(0, [])
        return ans if ans else None

    def get_combinations(self, pratiche_ente, importo_tot, id_ente, pratiche): # NOTE: `pratiche` here is already filtered by "Perfezionamento" in `get_pratiche_by_ente_and_stato()`
        # Caso 1
        filteredpratiche = pratiche_ente[(pratiche_ente['IMPORTO_RATA'] == importo_tot)]
        sum_importo_rata = pratiche_ente['IMPORTO_RATA'].sum()

        if len(filteredpratiche) == 1:
            self.n_caso1 += 1
            return [(filteredpratiche.iloc[0]['ID_PRATICA'], filteredpratiche.iloc[0]['IMPORTO_RATA'])], "caso1"
        elif importo_tot == sum_importo_rata: # Caso 2
            self.n_caso2 +=1
            return list(zip(pratiche_ente['ID_PRATICA'], pratiche_ente['IMPORTO_RATA'])), "caso2"

        # Caso3
        elif importo_tot != sum_importo_rata:
            self.n_caso3 += 1 
            combinations_caso3_1 = self.backtrackig_case3(importo_tot, id_ente, pratiche, perfezionamento=True, sinistro=False, estinte=False) # NOTE: we are not passing `pratiche_ente` in `backtrackig_case3()` because we create it inside `backtrackig_case3()`
            combinations_caso3_2 = self.backtrackig_case3(importo_tot, id_ente, pratiche, perfezionamento=True, sinistro=True, estinte=False) # NOTE: we are not passing `pratiche_ente` in `backtrackig_case3()` because we create it inside `backtrackig_case3()`
            combinations_caso3_3 = self.backtrackig_case3(importo_tot, id_ente, pratiche, perfezionamento=True, sinistro=True, estinte=True) # NOTE: we are not passing `pratiche_ente` in `backtrackig_case3()` because we create it inside `backtrackig_case3()`
            if not combinations_caso3_1 and not combinations_caso3_2 and not combinations_caso3_3:
                self.association_caso3_does_not_exist += 1
                return None, "caso3"
            
            combinations_merged = []
            if combinations_caso3_1:
                combinations_merged.extend(combinations_caso3_1)
                combinations_merged.extend(combinations_caso3_2)
                combinations_merged.extend(combinations_caso3_3)
            elif combinations_caso3_2:
                combinations_merged.extend(combinations_caso3_2)
                combinations_merged.extend(combinations_caso3_3)
            else:
                combinations_merged.extend(combinations_caso3_3)

            if all(elem == "greater_than_20" for elem in combinations_merged): # NOTE: TO REFACTOR: I have done that because I wanted to distingush between cases greater_than_20 and `combinations_caso3` is None which means that we did not find any combination for that input
                self.greater_than_20 += 1
                return "greater_than_20", "caso3"
            
            combinations_merged = [combination for combination in combinations_merged if combination != "greater_than_20"]
            return combinations_merged, "caso3"
        
        self.n_nessuno_dei_tre += 1
       
    def extract_iban(idco45):
        iban_match = re.search(r'RIF:([A-Z]{2}[0-9]{2}(?:\s?[A-Z0-9]){1,30})NOTE', idco45)
        if not iban_match:
            iban_match = re.search(r'IBANORD([A-Z]{2}[0-9]{2}[A-Z0-9]{1,30})\*', idco45)

        iban = iban_match.group(1) if iban_match else None
        return iban
    
    def get_associations(self, idco45, importo_tot, manuale, dtinput, iban_to_idente, pratiche):
        iban = AssociationAlgorithm.extract_iban(idco45)

        if iban == "IT75I0315801600BO0990000300":
            self.iban_banca_sistema += 1
            return None, "banca_sistema"
        
        if "INPS" in idco45 or "I.N.P.S" in idco45:
            self.iban_inps += 1

        if not iban:
            self.iban_none += 1
            return None, "iban_none"
        
        id_ente = self.get_id_ente(iban, iban_to_idente)
        if not id_ente:
            return None, "identi_none"

        pratiche_ente = self.get_pratiche_by_ente_and_stato(id_ente, pratiche, perfezionamento=True, sinistro=False, estinte=False)

        return self.get_combinations(pratiche_ente, importo_tot, id_ente, pratiche) # NOTE: here we are passing both `pratiche_ente` and `pratiche` because in case3 we need to have `pratiche` which is initially filtered by Perfezionamento, then we need both Perfezionamento and Estinte and then Perfezionamento, Estinte and Sinistro


    def get_list_all_combinations_for_metric(self, mandati_associati, iban_to_idente, pratiche_new):
        all_combinations = []
        for _, row in mandati_associati.iterrows():
            importo_tot = row['IMPO_TOTALE']
            idco45 = row['IDCO45']
            manuale = row['MANUALE']
            dtinput = row['DTINPUT']
            # TODO: why `dtinput` is not used?
            combinations, case_type = self.get_associations(idco45, importo_tot, manuale, dtinput, iban_to_idente, pratiche_new)

            if combinations is not None and combinations != "greater_than_20":
                all_combinations.append({'IDCO45': idco45, 'combinations': combinations, 'DTINPUT': dtinput, "case_type": case_type})
        
        n_rows_test = len(mandati_associati)
        print(f"Total rows examinated: {n_rows_test}")
        print(f"numb. of casi 1: {self.n_caso1}")
        print(f"numb. of casi 2: {self.n_caso2}")
        print(f"numb. of casi 3: {self.n_caso3}")
        print(f"numb. of n_nessuno_dei_tre: {self.n_nessuno_dei_tre}")
        print(f"Number of IBAN None: {self.iban_none}")
        print(f"Number of missing IDENTE: {self.identi_none}")
        print(f"Number of non existance case 3 combination: {self.association_caso3_does_not_exist}")
        print(f"Number of case 3 with candiates greater than 20: {self.greater_than_20}")
        print(f"Number of iban banca sistema: {self.iban_banca_sistema}")
        print(f"Number of total iban inps: {self.iban_inps}")
        
        return all_combinations

