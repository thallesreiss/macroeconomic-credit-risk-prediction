import sqlite3
import pandas as pd
import requests
from datetime import datetime

DB_NAME = "banco_macro_risco.db"

# Dicionário mapeando o nome da nossa tabela com o código oficial do SGS/BACEN
SERIES_BACEN = {
    "stg_macro_inadimplencia": 21084,  # Inadimplência PF - Total %
    "stg_macro_selic": 4189,           # Taxa Selic acumulada no mês %
    "stg_macro_inflacao": 433,         # IPCA - Variação mensal %
    "stg_macro_endividamento": 29038   # Endividamento das famílias %
}

def consumir_api_sgs(codigo_serie):
    # Consome a API oficial do Banco Central trazendo os dados de 2015 até hoje em formato JSON
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial=01/01/2015"
    response = requests.get(url)
    
    if response.status_code == 200:
        dados = response.json()
        df = pd.DataFrame(dados)
        
        # O BC retorna os dados como texto ('data' e 'valor'), vamos padronizar
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = df['valor'].astype(float)
        
        return df
    else:
        raise Exception(f"Erro ao acessar API do BACEN para a série {codigo_serie}. Status Code: {response.status_code}")

def executar_pipeline_ingestao():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a ingestão de dados abertos do Banco Central...")
    
    conn = sqlite3.connect(DB_NAME)
    
    for nome_tabela, codigo_serie in SERIES_BACEN.items():
        print(f"--> Coletando série {codigo_serie} para a tabela {nome_tabela}...")
        df_serie = consumir_api_sgs(codigo_serie)
        
        # Salva cada indicador econômico em sua respectiva tabela de staging
        df_serie.to_sql(nome_tabela, conn, if_exists="replace", index=False)
        print(f"   ✓ {len(df_serie)} registros importados com sucesso.")
        
    conn.close()
    print(f"\n[FIM DO PASSO 1] Camada de Staging preenchida com dados reais e oficiais do BACEN!")

if __name__ == "__main__":
    try:
        executar_pipeline_ingestao()
    except Exception as e:
        print(f"\n[ERRO NA INGESTÃO]: {str(e)}")