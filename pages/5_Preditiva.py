import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ======================================================
# Configuração da página
# ======================================================

st.subheader("Modelos Preditivos - Predição de Ingressantes")
st.markdown("Esta página apresenta os resultados dos modelos Frequentista e Bayesiano, usados com o objetivo de prever o número de ingressantes para o curso de **Ciência de Dados e Inteligência Artificial** do **IESB**, em 2023.")

# ======================================================
# Carregar resultados salvos
# ======================================================
with open("resultados_modelos.json", "r", encoding="utf-8") as f:
    resultados = json.load(f)

curso = resultados["previsoes"]["curso_alvo"]
ies = resultados["previsoes"]["ies_alvo"]
real_2023 = resultados["previsoes"]["real_2023"]
prev_glm = resultados["previsoes"]["glm_poisson"]
prev_bayes = resultados["previsoes"]["bayesian"]["media"]
ic_low = resultados["previsoes"]["bayesian"]["ic_low"]
ic_high = resultados["previsoes"]["bayesian"]["ic_high"]
metricas = resultados["metricas"]

st.markdown("<br>", unsafe_allow_html=True)


# tabs
tab1, tab2, tab3 = st.tabs(["Detalhes dos Modelos", "Resultados e Visualizações", "Comparação dos Modelos"])

