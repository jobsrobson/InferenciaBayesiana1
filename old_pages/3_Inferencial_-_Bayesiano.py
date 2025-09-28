import streamlit as st
import pandas as pd
import arviz as az
import plotly.express as px
import numpy as np

# ==========================
# Carregar resultados salvos
# ==========================
@st.cache_data
def carregar_resultados():
    try:
        trace = az.from_netcdf("modules/modelo_bayesiano_trace.nc")
        resultados = pd.read_csv("modules/resultados_bayes.csv", index_col=0)
        return trace, resultados, None
    except Exception as e:
        return None, None, str(e)

trace, resultados, error = carregar_resultados()

if error:
    st.error(f"❌ Erro ao carregar resultados Bayesianos: {error}")
    st.stop()


# Renomear a dimensão
trace.posterior = trace.posterior.rename_dims({"beta_dim_0": "coef"})

# Atribuir os nomes legíveis às coordenadas
colnames = resultados.index[:12].tolist()  # supondo que os 12 primeiros sejam betas
trace.posterior = trace.posterior.assign_coords({"coef": colnames})


st.subheader("Modelo Bayesiano - Regressão Binomial Negativa")

st.markdown("""
O modelo **Bayesiano Binomial Negativo** buscou identificar os fatores institucionais e socioeconômicos associados à **taxa de ingresso em cursos de graduação na RIDE-DF em 2023**, ajustada pelo tamanho do curso.
""")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Descrição do Modelo", "Variáveis do Modelo", "Resultados do Modelo"])

