import pandas as pd
import os

DATA_DIR = "./dados"
arquivo_csv_entrada = os.path.join(DATA_DIR, "SIH_2019.csv")
arquivo_csv_saida = os.path.join(DATA_DIR, "SIH_2019_com_CID_KEY.csv")

# Ler o CSV consolidado
df = pd.read_csv(arquivo_csv_entrada)

print(f"Total de registros lidos: {len(df)}")

# Criar a coluna CID_10_KEY
df['CID_10_KEY'] = df['DIAG_PRINC'].str.replace('.', '', regex=False).str.upper()

print("Coluna CID_10_KEY criada com sucesso!")

# Salvar o novo CSV com a coluna adicionada
df.to_csv(arquivo_csv_saida, index=False)

print(f"Novo CSV salvo em: {arquivo_csv_saida}")

