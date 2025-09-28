import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import arviz as az
import matplotlib.pyplot as plt
import numpy as np

# ========================
# 0. Carregar trace salvo
# ========================
idata = az.from_netcdf("modules/modelo_bayesiano_trace.nc")

# Lista de nomes dos betas na ordem correta
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

# Adicionar coordenadas legíveis
idata.posterior = idata.posterior.rename_dims({"beta_dim_0": "coef"})
idata.posterior = idata.posterior.assign_coords(coef=colnames)




# ========================
# 1. Título e Explicação
# ========================
st.subheader("Comparação entre Modelos - Frequentista vs Bayesiano")

st.markdown("""
Nesta seção, comparamos os resultados da **Regressão Binomial Negativa Frequentista** 
(GLM com statsmodels) e da **Regressão Binomial Negativa Bayesiana** (PyMC).   O objetivo é verificar se os dois modelos convergem para conclusões semelhantes e entender 
as vantagens de cada abordagem.
""")

st.divider()


# ========================
# 2. Carregar Resultados
# ========================
resultados_freq = pd.read_csv("modules/resultados_freq.csv", index_col=0)
resultados_bayes = pd.read_csv("modules/resultados_bayes.csv", index_col=0)

# ========================
# Padronização de nomes entre os modelos
# ========================
mapa_variaveis = {
    "C(tp_rede)[T.Pública]": "tp_rede_Pública",
    "C(tp_modalidade_ensino)[T.Presencial]": "tp_modalidade_ensino_Presencial",
    "C(tp_grau_academico)[T.Tecnológico]": "tp_grau_academico_Tecnológico",
    "C(tp_grau_academico)[T.Não aplicável]": "tp_grau_academico_Não aplicável",
    "C(tp_grau_academico)[T.Licenciatura]": "tp_grau_academico_Licenciatura",
    "C(tp_organizacao_academica)[T.Universidade]": "tp_organizacao_academica_Universidade",
    "C(tp_organizacao_academica)[T.Instituto Federal de Educação, Ciência e Tecnologia]":
        "tp_organizacao_academica_Instituto Federal de Educação, Ciência e Tecnologia",
    "C(tp_organizacao_academica)[T.Faculdade]": "tp_organizacao_academica_Faculdade",
    "qt_conc": "qt_conc",
    "prop_doc_avancado": "prop_doc_avancado",
    "prop_ing_pp": "prop_ing_pp",
    "prop_ing_financiados": "prop_ing_financiados",
    "Intercept": "Intercepto"
}

# Aplicar renomeação nas tabelas
resultados_freq = resultados_freq.rename(index=mapa_variaveis)
resultados_bayes = resultados_bayes.rename(index=lambda x: mapa_variaveis.get(x, x))

# ========================
# 3. Tabela Comparativa
# ========================
st.markdown("##### Tabela Comparativa")

tabela_comparativa = pd.DataFrame({
    "Frequentista (Coef)": resultados_freq["Coeficiente (log)"],
    "Frequentista (IRR)": resultados_freq["IRR (exp(coef))"],
    "Bayesiano (Média)": resultados_bayes["mean"],
    "Bayesiano (HDI 3%)": resultados_bayes["hdi_3%"],
    "Bayesiano (HDI 97%)": resultados_bayes["hdi_97%"],
})

st.dataframe(tabela_comparativa, use_container_width=True)

