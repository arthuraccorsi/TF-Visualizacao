from pysus.ftp.databases.sih import SIH
from pysus.ftp import Database
import os

# Diretório onde salvar os arquivos
DATA_DIR = "./dados"

# Cria a pasta se não existir
os.makedirs(DATA_DIR, exist_ok=True)

# Instanciar a base SIH
sih: Database = SIH().load()

# Ano que deseja baixar (exemplo: 2019)
ano = 2019

# Lista os arquivos disponíveis para o estado RS e ano selecionado
arquivos = sih.get_files("RD", uf="RS", year=ano)
print(f"Arquivos disponíveis para {ano}:")
print(arquivos)

# Faz o download dos arquivos diretamente para a pasta DATA_DIR
sih.download(files=arquivos, local_dir=DATA_DIR)

print(f"✅ Download concluído! Arquivos salvos em {DATA_DIR}")
