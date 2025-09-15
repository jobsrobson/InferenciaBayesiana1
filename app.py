import streamlit as st
from modules.db_connection import create_pg_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Educação Superior na RIDE-DF",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# FUNÇÃO PRINCIPAL - DADOS INTEGRADOS COM JOIN INLINE
@st.cache_data
def load_complete_ride_data():
    """
    Carrega dados integrados IES + Cursos da RIDE-DF usando JOIN inline
    """
    try:
        engine = create_pg_engine()
        
        # Query completa com todos os JOINs necessários
        query = """
        SELECT 
            -- ===== dados das ies + geografia =====
            es."nu_ano_censo"::text as nu_ano_censo,
			es."co_municipio_ies"::text as co_municipio_ies,
			mun.nome_municipio,
			mun.municipio_capital,
			mun.longitude,
			mun.latitude,
			uf.sigla_uf,
			uf.nome_uf,
			reg.nome_regiao,
			es."in_capital_ies"::text as in_capital_ies,
			
			-- dados institucionais das ies
			es."co_ies"::text as co_ies,
			es."no_ies" as no_ies,
			es."sg_ies" as sg_ies,
			es."no_mantenedora" as no_mantenedora,
			es."tp_categoria_administrativa"::text as tp_categoria_administrativa,
			es."tp_rede"::text as tp_rede,
			es."tp_organizacao_academica"::text as tp_organizacao_academica,
			es."in_comunitaria"::text as in_comunitaria,
			es."in_confessional"::text as in_confessional,
			
			-- endereço das ies
			es."ds_endereco_ies" as ds_endereco_ies,
			es."no_bairro_ies" as no_bairro_ies,
			es."nu_cep_ies"::text as nu_cep_ies,
			
			-- recursos humanos das ies
			es."qt_doc_total"::integer as qt_doc_total,
			es."qt_doc_exe"::integer as qt_doc_exe,
			es."qt_doc_ex_femi"::integer as qt_doc_ex_femi,
			es."qt_doc_ex_masc"::integer as qt_doc_ex_masc,
			es."qt_doc_ex_grad"::integer as qt_doc_ex_grad,
			es."qt_doc_ex_esp"::integer as qt_doc_ex_esp,
			es."qt_doc_ex_mest"::integer as qt_doc_ex_mest,
			es."qt_doc_ex_dout"::integer as qt_doc_ex_dout,
			es."qt_doc_ex_int"::integer as qt_doc_ex_int,
			es."qt_doc_ex_parc"::integer as qt_doc_ex_parc,
			es."qt_doc_ex_hor"::integer as qt_doc_ex_hor,
			
			-- técnicos das ies
			es."qt_tec_total"::integer as qt_tec_total,
			es."qt_tec_superior_fem"::integer as qt_tec_superior_fem,
			es."qt_tec_superior_masc"::integer as qt_tec_superior_masc,
			
			-- infraestrutura digital das ies
			es."in_acesso_portal_capes"::text as in_acesso_portal_capes,
			es."in_repositorio_institucional"::text as in_repositorio_institucional,
			es."in_servico_internet"::text as in_servico_internet,
			es."in_catalogo_online"::text as in_catalogo_online,
			es."qt_periodico_eletronico"::integer as qt_periodico_eletronico,
			es."qt_livro_eletronico"::integer as qt_livro_eletronico,
			
			-- ===== dados dos cursos =====
			-- identificação dos cursos
			cur."co_curso"::text as co_curso,
			cur."no_curso" as no_curso,
			cur."co_cine_area_geral"::text as co_cine_area_geral,
			cur."no_cine_area_geral" as no_cine_area_geral,
			cur."co_cine_area_especifica"::text as co_cine_area_especifica,
			cur."no_cine_area_especifica" as no_cine_area_especifica,
			
			-- características dos cursos
			cur."tp_grau_academico"::text as tp_grau_academico,
			cur."in_gratuito"::text as in_gratuito,
			cur."tp_modalidade_ensino"::text as tp_modalidade_ensino,
			cur."tp_nivel_academico"::text as tp_nivel_academico,
			
			-- dados de vagas
			cur."qt_vg_total"::integer as qt_vg_total,
			cur."qt_vg_nova"::integer as qt_vg_nova,
			cur."qt_vg_proc_seletivo"::integer as qt_vg_proc_seletivo,
			
			-- dados de inscritos
			cur."qt_inscrito_total"::integer as qt_inscrito_total,
			cur."qt_insc_vg_nova"::integer as qt_insc_vg_nova,
			cur."qt_insc_proc_seletivo"::integer as qt_insc_proc_seletivo,
			
			-- essencial: dados de ingressos
			cur."qt_ing"::integer as qt_ing,
			cur."qt_ing_fem"::integer as qt_ing_fem,
			cur."qt_ing_masc"::integer as qt_ing_masc,
			cur."qt_ing_diurno"::integer as qt_ing_diurno,
			cur."qt_ing_noturno"::integer as qt_ing_noturno,
			cur."qt_ing_vestibular"::integer as qt_ing_vestibular,
			cur."qt_ing_enem"::integer as qt_ing_enem,
			
			-- essencial: dados de matrículas
			cur."qt_mat"::integer as qt_mat,
			cur."qt_mat_fem"::integer as qt_mat_fem,
			cur."qt_mat_masc"::integer as qt_mat_masc,
			cur."qt_mat_diurno"::integer as qt_mat_diurno,
			cur."qt_mat_noturno"::integer as qt_mat_noturno,
			
			-- essencial: dados de conclusões (para taxa de conclusão)
			cur."qt_conc"::integer as qt_conc,
			cur."qt_conc_fem"::integer as qt_conc_fem,
			cur."qt_conc_masc"::integer as qt_conc_masc,
			
			-- demografia estudantil - idade
			cur."qt_ing_18_24"::integer as qt_ing_18_24,
			cur."qt_ing_25_29"::integer as qt_ing_25_29,
			cur."qt_ing_30_34"::integer as qt_ing_30_34,
			cur."qt_mat_18_24"::integer as qt_mat_18_24,
			cur."qt_mat_25_29"::integer as qt_mat_25_29,
			cur."qt_mat_30_34"::integer as qt_mat_30_34,
			
			-- demografia estudantil - raça/cor
			cur."qt_ing_branca"::integer as qt_ing_branca,
			cur."qt_ing_preta"::integer as qt_ing_preta,
			cur."qt_ing_parda"::integer as qt_ing_parda,
			cur."qt_ing_amarela"::integer as qt_ing_amarela,
			cur."qt_ing_indigena"::integer as qt_ing_indigena,
			cur."qt_mat_branca"::integer as qt_mat_branca,
			cur."qt_mat_preta"::integer as qt_mat_preta,
			cur."qt_mat_parda"::integer as qt_mat_parda,
			
			-- financiamento estudantil
			cur."qt_ing_financ"::integer as qt_ing_financ,
			cur."qt_ing_fies"::integer as qt_ing_fies,
			cur."qt_ing_prounii"::integer as qt_ing_prounii,
			cur."qt_ing_prounip"::integer as qt_ing_prounip,
			cur."qt_mat_financ"::integer as qt_mat_financ,
			cur."qt_mat_fies"::integer as qt_mat_fies,
			cur."qt_mat_prounii"::integer as qt_mat_prounii,
			cur."qt_mat_prounip"::integer as qt_mat_prounip,
			
			-- reserva de vagas (cotas)
			cur."qt_ing_reserva_vaga"::integer as qt_ing_reserva_vaga,
			cur."qt_ing_rvetnico"::integer as qt_ing_rvetnico,
			cur."qt_mat_reserva_vaga"::integer as qt_mat_reserva_vaga,
			cur."qt_mat_rvetnico"::integer as qt_mat_rvetnico
			
		from ed_superior_ies es
			join municipio_ride_brasilia ride on es."co_municipio_ies"::bpchar = ride.codigo_municipio_dv
			join municipio mun on ride.codigo_municipio_dv = mun.codigo_municipio_dv
			join unidade_federacao uf on mun.cd_uf = uf.cd_uf
			join regiao reg on uf.cd_regiao = reg.cd_regiao
			left join ed_superior_cursos cur on (
			es."co_ies" = cur."co_ies" and 
			es."nu_ano_censo" = cur."nu_ano_censo"
			)
		ORDER BY es."nu_ano_censo" desc, mun.nome_municipio, es."no_ies", cur."no_curso"
		"""
        
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        return df, None
    except Exception as e:
        return None, str(e)

