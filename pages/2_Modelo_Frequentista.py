import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from app import load_complete_ride_data, calcular_metricas_educacionais
import statsmodels.api as sm
import statsmodels.formula.api as smf
import altair as alt


# Carregar dados integrados
df, error = load_complete_ride_data()
if error:
    st.error(f'❌ Erro ao carregar dados integrados: {error}')
    st.stop()


if df is not None and not df.empty:
    print("Dados integrados carregados com sucesso.")


    # Execução do Modelo
    @st.cache_data

    # Função de preparação
    def preparar_dados(df: pd.DataFrame) -> pd.DataFrame:
        """Cria variáveis derivadas e prepara dados para modelagem NB."""
        df = df.copy()
        df.columns = [c.lower() for c in df.columns]

        # Total de docentes
        df["qt_doc_total_calc"] = (
            df["qt_doc_ex_grad"].fillna(0)
            + df["qt_doc_ex_esp"].fillna(0)
            + df["qt_doc_ex_mest"].fillna(0)
            + df["qt_doc_ex_dout"].fillna(0)
        )

        # Proporção de docentes avançados (mestres + doutores)
        df["prop_doc_avancado"] = (
            (df["qt_doc_ex_mest"].fillna(0) + df["qt_doc_ex_dout"].fillna(0))
            / df["qt_doc_total_calc"].replace(0, np.nan)
        )

        # Proporções de ingressantes
        df["prop_ing_pp"] = (df["qt_ing_preta"] + df["qt_ing_parda"]) / df["qt_ing"].replace(0, np.nan)
        df["prop_ing_financiados"] = (
            df["qt_ing_fies"] + df["qt_ing_prounii"] + df["qt_ing_prounip"]
        ) / df["qt_ing"].replace(0, np.nan)

        # Tratar NaN e limitar
        for col in ["prop_doc_avancado", "prop_ing_pp", "prop_ing_financiados"]:
            df[col] = df[col].fillna(0).clip(0, 1)

        # Remover linhas inválidas
        df_model = df[(df["qt_ing"].notnull()) & (df["qt_ing"] >= 0) & (df["qt_mat"] > 0)].copy()

        # Criar offset
        df_model["offset_log_qtmat"] = np.log(df_model["qt_mat"])

        return df_model


    # 2. Função de modelagem
    @st.cache_data
    def ajustar_modelo(df_model: pd.DataFrame):
        """Ajusta regressão Binomial Negativa com offset log(qt_mat)."""
        formula = """
        qt_ing ~ C(tp_rede)
            + C(tp_organizacao_academica)
            + C(tp_grau_academico)
            + C(tp_modalidade_ensino)
            + qt_conc
            + prop_doc_avancado
            + prop_ing_pp
            + prop_ing_financiados
        """

        modelo = smf.glm(
            formula=formula,
            data=df_model,
            family=sm.families.NegativeBinomial(),
            offset=df_model["offset_log_qtmat"]
        ).fit()

        return modelo


    # 3. Função de visualização
    def mostrar_resultados_formatados(modelo):
        """Mostra resultados do modelo NB em formato tabular e gráfico bonito."""

        # Extrair coeficientes, ICs e IRR
        coef = modelo.params
        pvals = modelo.pvalues
        conf = modelo.conf_int()
        irr = np.exp(coef)
        irr_low = np.exp(conf[0])
        irr_high = np.exp(conf[1])

        resultados = pd.DataFrame({
            "Variável": coef.index,
            "Coeficiente (log)": coef.values.round(3),
            "IRR (exp(coef))": irr.values.round(3),
            "IC 95% (low)": irr_low.values.round(3),
            "IC 95% (high)": irr_high.values.round(3),
            "p-valor": pvals.values.round(4)
        })

        # Mostrar tabela formatada
        st.dataframe(resultados, use_container_width=True)

        # Forest plot interativo
        fig = px.scatter(
            resultados,
            x="IRR (exp(coef))",
            y="Variável",
            error_x=resultados["IRR (exp(coef))"] - resultados["IC 95% (low)"],
            error_x_minus=resultados["IC 95% (high)"] - resultados["IRR (exp(coef))"],
            color=(resultados["p-valor"] < 0.05).map({True: "Significativo", False: "Não significativo"}),
            symbol=(resultados["p-valor"] < 0.05).map({True: "circle", False: "x"}),
            labels={"IRR (exp(coef))": "Razão de Taxa (IRR)", "Variável": "Variáveis"}
        )

        fig.update_layout(
            xaxis_type="log",
            shapes=[{"type": "line", "x0": 1, "x1": 1, "y0": -1, "y1": len(resultados),
                    "line": {"color": "red", "dash": "dash"}}],
            height=600
        )

        st.subheader("Forest Plot das Razões de Taxa (IRR)")
        st.plotly_chart(fig, use_container_width=True)



    df_model = preparar_dados(df)
    modelo = ajustar_modelo(df_model)


    st.subheader("Modelo Frequentista - Regressão Binomial Negativa")

    st.markdown("""
    O modelo de **Regressão Binomial Negativa** buscou identificar quais fatores institucionais e socioeconômicos estão associados à taxa de ingresso em cursos de graduação na RIDE-DF em 2023, isto é, o número de ingressantes ajustado pelo tamanho total de matrículas de cada curso.
            """)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Descrição do Modelo", "Variáveis do Modelo", "Resultados do Modelo"])
    with tab1:

        st.markdown("""#### Regressão Binomial Negativa com Offset""")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
                    O fenômeno analisado (quantidade de ingressantes em cursos de graduação) é um **dado de contagem**, ou seja, assume apenas valores inteiros não negativos. Modelos de regressão tradicionais (como OLS) não são adequados nesse contexto, pois assumem distribuição normal dos resíduos, o que não se verifica para contagens.

                    O modelo natural para esse tipo de dado seria a Regressão de Poisson, que supõe que a média e a variância da variável resposta sejam iguais. No entanto, ao analisar os dados da RIDE-DF, observou-se um padrão típico de sobredispersão: a variância dos ingressantes por curso é muito maior do que a média. Isso inviabiliza o uso do Poisson, pois leva a erros-padrão subestimados e a inferências estatísticas incorretas.
                    """)

        st.markdown("""
                    A Regressão Binomial Negativa é uma extensão de Poisson que introduz um parâmetro extra justamente para capturar essa sobredispersão, permitindo que a variância seja maior que a média. Isso torna o modelo mais realista e robusto para fenômenos em que há muitos cursos pequenos com poucos ingressantes e poucos cursos muito grandes com muitos ingressantes — exatamente o cenário do ensino superior brasileiro.

                    Além disso, incluiu-se um offset ```log(qt_mat)``` no modelo. Esse termo ajusta o número de ingressantes pelo tamanho total de matrículas de cada curso, permitindo interpretar os resultados em termos de taxa de ingresso proporcional ao tamanho do curso, e não apenas em números absolutos. Isso evita que cursos grandes dominem o modelo apenas por seu volume, trazendo uma visão mais justa sobre os fatores associados às diferenças de ingresso.
                    """)
        
        st.markdown("""
                    Assim, a Regressão Binomial Negativa com offset é o modelo mais apropriado porque:

                    - Trabalha com dados de contagem;

                    - Corrige o problema da sobredispersão;

                    - Permite analisar taxas de ingresso ajustadas pelo tamanho do curso;

                    - Fornece estimativas consistentes e interpretações claras via razões de taxa (IRR).
                    """)


    with tab2:
        st.markdown("#### Variáveis utilizadas no Modelo")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("###### Escolha das Variáveis")
        st.markdown(""" <ul>
                            <li><b>Relevância teórica:</b> variáveis reconhecidas pela literatura como determinantes do ingresso.</li>
                            <li><b>Disponibilidade:</b> dados oficiais e comparáveis do Censo da Educação Superior.</li>
                            <li><b>Evitar redundância:</b> uso de proporções em vez de valores absolutos, prevenindo colinearidade.</li>
                        </ul> 
                    """, unsafe_allow_html=True)

        st.divider()

        col1, col2 = st.columns(2, gap="large")
        with col1:

            st.markdown("""
                        <div style="text-align: justify">
                        <h5>Variável Dependente (Y) </h5>
                        <h6><code>qt_ing</code> - Quantidade de ingressantes em 2023</h6>

                        Essa é a variável de interesse central da pesquisa, pois responde diretamente à pergunta: <b><em>quais fatores institucionais e socioeconômicos estão associados ao ingresso de novos estudantes nos cursos de graduação da RIDE-DF em 2023?</em></b>
                        
                        Optou-se por modelar o número de ingressantes em vez do total de matrículas, já que este último mistura alunos veteranos com calouros, enquanto o ingresso capta melhor a dinâmica de expansão ou retração dos cursos.
                        </div>
                        """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
                        <div style="text-align: justify">
                        <h5>Variável Offset</h5>
                        <h6><code>log(qt_mat)</code> - Logaritmo do total de matrículas em 2023</h6>

                        Esse termo é crucial para ajustar o número de ingressantes pelo tamanho total de matrículas de cada curso, permitindo uma interpretação mais justa dos resultados. Ao incluir o offset, é possível analisar as taxas de ingresso proporcionais ao tamanho do curso, em vez de apenas números absolutos. Isso evita que cursos maiores dominem o modelo apenas por seu volume de matrículas.
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

        


    with tab3:
        st.markdown("#### **Resultados do Modelo**")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Extrair coeficientes, ICs e IRR
        coef = modelo.params
        pvals = modelo.pvalues
        conf = modelo.conf_int()
        irr = np.exp(coef)
        irr_low = np.exp(conf[0])
        irr_high = np.exp(conf[1])

        resultados = pd.DataFrame({
            "Variável": coef.index,
            "Coeficiente (log)": coef.values.round(3),
            "IRR (exp(coef))": irr.values.round(3),
            "IC 95% (low)": irr_low.values.round(3),
            "IC 95% (high)": irr_high.values.round(3),
            "p-valor": pvals.values.round(4)
        })

        # Mostrar tabela formatada
        st.markdown("<h5>Resultados Brutos da Regressão</h5>", unsafe_allow_html=True)
        st.dataframe(resultados, use_container_width=True)

        # Explicação dos resultados
        with st.expander("Sobre Coeficientes, IRR, IC e p-Valores", icon=":material/info:"):
            st.markdown("""
                        <div style="text-align: justify">
                        <p>Os coeficientes da regressão Binomial Negativa são apresentados em termos de logaritmos, o que pode dificultar a interpretação direta. Por isso, também reportamos as <b>Razões de Taxa (IRR)</b>, que são obtidas exponenciando os coeficientes. A IRR indica o fator multiplicativo esperado na taxa de ingresso para um aumento unitário na variável preditora, mantendo todas as outras constantes.</p>
                        <ul>
                            <li>Uma <b>IRR > 1</b> sugere que um aumento na variável está associado a um aumento na taxa de ingresso.</li>
                            <li>Uma <b>IRR < 1</b> indica que um aumento na variável está associado a uma diminuição na taxa de ingresso.</li>
                            <li>Uma <b>IRR = 1</b> implica que a variável não tem efeito sobre a taxa de ingresso.</li>
                        </ul>
                        <p>Os <b>Intervalos de Confiança (IC 95%)</b> fornecem uma faixa plausível para a verdadeira IRR. Se o IC incluir 1, o efeito pode não ser estatisticamente significativo. O valor-p associado testa a hipótese nula de que o coeficiente é zero (ou seja, IRR = 1). Valores-p menores que 0.05 são geralmente considerados estatisticamente significativos.</p>
                        <p>Essa abordagem permite uma interpretação intuitiva dos efeitos das variáveis preditoras sobre a taxa de ingresso, facilitando a comunicação dos resultados para públicos não técnicos.</p>
                        </div>
                        """, unsafe_allow_html=True)
            
        st.divider()

        st.markdown("<h5>Forest Plot</h5>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Forest plot interativo
        fig = px.scatter(
            resultados,
            x="IRR (exp(coef))",
            y="Variável",
            error_x=resultados["IRR (exp(coef))"] - resultados["IC 95% (low)"],
            error_x_minus=resultados["IC 95% (high)"] - resultados["IRR (exp(coef))"],
            color=(resultados["p-valor"] < 0.05).map({True: "Significativo", False: "Não significativo"}),
            symbol=(resultados["p-valor"] < 0.05).map({True: "circle", False: "x"}),
            labels={"IRR (exp(coef))": "Razão de Taxa (IRR)", "Variável": "Variáveis"},
            title="Forest Plot das Razões de Taxa (IRR)"
        )

        fig.update_layout(
            xaxis_type="log",
            shapes=[{"type": "line", "x0": 1, "x1": 1, "y0": -1, "y1": len(resultados),
                    "line": {"color": "red", "dash": "dash"}}],
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Interpretação do Forest Plot", icon=":material/info:"):
            st.markdown("""
                        <div style="text-align: justify">
                        <p>O Forest Plot acima visualiza as Razões de Taxa (IRR) para cada variável do modelo, juntamente com seus Intervalos de Confiança (IC 95%). Cada ponto representa a IRR estimada, enquanto as linhas horizontais indicam o intervalo plausível para essa estimativa.</p>
                        <ul>
                            <li>O eixo x está em escala logarítmica para melhor visualização das razões de taxa.</li>
                            <li>A linha vermelha vertical em x=1 indica o ponto onde a variável não teria efeito sobre a taxa de ingresso (IRR = 1).</li>
                            <li>Variáveis com IC que não cruzam a linha vermelha são consideradas estatisticamente significativas.</li>
                            <li>As cores e símbolos diferenciam variáveis significativas (círculo azul) de não significativas (x vermelho).</li>
                        </ul>
                        """, unsafe_allow_html=True)
            

        st.divider()

        st.markdown("#### **Análise dos Resultados**")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
                    <div style="text-align: justify">
                    O <b>modelo de regressão Binomial Negativa</b> buscou identificar os fatores institucionais e socioeconômicos associados à taxa de ingresso em cursos de graduação na RIDE-DF em 2023. A modelagem utilizou <code>qt_ing</code> (número de ingressantes) como variável dependente, com offset <code>log(qt_mat)</code>, de modo que os resultados devem ser interpretados como taxas relativas de ingresso em função do tamanho do curso.
                    <br>
                    Os coeficientes foram transformados em <b>Razões de Taxa (IRR)</b>, que indicam quanto a taxa de ingresso aumenta (>1) ou diminui (<1) em comparação à categoria de referência ou ao incremento unitário da variável.
                    """, unsafe_allow_html=True)
        
        st.markdown("""
                    <div style="text-align: justify">
                    <br>
                    <h5>Rede Institucional</h5>
                    <ul>
                        <li><b>Públicas vs Privadas:</b> Cursos ofertados em instituições públicas apresentaram taxa de ingresso <b>53% menor</b> em relação às privadas (IRR ≈ 0.47, p<0.001).
                        Esse resultado reflete a seletividade das instituições públicas, onde o acesso é mais restrito devido a processos concorridos de ingresso (vestibulares e SISU), ao passo que as privadas tendem a ajustar sua capacidade de absorção conforme a demanda.
                        A categoria <i>Privada</i> foi a referência do modelo, portanto todos os efeitos de “Pública” são comparativos a ela.</li>
                    </ul>
                    
                    <br>
                    <h5>Organização Acadêmica</h5>
                    <ul>
                        <li><b>Universidades:</b> Apresentaram taxas de ingresso cerca de <b>22% menores</b> do que os centros universitários (referência). Isso sugere que universidades concentram cursos maiores e mais tradicionais, mas proporcionalmente recebem menos ingressantes por matrícula, refletindo maior concorrência e seletividade. </li>
                        <li><b>Institutos Federais:</b> Mostraram um efeito positivo (IRR ≈ 1.36), porém não significativo estatisticamente. O sinal indica maior capacidade de absorção relativa, mas os resultados não permitem afirmar com segurança.</li>
                        <li><b>Faculdades:</b> Não diferiram significativamente dos centros universitários, indicando desempenho semelhante em termos de taxa de ingresso por matrícula.</li>
                        <li><b>Categoria base:</b> Centros universitários, utilizados como referência. </li>
                    </ul>

                    <br>
                    <h5>Grau acadêmico</h5>
                    <ul>
                        <li><b>Tecnológicos:</b> Cursos de curta duração e voltados ao mercado apresentaram 7% mais ingressantes em relação aos bacharelados (p<0.05), reforçando sua atratividade como formações rápidas e acessíveis.</li>
                        <li><b>Não aplicável:</b> Apresentaram efeito fortíssimo (IRR ≈ 4.47), indicando que esses cursos atraem mais de quatro vezes a taxa de ingresso dos bacharelados. Esse achado, provavelmente ligado a classificações administrativas específicas ou cursos em EAD, merece análise mais detalhada, pois pode refletir inconsistências de categorização no Censo.</li>
                        <li><b>Licenciaturas:</b> Não apresentaram diferenças estatisticamente significativas em relação aos bacharelados, sugerindo equivalência no padrão de ingressos por matrícula.</li>
                        <li><b>Categoria base:</b> Bacharelado, utilizados como referência. </li>
                    </ul>

                    <br>
                    <h5>Modalidade de Ensino</h5>
                    <ul>
                        <li><b>Presencial vs EAD:</b> Cursos presenciais exibiram <b>44% menos ingressantes por matrícula</b> em comparação aos cursos EAD (IRR ≈ 0.56, p<0.001). Esse resultado confirma o papel do ensino a distância como motor de expansão, com alta capacidade de escalar a captação de novos estudantes. No contexto da RIDE-DF, isso é particularmente relevante, dado o aumento da oferta de EAD em áreas metropolitanas e cidades do entorno.</li>
                    </ul>


                    <br>
                    <h5>Qualificação dos Docentes</h5>
                    <ul>
                        <li>A proporção de mestres e doutores entre os docentes está fortemente associada ao ingresso: cursos com maior qualificação acadêmica no corpo docente apresentam mais de 5 vezes a taxa de ingresso em comparação a cursos com menor qualificação (IRR ≈ 5.55, p<0.001).</li>
                        <li>Esse resultado indica que a percepção de qualidade, reputação e credibilidade institucional exerce papel fundamental na decisão dos estudantes.</li>
                        </li> Pode também refletir maior investimento em cursos estratégicos (como universidades privadas consolidadas e públicas federais), que possuem corpo docente mais qualificado e maior atratividade. </li>
                    </ul>

                    <br>
                    <h5>Perfil dos Ingressantes</h5>
                    <ul>
                        <li><b>Proporção de pretos e pardos:</b> Cursos com maior participação de pretos e pardos tiveram taxa de ingresso <b>42% superior</b> (IRR ≈ 1.42, p<0.001). Isso sugere que políticas de inclusão e a própria composição demográfica da região metropolitana de Brasília estão impulsionando a presença desses grupos nos cursos de graduação. </li>
                        <li><b>Proporção de Financiados:</b> O efeito não foi estatisticamente significativo após o ajuste pelo tamanho do curso. Isso indica que programas como FIES e PROUNI são importantes para viabilizar o acesso, mas sua distribuição é relativamente homogênea entre cursos de diferentes características, não alterando de forma clara as taxas proporcionais de ingresso. </li>
                    </ul>

                    <br>
                    <h5>Concluintes</h5>
                    <ul>
                        <li>O número de concluintes não apresentou efeito significativo (IRR ≈ 1.00). Ou seja, o fato de um curso já ter formado mais ou menos turmas em 2023 não influencia diretamente sua capacidade de atrair novos alunos no mesmo ano. </li>
                    </ul>

                    </div>
                    
                    <div style="text-align: justify">
                    <br>

                    <h4>Considerações Finais</h4>
                    O modelo evidencia que as taxas de ingresso na RIDE-DF em 2023 foram fortemente determinadas por três grandes eixos:
                    <ul>
                        <li><b>Modalidade de Ensino:</b> Cursos EAD se destacam por absorver muito mais ingressantes proporcionalmente, enquanto cursos presenciais apresentam limitações estruturais de expansão.</li>
                        <li><b>Qualificação do Docente:</b> Cursos com maior proporção de mestres e doutores no corpo docente são os que mais atraem novos alunos, evidenciando a importância da qualidade acadêmica para a atratividade.</li>
                        <li><b>Perfil Racial dos Ingressantes:</b> Cursos com maior presença de pretos e pardos registraram taxas mais elevadas de ingresso, refletindo tanto a demanda social reprimida quanto os efeitos de políticas de inclusão.</li>
                    </ul>

                    Por outro lado, universidades e instituições públicas mostraram seletividade maior, com taxas proporcionais menores de ingresso. O financiamento estudantil (FIES/PROUNI) e o número de concluintes não explicaram diferenças significativas quando controlado o tamanho do curso.

                    Em síntese: o ingresso no ensino superior da RIDE-DF em 2023 foi mais sensível a fatores de modalidade, qualidade docente e inclusão social do que ao simples perfil institucional ou às políticas de financiamento.

                    </div>
        
""", unsafe_allow_html=True)

else:
    st.warning('⚠️ Dados integrados não disponíveis.')
    st.stop()