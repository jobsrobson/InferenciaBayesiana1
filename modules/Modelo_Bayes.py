from modules.db_connection import create_pg_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# FUNÇÃO PRINCIPAL - DADOS INTEGRADOS COM JOIN INLINE
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

df, error = load_complete_ride_data()


# MODELO BAYESIANO

import pymc as pm
import arviz as az


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



# Função do Modelo Bayesiano 
def ajustar_modelo_bayesiano(df_model):
    y = df_model["qt_ing"].values
    offset = df_model["offset_log_qtmat"].values
    # Criar dummies das variáveis categóricas
    X = pd.get_dummies(
        df_model[[
            "tp_rede",
            "tp_organizacao_academica",
            "tp_grau_academico",
            "tp_modalidade_ensino"
        ]],
        drop_first=True
    )
    # Variáveis contínuas
    X["qt_conc"] = df_model["qt_conc"]
    X["prop_doc_avancado"] = df_model["prop_doc_avancado"]
    X["prop_ing_pp"] = df_model["prop_ing_pp"]
    X["prop_ing_financiados"] = df_model["prop_ing_financiados"]
    # Guardar nomes das variáveis
    colnames = X.columns.tolist()
    X = X.fillna(0).astype(float).values
    n, k = X.shape
    
    with pm.Model() as model:
        # Priors
        beta = pm.Normal("beta", mu=0, sigma=2, shape=k)
        intercept = pm.Normal("intercept", mu=0, sigma=5)
        alpha = pm.Exponential("alpha", 1)
        # Previsão linear + offset
        mu = pm.math.exp(intercept + pm.math.dot(X, beta) + offset)
        # Verossimilhança
        y_obs = pm.NegativeBinomial("y_obs", mu=mu, alpha=alpha, observed=y)
        # Amostragem
        trace = pm.sample(2000, tune=1000, chains=4, target_accept=0.95, random_seed=42)

    return model, trace, colnames

def tabela_resultados(trace, colnames, hdi_prob=0.94):
    summary = az.summary(trace, hdi_prob=hdi_prob)
    # Extrair apenas os betas
    betas = summary.loc[[f"beta[{i}]" for i in range(len(colnames))]].copy()
    betas["variável"] = colnames
    betas = betas.set_index("variável")
    # Adicionar intercepto e alpha
    intercept = summary.loc["intercept"].to_frame().T
    intercept.index = ["Intercepto"]
    alpha = summary.loc["alpha"].to_frame().T
    alpha.index = ["Alpha (dispersão)"]
    resultados = pd.concat([betas, intercept, alpha], axis=0)
    return resultados




df_model = preparar_dados(df)
model, trace, colnames = ajustar_modelo_bayesiano(df_model)
az.to_netcdf(trace, "modelo_bayesiano_trace.nc")
resultados = tabela_resultados(trace, colnames)
resultados.to_csv("resultados_bayes.csv")