import pandas as pd
import os

DATA_DIR = "./dados"
arquivo_csv_entrada = os.path.join(DATA_DIR, "SIH_2019_com_CID_KEY.csv")
arquivo_csv_saida = os.path.join(DATA_DIR, "SIH_2019_filtrado_dialise_POA.csv")

# Ler o CSV consolidado
df = pd.read_csv(arquivo_csv_entrada)

print(f"Total de registros no CSV: {len(df)}")

# Corrigir MUNIC_RES: código de Porto Alegre = 431490 (6 dígitos no dataset)
codigo_poa = 431490
df_poars = df[df['MUNIC_RES'] == codigo_poa]
print(f"Total de internações de residentes em Porto Alegre: {len(df_poars)}")

# Corrigir PROC_REA para 10 dígitos
df_poars['PROC_REA'] = df_poars['PROC_REA'].astype(str).str.zfill(10)

# Definir os códigos de diálise (oficiais do SIH/SUS)
codigos_dialise = ['0303010030', '0303010048', '0303010060']

# Filtrar apenas os procedimentos de diálise
df_dialise = df_poars[df_poars['PROC_REA'].isin(codigos_dialise)]
print(f"Total de internações por diálise em Porto Alegre: {len(df_dialise)}")

# Salvar o CSV filtrado
df_dialise.to_csv(arquivo_csv_saida, index=False)

print(f"CSV filtrado salvo em: {arquivo_csv_saida}")