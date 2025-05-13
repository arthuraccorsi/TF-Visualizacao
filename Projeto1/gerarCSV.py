import pandas as pd
import os

DATA_DIR = "./dados"
arquivos_parquet = [f for f in os.listdir(DATA_DIR) if f.startswith("RDRS19") and f.endswith(".parquet")]

dfs = []

for arquivo in arquivos_parquet:
    caminho = os.path.join(DATA_DIR, arquivo)
    df = pd.read_parquet(caminho)
    dfs.append(df)

df_final = pd.concat(dfs, ignore_index=True)
print(f"Total de registros no ano: {len(df_final)}")

# Opcional: salvar CSV consolidado
df_final.to_csv(f"{DATA_DIR}/SIH_2019.csv", index=False)
print(f"CSV consolidado salvo em {DATA_DIR}/SIH_2019.csv")