with tab1:

    st.markdown("#### Detalhes dos Modelos")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    - **Modelo Frequentista (GLM Poisson)**: Utiliza a função de ligação log para modelar a contagem de ingressantes, assumindo que os dados seguem uma distribuição de Poisson. Este modelo é adequado para dados de contagem e permite interpretar os coeficientes como efeitos multiplicativos na taxa de ingresso.
    
    - **Modelo Bayesiano**: Adota uma abordagem probabilística, incorporando incertezas nos parâmetros do modelo através de distribuições a priori. Utiliza amostragem MCMC para estimar a distribuição posterior dos parâmetros, permitindo obter previsões com intervalos de credibilidade que refletem a incerteza inerente ao processo de modelagem.
    
    Ambos os modelos foram ajustados utilizando variáveis preditoras relevantes, descobertas na análise inferencial, para capturar os fatores que influenciam o número de ingressantes.
    """)

with tab2:

    st.markdown("#### Resultados dos Modelos")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### 📊 GLM Poisson")

    st.markdown(f"""
    - **Curso:** {curso}  
    - **IES:** {ies}  
    - **Valor Real (2023):** {real_2023} ingressantes  
    - **Previsão GLM (Poisson):** {prev_glm:.1f} ingressantes  
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("###### GLM Poisson vs Valor Real")
        
        # Gráfico comparativo simples GLM x Real usando Plotly
        import plotly.graph_objects as go

        categorias = ["Real 2023", "GLM Poisson"]
        valores = [real_2023, prev_glm]

        fig = go.Figure(data=[
            go.Bar(x=categorias, y=valores, marker_color=["#66c2a5", "#fc8d62"])
        ])
        fig.update_layout(
            yaxis_title="Número de ingressantes",
            height=400,
            width=500
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Métricas
        if "glm_poisson" in metricas:
            st.markdown("###### Métricas GLM")
            st.dataframe(pd.DataFrame(metricas["glm_poisson"], index=["GLM"]).T)
        else:
            st.warning("Nenhuma métrica GLM salva.")

    with st.expander("Interpretação do GLM Poisson", icon=":material/info:"):
        st.markdown("""
        O **modelo GLM Poisson** utiliza uma função de ligação logarítmica e pressupõe que os dados seguem uma distribuição de Poisson.
        Ele é adequado para **dados de contagem**, mas tende a puxar previsões para o “tamanho médio” dos cursos.

        - O modelo previu **46 ingressantes** para o curso, enquanto o valor real foi **16** → **superestimação**.  
        - A tabela mostra R² razoável (0,83), mas **RMSE alto (586)**, indicando grandes erros em alguns casos.  
        - Para cursos pequenos como o do IESB, o GLM é pouco confiável, porque “herda” o padrão de cursos maiores.  

        📌 **Resumo:** o GLM ajuda a identificar tendências gerais, mas neste caso **superestimou bastante**.
        """)

    st.divider()

    st.markdown("##### 📈 Modelo Bayesiano")

    st.markdown(f"""
    - **Curso:** {curso}  
    - **IES:** {ies}  
    - **Valor Real (2023):** {real_2023} ingressantes  
    - **Previsão Bayesiana (média):** {prev_bayes:.1f} ingressantes  
    - **Intervalo de Credibilidade 90%:** {ic_low:.1f} – {ic_high:.1f}
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("###### Bayesiano vs Valor Real")
        # Gráfico comparativo Bayes x Real
        fig, ax = plt.subplots(figsize=(6, 4))
        categorias = ["Real 2023", "Bayesiano (média)"]
        valores = [real_2023, prev_bayes]
        sns.barplot(x=categorias, y=valores, ax=ax, palette="Set2")

        # Intervalo de credibilidade
        # Adicionar intervalo de credibilidade com Plotly
        import plotly.graph_objects as go

        fig_bayes = go.Figure()

        # Barras
        fig_bayes.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker_color=["#66c2a5", "#8da0cb"],
            name="Previsão"
        ))

        # Intervalo de credibilidade como barra de erro para Bayesiano
        fig_bayes.add_trace(go.Scatter(
            x=["Bayesiano (média)"],
            y=[prev_bayes],
            mode="markers",
            marker=dict(color="black", size=10),
            error_y=dict(
            type="data",
            symmetric=False,
            array=[ic_high - prev_bayes],
            arrayminus=[prev_bayes - ic_low],
            thickness=2,
            width=10,
            color="black"
            ),
            name="IC 90% Bayesiano"
        ))

        fig_bayes.update_layout(
            yaxis_title="Número de ingressantes",
            showlegend=True
        )
        st.plotly_chart(fig_bayes, use_container_width=True)

    with col2:
        # Distribuição posterior
        st.markdown("###### Distribuição Posterior")
        bayes_sim = np.random.normal(loc=prev_bayes, scale=(ic_high - ic_low) / 3, size=1000)
        import plotly.graph_objects as go

        hist_data = bayes_sim
        hist = np.histogram(hist_data, bins=30)
        bin_edges = hist[1]
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Bar(
            x=bin_centers,
            y=hist[0],
            marker_color="skyblue",
            opacity=0.7,
            name="Posterior"
        ))

        # Valor Real
        fig.add_vline(x=real_2023, line_dash="dash", line_color="red", name="Valor Real 2023")
        # Média Bayesiana
        fig.add_vline(x=prev_bayes, line_dash="dash", line_color="blue", name="Média Bayesiana")
        # IC90% limites
        fig.add_vline(x=ic_low, line_dash="dot", line_color="black", name="IC90% - limite inferior")
        fig.add_vline(x=ic_high, line_dash="dot", line_color="black", name="IC90% - limite superior")

        fig.update_layout(
            xaxis_title="Ingressantes previstos",
            yaxis_title="Frequência",
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Interpretação do Modelo Bayesiano", icon=":material/info:"):
        st.markdown("""
        O **modelo Bayesiano** trata os parâmetros como distribuições de probabilidade, incorporando incertezas.
        Isso permite não apenas dar uma previsão pontual, mas também um **intervalo de credibilidade**.

        - A previsão média foi **12,8**, próxima do valor real (**16**).  
        - O IC90% foi de **1 a 41**, mostrando alta incerteza, mas **incluindo o valor real**.  
        - O gráfico da distribuição posterior ilustra o “leque” de valores plausíveis:  
          - Linha vermelha = valor real  
          - Linha azul = média prevista  
          - Linhas pretas = intervalo de credibilidade  

        📌 **Resumo:** o Bayesiano foi **mais conservador**, capturou a incerteza e incluiu o valor real dentro do intervalo.
        """)

with tab3:

    st.markdown("#### Resumo dos Resultados")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""
    - **Curso:** {curso}  
    - **IES:** {ies}  
    - **Valor Real (2023):** {real_2023} ingressantes  
    - **Previsão GLM (Poisson):** {prev_glm:.1f} ingressantes  
    - **Previsão Bayesiana (média):** {prev_bayes:.1f} ingressantes  
    - **Intervalo de Credibilidade 90% (Bayesiano):** {ic_low:.1f} – {ic_high:.1f} ingressantes
    """)

    st.info("Interpretação: O GLM superestimou o número de ingressantes, enquanto o modelo Bayesiano apresentou uma previsão mais conservadora, com o valor real de 2023 incluso dentro do intervalo de credibilidade.")

    st.divider()


    col1, col2 = st.columns(2)
    with col1:
        st.markdown("###### Comparação das Previsões")

        import plotly.graph_objects as go

        categorias = ["Real 2023", "GLM Poisson", "Bayesiano (média)"]
        valores = [real_2023, prev_glm, prev_bayes]

        fig = go.Figure()

        # Barras para cada modelo
        fig.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker_color=["#66c2a5", "#fc8d62", "#8da0cb"],
            name="Previsão"
        ))

        # Adicionar intervalo de credibilidade para Bayesiano
        fig.add_trace(go.Scatter(
            x=["Bayesiano (média)"],
            y=[prev_bayes],
            mode="markers",
            marker=dict(color="black", size=10),
            error_y=dict(
            type="data",
            symmetric=False,
            array=[ic_high - prev_bayes],
            arrayminus=[prev_bayes - ic_low],
            thickness=2,
            width=10,
            color="black"
            ),
            name="IC 90% Bayesiano"
        ))

        fig.update_layout(
            yaxis_title="Número de ingressantes",
            title="Previsão vs Valor Real",
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("###### Distribuição Posterior das Previsões (Bayesiano)")

        # Simular distribuição normal aproximada só para visualização
        bayes_sim = np.random.normal(loc=prev_bayes, scale=(ic_high - ic_low) / 3, size=1000)

        import plotly.graph_objects as go
        hist = np.histogram(bayes_sim, bins=30)
        bin_edges = hist[1]
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Bar(
            x=bin_centers,
            y=hist[0],
            marker_color="skyblue",
            opacity=0.7,
            name="Posterior"
        ))

        # Valor Real
        fig.add_vline(x=real_2023, line_dash="dash", line_color="red", name="Valor Real 2023")
        # Média Bayesiana
        fig.add_vline(x=prev_bayes, line_dash="dash", line_color="blue", name="Média Bayesiana")
        # IC90% limites
        fig.add_vline(x=ic_low, line_dash="dot", line_color="black", name="IC90% - limite inferior")
        fig.add_vline(x=ic_high, line_dash="dot", line_color="black", name="IC90% - limite superior")

        fig.update_layout(
            xaxis_title="Ingressantes previstos",
            yaxis_title="Frequência",
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown("###### Métricas de Performance (Conjunto de Validação)")
    if metricas:
        df_metricas = pd.DataFrame(metricas).T
        st.dataframe(df_metricas, use_container_width=True)
    else:
        st.warning("Nenhuma métrica foi salva.")