# ========================
# 8. Interpretação da Tabela Comparativa
# ========================
with st.expander("Interpretação da Tabela Comparativa", icon=":material/bar_chart:"):

    st.markdown("""
    - **Frequentista (Coef):**  
        Coeficiente estimado pelo modelo de regressão Binomial Negativa (na escala log). Valores negativos indicam redução na taxa de ingresso, e positivos indicam aumento.
    - **Frequentista (IRR):**  
        Razão de Taxa (Incidence Rate Ratio = exp(coef)). Indica o efeito multiplicativo sobre a taxa de ingresso.  
        - IRR > 1 → efeito de aumento.  
        - IRR < 1 → efeito de redução.  
        - IRR = 1 → ausência de efeito.
    - **Bayesiano (Média):**  
        Média da distribuição posterior do coeficiente (na escala log). É equivalente ao coeficiente frequentista, mas levando em conta a incerteza da amostragem MCMC.
    - **Bayesiano (HDI 3%):**  
        Limite inferior do Intervalo de Densidade de Maior Probabilidade (HDI) a 95%. Representa o ponto mais baixo plausível para o coeficiente.
    - **Bayesiano (HDI 97%):**  
        Limite superior do Intervalo de Densidade de Maior Probabilidade (HDI) a 95%. Representa o ponto mais alto plausível para o coeficiente.


    ###### ✅ Em resumo
    O modelo **Frequentista** fornece apenas uma estimativa pontual e intervalo de confiança, enquanto o **Bayesiano** fornece toda a distribuição de incerteza dos parâmetros.
    """)

    st.divider()

    st.markdown("""
        A tabela acima mostra lado a lado os coeficientes estimados pelos dois modelos 
        (**Frequentista** e **Bayesiano**) para cada variável, permitindo identificar 
        semelhanças e diferenças.

        1. **Consistência geral entre os modelos**  
            - Para a maioria das variáveis, as estimativas frequentistas e bayesianas estão muito próximas, reforçando a robustez dos resultados.  
            - As diferenças aparecem mais na **amplitude dos intervalos**, já que o Bayesiano tende a ser mais conservador (intervalos mais largos).              
        2. **Rede Pública (`tp_rede_Pública`)**  
            - Frequentista: coeficiente negativo claro.  
            - Bayesiano: média semelhante, com HDI igualmente negativo.  
            - Conclusão: forte evidência de que instituições públicas têm menor taxa de ingresso.               
        3. **Modalidade Presencial (`tp_modalidade_ensino_Presencial`)**  
            - Ambos os modelos indicam redução significativa no ingresso em cursos presenciais, confirmando a força da modalidade EAD na expansão.                             
        4. **Proporção de Docentes Avançados (`prop_doc_avancado`)**  
            - Nos dois modelos, o coeficiente é **positivo e forte**, mostrando que cursos com mais mestres/doutores atraem mais ingressantes.  
            - O Bayesiano reforça esse efeito, mas reconhece maior incerteza.           
        5. **Proporção de Ingressantes Pretos e Pardos (`prop_ing_pp`)**  
            - Ambos os métodos apontam tendência positiva.  
            - O Bayesiano apresenta intervalo HDI um pouco mais largo, mas ainda consistente.              
        6. **Proporção de Ingressantes Financiados (`prop_ing_financiados`)**  
            - Aqui aparece uma diferença:  
                - O Frequentista sugere impacto negativo mais definido.  
                - O Bayesiano aponta efeito negativo, mas com maior incerteza (intervalo cobre valores próximos de 0).  
            - Isso mostra que o efeito do financiamento pode não ser tão robusto.
        7. **Intercepto**  
            - Os valores absolutos diferem bastante (por construção dos modelos), mas isso não altera a interpretação prática, já que o interesse principal está nos efeitos relativos das variáveis.


        ###### ✅ Em resumo
        - **Ambos os modelos convergem** nas conclusões principais:  
            - Menor ingresso em instituições públicas e cursos presenciais.  
            - Maior ingresso em cursos com mais docentes qualificados e maior participação de estudantes pretos/pardos.               
        - **Diferenças sutis** surgem em variáveis mais incertas, como financiamento estudantil.  
        - O **Frequentista** é mais direto e tende a intervalos estreitos.  
        - O **Bayesiano** é mais cauteloso, ampliando os intervalos e deixando claro onde a evidência é forte ou fraca.
    """)



st.divider()

# ========================
# 4. Gráfico Comparativo (corrigido e limpo)
# ========================
st.markdown("##### Forest Plot Comparativo")

fig = go.Figure()

# Frequentista: pontos com barras de erro
fig.add_trace(go.Scatter(
    x=resultados_freq["IRR (exp(coef))"],
    y=resultados_freq.index,
    mode="markers",
    name="Frequentista (IRR)",
    marker=dict(color="blue", symbol="circle", size=10),
    error_x=dict(
        type="data",
        symmetric=False,
        array=resultados_freq["IC 95% (high)"] - resultados_freq["IRR (exp(coef))"],
        arrayminus=resultados_freq["IRR (exp(coef))"] - resultados_freq["IC 95% (low)"],
        color="blue"
    )
))

# Bayesiano: pontos com barras de erro
fig.add_trace(go.Scatter(
    x=np.exp(resultados_bayes["mean"]),
    y=resultados_bayes.index,
    mode="markers",
    name="Bayesiano (IRR)",
    marker=dict(color="red", symbol="diamond", size=10),
    error_x=dict(
        type="data",
        symmetric=False,
        array=np.exp(resultados_bayes["hdi_97%"]) - np.exp(resultados_bayes["mean"]),
        arrayminus=np.exp(resultados_bayes["mean"]) - np.exp(resultados_bayes["hdi_3%"]),
        color="red"
    )
))

# Linha vertical em IRR = 1
fig.update_layout(
    xaxis_type="log",
    xaxis_title="Razão de Taxa (IRR, escala log)",
    yaxis_title="Variáveis",
    height=800,
    legend=dict(orientation="h", y=-0.2, x=0.2),
    shapes=[{"type": "line", "x0": 1, "x1": 1, "y0": -1, "y1": len(resultados_freq),
             "line": {"color": "black", "dash": "dash"}}]
)

st.plotly_chart(fig, use_container_width=True)

