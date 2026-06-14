import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

DB_NAME = "banco_macro_risco.db"

def treinar_modelo_macro():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Carregando a tabela fato do banco de dados...")
    
    # 1. Conecta ao banco e extrai a tabela fato
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM fct_macro_credit_analytics ORDER BY ano_mes;", conn)
    conn.close()
    
    # 2. Definindo as Variáveis Preditivas (X) e a Variável Alvo (y)
    features = ['pct_selic', 'pct_inflacao', 'pct_endividamento', 'selic_lag_1', 'selic_lag_3', 'inflacao_lag_1']
    target = 'target_inadimplencia_proximo_mes'
    
    X = df[features]
    y = df[target]
    
    # 3. Separando os dados em Treino (80%) e Teste (20%) de forma temporal
    # Em séries temporais, não usamos amostragem aleatória pura para não quebrar a ordem do tempo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    print(f"--> Base de dados dividida: {len(X_train)} meses para treino | {len(X_test)} meses para teste.")
    
    # 4. Treinando o Modelo de Regressão Linear
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # 5. Fazendo previsões na base de teste para avaliar a performance
    y_pred = model.predict(X_test)
    
    # 6. Calculando as Métricas Estatísticas
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("\n" + "="*45)
    print("📊 RESULTADOS DO MODELO PREDITIVO (BACEN):")
    print(f"--> Erro Médio Absoluto (MAE): {mae:.4f}%")
    print(f"--> Poder Explicativo do Modelo (R² Score): {r2:.4f}")
    print("="*45)
    
    # 7. Exibindo a importância/peso de cada variável econômica
    print("\n💡 PESO DE CADA VARIÁVEL NA INADIMPLÊNCIA:")
    for feat, coef in zip(features, model.coef_):
        print(f"   ✓ {feat}: {coef:.4f}")
    print("="*45 + "\n")

if __name__ == "__main__":
    try:
        treinar_modelo_macro()
    except Exception as e:
        print(f"\n[ERRO NO TREINAMENTO]: {str(e)}")