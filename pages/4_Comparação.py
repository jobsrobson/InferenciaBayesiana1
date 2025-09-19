import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import arviz as az
import matplotlib.pyplot as plt
import numpy as np


# Carregar trace salvo
idata = az.from_netcdf("modules/modelo_bayesiano_trace.nc")

# Lista de nomes dos betas na ordem correta (mesma que você usou no treinamento)
colnames = [
    "tp_rede_Pública",
    "tp_organizacao_academica_Faculdade",
    "tp_organizacao_academica_Instituto Federal de Educação, Ciência e Tecnologia",
    "tp_organizacao_academica_Universidade",
    "tp_grau_academico_Licenciatura",
    "tp_grau_academico_Não aplicável",
    "tp_grau_academico_Tecnológico",
    "tp_modalidade_ensino_Presencial",
    "qt_conc",
    "prop_doc_avancado",
    "prop_ing_pp",
    "prop_ing_financiados"
]

# Adicionar coordenadas "coef" à dimensão beta_dim_0
idata.posterior = idata.posterior.assign_coords(coef=("beta_dim_0", colnames))



# ========================
# 1. Título e Explicação
# ========================
st.title("🔍 Comparação entre Modelos: Frequentista vs Bayesiano")

st.markdown("""
Nesta seção, comparamos os resultados da **Regressão Binomial Negativa Frequentista** 
(GLM com statsmodels) e da **Regressão Binomial Negativa Bayesiana** (PyMC3/PyMC).  

O objetivo é verificar se os dois modelos convergem para conclusões semelhantes e entender 
as vantagens de cada abordagem:

- **Frequentista**: fornece estimativas pontuais (coeficientes, IRR) e intervalos de confiança.  
- **Bayesiano**: fornece distribuições posteriores completas para cada parâmetro, permitindo 
incorporar incerteza e realizar inferências mais robustas.
""")


# ========================
# 2. Carregar Resultados
# ========================
# Resultados frequentistas
resultados_freq = pd.read_csv("modules/resultados_freq.csv", index_col=0)

# Resultados bayesianos
resultados_bayes = pd.read_csv("modules/resultados_bayes.csv", index_col=0)

# ========================
# 3. Tabela Comparativa
# ========================
st.subheader("📊 Tabela Comparativa")

tabela_comparativa = pd.DataFrame({
    "Frequentista (Coef)": resultados_freq["Coeficiente (log)"],
    "Frequentista (IRR)": resultados_freq["IRR (exp(coef))"],
    "Bayesiano (Média)": resultados_bayes["mean"],
    "Bayesiano (HDI 3%)": resultados_bayes["hdi_3%"],
    "Bayesiano (HDI 97%)": resultados_bayes["hdi_97%"],
})

st.dataframe(tabela_comparativa, use_container_width=True)

st.markdown("""
**Interpretação rápida**:  
- Se os intervalos de confiança (Frequentista) e os intervalos de densidade (Bayesiano) 
estiverem na mesma direção (todos abaixo de 0, ou todos acima), os modelos estão consistentes.  
- Diferenças pequenas são normais, pois o Bayesiano incorpora incerteza via priors e amostragem.
""")


# ========================
# 4. Gráfico Comparativo
# ========================
st.subheader("📈 Forest Plot Comparativo")

fig = go.Figure()

# Frequentista
fig.add_trace(go.Scatter(
    x=resultados_freq["IRR (exp(coef))"],
    y=resultados_freq.index,
    mode="markers",
    name="Frequentista (IRR)",
    marker=dict(color="blue", symbol="circle", size=10)
))
fig.add_trace(go.Scatter(
    x=resultados_freq["IC 95% (low)"],
    y=resultados_freq.index,
    mode="lines",
    line=dict(color="blue", width=2),
    name="IC 95% (Freq)"
))
fig.add_trace(go.Scatter(
    x=resultados_freq["IC 95% (high)"],
    y=resultados_freq.index,
    mode="lines",
    line=dict(color="blue", width=2),
    showlegend=False
))

# Bayesiano
fig.add_trace(go.Scatter(
    x=resultados_bayes["mean"].apply(lambda v: np.exp(v)),  # transformar em IRR
    y=resultados_bayes.index,
    mode="markers",
    name="Bayesiano (IRR)",
    marker=dict(color="red", symbol="diamond", size=10)
))
fig.add_trace(go.Scatter(
    x=resultados_bayes["hdi_3%"].apply(lambda v: np.exp(v)),
    y=resultados_bayes.index,
    mode="lines",
    line=dict(color="red", width=2),
    name="HDI 95% (Bayes)"
))
fig.add_trace(go.Scatter(
    x=resultados_bayes["hdi_97%"].apply(lambda v: np.exp(v)),
    y=resultados_bayes.index,
    mode="lines",
    line=dict(color="red", width=2),
    showlegend=False
))

fig.update_layout(
    xaxis_type="log",
    title="Comparação IRR: Frequentista vs Bayesiano",
    xaxis_title="Razão de Taxa (IRR)",
    yaxis_title="Variáveis",
    height=800,
    shapes=[{"type": "line", "x0": 1, "x1": 1, "y0": -1, "y1": len(resultados_freq),
             "line": {"color": "black", "dash": "dash"}}]
)

st.plotly_chart(fig, use_container_width=True)


# ========================
# 5. Distribuições Posteriores vs Pontos Frequentistas
# ========================
st.subheader("📉 Distribuições Bayes vs Estimativas Freq")

params_to_show = ["tp_rede_Pública", "tp_modalidade_ensino_Presencial", "prop_doc_avancado"]

fig, axes = plt.subplots(len(params_to_show), 1, figsize=(8, 10))

for i, param in enumerate(params_to_show):
    az.plot_posterior(
        az.from_netcdf("modules/modelo_bayesiano_trace.nc"),
        var_names=["beta"],
        coords={"coef": [param]},
        hdi_prob=0.95,
        ax=axes[i]
    )
    if param in resultados_freq.index:
        freq_val = resultados_freq.loc[param, "Coeficiente (log)"]
        axes[i].axvline(freq_val, color="blue", linestyle="--", label="Freq Coef")
        axes[i].legend()

st.pyplot(fig)


# ========================
# 6. Conclusão
# ========================
st.subheader("📌 Considerações Finais")

st.markdown("""
- Ambos os modelos convergem para conclusões semelhantes nos efeitos mais fortes:  
  **rede pública (efeito negativo)**, **docentes avançados (efeito positivo)** e **modalidade presencial (efeito negativo)**.  

- O modelo **Bayesiano** fornece **mais nuances** (distribuições completas), 
enquanto o **Frequentista** é mais rápido e prático para rodar em tempo real.  

- Diferenças pequenas nos valores se devem a:  
  1. Priors do modelo Bayesiano.  
  2. Sobredispersão ajustada de forma mais flexível no Bayesiano.  
  3. Amostragem MCMC vs estimação por máxima verossimilhança.  
""")