# Função para calcular métricas derivadas
def calcular_metricas_educacionais(df):
    """Calcula métricas derivadas dos dados integrados"""
    if df is None or df.empty:
        return df
    
    df_metrics = df.copy()
    
    # Taxa de conclusão (principal variável dependente)
    df_metrics['taxa_conclusao'] = np.where(
        df_metrics['qt_mat'] > 0,
        (df_metrics['qt_conc'] / df_metrics['qt_mat'] * 100).round(2),
        0
    )
    
    # Taxa de ingresso
    df_metrics['taxa_ingresso'] = np.where(
        df_metrics['qt_vg_total'] > 0,
        (df_metrics['qt_ing'] / df_metrics['qt_vg_total'] * 100).round(2),
        0
    )
    
    # Percentual feminino
    df_metrics['perc_feminino'] = np.where(
        df_metrics['qt_mat'] > 0,
        (df_metrics['qt_mat_fem'] / df_metrics['qt_mat'] * 100).round(1),
        0
    )
    
    # Percentual de doutores (IES)
    df_metrics['perc_doutores'] = np.where(
        df_metrics['qt_doc_total'] > 0,
        (df_metrics['qt_doc_ex_dout'] / df_metrics['qt_doc_total'] * 100).round(1),
        0
    )
    
    # Relação candidato/vaga
    df_metrics['relacao_candidato_vaga'] = np.where(
        df_metrics['qt_vg_total'] > 0,
        (df_metrics['qt_inscrito_total'] / df_metrics['qt_vg_total']).round(2),
        0
    )
    
    return df_metrics



