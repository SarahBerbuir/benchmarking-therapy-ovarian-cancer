import pandas as pd

# Summarize automatic benchmark scores separately for suspected and confirmed cases.
# TODO Generalize
df_raw = pd.read_excel(
    '/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/masterthesis/benchmarking-therapy-ovarian-cancer/data/processed/Auswertung_final_results-MA!!.xlsx',
    sheet_name='raw_scores'
)

print(df_raw['Status'].value_counts())

metrics = {
    'LLM': ['embed_cosine_vanilla', 'bert_vanilla'],
    'RAG': ['embed_cosine_rag', 'bert_rag'],
    'GraphRAG': ['embed_cosine_graphrag', 'bert_graphrag'],
}

for status in ['Verdacht', 'Diagnose']:
    df_sub = df_raw[df_raw['Status'] == status]

    print(f"\n=== {status} (n={len(df_sub)}) ===")

    for system, cols in metrics.items():
        for col in cols:
            print(f"{system} {col}: median={df_sub[col].median():.3f}")