
def backtracking_case3(self, target, id_ente, pratiche, perfezionamento, sinistro, estinte):
    candidates_df = self.get_pratiche_by_ente_and_stato(
        id_ente, pratiche, perfezionamento=perfezionamento, sinistro=sinistro, estinte=estinte
    )
    candidates = [
        (row['ID_PRATICA'], row['IMPORTO_RATA'])
        for _, row in candidates_df.iterrows()
        if row['IMPORTO_RATA'] < target
    ]

    results = []
    
    def backtrack(start_idx, current_combination):
        total_importo = sum(importo for _, importo in current_combination)
        
        if total_importo == target:
            results.append(current_combination.copy())
            return
        if total_importo > target:
            return
        
        for i in range(start_idx, len(candidates)):
            current_combination.append(candidates[i])
            backtrack(i + 1, current_combination)
            current_combination.pop()
    
    backtrack(0, [])
    return results if results else None
