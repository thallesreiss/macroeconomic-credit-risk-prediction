import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

DB_NAME = "banco_macro_risco.db"

def carregar_e_treinar_modelo_base():
    # Recarrega e treina rapidamente o modelo para usarmos na previsao do cenario
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM fct_macro_credit_analytics ORDER BY ano_mes;", conn)
    conn.close()
    
    features = ['pct_selic', 'pct_inflacao', 'pct_endividamento', 'selic_lag_1', 'selic_lag_3', 'inflacao_lag_1']
    target = 'target_inadimplencia_proximo_mes'
    
    X = df[features]
    y = df[target]
    
    model = LinearRegression()
    model.fit(X, y)
    return model

def simular_politica_de_credito():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando Simulador de Politica de Credito e Estresse...")
    
    model = carregar_e_treinar_modelo_base()
    
    # Criando 3 cenarios macroeconomicos hipoteticos para teste
    # Formato: ['pct_selic', 'pct_inflacao', 'pct_endividamento', 'selic_lag_1', 'selic_lag_3', 'inflacao_lag_1']
    cenarios = {
        "Cenário Otimista (Queda de Juros e Inflação Controlada)": [10.50, 0.20, 45.0, 11.25, 11.75, 0.35],
        "Cenário Neutro (Economia Estável)": [12.25, 0.40, 48.0, 12.25, 12.50, 0.45],
        "Cenário de Estresse (Inflação em Alta e Juros Elevados)": [14.25, 0.85, 52.0, 13.75, 13.25, 0.70]
    }
    
    print("\n" + "="*60)
    print("📢 RELATÓRIO DO COMITÊ DE POLÍTICA DE CRÉDITO:")
    print("="*60)
    
    relatorio_md = "# Relatorio de Estresse de Credito Macroeconômico\n\n"
    relatorio_md += f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
    
    for nome, variaveis in cenarios.items():
        # Transforma em array e faz a predicao da inadimplencia futura
        dados_input = np.array(variaveis).reshape(1, -1)
        predicao_inadimplencia = model.predict(dados_input)[0]
        
        # Regra de Decisao de Negocio baseada nas faixas de inadimplencia
        if predicao_inadimplencia < 4.0:
            status_risco = "🟢 RISCO BAIXO (NORMAL)"
            recomendacao = "Liberar linhas de credito de varejo. Expandir apetite de risco."
        elif 4.0 <= predicao_inadimplencia < 5.5:
            status_risco = "🟡 RISCO MODERADO (ATENÇÃO)"
            recomendacao = "Aumentar exigencia de Score minimo. Monitorar safras recentes."
        else:
            status_risco = "🔴 RISCO CRÍTICO (ESTRESSE)"
            recomendacao = "Bloquear concessao de cartoes para novos clientes de baixa renda. Reter limites."
            
        print(f"\n📌 {nome}")
        print(f"--> Inadimplência Prevista para o próximo mês: {predicao_inadimplencia:.2f}%")
        print(f"--> Status de Risco: {status_risco}")
        print(f"--> Recomendação Operacional: {recomendacao}")
        
        # Alimentando o corpo do arquivo Markdown
        relatorio_md += f"### {nome}\n"
        relatorio_md += f"- **Inadimplência Prevista:** {predicao_inadimplencia:.2f}%\n"
        relatorio_md += f"- **Status de Risco:** {status_risco}\n"
        relatorio_md += f"- **Diretriz de Negócio:** {recomendacao}\n\n"
        
    # Salvando o arquivo de relatorio final para o portfólio
    with open("relatorio_comite_credito.md", "w", encoding="utf-8") as f:
        f.write(relatorio_md)
        
    print("\n" + "="*60)
    print("✓ Sucesso! Arquivo 'relatorio_comite_credito.md' exportado para a raiz do seu projeto.")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        simular_politica_de_credito()
    except Exception as e:
        print(f"\n[ERRO NA DECISÃO]: {str(e)}")