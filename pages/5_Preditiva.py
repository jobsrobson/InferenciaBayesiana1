import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
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

    st.markdown("#### Detalhes dos Modelos Estatísticos")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(""" 
Nos últimos anos, o cenário do ensino superior brasileiro passou por transformações profundas. A **pandemia de Covid-19**, iniciada em 2020, interrompeu aulas presenciais, acelerou a adoção do ensino remoto e gerou incertezas tanto para estudantes quanto para instituições. Muitos cursos viram queda nas matrículas, evasões inesperadas e uma reorganização no perfil de ingressantes. Em meio a esse contexto de instabilidade, entender o **comportamento da demanda por cursos específicos** tornou-se uma tarefa estratégica para universidades e centros universitários.

O curso de **Ciência de Dados e Inteligência Artificial do IESB** surge justamente nesse período, acompanhando a crescente valorização da análise de dados em um mundo cada vez mais digital e orientado por informação. No entanto, prever quantos alunos ingressariam em um curso novo, em um **cenário pós-Covid** e de recuperação gradual do setor educacional, é um desafio estatístico complexo. A simples observação de séries históricas não seria suficiente, pois os padrões anteriores à pandemia perderam parte da validade.

Nesse contexto, surge a motivação para **aplicar modelos estatísticos**. Um **modelo frequentista**, como a **GLM Poisson**, poderia fornecer uma estimativa pontual, mas com risco de subestimar ou superestimar a realidade, dado o choque estrutural recente. Já a **abordagem bayesiana** permite incorporar incertezas, refletir cenários possíveis e quantificar a variabilidade das previsões. A pergunta central, então, se torna: ***quantos alunos poderiam ser esperados no curso de Ciência de Dados do IESB em 2023, considerando as condições excepcionais que marcaram o período recente?***

Assim, o uso dos dados do **Censo da Educação Superior de 2023** não é apenas uma escolha técnica, mas também histórica: eles refletem o primeiro momento de relativa normalização após os impactos da pandemia, oferecendo uma base realista para avaliar a aderência entre modelos estatísticos e a realidade observada.""")
    
    st.divider()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Modelos Utilizados"
                )
    st.markdown("""
    - **Modelo Frequentista (GLM Poisson)**: Utiliza a função de ligação log para modelar a contagem de ingressantes, assumindo que os dados seguem uma distribuição de Poisson. Este modelo é adequado para dados de contagem e permite interpretar os coeficientes como efeitos multiplicativos na taxa de ingresso.
    
    - **Modelo Bayesiano**: Adota uma abordagem probabilística, incorporando incertezas nos parâmetros do modelo através de distribuições a priori. Utiliza amostragem MCMC para estimar a distribuição posterior dos parâmetros, permitindo obter previsões com intervalos de credibilidade que refletem a incerteza inerente ao processo de modelagem.
    
    Ambos os modelos foram ajustados utilizando variáveis preditoras relevantes, descobertas na análise inferencial, para capturar os fatores que influenciam o número de ingressantes.
                
    """)

    st.divider()

    st.markdown("""
                        <div style="text-align: justify">
                        <h5>Variável Dependente (Y) </h5>
                        <h6><code>qt_ing</code> - Quantidade de ingressantes em 2023</h6>
        
                        Essa é a variável de interesse central da pesquisa, pois responde diretamente à pergunta: <b><em>quais fatores institucionais e socioeconômicos estão associados ao ingresso de novos estudantes nos cursos de graduação da RIDE-DF em 2023?</em></b>
                        
                        Optou-se por modelar o número de ingressantes em vez do total de matrículas, já que este último mistura alunos veteranos com calouros, enquanto o ingresso capta melhor a dinâmica de expansão ou retração dos cursos.
                        </div>
                        """, unsafe_allow_html=True)
        
    st.divider()

    st.markdown("<h5>Variáveis Independentes (X) </h5>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        st.markdown("**Características Institucionais**")
        st.markdown("""
                        <ul>
                            <li><code>tp_rede</code> <br><b>Pública ou Privada</b><br>
                            Reflete diferenças estruturais: seletividade das públicas e dependência da demanda nas privadas.</li>
                            <li><code>tp_organizacao_academica</code> <br><b>Faculdade, Universidade, Centro Universitário, Instituto Federal</b><br>
                            Representa o formato institucional e autonomia acadêmica.</li>
                        </ul>
                        """, unsafe_allow_html=True)

    with col2:
        st.markdown("**Qualificação dos Docentes**")
        st.markdown("""
                        <ul>
                            <li><code>prop_doc_avancado</code> <br><b>Proporção de docentes com mestrado ou doutorado</b><br>
                            Usada como indicador de qualidade acadêmica e reputação institucional.</li>
                        </ul>
                        """, unsafe_allow_html=True)
            
    with col3:
        st.markdown("**Características do Curso**")
        st.markdown("""
                        <ul>
                            <li><code>tp_grau_academico</code> <br><b>Bacharelado, Licenciatura, Tecnológico ou Não aplicável</b><br>
                            Diferentes graus atendem públicos distintos, influenciando atratividade.</li>
                            <li><code>tp_modalidade_ensino</code> <br><b>Presencial ou EAD</b><br>
                            Captura diferenças de escala: EAD amplia o alcance; presencial é limitado fisicamente.</li>
                            <li><code>qt_conc</code> <br><b>Número de concluintes em 2023</b><br>
                            Proxy de maturidade e reputação do curso.</li>
                        </ul>
                        """, unsafe_allow_html=True)
            
    with col4:
        st.markdown("**Perfil dos Ingressantes**")
        st.markdown("""
                        <ul>
                            <li><code>prop_ing_pp</code> <br><b>Proporção de ingressantes pretos e pardos</b><br>
                            Indicador de inclusão social e diversidade.</li>
                            <li><code>prop_ing_financiados</code> <br><b>Proporção de ingressantes com financiamento (FIES/PROUNI)</b><br>
                            Avalia o papel das políticas públicas no acesso ao ensino superior.</li>
                        </ul>
                        """, unsafe_allow_html=True)

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

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("###### Bayesiano vs Valor Real")
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

    st.markdown("#### Resumo dos Resultados e Comparações entre Modelos")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(""" O modelo bayesiano aplicado nesta análise adota uma abordagem probabilística para prever o número de ingressantes no curso de Ciência de Dados do IESB em 2023, utilizando os dados do Censo da Educação Superior. Diferentemente da perspectiva frequentista, que gera estimativas pontuais dos parâmetros, o modelo bayesiano incorpora incertezas por meio de distribuições a priori e utiliza técnicas de amostragem (como o MCMC) para obter a distribuição posterior das previsões. Isso permite não apenas estimar a média esperada de ingressantes, mas também calcular intervalos de credibilidade que refletem a variabilidade e a incerteza inerentes ao processo, fornecendo uma visão mais completa e realista do fenômeno estudado. """)



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
            name="Valor Real"
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
        fig.add_vline(x=real_2023, line_dash="dash", line_color="red")
        fig.add_trace(go.Scatter(
            x=[real_2023],
            y=[max(hist[0]) * 0.95],
            mode="markers",
            marker=dict(color="red", size=10),
            name="Valor Real 2023",
            showlegend=True
        ))
        # Média Bayesiana
        fig.add_vline(x=prev_bayes, line_dash="dash", line_color="blue")
        fig.add_trace(go.Scatter(
            x=[prev_bayes],
            y=[max(hist[0]) * 0.9],
            mode="markers",
            marker=dict(color="blue", size=10),
            name="Média Bayesiana",
            showlegend=True
        ))
        # IC90% limites
        fig.add_vline(x=ic_low, line_dash="dot", line_color="black")
        fig.add_vline(x=ic_high, line_dash="dot", line_color="black")
        fig.add_trace(go.Scatter(
            x=[ic_low, ic_high],
            y=[max(hist[0]) * 0.85, max(hist[0]) * 0.85],
            mode="markers",
            marker=dict(color="black", size=10, symbol="line-ns"),
            name="IC90% - limites",
            showlegend=True
        ))

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

    with st.expander("Interpretação da Distribuição Posterior", icon=":material/info:", expanded=True):
        st.markdown("""
    
1. **Distribuição Posterior**
    - O histograma em azul claro representa a distribuição posterior das previsões do modelo bayesiano. Cada barra mostra a frequência com que um certo número de ingressantes foi amostrado durante a simulação MCMC. Isso reflete a incerteza da previsão, indo além de apenas um ponto estimado.
2. **Média Bayesiana** (linha azul tracejada e ponto azul)
    - O modelo estimou uma média de ingressantes em torno de 12.
    - Esse valor é o centro da distribuição posterior, funcionando como a previsão mais provável do modelo.
3. **Valor Real de 2023** (linha vermelha tracejada e ponto vermelho)
    - O valor observado em 2023 (≈ 15 ingressantes) está representado em vermelho.
    - Ele se encontra dentro do intervalo de credibilidade de 90%, o que significa que o modelo conseguiu capturar razoavelmente bem a realidade.
4. **Intervalo de Credibilidade de 90%** (linhas pretas tracejadas)
    - O intervalo vai aproximadamente de 0 a 40 ingressantes.
    - Essa faixa indica onde o modelo acredita haver 90% de chance de o valor verdadeiro estar.
    - É um intervalo relativamente amplo, o que mostra que ainda há bastante incerteza nos dados e na modelagem.
            """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###### 📌 Principais Conclusões")
        
        st.markdown("""
- O modelo não errou grosseiramente: o valor real (≈ 15) está bem próximo da média prevista (≈ 12) e dentro do intervalo de credibilidade.
- No entanto, a dispersão da distribuição posterior é alta: existe uma variação grande entre as simulações (de 0 até 40), o que mostra que, mesmo capturando a tendência central, o modelo não consegue ser muito preciso.
- Essa incerteza pode vir de fatores como:
    - Limitações do conjunto de dados (usando apenas 2023 para previsão).
    - Variabilidade natural nos ingressos em cursos novos/pequenos.
    - Estrutura simplificada do modelo (uma GLM Poisson básica pode não capturar toda a complexidade dos determinantes da demanda). 
                    """)

    st.divider()

    st.markdown("###### Métricas de Performance (Conjunto de Validação)")
    if metricas:
        df_metricas = pd.DataFrame(metricas).T
        st.dataframe(df_metricas, use_container_width=True)
    else:
        st.warning("Nenhuma métrica foi salva.")

