import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "banco_macro_risco.db"

def executar_feature_engineering_sql():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a Engenharia de Atributos com SQL Avançado...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Query corrigida: Window Functions isoladas dentro da subquery 'sub_calculada'
    query_transformacao = """
    CREATE TABLE IF NOT EXISTS fct_macro_credit_analytics AS
    WITH cte_datas_padronizadas AS (
        SELECT DISTINCT strftime('%Y-%m', data) AS ano_mes FROM stg_macro_inadimplencia
    ),
    cte_inadimplencia AS (
        SELECT strftime('%Y-%m', data) AS ano_mes, valor AS pct_inadimplencia FROM stg_macro_inadimplencia
    ),
    cte_selic AS (
        SELECT strftime('%Y-%m', data) AS ano_mes, valor AS pct_selic FROM stg_macro_selic
    ),
    cte_inflacao AS (
        SELECT strftime('%Y-%m', data) AS ano_mes, valor AS pct_inflacao FROM stg_macro_inflacao
    ),
    cte_endividamento AS (
        SELECT strftime('%Y-%m', data) AS ano_mes, valor AS pct_endividamento FROM stg_macro_endividamento
    ),
    cte_base_consolidada AS (
        SELECT 
            d.ano_mes,
            i.pct_inadimplencia,
            s.pct_selic,
            inf.pct_inflacao,
            e.pct_endividamento
        FROM cte_datas_padronizadas d
        LEFT JOIN cte_inadimplencia i ON d.ano_mes = i.ano_mes
        LEFT JOIN cte_selic s ON d.ano_mes = s.ano_mes
        LEFT JOIN cte_inflacao inf ON d.ano_mes = inf.ano_mes
        LEFT JOIN cte_endividamento e ON d.ano_mes = e.ano_mes
    ),
    sub_calculada AS (
        SELECT 
            ano_mes,
            pct_inadimplencia,
            pct_selic,
            pct_inflacao,
            pct_endividamento,
            LAG(pct_selic, 1) OVER (ORDER BY ano_mes) AS selic_lag_1,
            LAG(pct_selic, 3) OVER (ORDER BY ano_mes) AS selic_lag_3,
            LAG(pct_inflacao, 1) OVER (ORDER BY ano_mes) AS inflacao_lag_1,
            LEAD(pct_inadimplencia, 1) OVER (ORDER BY ano_mes) AS target_inadimplencia_proximo_mes
        FROM cte_base_consolidada
    )
    SELECT * FROM sub_calculada
    WHERE target_inadimplencia_proximo_mes IS NOT NULL 
      AND selic_lag_3 IS NOT NULL;
    """
    
    # Executa a limpeza e criacao da Tabela Fato
    cursor.execute("DROP TABLE IF EXISTS fct_macro_credit_analytics;")
    cursor.execute(query_transformacao)
    conn.commit()
    
    # Validacao da volumetria dos dados extraidos do BACEN
    df_valida = pd.read_sql("SELECT COUNT(*) as total FROM fct_macro_credit_analytics", conn)
    total_linhas = df_valida['total'].values[0]
    
    conn.close()
    print(f"--> Sucesso! Tabela Fato 'fct_macro_credit_analytics' criada com {total_linhas} meses processados para o Machine Learning.")

if __name__ == "__main__":
    try:
        executar_feature_engineering_sql()
    except Exception as e:
        print(f"\n[ERRO NA MODELAGEM]: {str(e)}")