# ========================
# 7. Interpretação Textual
# ========================
with st.expander("Interpretação do Forest Plot Comparativo", icon=":material/insights:"):
    
    
    st.markdown("""
        O gráfico acima apresenta a comparação entre os **modelos Frequentista (azul)** e **Bayesiano (vermelho)** 
        para a Regressão Binomial Negativa, mostrando a **Razão de Taxa (IRR)** com seus respectivos intervalos de incerteza.

        1. **Rede Pública (`tp_rede_Pública`)**  
            - Ambos os modelos apontam efeito **negativo** (IRR < 1), indicando que cursos em instituições públicas tendem a ter menos ingressantes em relação às privadas.  
            - A consistência entre os modelos reforça a robustez desse achado.
        2. **Modalidade Presencial (`tp_modalidade_ensino_Presencial`)**  
            - Também apresenta efeito **negativo** nos dois modelos.  
            - Cursos presenciais têm menor taxa de ingresso comparados ao EAD, possivelmente refletindo a expansão recente da modalidade a distância.
        3. **Docentes avançados (`prop_doc_avancado`)**  
            - Efeito **positivo forte** e consistente: quanto maior a proporção de mestres e doutores, maior o número de ingressantes.  
            - Isso sugere que a **qualidade do corpo docente** é um atrativo para os estudantes.
        4. **Ingressantes pretos e pardos (`prop_ing_pp`)**  
            - Os dois modelos indicam efeito **positivo moderado**, mas com sobreposição de incerteza.  
            - Pode refletir políticas afirmativas e expansão do acesso.
        5. **Ingressantes financiados (`prop_ing_financiados`)**  
            - Resultados mistos: o frequentista sugere efeito mais forte, enquanto o bayesiano é mais conservador.  
            - Mostra que o impacto do financiamento sobre o ingresso pode variar conforme o método de inferência.
        6. **Nível acadêmico**  
            - Variáveis como `Tecnológico`, `Licenciatura` e `Não aplicável` variam, mas no geral os efeitos são menores em comparação ao bacharelado.  
            - O Bayesiano tende a gerar intervalos mais largos, refletindo maior cautela.
        7. **Intercepto e dispersão (Alpha)**  
            - O **Intercepto** difere em escala, mas não afeta a interpretação prática dos efeitos relativos.  
            - O **Alpha (dispersão)** só aparece no modelo Bayesiano, captando a variabilidade extra que o frequentista trata de forma fixa.

        ---

        - Ambos os modelos chegam a **conclusões convergentes nos efeitos principais**:  
            - **Negativo** para rede pública e presencial.  
            - **Positivo** para proporção de docentes avançados.  
        - O **Bayesiano** fornece **intervalos mais realistas** (incorporando incerteza via priors), enquanto o **Frequentista** tende a intervalos mais estreitos.  
        - Em termos práticos: os resultados são robustos e complementares, reforçando a confiança nas variáveis-chave que explicam o ingresso no ensino superior da RIDE-DF.
""")




# ========================
# 9. Conclusão Geral
# ========================

st.divider()

st.markdown("##### Conclusão Geral")

st.markdown("""
A comparação entre os modelos **Frequentista** e **Bayesiano** confirma que, apesar 
das diferenças metodológicas, ambos levam a conclusões muito semelhantes sobre os 
determinantes da taxa de ingresso na RIDE-DF.

###### ↘️ Pontos centrais de convergência
- **Instituições públicas** → consistentemente associadas a taxas de ingresso menores.  
- **Modalidade presencial** → reduz significativamente a proporção de ingressantes, em favor do EAD.  
- **Qualificação docente** → cursos com maior proporção de mestres e doutores atraem mais ingressantes.  
- **Perfil racial dos ingressantes (pretos e pardos)** → efeito positivo robusto, evidenciando inclusão crescente.
###### 🔀 Diferenças principais
- O **Frequentista** gera estimativas mais pontuais e intervalos estreitos.  
- O **Bayesiano** apresenta distribuições completas, deixando mais claro o grau de incerteza em variáveis ambíguas, como **financiamento estudantil**.  
###### ℹ️ Interpretação
- Para **políticas educacionais**, ambos os modelos indicam a necessidade de:  
  - Expandir e fortalecer o **EAD de qualidade**.  
  - Valorizar a **formação de docentes** (mestres/doutores).  
  - Incentivar **iniciativas de inclusão racial** no ensino superior.  
- O **Bayesiano** acrescenta uma camada de cautela, mostrando onde a evidência é sólida e onde ainda há incerteza.


###### ✅ **Em resumo**
            
Os dois modelos não competem entre si, eles se **complementam**. O Frequentista é rápido e direto, enquanto o Bayesiano oferece uma visão mais rica sobre incertezas. Juntos, eles fornecem uma análise robusta para apoiar decisões estratégicas sobre a expansão e inclusão no ensino superior da RIDE-DF.
""")