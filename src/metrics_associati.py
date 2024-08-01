import pandas as pd
import numpy as np

class MetricsAssociati():
    
    def __init__(self, all_combinations, mandati_associati):
        self.combinations_results = pd.DataFrame(all_combinations)
        self.mandati_associati = mandati_associati
        self.mandati_associati["DTINPUT"] = pd.to_datetime(mandati_associati["DTINPUT"], format="%d/%m/%Y")
        self.mandati_associati = mandati_associati[mandati_associati['TIPO_PAG'].isin(['Z', 'F', 'A', 'PDR'])]
        self.iban_inps = 0
        self.iban_inps_correctly_matched = 0

    def __create_predictions_dataframe(self, combinations_results):
        df1 = pd.DataFrame(columns=['combinations', 'DTINPUT', 'IDCO45', 'case_type'])
        df2 = pd.DataFrame(columns=['combinations', 'DTINPUT', 'IDCO45', 'case_type'])
        df3 = pd.DataFrame(columns=['combinations', 'DTINPUT', 'IDCO45', 'case_type'])
        for i in range(combinations_results.shape[0]):
            if combinations_results['case_type'].iloc[i] == "caso1":
                df1.loc[i] = [combinations_results['combinations'].iloc[i]] + [combinations_results['DTINPUT'].iloc[i]] + [combinations_results['IDCO45'].iloc[i]] + [combinations_results['case_type'].iloc[i]]
            elif combinations_results['case_type'].iloc[i] == "caso2":
                df2.loc[i] = [combinations_results['combinations'].iloc[i]] + [combinations_results['DTINPUT'].iloc[i]] + [combinations_results['IDCO45'].iloc[i]] + [combinations_results['case_type'].iloc[i]]
            elif combinations_results['case_type'].iloc[i] == "caso3":
                df3.loc[i] = [combinations_results['combinations'].iloc[i]] + [combinations_results['DTINPUT'].iloc[i]] + [combinations_results['IDCO45'].iloc[i]] + [combinations_results['case_type'].iloc[i]]
        return df1, df2, df3

    def __get_metrics_case12(self, df):
        combinations_df = df.explode('combinations').reset_index(drop=True)
        combinations_df['Y_pratica'] = combinations_df['combinations'].apply(lambda x: x[0])
        combinations_df['Y_importo'] = combinations_df['combinations'].apply(lambda x: x[1])
        combinations_df = combinations_df.drop(columns='combinations')

        r = []
        unique_idco45_dtinput = combinations_df[['DTINPUT', 'IDCO45']].drop_duplicates()
        for _, data in unique_idco45_dtinput.iterrows():
            dtinput = data.iloc[0]
            idco45 = data.iloc[1]
            matrice_associati = self.mandati_associati[(self.mandati_associati['IDCO45'] == idco45) & (self.mandati_associati['DTINPUT'] == dtinput)]
            combinations_df_prediction = combinations_df[(combinations_df['IDCO45'] == idco45) & (combinations_df['DTINPUT'] == dtinput)]
            pratica_importo_label = matrice_associati[['PRATICA', 'IMPORTO']].sort_values(by=['PRATICA'], ascending=False).reset_index(drop=True)
            pratica_importo_prediction = combinations_df_prediction[['Y_pratica', 'Y_importo']]
            pratica_importo_prediction = pratica_importo_prediction.rename(columns={'Y_pratica': 'PRATICA', 'Y_importo': 'IMPORTO'})
            pratica_importo_prediction = pratica_importo_prediction.sort_values(by=['PRATICA'], ascending=False).reset_index(drop=True)
            res = pratica_importo_label.equals(pratica_importo_prediction)
            if res and ("INPS" in idco45 or "I.N.P.S" in idco45):
                self.iban_inps_correctly_matched += 1
            r.append(res)
        return r

    def __get_metrics_case3(self, df):
        r3 = []
        combination_case3_rows_length = []
        allcombination_case3_length = []
        unique_idco45_dtinput_df = df[['combinations','DTINPUT', 'IDCO45']]
        for idx, data in unique_idco45_dtinput_df.iterrows():
            all_combinations = data.iloc[0]
            allcombination_case3_length.append(len(all_combinations)) # NOTE: this represents the number of combinations found per each input
            dtinput = data.iloc[1]
            idco45 = data.iloc[2]
            matrice_associati = self.mandati_associati[(self.mandati_associati['IDCO45'] == idco45) & (self.mandati_associati['DTINPUT'] == dtinput)]
            pratica_importo_label = matrice_associati[['PRATICA', 'IMPORTO']].sort_values(by=['PRATICA'], ascending=False).reset_index(drop=True)
            combination_found = False
            for comb_list in all_combinations:
                combination_case3_rows_length.append(len(comb_list)) # NOTE: this represents the number of rows per combinations found per each input
                pratica_importo_prediction = pd.DataFrame(columns=['PRATICA', 'IMPORTO'])
                for idx, (pratica, importo) in enumerate(comb_list):
                    pratica_importo_prediction.loc[idx] = [pratica] + [importo]
                pratica_importo_prediction = pratica_importo_prediction.sort_values(by=['PRATICA'], ascending=False).reset_index(drop=True)            
                res = pratica_importo_label.equals(pratica_importo_prediction)
                if res and ("INPS" in idco45 or "I.N.P.S" in idco45):
                    self.iban_inps_correctly_matched += 1
                if res:
                    r3.append(res)
                    combination_found = True
                    break
            if not combination_found:
                r3.append(False)
        return r3, combination_case3_rows_length, allcombination_case3_length

    def get_associati_metrics(self):
        df1, df2, df3 = self.__create_predictions_dataframe(self.combinations_results)
        metric1 = self.__get_metrics_case12(df1)
        metric2 = self.__get_metrics_case12(df2)
        metric3, combination_case3_rows_length, allcombination_case3_length = self.__get_metrics_case3(df3)
        print(f"Len df1: {len(df1)}")
        print(f"Len df2: {len(df2)}")
        print(f"Len df3: {len(df3)}")
        
        print(f"Accuracy case1: {(sum(metric1))/len(df1)}")
        print(f"Accuracy case2: {(sum(metric2))/len(df2)}")
        print("Accuracy case3 and mean of #combinations: ", [sum(metric3)/len(df3), np.mean(combination_case3_rows_length), np.mean(allcombination_case3_length)])
        print(f"Number of solved iban inps: {self.iban_inps_correctly_matched}")
