"""
Dashboard Streamlit para Análise Bayesiana
Censo da Educação Superior 2023

Autor: Robson Jobs
Disciplina: Inferência Bayesiana (2/2025)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configurações da página
st.set_page_config(
    page_title="Dashboard - Inferência Bayesiana",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos locais
try:
    from data_loader import DataLoader
    from bayesian_models import BayesianModels
    from visualizations import Visualizations
    from utils import Utils
    import config
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.info("Certifique-se de que todos os arquivos necessários estão presentes.")

def main():
    """Função principal do dashboard"""
    
    # Título principal
    st.title("🎓 Dashboard de Inferência Bayesiana")
    st.markdown("### Análise do Censo da Educação Superior 2023")
    
    # Sidebar para navegação
    st.sidebar.title("🧭 Navegação")
    
    # Menu de opções
    menu_opcoes = [
        "🏠 Início",
        "📊 Análise Exploratória", 
        "🔬 Modelos Bayesianos",
        "📈 Visualizações",
        "🔍 Comparação de Modelos",
        "📋 Relatórios",
        "ℹ️ Sobre"
    ]
    
    escolha = st.sidebar.selectbox("Selecione uma opção:", menu_opcoes)
    
    # Seção de upload de dados
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Dados")
    
    uploaded_file = st.sidebar.file_uploader(
        "Carregar arquivo CSV",
        type=['csv'],
        help="Faça upload dos dados do Censo da Educação Superior"
    )
    
    # Inicializar session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    
    # Carregar dados
    if uploaded_file is not None:
        try:
            data_loader = DataLoader()
            st.session_state.data = data_loader.load_csv(uploaded_file)
            st.sidebar.success(f"✅ Dados carregados: {st.session_state.data.shape[0]} registros")
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao carregar dados: {e}")
    
    # Roteamento das páginas
    if escolha == "🏠 Início":
        pagina_inicio()
    elif escolha == "📊 Análise Exploratória":
        pagina_analise_exploratoria()
    elif escolha == "🔬 Modelos Bayesianos":
        pagina_modelos_bayesianos()
    elif escolha == "📈 Visualizações":
        pagina_visualizacoes()
    elif escolha == "🔍 Comparação de Modelos":
        pagina_comparacao_modelos()
    elif escolha == "📋 Relatórios":
        pagina_relatorios()
    elif escolha == "ℹ️ Sobre":
        pagina_sobre()

def pagina_inicio():
    """Página inicial do dashboard"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🎯 Objetivo do Projeto
        
        Este dashboard foi desenvolvido para análise bayesiana dos dados do **Censo da Educação Superior 2023**, 
        permitindo explorar tendências, padrões e fazer inferências estatísticas sobre o ensino superior brasileiro.
        
        ### 🔧 Funcionalidades Principais:
        
        - **📊 Análise Exploratória**: Estatísticas descritivas e visualizações iniciais
        - **🔬 Modelos Bayesianos**: Implementação de diversos modelos estatísticos
        - **📈 Visualizações**: Gráficos interativos e dashboards customizados
        - **🔍 Comparação**: Análise comparativa entre diferentes modelos
        - **📋 Relatórios**: Geração de relatórios detalhados
        
        ### 🚀 Como Começar:
        
        1. **Carregue seus dados** usando o painel lateral
        2. **Explore** as diferentes seções do menu
        3. **Configure** os modelos bayesianos
        4. **Analise** os resultados e interpretações
        """)
    
    with col2:
        st.markdown("### 📈 Status do Sistema")
        
        # Verificar status dos dados
        if st.session_state.data is not None:
            st.success("✅ Dados carregados")
            st.metric("Registros", st.session_state.data.shape[0])
            st.metric("Variáveis", st.session_state.data.shape[1])
        else:
            st.warning("⚠️ Nenhum dado carregado")
            st.info("👆 Use o painel lateral para carregar seus dados")
        
        # Exemplo de métricas
        if st.session_state.data is not None:
            st.markdown("### 🔢 Estatísticas Rápidas")
            st.metric("Universidades", "2.431", delta="12")
            st.metric("Cursos", "41.891", delta="1.254")
            st.metric("Matrículas", "9.046.251", delta="105.476")

def pagina_analise_exploratoria():
    """Página de análise exploratória dos dados"""
    
    st.header("📊 Análise Exploratória dos Dados")
    
    if st.session_state.data is None:
        st.warning("⚠️ Carregue os dados primeiro usando o painel lateral.")
        return
    
    df = st.session_state.data
    
    # Tabs para organizar a análise
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Visão Geral", "📊 Distribuições", "🔗 Correlações", "🎯 Filtros"])
    
    with tab1:
        st.subheader("Visão Geral dos Dados")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Registros", df.shape[0])
        with col2:
            st.metric("Total de Variáveis", df.shape[1])
        with col3:
            st.metric("Valores Nulos", df.isnull().sum().sum())
        with col4:
            st.metric("Memória (MB)", f"{df.memory_usage().sum() / 1024**2:.2f}")
        
        st.subheader("Amostra dos Dados")
        st.dataframe(df.head(10), use_container_width=True)
        
        st.subheader("Informações das Variáveis")
        st.dataframe(df.describe(), use_container_width=True)
    
    with tab2:
        st.subheader("Distribuições das Variáveis")
        
        # Selecionar coluna para análise
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Selecione uma variável:", numeric_cols)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df, x=selected_col, title=f"Distribuição de {selected_col}")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(df, y=selected_col, title=f"Box Plot de {selected_col}")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Matriz de Correlação")
        
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                          title="Matriz de Correlação")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Filtros e Segmentação")
        st.info("🔧 Funcionalidade em desenvolvimento")

def pagina_modelos_bayesianos():
    """Página para configuração e execução de modelos bayesianos"""
    
    st.header("🔬 Modelos Bayesianos")
    
    if st.session_state.data is None:
        st.warning("⚠️ Carregue os dados primeiro usando o painel lateral.")
        return
    
    st.markdown("""
    ### Modelos Disponíveis:
    
    Selecione o tipo de modelo bayesiano que deseja aplicar aos dados:
    """)
    
    # Seleção do modelo
    modelo_opcoes = [
        "Regressão Linear Bayesiana",
        "Regressão Logística Bayesiana", 
        "Modelo Hierárquico",
        "Análise de Variância Bayesiana",
        "Modelo de Mistura"
    ]
    
    modelo_selecionado = st.selectbox("Escolha um modelo:", modelo_opcoes)
    
    # Configurações do modelo
    st.subheader("⚙️ Configurações do Modelo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Parâmetros Gerais:**")
        n_samples = st.number_input("Número de amostras:", min_value=1000, max_value=10000, value=2000)
        n_chains = st.number_input("Número de cadeias:", min_value=1, max_value=8, value=2)
        tune_steps = st.number_input("Passos de tuning:", min_value=500, max_value=2000, value=1000)
    
    with col2:
        st.markdown("**Seleção de Variáveis:**")
        numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            target_var = st.selectbox("Variável dependente:", numeric_cols)
            predictor_vars = st.multiselect("Variáveis independentes:", 
                                          [col for col in numeric_cols if col != target_var])
    
    # Botão para executar modelo
    if st.button("🚀 Executar Modelo"):
        with st.spinner("Executando modelo bayesiano..."):
            st.info("🔧 Funcionalidade em desenvolvimento - Modelo será implementado em breve")
            # Aqui será implementada a lógica do modelo bayesiano
            
    # Resultados (placeholder)
    st.subheader("📊 Resultados do Modelo")
    st.info("Os resultados aparecerão aqui após a execução do modelo")

def pagina_visualizacoes():
    """Página para visualizações avançadas"""
    
    st.header("📈 Visualizações Interativas")
    
    if st.session_state.data is None:
        st.warning("⚠️ Carregue os dados primeiro usando o painel lateral.")
        return
    
    df = st.session_state.data
    
    # Tipos de visualização
    viz_opcoes = [
        "Gráfico de Dispersão",
        "Série Temporal", 
        "Mapa de Calor",
        "Gráfico de Barras",
        "Distribuição 3D"
    ]
    
    viz_selecionada = st.selectbox("Tipo de visualização:", viz_opcoes)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if viz_selecionada == "Gráfico de Dispersão" and len(numeric_cols) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            x_var = st.selectbox("Eixo X:", numeric_cols)
        with col2:
            y_var = st.selectbox("Eixo Y:", [col for col in numeric_cols if col != x_var])
        
        if st.button("Gerar Gráfico"):
            fig = px.scatter(df, x=x_var, y=y_var, title=f"{y_var} vs {x_var}")
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info(f"🔧 Visualização '{viz_selecionada}' em desenvolvimento")

def pagina_comparacao_modelos():
    """Página para comparação entre modelos"""
    
    st.header("🔍 Comparação de Modelos")
    st.info("🔧 Funcionalidade em desenvolvimento")
    
    st.markdown("""
    ### Métricas de Comparação:
    
    - **WAIC** (Widely Applicable Information Criterion)
    - **LOO** (Leave-One-Out Cross-Validation)
    - **R-hat** (Potential Scale Reduction Factor)
    - **ESS** (Effective Sample Size)
    """)

def pagina_relatorios():
    """Página para geração de relatórios"""
    
    st.header("📋 Relatórios")
    st.info("🔧 Funcionalidade em desenvolvimento")
    
    st.markdown("""
    ### Tipos de Relatório:
    
    - **Relatório Executivo**: Resumo das principais descobertas
    - **Relatório Técnico**: Detalhes metodológicos e estatísticos
    - **Relatório de Qualidade**: Avaliação da qualidade dos dados
    """)

def pagina_sobre():
    """Página com informações sobre o projeto"""
    
    st.header("ℹ️ Sobre o Projeto")
    
    st.markdown("""
    ## 🎓 Inferência Bayesiana - Censo da Educação Superior 2023
    
    ### 👨‍💻 Autor
    **Robson Jobs**
    
    ### 🏫 Contexto Acadêmico
    - **Disciplina**: Inferência Bayesiana
    - **Período**: 2/2025
    - **Objetivo**: Trabalho 1 da disciplina
    
    ### 📊 Fonte dos Dados
    **Censo da Educação Superior 2023** - INEP/MEC
    
    ### 🛠️ Tecnologias Utilizadas
    - **Streamlit**: Framework para criação do dashboard
    - **PyMC**: Biblioteca para modelagem bayesiana
    - **Plotly**: Visualizações interativas
    - **Pandas**: Manipulação de dados
    - **NumPy**: Computação numérica
    - **ArviZ**: Análise de resultados bayesianos
    
    ### 📚 Referências
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [PyMC Documentation](https://docs.pymc.io/)
    - [Bayesian Methods for Hackers](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers)
    
    ### 📄 Licença
    Este projeto está sob a licença especificada no arquivo LICENSE.
    """)

if __name__ == "__main__":
    main()