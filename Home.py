import streamlit as st
from modules.db_connection import create_pg_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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



st.markdown("### Análise Comparativa entre Modelo Frequentista e Bayesiano<br>nos dados de Educação Superior na RIDE-DF", unsafe_allow_html=True)

st.markdown("<br>**Autor:** Robson Ricardo Leite da Silva <br> **Matrícula:** 22112120015 <br> **Curso:** Ciência de Dados e Inteligência Artificial<br> **Disciplina:** Inferência Bayesiana (2°/2025) <br> **Instituição:** IESB - Instituto de Educação Superior de Brasília", unsafe_allow_html=True)

st.divider()

st.markdown("##### **Objetivo**")
st.markdown("Analisar os fatores institucionais e socioeconômicos associados ao número de matrículas (QT_MAT) nos cursos de graduação da RIDE-DF em 2023, considerando características dos cursos, perfis dos discentes e atributos das instituições de ensino.")

st.divider()

st.markdown("##### **Problema de Pesquisa**")
st.markdown(
	"<span style='color:#1565c0; font-weight:bold;'>***Quais fatores institucionais e socioeconômicos estão associados ao número de matrículas em cursos de graduação na RIDE-DF em 2023?***</span>",
	unsafe_allow_html=True
)
st.markdown("O Censo da Educação Superior fornece uma fotografia transversal das matrículas em 2023, impossibilitando análises de trajetória longitudinal ou projeções futuras. Nesse contexto, torna-se relevante investigar quais elementos institucionais, acadêmicos e sociodemográficos explicam a variação no volume de matrículas entre cursos e instituições na RIDE-DF, permitindo compreender padrões de acesso e atratividade do ensino superior na região.",
	unsafe_allow_html=True
)

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
    st.markdown("- QT_MAT (Número de Matrículas)")
with c2:
	st.markdown("""
**Variáveis Independentes (Grupos):**
- Institucionais
- Acadêmicas
- Demográficas
- Socioeconômicas
- Geográficas
""")
    