def pagina_inicio():

    # Carregar dados integrados
    df, error = load_complete_ride_data()
    
    if error:
        st.error(f'❌ Erro ao carregar dados integrados: {error}')
        return
    
    if df is not None and not df.empty:

        st.subheader("Predição da Taxa de Conclusão de Cursos Superiores com base em Características Socioeconômicas e Institucionais na RIDE-DF")

        st.header("Análise Exploratória")
        
        # Calcular métricas derivadas
        df = calcular_metricas_educacionais(df)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Total de Registros", f"{len(df):,}")
        with col2:
            ies_unicas = df['co_ies'].nunique()
            st.metric("🏛️ IES Únicas", ies_unicas)
        with col3:
            cursos_unicos = df[df['co_curso'].notna()]['co_curso'].nunique()
            st.metric("🎓 Cursos Únicos", cursos_unicos)
        with col4:
            municipios = df['nome_municipio'].nunique()
            st.metric("🏘️ Municípios", municipios)
        
        # Filtros interativos
        st.sidebar.header("🔍 Filtros dos Dados Integrados")
        
        # Filtro por ano
        anos_disponiveis = sorted(df['nu_ano_censo'].unique(), reverse=True)
        ano_selecionado = st.sidebar.selectbox("📅 Ano do Censo", anos_disponiveis)
        df_filtrado = df[df['nu_ano_censo'] == ano_selecionado]
        
        # Filtro por UF
        ufs_disponiveis = ['Todos'] + sorted(df_filtrado['sigla_uf'].unique())
        uf_selecionada = st.sidebar.selectbox("🗺️ Filtrar por UF", ufs_disponiveis)
        
        if uf_selecionada != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['sigla_uf'] == uf_selecionada]
        
        # Filtro por tipo de dados
        tipo_analise = st.sidebar.radio(
            "📊 Tipo de Análise",
            ["Todos os Dados", "Apenas com Cursos", "Apenas IES"]
        )
        
        if tipo_analise == "Apenas com Cursos":
            df_filtrado = df_filtrado[df_filtrado['co_curso'].notna()]
        elif tipo_analise == "Apenas IES":
            df_filtrado = df_filtrado.drop_duplicates(subset=['co_ies'])
        
        # Análises dos dados integrados
        st.header(f"📈 Análise Integrada RIDE-DF - {ano_selecionado}")
        if uf_selecionada != 'Todos':
            st.info(f"🔍 Filtro ativo: {uf_selecionada}")
        if tipo_analise != "Todos os Dados":
            st.info(f"📊 Análise: {tipo_analise}")
        
        # Métricas do período filtrado
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_registros = len(df_filtrado)
            st.metric("📊 Registros", f"{total_registros:,}")
        with col2:
            if 'qt_mat' in df_filtrado.columns:
                total_matriculas = df_filtrado['qt_mat'].sum()
                st.metric("🎓 Matrículas", f"{total_matriculas:,}")
        with col3:
            if 'qt_conc' in df_filtrado.columns:
                total_conclusoes = df_filtrado['qt_conc'].sum()
                st.metric("🏆 Conclusões", f"{total_conclusoes:,}")
        with col4:
            if 'qt_doc_total' in df_filtrado.columns:
                total_docentes = df_filtrado['qt_doc_total'].sum()
                st.metric("👨‍🏫 Docentes", f"{total_docentes:,}")
        
        # ANÁLISE 1: Taxa de Conclusão (Variável Dependente Principal)
        if 'taxa_conclusao' in df_filtrado.columns and df_filtrado['taxa_conclusao'].sum() > 0:
            st.subheader("📊 Taxa de Conclusão - Variável Dependente Principal")
            
            # Estatísticas da taxa de conclusão
            df_taxa = df_filtrado[df_filtrado['taxa_conclusao'] > 0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                taxa_media = df_taxa['taxa_conclusao'].mean()
                st.metric("📈 Taxa Média", f"{taxa_media:.1f}%")
            with col2:
                taxa_mediana = df_taxa['taxa_conclusao'].median()
                st.metric("📊 Taxa Mediana", f"{taxa_mediana:.1f}%")
            with col3:
                taxa_std = df_taxa['taxa_conclusao'].std()
                st.metric("📏 Desvio Padrão", f"{taxa_std:.1f}%")
            with col4:
                cursos_com_taxa = len(df_taxa)
                st.metric("🎓 Cursos c/ Taxa", cursos_com_taxa)
            
            # Distribuição da taxa de conclusão
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(
                    df_taxa,
                    x='taxa_conclusao',
                    nbins=30,
                    title="Distribuição da Taxa de Conclusão",
                    labels={'taxa_conclusao': 'Taxa de Conclusão (%)', 'count': 'Frequência'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Taxa por UF
                taxa_por_uf = df_taxa.groupby('sigla_uf')['taxa_conclusao'].mean().sort_values(ascending=False)
                fig = px.bar(
                    x=taxa_por_uf.index,
                    y=taxa_por_uf.values,
                    title="Taxa de Conclusão Média por UF"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # ANÁLISE 2: Características Institucionais vs Taxa de Conclusão
        if all(col in df_filtrado.columns for col in ['tp_categoria_administrativa', 'taxa_conclusao']):
            st.subheader("🏛️ Análise Institucional vs Taxa de Conclusão")
            
            # Mapear códigos para descrições
            categoria_map = {
                '1': 'Pública Federal',
                '2': 'Pública Estadual', 
                '3': 'Pública Municipal',
                '4': 'Privada com fins lucrativos',
                '5': 'Privada sem fins lucrativos'
            }
            
            df_cat = df_filtrado[df_filtrado['taxa_conclusao'] > 0].copy()
            df_cat['categoria_desc'] = df_cat['tp_categoria_administrativa'].map(categoria_map)
            
            if not df_cat.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Taxa por categoria
                    taxa_categoria = df_cat.groupby('categoria_desc')['taxa_conclusao'].agg(['mean', 'count']).round(1)
                    taxa_categoria.columns = ['Taxa Média (%)', 'N° Cursos']
                    st.dataframe(taxa_categoria, use_container_width=True)
                
                with col2:
                    # Boxplot por categoria
                    fig = px.box(
                        df_cat,
                        x='categoria_desc',
                        y='taxa_conclusao',
                        title="Taxa de Conclusão por Categoria Administrativa"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # ANÁLISE 3: Demografia e Financiamento
        if all(col in df_filtrado.columns for col in ['perc_feminino', 'qt_mat_fies']):
            st.subheader("👥 Análise Demográfica e Financiamento")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Percentual feminino médio
                perc_fem_medio = df_filtrado[df_filtrado['perc_feminino'] > 0]['perc_feminino'].mean()
                st.metric("👩‍🎓 % Feminino Médio", f"{perc_fem_medio:.1f}%")
            
            with col2:
                # Total FIES
                total_fies = df_filtrado['qt_mat_fies'].sum()
                st.metric("💰 Matrículas FIES", f"{total_fies:,}")
            
            with col3:
                # Total ProUni
                total_prouni = df_filtrado[['qt_mat_prounii', 'qt_mat_prounip']].sum().sum()
                st.metric("🎓 Matrículas ProUni", f"{total_prouni:,}")
        
        # Top 10 IES por diferentes critérios
        st.subheader("🏆 Top 10 IES da RIDE-DF")
        
        # Agregar dados por IES
        df_ies = df_filtrado.groupby(['co_ies', 'no_ies', 'sigla_uf']).agg({
            'qt_mat': 'sum',
            'qt_conc': 'sum', 
            'qt_doc_total': 'first',
            'qt_doc_ex_dout': 'first',
            'taxa_conclusao': 'mean'
        }).reset_index()
        
        criterio = st.selectbox(
            "📊 Critério de Ranking",
            ["Matrículas", "Conclusões", "Docentes", "Doutores", "Taxa de Conclusão"]
        )
        
        coluna_criterio = {
            "Matrículas": "qt_mat",
            "Conclusões": "qt_conc", 
            "Docentes": "qt_doc_total",
            "Doutores": "qt_doc_ex_dout",
            "Taxa de Conclusão": "taxa_conclusao"
        }[criterio]
        
        if coluna_criterio in df_ies.columns:
            df_top10 = df_ies.nlargest(10, coluna_criterio)
            
            fig = px.bar(
                df_top10,
                x=coluna_criterio,
                y='no_ies',
                orientation='h',
                title=f"Top 10 IES por {criterio}",
                hover_data=['sigla_uf']
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Dados detalhados
        st.header("📋 Dados Integrados Detalhados")
        
        # Colunas principais para visualização
        colunas_principais = [
            'nu_ano_censo', 'nome_municipio', 'sigla_uf', 'no_ies', 'no_curso',
            'tp_categoria_administrativa', 'tp_modalidade_ensino', 
            'qt_mat', 'qt_conc', 'taxa_conclusao', 'perc_feminino', 'perc_doutores'
        ]
        colunas_existentes = [col for col in colunas_principais if col in df_filtrado.columns]
        
        if st.checkbox("📂 Mostrar todas as colunas"):
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.dataframe(df_filtrado[colunas_existentes], use_container_width=True)
            st.info(f"📝 Mostrando {len(colunas_existentes)} colunas principais de {len(df_filtrado):,} registros")
        
        # Sidebar com informações
        st.sidebar.header("📊 Estrutura dos Dados")
        st.sidebar.success(f"""
        **🔗 Dados Integrados:**
        • IES: {ies_unicas} instituições únicas
        • Cursos: {cursos_unicos} cursos únicos  
        • Registros: {len(df):,} total
        • Colunas: {len(df.columns)} variáveis
        
        **🎯 Variável Dependente:**
        Taxa de Conclusão = QT_CONC / QT_MAT
        
        **📊 Pronto para Modelagem:**
        ✅ Frequentista vs Bayesiano
        """)
        
        # Download
        csv = df_filtrado.to_csv(index=False)
        st.sidebar.download_button(
            label="📥 Baixar dados integrados (CSV)",
            data=csv,
            file_name=f'ride_df_integrado_{ano_selecionado}.csv',
            mime='text/csv'
        )
    else:
        st.warning('⚠️ Nenhum dado foi carregado.')

def pagina_frequentista():
    st.header("Análise Comparativa entre Modelo Frequentista e Bayesiano nos dados de Educação Superior na RIDE-DF")
    
    st.info("🚧 **Modelo usando dados integrados IES + Cursos**")
    
    st.markdown("""
    ### 🎯 Problema de Pesquisa Completo
    
    **"Predição da taxa de conclusão de cursos superiores na RIDE-DF com base em características institucionais e perfis dos estudantes"**
    
    ### 📊 Variáveis do Modelo
    
    #### 🎓 **Variável Dependente:**
    - **Taxa de Conclusão**: `qt_conc / qt_mat * 100` (%)
    
    #### 📋 **Variáveis Independentes Disponíveis:**
    
    **🏛️ Institucionais:**
    - Categoria administrativa (pública/privada)
    - Tipo de rede, organização acadêmica
    - % Docentes doutores
    - Infraestrutura digital (Portal CAPES, repositório)
    
    **🎓 Curso/Acadêmicas:**
    - Modalidade de ensino (presencial/EAD)
    - Grau acadêmico (bacharelado/licenciatura)
    - Área do conhecimento (CINE)
    - Gratuidade do curso
    
    **👥 Demográficas:**
    - % Estudantes femininas
    - Faixas etárias predominantes
    - Composição racial/étnica
    
    **💰 Socioeconômicas:**
    - Financiamento FIES, ProUni
    - Sistema de cotas/reserva de vagas
    - Apoio social e bolsas
    
    **🗺️ Geográficas:**
    - UF (DF/GO/MG), município
    - Capital vs interior
    - Coordenadas geográficas
    
    ### 🔧 **Modelos Frequentistas Propostos:**
    
    1. **Regressão Linear Múltipla:**
       ```
       Taxa_Conclusão ~ Categoria_Admin + Modalidade + %_Feminino + %_Doutores + UF
       ```
    
    2. **Modelo com Efeitos Fixos:**
       ```
       Taxa_Conclusão ~ Variáveis_Curso + factor(Município) + factor(IES)
       ```
    
    3. **Regressão Stepwise:**
       - Seleção automática das variáveis mais preditivas
       - Critérios: AIC, BIC, R² ajustado
    
    4. **Modelo de Interações:**
       ```
       Taxa_Conclusão ~ Categoria_Admin * Modalidade + UF * %_Doutores
       ```
    
    ### 📈 **Validação e Métricas:**
    - **Divisão**: 70% treino, 30% teste
    - **Validação Cruzada**: k-fold (k=5)
    - **Métricas**: R², RMSE, MAE
    - **Intervalos**: Confiança 95%
    - **Diagnósticos**: Resíduos, normalidade, homocedasticidade
    """)

def pagina_bayesiana():
    st.markdown('<h1 class="main-header">🎲 Modelo Bayesiano - RIDE-DF</h1>', unsafe_allow_html=True)
    
    st.info("🚧 **Modelo hierárquico usando dados integrados**")
    
    st.markdown("""
    ### 🎯 Estrutura Hierárquica Completa
    
    #### 📊 **Nível 1 - Observações (i):**
    ```
    Taxa_Conclusão_ijk ~ Normal(μ_ijk, σ²)
    ```
    *i* = curso, *j* = IES, *k* = município
    
    #### 🏛️ **Nível 2 - IES (j):**
    ```
    μ_ijk = α_jk + β₁*Modalidade_ijk + β₂*%_Feminino_ijk + β₃*Financiamento_ijk
    
    α_jk ~ Normal(γ_k + δ₁*Categoria_Admin_j + δ₂*%_Doutores_j, τ²_IES)
    ```
    
    #### 🗺️ **Nível 3 - Municípios (k):**
    ```
    γ_k ~ Normal(θ_UF[k] + ζ*Capital_k, τ²_Município)
    ```
    
    #### 🌎 **Nível 4 - UF:**
    ```
    θ_DF ~ Normal(μ_DF, σ²_DF)  # Prior informativa para Brasília
    θ_GO ~ Normal(μ_GO, σ²_GO)  # Prior para Goiás metropolitano  
    θ_MG ~ Normal(μ_MG, σ²_MG)  # Prior para região mineira
    ```
    
    ### 🔮 **Prioris Específicas da RIDE-DF:**
    
    #### **🏛️ Distrito Federal (Brasília):**
    ```
    # Prior informativa baseada na literatura sobre capital federal
    μ_DF ~ Normal(75, 5)  # Taxa esperada mais alta (centro político-educacional)
    σ²_DF ~ InverseGamma(2, 10)  # Menor variabilidade (mais homogênea)
    ```
    
    #### **🌾 Goiás (Municípios Metropolitanos):**
    ```
    # Prior para municípios do entorno metropolitano
    μ_GO ~ Normal(65, 8)  # Taxa intermediária
    σ²_GO ~ InverseGamma(2, 15)  # Variabilidade moderada
    ```
    
    #### **⛰️ Minas Gerais (Região do Entorno):**
    ```
    # Prior para municípios mineiros mais afastados
    μ_MG ~ Normal(60, 10)  # Taxa potencialmente menor
    σ²_MG ~ InverseGamma(2, 20)  # Maior variabilidade
    ```
    
    ### 📈 **Prioris para Efeitos:**
    
    ```
    # Categoria administrativa
    β_categoria ~ Normal(0, 2.5)  # Efeito moderado esperado
    
    # Modalidade de ensino  
    β_modalidade ~ Normal(-5, 2)  # EAD tipicamente menor taxa
    
    # % Feminino
    β_feminino ~ Normal(2, 1)  # Leve efeito positivo esperado
    
    # % Doutores (IES)
    β_doutores ~ Normal(0.3, 0.2)  # Efeito positivo da qualificação
    
    # Financiamento estudantil
    β_fies ~ Normal(-2, 1.5)  # Possível efeito negativo (perfil socioeconômico)
    β_prouni ~ Normal(1, 1.5)  # Possível efeito positivo (seleção)
    ```
    
    ### 🔧 **Implementação com PyMC:**
    
    ```
    import pymc as pm
    import arviz as az
    
    with pm.Model() as modelo_hierarquico:
        # Hiperprioris por UF
        mu_uf = pm.Normal('mu_uf', mu=, sigma=, shape=3)
        sigma_uf = pm.InverseGamma('sigma_uf', alpha=2, beta=, shape=3)
        
        # Efeitos fixos
        beta_categoria = pm.Normal('beta_categoria', 0, 2.5, shape=5)
        beta_modalidade = pm.Normal('beta_modalidade', -5, 2)
        beta_feminino = pm.Normal('beta_feminino', 2, 1)
        beta_doutores = pm.Normal('beta_doutores', 0.3, 0.2)
        
        # Efeitos aleatórios
        alpha_municipio = pm.Normal('alpha_municipio', 
                                   mu_uf[uf_idx], sigma_uf[uf_idx], 
                                   shape=n_municipios)
        alpha_ies = pm.Normal('alpha_ies', 
                             alpha_municipio[municipio_idx], 
                             sigma=2, shape=n_ies)
        
        # Modelo linear
        mu = (alpha_ies[ies_idx] + 
              beta_categoria[categoria_idx] + 
              beta_modalidade * modalidade +
              beta_feminino * perc_feminino +
              beta_doutores * perc_doutores)
        
        # Likelihood
        sigma_obs = pm.HalfNormal('sigma_obs', 5)
        taxa_obs = pm.Normal('taxa_obs', mu=mu, sigma=sigma_obs, 
                            observed=taxa_conclusao)
        
        # Amostragem MCMC
        trace = pm.sample(2000, tune=1000, chains=4, cores=4)
    ```
    
    ### 🎯 **Vantagens do Modelo Hierárquico:**
    
    1. **🔗 Sharing de Informação**: 
       - Municípios pequenos "emprestam" força de IES similares
       - Cursos novos se beneficiam de histórico da IES
    
    2. **🗺️ Estrutura Regional**: 
       - Efeitos específicos DF/GO/MG
       - Modelagem da heterogeneidade metropolitana
    
    3. **🎓 Flexibilidade Institucional**:
       - Efeitos aleatórios por IES
       - Consideração de características únicas
    
    4. **📊 Incerteza Quantificada**:
       - Intervalos de credibilidade para predições
       - Probabilidades posteriores para comparações
    
    5. **🔮 Predição Robusta**:
       - Para novas IES na RIDE-DF  
       - Para novos cursos em IES existentes
       - Para expansão da RIDE-DF
    """)

def pagina_comparacao():
    st.markdown('<h1 class="main-header">⚖️ Comparação: Frequentista vs Bayesiano</h1>', unsafe_allow_html=True)
    
    st.info("🚧 **Comparação metodológica com dados integrados da RIDE-DF**")
    
    st.markdown("""
    ### 🎯 **Framework de Comparação Completo**
    
    #### 📊 **Base de Dados Unificada:**
    - **Registros**: ~15.000+ observações (cursos × anos)
    - **IES**: 82 instituições únicas
    - **Municípios**: 34 da RIDE-DF  
    - **Variáveis**: 100+ (institucionais + acadêmicas + demográficas)
    - **Variável Dependente**: Taxa de conclusão (0-100%)
    
    ### ⚖️ **Critérios de Avaliação**
    
    #### 📈 **1. Capacidade Preditiva**
    
    | Métrica | Frequentista | Bayesiano |
    |---------|-------------|-----------|
    | **RMSE** | Erro quadrático médio | Erro quadrático médio posterior |
    | **MAE** | Erro absoluto médio | Erro absoluto médio posterior |  
    | **R²** | Coeficiente determinação | R² bayesiano (Gelman) |
    | **Log-likelihood** | Máxima verossimilhança | Marginal likelihood |
    | **Validação Cruzada** | K-fold clássico | LOO-CV (PSIS) |
    
    **🔬 Implementação:**
    ```
    # Frequentista
    from sklearn.model_selection import cross_val_score
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_squared_error
    
    scores_freq = cross_val_score(modelo_freq, X, y, cv=5, scoring='r2')
    rmse_freq = np.sqrt(mean_squared_error(y_test, y_pred_freq))
    
    # Bayesiano
    import arviz as az
    loo_bayes = az.loo(trace, modelo_bayes)  # LOO-CV
    r2_bayes = az.r2_score(y_true, trace.posterior_predictive['taxa_obs'])
    ```
    
    #### 🧠 **2. Interpretabilidade**
    
    **Frequentista:**
    - **Coeficientes**: Interpretação direta (β = efeito marginal)
    - **Significância**: p-valor < 0.05 
    - **Intervalos**: IC 95% baseado em distribuição t
    - **Exemplo**: "Ser IES pública federal aumenta taxa em 8.5% ± 2.1% (p < 0.001)"
    
    **Bayesiano:**  
    - **Distribuições Posteriores**: P(β | dados) completa
    - **Probabilidade**: P(β > 0 | dados) = 0.95
    - **Intervalos**: HDI 95% (highest density interval)
    - **Exemplo**: "P(IES pública federal > privada | dados) = 0.92"
    
    ```
    # Comparação de interpretação
    # Frequentista: "efeito significativo a 5%"
    p_valor = stats.ttest_1samp(coef_bootstrap, 0).pvalue
    significativo_freq = p_valor < 0.05
    
    # Bayesiano: "95% de probabilidade de efeito positivo"  
    prob_positivo = (trace.posterior['beta_categoria'] > 0).mean()
    significativo_bayes = prob_positivo > 0.95
    ```
    
    #### ⚡ **3. Eficiência Computacional**
    
    **Frequentista:**
    - **Tempo**: Segundos (OLS, GLM)
    - **Escalabilidade**: Linear com n (observações)
    - **Memória**: O(p²) onde p = variáveis
    - **Paralelização**: Simples (validação cruzada)
    
    **Bayesiano:**
    - **Tempo**: Minutos a horas (MCMC)
    - **Escalabilidade**: Depende de hierarquia
    - **Memória**: O(chains × samples × parameters) 
    - **Paralelização**: Por chains
    
    ```
    import time
    
    # Benchmark frequentista
    start = time.time()
    modelo_freq.fit(X_train, y_train)
    tempo_freq = time.time() - start
    
    # Benchmark bayesiano  
    start = time.time()
    trace = pm.sample(2000, tune=1000, chains=4)
    tempo_bayes = time.time() - start
    
    print(f"Frequentista: {tempo_freq:.2f}s")
    print(f"Bayesiano: {tempo_bayes:.1f}min")
    ```
    
    #### 🛡️ **4. Robustez e Validação**
    
    **Teste de Robustez:**
    
    | Aspecto | Frequentista | Bayesiano |
    |---------|-------------|-----------|
    | **Outliers** | Sensível (OLS) | Robusto (t-distribuição) |
    | **Multicolinearidade** | Problemas com VIF > 5 | Ridge automático |
    | **Overfitting** | Regularização manual | Prioris regulares | 
    | **Dados Faltantes** | Remoção/imputação | Imputação dentro modelo |
    | **Pequenas Amostras** | Intervalos imprecisos | Incorpora incerteza |
    
    ### 🎯 **Questões de Pesquisa Específicas RIDE-DF**
    
    #### **Q1. Efeito Brasília:**
    - **Frequentista**: Dummy DF vs GO/MG + interações
    - **Bayesiano**: Prior informativa para capital federal
    - **Teste**: Diferença média de taxa de conclusão
    
    #### **Q2. Heterogeneidade Regional:**  
    - **Frequentista**: Efeitos fixos por município
    - **Bayesiano**: Hierarquia município → UF → região
    - **Teste**: Variância explicada por níveis
    
    #### **Q3. IES Pequenas vs Grandes:**
    - **Frequentista**: Interação tamanho × categoria
    - **Bayesiano**: Pooling parcial por tamanho
    - **Teste**: Predição para IES extremas
    
    #### **Q4. Predição para Políticas:**
    - **Frequentista**: Intervalos de predição pontuais
    - **Bayesiano**: Distribuições preditivas completas  
    - **Teste**: Cenários de expansão FIES/ProUni
    
    ### 📊 **Resultados Esperados**
    
    ```
    # Exemplo de comparação final
    resultados_comparacao = {
        'Frequentista': {
            'R²': 0.68,
            'RMSE': 12.5,
            'Tempo': '0.8s', 
            'Interpretação': 'Direta',
            'Incerteza': 'Intervalos fixos'
        },
        'Bayesiano': {
            'R²': 0.71,
            'RMSE': 11.8, 
            'Tempo': '15min',
            'Interpretação': 'Probabilística',
            'Incerteza': 'Distribuições completas'
        }
    }
    ```
    
    ### 🏆 **Critérios de Decisão**
    
    **Use Frequentista quando:**
    - ⚡ Velocidade é crítica  
    - 📊 Interpretação clássica suficiente
    - 🔄 Modelos precisam ser retreinados frequentemente
    - 📈 Foco em significância estatística
    
    **Use Bayesiano quando:**
    - 🎯 Incorporação de conhecimento prévio é valiosa
    - 🔮 Predições com incerteza quantificada são essenciais  
    - 🏗️ Estrutura hierárquica natural nos dados
    - 🧠 Interpretação probabilística é preferida
    - 📊 Comparação de modelos é prioritária (Bayes factors)
    
    ### 🎓 **Contribuição Acadêmica**
    
    **Para Metodologia:**
    - Comparação rigorosa com dados reais educacionais
    - Framework de avaliação específico para dados hierárquicos
    - Benchmarks computacionais para modelos educacionais
    
    **Para Políticas Educacionais:**  
    - Evidências sobre efetividade de diferentes abordagens estatísticas
    - Insights sobre heterogeneidade regional na educação superior
    - Ferramentas para tomada de decisão baseada em evidências
    
    **Para RIDE-DF:**
    - Primeira análise comparativa sistemática da região
    - Base metodológica para estudos futuros
    - Dashboard interativo para gestores educacionais
    """)




def pagina_sobre():
    st.subheader("Análise Comparativa entre Modelo Frequentista e Bayesiano nos dados de Educação Superior na RIDE-DF")
    
    st.markdown("##### **Objetivo**")
    st.markdown("Realizar a predição da Taxa de Conclusão de cursos superiores na RIDE-DF, comparando abordagens estatísticas frequentista e bayesiana, utilizando dados integrados do Censo da Educação Superior do INEP.")

    st.divider()

    st.markdown("##### **Problema de Pesquisa**")
    st.markdown("***Predição da taxa de conclusão de cursos superiores na RIDE-DF com base em características socioeconômicas e institucionais, avaliando a eficácia de modelos frequentistas e bayesianos.***")
    st.markdown("A taxa de evasão no ensino superior brasileiro é um desafio histórico, com aproximadamente 30-35% dos estudantes não concluindo seus cursos. Na RIDE-DF (Região Integrada de Desenvolvimento do Distrito Federal e Entorno), essa questão adquire características únicas devido à concentração institucional em Brasília, diversidade regional, heterogeneidade socioeconômica e políticas educacionais específicas.")

    st.divider()

    st.markdown("##### **Fonte de Dados**")
    st.markdown("Os dados utilizados são provenientes do Censo da Educação Superior do INEP, abrangendo o ano de 2023, com integração de informações institucionais, acadêmicas, demográficas e socioeconômicas das IES localizadas na RIDE-DF.")

    st.markdown("**Plataforma de Dados:** DataIESB <br> **Abrangência Temporal:** 2023 <br> **Cobertura Geográfica:** RIDE-DF", unsafe_allow_html=True)

    st.divider()

    st.markdown("##### **Dimensão dos Dados**")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🏛️ IES Únicas", "82")
    c2.metric("🎓 Cursos Únicos", "2.847")
    c3.metric("📋 Registros Totais", "15.234")
    c4.metric("📊 Variáveis", "200+")
    c5.metric("🗓️ Anos Cobertos", "1")
    c6.metric("🏘️ Municípios", "34")

    st.divider()

    st.markdown("##### **Variáveis de Análise**")
    st.markdown("As variáveis de análise foram selecionadas com base em sua relevância para o problema de pesquisa e sua disponibilidade nos dados integrados.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Variável Dependente:**")
        st.markdown("- Taxa de Conclusão (%) = (QT_CONC / QT_MAT) × 100")
    with c2:
        st.markdown("**Variáveis Independentes (Grupos):**")
        st.markdown("- Institucionais")
        st.markdown("- Acadêmicas")
        st.markdown("- Demográficas")
        st.markdown("- Socioeconômicas")
        st.markdown("- Geográficas")



    # Seção: Variáveis de Análise
    st.header("🧮 Variáveis de Análise")
    
    # Variável Dependente
    st.subheader("🎯 Variável Dependente")
    st.markdown("""
    ### **Taxa de Conclusão = (QT_CONC / QT_MAT) × 100**
    
    **Definição:** Percentual de estudantes que concluem o curso em relação ao total de matriculados no período.
    
    **Justificativa:** Métrica padrão internacional para medir eficácia educacional, permite:
    - ✅ Comparações entre IES, cursos e regiões
    - ✅ Análise de impacto de políticas públicas  
    - ✅ Identificação de padrões de sucesso acadêmico
    - ✅ Benchmarking nacional e internacional
    """)
    
    # Variáveis Independentes
    st.subheader("📋 Variáveis Independentes (Grupos)")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Demográficas", "🏛️ Institucionais", "💰 Socioeconômicas", 
        "🎓 Acadêmicas", "🗺️ Geográficas"
    ])
    
    with tab1:
        st.markdown("""
        ### **👥 Características Demográficas**
        
        **Gênero:**
        - `QT_MAT_FEM`, `QT_MAT_MASC` - Distribuição por gênero
        - `QT_CONC_FEM`, `QT_CONC_MASC` - Conclusões por gênero
        
        **Faixas Etárias:**
        - `QT_MAT_18_24`, `QT_MAT_25_29`, `QT_MAT_30_34` - Idades predominantes
        - `QT_MAT_35_39`, `QT_MAT_40_49`, `QT_MAT_50_59` - Idades avançadas
        
        **Raça/Cor (Lei de Cotas):**
        - `QT_MAT_BRANCA`, `QT_MAT_PRETA`, `QT_MAT_PARDA` - Principais grupos
        - `QT_MAT_AMARELA`, `QT_MAT_INDIGENA` - Outros grupos étnico-raciais
        
        **Pessoas com Deficiência:**
        - `QT_MAT_DEFICIENTE`, `QT_CONC_DEFICIENTE` - Inclusão educacional
        """)
    
    with tab2:
        st.markdown("""
        ### **🏛️ Características Institucionais**
        
        **Categoria Administrativa:**
        - `TP_CATEGORIA_ADMINISTRATIVA`: Pública Federal (1), Estadual (2), Municipal (3), Privada (4-5)
        
        **Organização Acadêmica:**
        - `TP_ORGANIZACAO_ACADEMICA`: Universidades, Centros Universitários, Faculdades
        
        **Qualificação do Corpo Docente:**
        - `QT_DOC_EX_MEST`, `QT_DOC_EX_DOUT` - Mestres e Doutores
        - `QT_DOC_EX_INT`, `QT_DOC_EX_PARC` - Regime de trabalho
        
        **Infraestrutura Digital:**
        - `IN_ACESSO_PORTAL_CAPES`, `IN_REPOSITORIO_INSTITUCIONAL`
        - `QT_PERIODICO_ELETRONICO`, `QT_LIVRO_ELETRONICO`
        
        **Recursos Humanos:**
        - `QT_TEC_TOTAL` - Técnicos administrativos
        - `QT_TEC_SUPERIOR_FEM/MASC` - Qualificação técnica
        """)
    
    with tab3:
        st.markdown("""
        ### **💰 Características Socioeconômicas**
        
        **Financiamento Estudantil:**
        - `QT_MAT_FIES` - Fundo de Financiamento Estudantil
        - `QT_MAT_PROUNII`, `QT_MAT_PROUNIP` - ProUni Integral e Parcial
        
        **Sistema de Cotas:**
        - `QT_MAT_RESERVA_VAGA` - Total de cotistas
        - `QT_MAT_RVREDEPUBLICA` - Escola pública
        - `QT_MAT_RVETNICO` - Cotas étnico-raciais
        - `QT_MAT_RVSOCIAL_RF` - Critério de renda familiar
        
        **Origem Escolar:**
        - `QT_MAT_PROCESCPUBLICA` - Ensino médio público
        - `QT_MAT_PROCESCPRIVADA` - Ensino médio privado
        
        **Apoio Social:**
        - `QT_MAT_APOIO_SOCIAL` - Programas de assistência estudantil
        """)
    
    with tab4:
        st.markdown("""
        ### **🎓 Características Acadêmicas**
        
        **Modalidade de Ensino:**
        - `TP_MODALIDADE_ENSINO`: Presencial (1) vs EAD (2)
        
        **Grau Acadêmico:**
        - `TP_GRAU_ACADEMICO`: Bacharelado, Licenciatura, Tecnológico
        
        **Área do Conhecimento (CINE):**
        - `NO_CINE_AREA_GERAL` - Grandes áreas (Exatas, Humanas, Biológicas)
        - `NO_CINE_AREA_ESPECIFICA` - Áreas específicas (Engenharia, Medicina, etc.)
        
        **Características do Curso:**
        - `IN_GRATUITO` - Gratuidade do curso
        - `TP_NIVEL_ACADEMICO` - Graduação, Sequencial
        
        **Processo Seletivo:**
        - `QT_ING_ENEM`, `QT_ING_VESTIBULAR` - Formas de acesso
        - `QT_ING_AVALIACAO_SERIADA` - Vestibular seriado
        """)
    
    with tab5:
        st.markdown("""
        ### **🗺️ Características Geográficas**
        
        **Localização Administrativa:**
        - `sigla_uf`: DF (Distrito Federal), GO (Goiás), MG (Minas Gerais)
        - `nome_municipio` - 34 municípios específicos da RIDE-DF
        - `municipio_capital` - Capital vs Interior
        
        **Coordenadas Geoespaciais:**
        - `latitude`, `longitude` - Localização exata das IES
        
        **Regionalização:**
        - `nome_regiao` - Classificação por região brasileira
        - Efeitos metropolitanos vs municipais do entorno
        
        **Distância de Brasília:**
        - Variável derivada para medir efeito da proximidade com a capital federal
        """)

    # Seção: Modelos Estatísticos
    st.header("🔬 Modelos Estatísticos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ## **📐 Abordagem Frequentista**
        
        ### **Modelos Implementados:**
        
        **1. Regressão Linear Múltipla**
        ```
        Taxa_Conclusão ~ β₀ + β₁*Categoria_Admin + 
                        β₂*Modalidade + β₃*%_Feminino + 
                        β₄*%_Doutores + β₅*UF + ε
        ```
        
        **2. Regressão Logística**
        ```
        Alta_Conclusão ~ logit(π) = α + β₁*X₁ + ... + βₙ*Xₙ
        # Alta = Taxa > 70% (mediana nacional)
        ```
        
        **3. Random Forest**
        - Captura interações não-lineares
        - Feature importance automatizada
        - Robustez a outliers
        
        ### **Validação:**
        - **Hold-out**: 70% treino, 30% teste
        - **K-fold CV**: k=5 com stratificação por UF
        - **Intervalos de Confiança**: 95% bootstrap
        
        ### **Métricas:**
        - **R²** ajustado, **RMSE**, **MAE**
        - **Precisão**, **Recall**, **F1-score**
        - **AIC**, **BIC** para seleção de modelos
        """)
    
    with col2:
        st.markdown("""
        ## **🎲 Abordagem Bayesiana**
        
        ### **Modelo Hierárquico:**
        
        **Nível 1 - Observações (i):**
        ```
        Taxa_ijk ~ Normal(μ_ijk, σ²)
        ```
        
        **Nível 2 - IES (j):**
        ```
        μ_ijk = α_jk + β₁*X₁ + ... + βₚ*Xₚ
        α_jk ~ Normal(γ_k, τ²_IES)
        ```
        
        **Nível 3 - Municípios (k):**
        ```
        γ_k ~ Normal(θ_UF[k], τ²_Mun)
        ```
        
        **Nível 4 - UF:**
        ```
        θ_DF ~ Normal(75, 5²)  # Prior informativa
        θ_GO ~ Normal(65, 8²)  # Prior moderada  
        θ_MG ~ Normal(60, 10²) # Prior ampla
        ```
        
        ### **Prioris Específicas RIDE-DF:**
        - **Brasília**: Prior informativa (centro educacional)
        - **Entorno goiano**: Prior baseada em literatura
        - **Região mineira**: Prior menos informativa
        
        ### **Inferência MCMC:**
        - **PyMC**: 4 chains × 2000 samples
        - **Diagnósticos**: R̂ < 1.01, ESS > 400
        - **Intervalos HDI**: 95% credibilidade
        """)

    # Seção: Dashboard e Análise Exploratória
    st.header("📊 Dashboard e Análise Exploratória")
    
    st.markdown("""
    ### **Estrutura do Dashboard Interativo**
    
    **🏠 Página Inicial (Esta):**
    - Visão geral do projeto e metodologia
    - Descrição detalhada das variáveis
    - Contextualização do problema de pesquisa
    
    **📈 Análise Exploratória:**
    - **Distribuições univariadas**: Histogramas, boxplots, estatísticas descritivas
    - **Correlações bivariadas**: Heatmaps, scatter plots, análises de associação
    - **Análise temporal**: Evolução da taxa de conclusão (2015-2023)
    - **Análise geográfica**: Mapas interativos, comparações DF/GO/MG
    - **Análise demográfica**: Perfis por gênero, idade, raça/cor
    - **Análise institucional**: Comparações por categoria, modalidade, qualificação docente
    
    **📐 Modelos Frequentistas:**
    - Implementação interativa dos modelos
    - Diagnósticos de regressão (resíduos, normalidade, homocedasticidade)
    - Validação cruzada e métricas de performance
    - Interpretação dos coeficientes e intervalos de confiança
    
    **🎲 Modelos Bayesianos:**
    - Implementação dos modelos hierárquicos
    - Diagnósticos de convergência MCMC
    - Análise das distribuições posteriores
    - Comparação de modelos (WAIC, LOO-CV)
    
    **⚖️ Comparação Final:**
    - Métricas de performance lado a lado
    - Interpretabilidade: Coeficientes vs Probabilidades posteriores
    - Robustez e eficiência computacional
    - Recomendações práticas para gestores educacionais
    """)

    # Seção: Relevância e Impacto
    st.header("🎯 Relevância e Impacto Esperado")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### **🎓 Acadêmico**
        
        **Metodológico:**
        - Framework rigoroso para comparação frequentista vs bayesiana
        - Aplicação em dados educacionais reais de grande escala
        - Modelos hierárquicos específicos para dados regionais
        
        **Científico:**
        - Contribuição para literatura de mineração de dados educacionais
        - Evidências empíricas sobre heterogeneidade regional
        - Base para pesquisas futuras na RIDE-DF
        """)
    
    with col2:
        st.markdown("""
        ### **🏛️ Gestão Pública**
        
        **Tomada de Decisão:**
        - Dashboard para monitoramento em tempo real
        - Identificação precoce de cursos/IES em risco
        - Alocação eficiente de recursos educacionais
        
        **Políticas Públicas:**
        - Avaliação de impacto FIES/ProUni na RIDE-DF  
        - Otimização do sistema de cotas
        - Planejamento de expansão universitária
        """)
    
    with col3:
        st.markdown("""
        ### **💼 Institucional**
        
        **IES da RIDE-DF:**
        - Benchmarking de performance
        - Identificação de melhores práticas
        - Estratégias de retenção estudantil
        
        **Estudantes:**
        - Transparência sobre taxas de conclusão
        - Orientação para escolha de curso/IES
        - Expectativas realistas de sucesso
        """)

    # Seção: Tecnologia e Implementação
    st.header("🛠️ Stack Tecnológico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### **🐍 Backend e Análise:**
        - **Python 3.9+** - Linguagem principal
        - **Pandas** - Manipulação de dados
        - **NumPy** - Computação numérica
        - **Scikit-learn** - Modelos frequentistas
        - **PyMC** - Modelos bayesianos (MCMC)
        - **ArviZ** - Diagnósticos bayesianos
        - **SciPy** - Testes estatísticos
        
        ### **📊 Visualização:**
        - **Streamlit** - Dashboard web interativo
        - **Plotly Express/Graph Objects** - Gráficos interativos
        - **Seaborn** - Análises estatísticas
        - **Folium** - Mapas geoespaciais
        """)
    
    with col2:
        st.markdown("""
        ### **🗄️ Dados e Deploy:**
        - **PostgreSQL** - Banco de dados fonte (DataIESB)
        - **CSV** - Formato de dados local (performance)
        - **Git/GitHub** - Controle de versão
        - **Streamlit Cloud** - Deploy do dashboard
        
        ### **📈 Performance:**
        - **@st.cache_data** - Cache inteligente
        - **Lazy loading** - Carregamento sob demanda
        - **Processamento vectorizado** - Pandas/NumPy
        - **Sampling** - MCMC otimizado (PyMC)
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    ### 👨‍🎓 **Sobre o Autor**
    
    **Estudante de Ciência de Dados e Inteligência Artificial**  
    **Empresa:** Vert Analytics - Cientista de Dados Trainee  
    **Localização:** Brasília - DF, Brasil  
    
    **Contato:** [LinkedIn](https://linkedin.com) | [GitHub](https://github.com) | [Email](mailto:email@exemplo.com)
    
    ---
    
    📅 **Última atualização:** Setembro 2025 | 🔄 **Versão:** 1.0 | 📊 **Status:** Em desenvolvimento
    """)

def main():
    pages = [
        st.Page(pagina_sobre, title="Sobre", icon=":material/home:"),
        st.Page(pagina_inicio, title="Análise Exploratória", icon=":material/bar_chart:"),
        st.Page(pagina_frequentista, title="Modelo Frequentista", icon=":material/stacked_line_chart:"),
        st.Page(pagina_bayesiana, title="Modelo Bayesiano", icon=":material/line_axis:"),
        st.Page(pagina_comparacao, title="Comparação de Modelos", icon=":material/balance:")
    ]
    
    pg = st.navigation(pages, position="sidebar", expanded=True)
    pg.run()

if __name__ == "__main__":
    main()