# ==========================
# TAB 1 - Descrição do Modelo
# ==========================
with tab1:
    st.markdown("#### Regressão Bayesiana Binomial Negativa com Offset")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    A modelagem Bayesiana utiliza **probabilidades a priori** e atualiza essas crenças com os dados observados, produzindo **distribuições posteriores** para cada parâmetro.
    
    Isso oferece vantagens importantes:
    - Resultados interpretados como **probabilidades diretas** (e não apenas p-valores);
    - Intervalos de credibilidade (HDI) que representam faixas mais plausíveis para os efeitos;
    - Maior robustez em amostras pequenas ou cenários complexos.
    """)

    st.markdown("""
    Foi ajustado um modelo de **Regressão Binomial Negativa** com offset `log(qt_mat)`, garantindo que os efeitos sejam interpretados como **taxas proporcionais de ingresso**, não números absolutos.
    
    O sampler MCMC (NUTS) foi rodado em **4 cadeias** com **2000 iterações** cada, após 1000 de aquecimento, totalizando **8000 amostras válidas**.
    """)

# ==========================
# TAB 2 - Variáveis do Modelo
# ==========================
with tab2:
    st.markdown("#### Variáveis utilizadas no Modelo Bayesiano")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        st.markdown("**Características Institucionais**")
        st.markdown("""
        - `tp_rede`: Pública ou Privada  
        - `tp_organizacao_academica`: Faculdade, Universidade, Centro Universitário, IF
        """)

    with col2:
        st.markdown("**Qualificação Docente**")
        st.markdown("""
        - `prop_doc_avancado`: Proporção de mestres e doutores  
        """)

    with col3:
        st.markdown("**Características do Curso**")
        st.markdown("""
        - `tp_grau_academico`: Bacharelado, Licenciatura, Tecnológico, etc.  
        - `tp_modalidade_ensino`: Presencial ou EAD  
        - `qt_conc`: Quantidade de concluintes em 2023  
        """)

    with col4:
        st.markdown("**Perfil dos Ingressantes**")
        st.markdown("""
        - `prop_ing_pp`: Proporção de ingressantes pretos e pardos  
        - `prop_ing_financiados`: Proporção com FIES/PROUNI  
        """)

    st.divider()

    st.markdown("""
    - **Variável Dependente (Y):** `qt_ing` – Número de ingressantes em 2023  
    - **Offset:** `log(qt_mat)` – Ajusta pelo tamanho total de matrículas  
    """)

# ==========================
# TAB 3 - Resultados
# ==========================
with tab3:
    st.markdown("#### Resultados do Modelo Bayesiano")
    st.markdown("<br>", unsafe_allow_html=True)

    # Mostrar tabela
    st.markdown("<h5>Posterior Summary (Médias e HDI 94%)</h5>", unsafe_allow_html=True)
    st.dataframe(resultados, use_container_width=True)

    st.divider()

    # Forest Plot
    st.markdown("<h5>Forest Plot Bayesiano</h5>", unsafe_allow_html=True)

    df_plot = resultados.reset_index().rename(columns={"index": "Variável"})

    fig = px.scatter(
        df_plot,
        x="mean",
        y="Variável",
        error_x=df_plot["mean"] - df_plot["hdi_3%"],
        error_x_minus=df_plot["hdi_97%"] - df_plot["mean"],
        labels={"mean": "Coeficiente (log da Razão de Taxa)", "Variável": "Variáveis"},
        color_discrete_sequence=["blue"],
        title="Forest Plot - Efeitos Posteriores"
    )

    fig.update_layout(
        xaxis_title="Efeito estimado (escala log)",
        yaxis_title="",
        height=700,
        shapes=[{"type": "line", "x0": 0, "x1": 0, "y0": -1, "y1": len(df_plot),
                 "line": {"color": "red", "dash": "dash"}}]
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Como interpretar o Forest Plot", icon=":material/info:"):
        st.markdown("""
        - Cada ponto azul representa a **média posterior** de um coeficiente;  
        - As barras horizontais mostram o **intervalo de credibilidade (HDI 94%)**;  
        - Se o HDI não cruza a linha vermelha (zero), há forte evidência de efeito real;  
        - Valores positivos → aumentam a taxa de ingresso;  
        - Valores negativos → reduzem a taxa de ingresso.  
        """)

    st.divider()

    import matplotlib.pyplot as plt


    st.markdown("#### Distribuições Posteriores dos Parâmetros (Densidade)")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    As curvas abaixo mostram a distribuição da incerteza de cada parâmetro.  
    Quando a massa posterior está toda de um lado de 0, temos **forte evidência do efeito**.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    params_to_show = [
        "tp_rede_Pública",
        "tp_modalidade_ensino_Presencial",
        "prop_doc_avancado",
        "prop_ing_pp",
        "tp_grau_academico_Tecnológico",
        "tp_organizacao_academica_Instituto Federal de Educação, Ciência e Tecnologia"
    ]

    # Criar grade 3x2
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    axes = axes.flatten()

    for i, param in enumerate(params_to_show):
        az.plot_posterior(
            trace,
            var_names=["beta"],
            coords={"coef": [param]},
            hdi_prob=0.95,
            ax=axes[i],
            kind="kde"
        )
        axes[i].set_title(param, fontsize=10)

    # Esconder subplots vazios se sobrar espaço
    for j in range(len(params_to_show), len(axes)):
        fig.delaxes(axes[j])

    fig.tight_layout()
    st.pyplot(fig)


    st.divider()

    st.markdown("#### Interpretação dos Resultados")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    O modelo Bayesiano confirma tendências observadas no frequentista, mas com interpretações mais intuitivas em termos de **probabilidade**:

    - **Instituições públicas**: com probabilidade ~97%, apresentam taxas de ingresso menores que as privadas;  
    - **Universidades**: alta probabilidade de taxas proporcionais menores em comparação aos centros universitários;  
    - **Modalidade Presencial**: praticamente certo que reduz ingressos em relação ao EAD (~44% a menos);  
    - **Qualificação docente (mestres/doutores)**: probabilidade ~100% de aumentar significativamente os ingressos;  
    - **Proporção de pretos e pardos**: alta probabilidade (~94%) de aumentar as taxas de ingresso;  
    - **Financiamento (FIES/PROUNI)** e **número de concluintes**: efeitos incertos, com HDIs abrangendo zero.  

    Em resumo: **EAD, qualidade docente e inclusão racial** são os fatores mais robustos e com evidência posterior forte para explicar as taxas de ingresso na RIDE-DF em 2023.
    """)

