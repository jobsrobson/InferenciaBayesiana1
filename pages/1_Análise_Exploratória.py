import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from app import load_complete_ride_data, calcular_metricas_educacionais

# Carregar dados integrados
df, error = load_complete_ride_data()
if error:
    st.error(f'❌ Erro ao carregar dados integrados: {error}')
    st.stop()


if df is not None and not df.empty:

    # Sidebar
    st.sidebar.subheader("Filtros")

    # Filtro por UF
    ufs_disponiveis = sorted(df['sigla_uf'].unique())
    uf_selecionada = st.sidebar.multiselect("📍 Filtrar por UF", ufs_disponiveis)
    if uf_selecionada:
        df_filtrado = df[df['sigla_uf'].isin(uf_selecionada)]
    else:
        df_filtrado = df.copy()

    # Filtro por IES (opções dependem do filtro de UF)
    if uf_selecionada:
        ies_disponiveis = sorted(df[df['sigla_uf'].isin(uf_selecionada)]['no_ies'].unique())
    else:
        ies_disponiveis = sorted(df['no_ies'].unique())
    ies_selecionada = st.sidebar.multiselect("🏫 Filtrar por IES", ies_disponiveis)
    if ies_selecionada:
        df_filtrado = df_filtrado[df_filtrado['no_ies'].isin(ies_selecionada)]
    else:
        df_filtrado = df_filtrado.copy()

    # Filtro por Curso (opções dependem dos filtros de UF e IES)
    if ies_selecionada:
        cursos_disponiveis = sorted(df_filtrado['no_curso'].unique())
    elif uf_selecionada:
        cursos_disponiveis = sorted(df[df['sigla_uf'].isin(uf_selecionada)]['no_curso'].unique())
    else:
        cursos_disponiveis = sorted(df['no_curso'].unique())
    curso_selecionado = st.sidebar.multiselect("📚 Filtrar por Curso", cursos_disponiveis)

    if curso_selecionado:
        df_filtrado = df_filtrado[df_filtrado['no_curso'].isin(curso_selecionado)]
    else:
        df_filtrado = df_filtrado.copy()

    # Limpar Filtros
    # if st.sidebar.button("🧹 Limpar Filtros"):
    #    df = load_complete_ride_data()[0]  # Recarregar dados sem filtros



    # Cálculo de Métricas Gerais (aplicando filtros)
    df_metricas = df_filtrado if 'df_filtrado' in locals() else df

    ies_unicas = df_metricas['co_ies'].nunique()
    cursos_unicos = df_metricas['no_curso'].nunique()
    municipios_com_ies = df_metricas['nome_municipio'].nunique()
    total_matriculas = df_metricas['qt_mat'].sum()
    total_matriculas = f"{total_matriculas:,}".replace(",", ".")
    total_conclusoes = df_metricas['qt_conc'].sum()
    total_conclusoes = f"{total_conclusoes:,}".replace(",", ".")

    # Dados de Gênero
    total_feminino = df_metricas['qt_mat_fem'].sum()
    total_masculino = df_metricas['qt_mat_masc'].sum()




    # Página Principal
    st.subheader("Análise Exploratória dos Dados")
    st.markdown("<br>", unsafe_allow_html=True)


    # Métricas Iniciais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📋 Total de Matriculados", total_matriculas)
    with col2:
        st.metric("🎓 Total de Concluintes", total_conclusoes)
    with col3:
        st.metric("📚 Cursos Ofertados", cursos_unicos)
    with col4:
        st.metric("🏛️ IES Ativas", ies_unicas)

    st.markdown("<br>", unsafe_allow_html=True)


    # Abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧑 Estudantes", 
        "🧑‍🏫 Professores", 
        "🏫 Instituições",
        "📚 Cursos"
    ])

    with tab1:
        st.subheader("Sobre os Estudantes Matriculados")
        st.markdown("<br>", unsafe_allow_html=True)

        # Use os dados filtrados para aplicar os filtros selecionados
        df_estudantes = df_filtrado if 'df_filtrado' in locals() else df

        # Totais de gênero
        total_feminino = df_estudantes['qt_mat_fem'].sum()
        total_masculino = df_estudantes['qt_mat_masc'].sum()

        col1, col2 = st.columns(2)

        with col1:    
            st.markdown("**Distribuição por Gênero**")

            genero_data = pd.DataFrame({
                'Gênero': ['Feminino', 'Masculino'],
                'Quantidade': [total_feminino, total_masculino]
            })
            fig = px.pie(
                genero_data, 
                names='Gênero', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.amp
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Distribuição por Faixa Etária**")

            faixa_data = pd.DataFrame({
                'Faixa Etária': ['18-24 anos', '25-29 anos', '30-34 anos'],
                'Quantidade': [
                    df_estudantes['qt_mat_18_24'].sum(),
                    df_estudantes['qt_mat_25_29'].sum(),
                    df_estudantes['qt_mat_30_34'].sum(),
                ]
            })

            fig = px.pie(
                faixa_data, 
                names='Faixa Etária', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.amp
            )
            st.plotly_chart(fig, use_container_width=True)

        # Totais de matrículas por faixa (independente de sexo)
        faixa_data = {
            "Faixa Etária": ["18-24 anos", "25-29 anos", "30-34 anos"],
            "Total": [
                df_estudantes['qt_mat_18_24'].sum(),
                df_estudantes['qt_mat_25_29'].sum(),
                df_estudantes['qt_mat_30_34'].sum()
            ]
        }
        faixa_df = pd.DataFrame(faixa_data)

        # Distribuir por gênero (proporção)
        total_geral = faixa_df["Total"].sum()
        soma_genero = total_feminino + total_masculino
        prop_fem = total_feminino / soma_genero if soma_genero > 0 else 0
        prop_masc = total_masculino / soma_genero if soma_genero > 0 else 0

        faixa_df["Feminino"] = (faixa_df["Total"] * prop_fem).round().astype(int)
        faixa_df["Masculino"] = (faixa_df["Total"] * prop_masc).round().astype(int)

        # Transformar para formato longo
        faixa_long = faixa_df.melt(id_vars="Faixa Etária", value_vars=["Feminino", "Masculino"],
                                var_name="Gênero", value_name="Matriculados")

        # Gráfico
        fig = px.bar(
            faixa_long,
            x="Faixa Etária",
            y="Matriculados",
            color="Gênero",
            barmode="group",
            text="Matriculados",
            title="Distribuição de Matriculados por Faixa Etária e Gênero",
            color_discrete_sequence=px.colors.sequential.amp
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)


        st.divider()


        # Gráfico de Barras - 'qt_mat_branca', 'qt_mat_preta', 'qt_mat_parda'
        raca_data = pd.DataFrame({
            'Raça/Cor': ['Branca', 'Preta', 'Parda'],
            'Quantidade': [
                df_estudantes['qt_mat_branca'].sum(),
                df_estudantes['qt_mat_preta'].sum(),
                df_estudantes['qt_mat_parda'].sum(),
            ]
        })

        raca_data = raca_data.sort_values(by='Quantidade', ascending=False)

        fig = px.bar(
            raca_data, 
            x='Quantidade', 
            y='Raça/Cor',
            color='Raça/Cor',
            text='Quantidade',
            orientation='h',
            title="Distribuição de Matriculados por Raça/Cor",
            color_discrete_sequence=px.colors.sequential.amp
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False)  # Esconde a caixa de legenda de cores
        st.plotly_chart(fig, use_container_width=True)


        st.divider()


        # Gráficos sobre Financeiro
        col1, col2 = st.columns(2, gap="large")

        with col1:
            # Gráfico de Pizza com Matrículas via Bolsas
            # qt_mat_financ', 'qt_mat_fies', 'qt_mat_prounii', 'qt_mat_prounip'
            total_matriculados = df_estudantes['qt_mat'].sum()
            total_financiados = (
                df_estudantes['qt_mat_financ'].sum() +
                df_estudantes['qt_mat_fies'].sum() +
                df_estudantes['qt_mat_prounii'].sum() +
                df_estudantes['qt_mat_prounip'].sum()
            )
            nao_financiados = total_matriculados - total_financiados

            financ_data = pd.DataFrame({
                'Tipo de Financiamento': [
                    'Não Financiado',
                    'Financiado (Outros)',
                    'FIES',
                    'ProUni Integral',
                    'ProUni Parcial'
                ],
                'Quantidade': [
                    nao_financiados,
                    df_estudantes['qt_mat_financ'].sum(),
                    df_estudantes['qt_mat_fies'].sum(),
                    df_estudantes['qt_mat_prounii'].sum(),
                    df_estudantes['qt_mat_prounip'].sum(),
                ]
            })
                        
            st.markdown("**Distribuição de Matrículas por Tipo de Financiamento**")
            fig = px.pie(
                financ_data, 
                names='Tipo de Financiamento', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.amp
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Tabela com Cursos Únicos com mais Financiamentos (FIES, ProUni)
            financ_cursos = df_estudantes.groupby('no_curso')[['qt_mat_fies', 'qt_mat_prounii', 'qt_mat_prounip']].sum().reset_index()
            financ_cursos['Total Financiamentos'] = (
                financ_cursos['qt_mat_fies'] +
                financ_cursos['qt_mat_prounii'] +
                financ_cursos['qt_mat_prounip']
            )
            financ_cursos = financ_cursos.sort_values(by='Total Financiamentos', ascending=False).head(10)

            st.markdown("**Cursos com mais Matriculados via Financiamento (FIES, ProUni)**")
            financ_cursos_renomeado = financ_cursos.rename(columns={
                'no_curso': 'Curso',
                'qt_mat_fies': 'FIES',
                'qt_mat_prounii': 'ProUni Integral',
                'qt_mat_prounip': 'ProUni Parcial',
                'Total Financiamentos': 'Total Financiamentos'
            })
            st.dataframe(
                financ_cursos_renomeado[['Curso', 'FIES', 'ProUni Integral', 'ProUni Parcial', 'Total Financiamentos']],
                use_container_width=True,
                hide_index=True
            )


        st.divider()

        st.subheader("Sobre os Estudantes Ingressantes em 2023")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            # Quantidade de Ingressantes por Gênero 'qt_ing_fem', 'qt_ing_masc'
            ingressantes_fem = df_estudantes['qt_ing_fem'].sum()
            ingressantes_masc = df_estudantes['qt_ing_masc'].sum()
            ingressantes_data = pd.DataFrame({
                'Gênero': ['Feminino', 'Masculino'],
                'Quantidade': [ingressantes_fem, ingressantes_masc]
            })
            fig = px.pie(
                ingressantes_data, 
                names='Gênero', 
                values='Quantidade',
                title="Distribuição de Ingressantes por Gênero",
                color_discrete_sequence=px.colors.sequential.algae
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Quantidade de Ingressantes por Faixa Etária 'qt_ing_18_24', 'qt_ing_25_29', 'qt_ing_30_34'
            ingressantes_faixa = pd.DataFrame({
                'Faixa Etária': ['18-24 anos', '25-29 anos', '30-34 anos'],
                'Quantidade': [
                    df_estudantes['qt_ing_18_24'].sum(),
                    df_estudantes['qt_ing_25_29'].sum(),
                    df_estudantes['qt_ing_30_34'].sum()
                ]
            })
            fig = px.pie(
                ingressantes_faixa, 
                names='Faixa Etária', 
                values='Quantidade',
                title="Distribuição de Ingressantes por Faixa Etária",
                color_discrete_sequence=px.colors.sequential.algae
            )
            st.plotly_chart(fig, use_container_width=True)

        
        st.divider()

        col1, col2 = st.columns(2, gap="large")
        with col1:

            # Quantidade de Ingressantes por Raça/Cor 'qt_ing_branca', 'qt_ing_preta', 'qt_ing_parda'
            ingressantes_raca = pd.DataFrame({
                'Raça/Cor': ['Branca', 'Preta', 'Parda'],
                'Quantidade': [
                    df_estudantes['qt_ing_branca'].sum(),
                    df_estudantes['qt_ing_preta'].sum(),
                    df_estudantes['qt_ing_parda'].sum()
                ]
            })
            ingressantes_raca = ingressantes_raca.sort_values(by='Quantidade', ascending=False)
            fig = px.bar(
                ingressantes_raca, 
                x='Quantidade', 
                y='Raça/Cor',
                color='Raça/Cor',
                text='Quantidade',
                orientation='h',
                title="Distribuição de Ingressantes por Raça/Cor",
                color_discrete_sequence=px.colors.sequential.algae
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False)  # Esconde a caixa de legenda de cores
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Quantidade de Ingressantes por Tipo de Ingresso 'qt_ing_vestibular', 'qt_ing_enem'
            ingressantes_tipo = pd.DataFrame({
                'Tipo de Ingresso': ['Vestibular', 'ENEM'],
                'Quantidade': [
                    df_estudantes['qt_ing_vestibular'].sum(),
                    df_estudantes['qt_ing_enem'].sum()
                ]
            })
            fig = px.bar(
                ingressantes_tipo, 
                x='Quantidade',
                y='Tipo de Ingresso',
                color='Tipo de Ingresso',
                text='Quantidade',
                orientation='h',
                title="Distribuição de Ingressantes por Tipo de Ingresso",
                color_discrete_sequence=px.colors.sequential.algae
            )
            # hide legend
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False)  # Esconde a caixa de legenda de cores
            st.plotly_chart(fig, use_container_width=True)


        st.divider()

        col1, col2 = st.columns(2, gap="large")
        with col1:
            # Distribuição de Ingressantes por tipo de Financiamento 'qt_ing_financ', 'qt_ing_fies', 'qt_ing_prounii', 'qt_ing_prounip'
            total_ingressantes = df_estudantes['qt_ing'].sum()
            total_ingressantes_financiados = (
                df_estudantes['qt_ing_financ'].sum() +
                df_estudantes['qt_ing_fies'].sum() +
                df_estudantes['qt_ing_prounii'].sum() +
                df_estudantes['qt_ing_prounip'].sum()
            )
            nao_financiados_ing = total_ingressantes - total_ingressantes_financiados

            ingressantes_financ_data = pd.DataFrame({
                'Tipo de Financiamento': [
                    'Não Financiado',
                    'Financiado (Outros)',
                    'FIES',
                    'ProUni Integral',
                    'ProUni Parcial'
                ],
                'Quantidade': [
                    nao_financiados_ing,
                    df_estudantes['qt_ing_financ'].sum(),
                    df_estudantes['qt_ing_fies'].sum(),
                    df_estudantes['qt_ing_prounii'].sum(),
                    df_estudantes['qt_ing_prounip'].sum(),
                ]
            })
            st.markdown("**Distribuição de Ingressantes por Tipo de Financiamento**")
            fig = px.pie(
                ingressantes_financ_data, 
                names='Tipo de Financiamento', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.algae
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Tabela com Cursos Únicos com mais Ingressantes via Financiamentos (FIES, ProUni)
            financ_ing_cursos = df_estudantes.groupby('no_curso')[['qt_ing_fies', 'qt_ing_prounii', 'qt_ing_prounip']].sum().reset_index()
            financ_ing_cursos['Total Ingressantes Financiados'] = (
                financ_ing_cursos['qt_ing_fies'] +
                financ_ing_cursos['qt_ing_prounii'] +
                financ_ing_cursos['qt_ing_prounip']
            )
            financ_ing_cursos = financ_ing_cursos.sort_values(by='Total Ingressantes Financiados', ascending=False).head(10)

            st.markdown("**Cursos com mais Ingressantes via Financiamento (FIES, ProUni)**")
            financ_ing_cursos_renomeado = financ_ing_cursos.rename(columns={
                'no_curso': 'Curso',
                'qt_ing_fies': 'FIES',
                'qt_ing_prounii': 'ProUni Integral',
                'qt_ing_prounip': 'ProUni Parcial',
                'Total Ingressantes Financiados': 'Total Ingressantes Financiados'
            })
            st.dataframe(
                financ_ing_cursos_renomeado[['Curso', 'FIES', 'ProUni Integral', 'ProUni Parcial', 'Total Ingressantes Financiados']],
                use_container_width=True,
                hide_index=True
            )



    # PROFESSORES
    with tab2:

        st.subheader("Sobre os Professores")

        # Se tiver o filtro de curso, mostrar aviso que os dados de professores são por IES
        if curso_selecionado:
            st.warning("ℹ️ Os dados sobre professores são agregados por Instituição de Ensino Superior (IES) e não por curso.\n Os filtros aplicados por curso foram ignorados.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Use os dados filtrados para aplicar os filtros selecionados
        df_professores = df_filtrado if 'df_filtrado' in locals() else df

        # Garantir que cada IES seja considerada apenas uma vez
        df_professores_unicos = df_professores.drop_duplicates(subset=['co_ies'])

        # Agora os totais corretos
        total_docentes = df_professores_unicos['qt_doc_exe'].sum()
        total_doutores = df_professores_unicos['qt_doc_ex_dout'].sum()
        total_mestres = df_professores_unicos['qt_doc_ex_mest'].sum()
        total_especialistas = df_professores_unicos['qt_doc_ex_esp'].sum()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("👨‍🏫 Total de Docentes", f"{total_docentes:,}".replace(",", "."))
        with col2:
            st.metric("🎓 Total de Doutores", f"{total_doutores:,}".replace(",", "."))
        with col3:
            st.metric("🎓 Total de Mestres", f"{total_mestres:,}".replace(",", "."))
        with col4:
            st.metric("🎓 Total de Especialistas", f"{total_especialistas:,}".replace(",", "."))

        st.markdown("<br>", unsafe_allow_html=True)


        col1, col2 = st.columns(2, gap="large")
        with col1:
            # Percentual de Doutores
            perc_doutores = (total_doutores / total_docentes * 100) if total_docentes > 0 else 0
            perc_mestres = (total_mestres / total_docentes * 100) if total_docentes > 0 else 0
            perc_especialistas = (total_especialistas / total_docentes * 100) if total_docentes > 0 else 0

            perc_data = pd.DataFrame({
                'Nível de Formação': ['Doutores', 'Mestres', 'Especialistas'],
                'Percentual': [perc_doutores, perc_mestres, perc_especialistas]
            })

            fig = px.pie(
                perc_data, 
                names='Nível de Formação', 
                values='Percentual',
                title="Distribuição Percentual dos Níveis de Formação dos Docentes",
                color_discrete_sequence=px.colors.sequential.Burg
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Distribuição de Docentes por Sexo
            total_docentes_fem = df_professores_unicos['qt_doc_ex_femi'].sum()
            total_docentes_masc = df_professores_unicos['qt_doc_ex_masc'].sum()

            genero_data = pd.DataFrame({
                'Gênero': ['Feminino', 'Masculino'],
                'Quantidade': [total_docentes_fem, total_docentes_masc]
            })

            # Gráfico de Pizza
            fig = px.pie(
                genero_data, 
                names='Gênero', 
                values='Quantidade',
                title="Distribuição de Docentes por Gênero",
                color_discrete_sequence=px.colors.sequential.Burg
            )
            st.plotly_chart(fig, use_container_width=True)


    with tab3:
        st.subheader("Sobre as Instituições de Ensino Superior (IES)")
        st.markdown("<br>", unsafe_allow_html=True)

        # Use os dados filtrados para aplicar os filtros selecionados
        df_instituicoes = df_filtrado if 'df_filtrado' in locals() else df

        # Garantir que cada IES seja considerada apenas uma vez
        df_instituicoes_unicos = df_instituicoes.drop_duplicates(subset=['co_ies'])

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("**Distribuição de IES por Categoria Administrativa**")
            # Totais por Categoria Administrativa
            categoria_counts = df_instituicoes_unicos['tp_categoria_administrativa'].value_counts().rename(index={
                '1': 'Pública Federal',
                '2': 'Pública Estadual',
                '3': 'Pública Municipal',
                '4': 'Privada com fins lucrativos',
                '5': 'Privada sem fins lucrativos'
            })

            categoria_data = pd.DataFrame({
                'Categoria Administrativa': categoria_counts.index,
                'Quantidade': categoria_counts.values
            })

            fig = px.pie(
                categoria_data, 
                names='Categoria Administrativa', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.Mint
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Distribuição de IES por Tipo de Organização Acadêmica**")
            # Totais por Tipo de Organização Acadêmica
            org_counts = df_instituicoes_unicos['tp_organizacao_academica'].value_counts().rename(index={
                '1': 'Universidade',
                '2': 'Centro Universitário',
                '3': 'Faculdade',
                '4': 'Instituto Superior',
                '5': 'Centro de Ensino Superior',
                '6': 'Escola Superior'  
            })
            org_data = pd.DataFrame({
                'Tipo de Organização Acadêmica': org_counts.index,
                'Quantidade': org_counts.values
            })
            fig = px.pie(
                org_data, 
                names='Tipo de Organização Acadêmica', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.Mint
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()


        # Top 10 IES por diferentes critérios
        st.markdown(f"**Ranking das IES na RIDE-DF**")

        criterio = st.selectbox(
            "📊 Critério de Ranking",
            ["Matrículas", "Conclusões", "Docentes", "Doutores"]
        )

        # Agregar dados por IES
        df_ies = df_filtrado.groupby(['co_ies', 'no_ies', 'sigla_uf']).agg({
            'qt_mat': 'sum',
            'qt_conc': 'sum', 
            'qt_doc_total': 'first',
            'qt_doc_ex_dout': 'first'
        }).reset_index()
        
        coluna_criterio = {
            "Matrículas": "qt_mat",
            "Conclusões": "qt_conc", 
            "Docentes": "qt_doc_total",
            "Doutores": "qt_doc_ex_dout"
        }[criterio]
        
        if coluna_criterio in df_ies.columns:
            df_top10 = df_ies.nlargest(10, coluna_criterio)
            
            fig = px.bar(
                df_top10,
                x=coluna_criterio,
                y='no_ies',
                orientation='h',
                hover_data=['sigla_uf'],
                color_discrete_sequence=px.colors.sequential.Mint_r,
                labels={
                    coluna_criterio: criterio,
                    'no_ies': 'Nome da IES'
                }
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)


        # Tabela com todas as IES
        with st.expander("Tabela de Instituições de Ensino Superior (IES)"):
        
            ies_tabela = df_instituicoes_unicos.rename(columns={
                'no_ies': 'Nome da IES',
                'sg_ies': 'Sigla',
                'sigla_uf': 'UF',
                'tp_categoria_administrativa': 'Categoria Administrativa',
                'tp_organizacao_academica': 'Tipo de Organização Acadêmica',
                'qt_doc_total': 'Total de Docentes'
            })
            ies_tabela['Categoria Administrativa'] = ies_tabela['Categoria Administrativa'].replace({
                '1': 'Pública Federal',
                '2': 'Pública Estadual',
                '3': 'Pública Municipal',
                '4': 'Privada com fins lucrativos',
                '5': 'Privada sem fins lucrativos'
            })

            ies_tabela['Tipo de Organização Acadêmica'] = ies_tabela['Tipo de Organização Acadêmica'].replace({
                '1': 'Universidade',
                '2': 'Centro Universitário',
                '3': 'Faculdade',
                '4': 'Instituto Superior',
                '5': 'Centro de Ensino Superior',
                '6': 'Escola Superior'  
            })
            st.dataframe(
                ies_tabela[['Nome da IES', 'Sigla', 'UF', 'Categoria Administrativa', 'Tipo de Organização Acadêmica', 'Total de Docentes']].sort_values(by='Nome da IES'),
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # Razão entre Matriculados e Docentes por IES
        st.markdown("**Relação entre Matriculados e Docentes por IES (Média de Alunos por Professor)**")
        df_instituicoes_unicos['Relação Matriculados/Docentes'] = df_instituicoes_unicos.apply(
            lambda row: row['qt_mat'] / row['qt_doc_total'] if row['qt_doc_total'] > 0 else np.nan,
            axis=1
        )
        relacao_data = df_instituicoes_unicos[['no_ies', 'qt_mat', 'qt_doc_total', 'Relação Matriculados/Docentes']].dropna()
        relacao_data = relacao_data.sort_values(by='Relação Matriculados/Docentes', ascending=False)
        relacao_data = relacao_data.rename(columns={
            'no_ies': 'Nome da IES',
            'qt_mat': 'Total de Matriculados',
            'qt_doc_total': 'Total de Docentes',
            'Relação Matriculados/Docentes': 'Média de Alunos por Professor'
        })
        st.dataframe(
            relacao_data[['Nome da IES', 'Total de Matriculados', 'Total de Docentes', 'Média de Alunos por Professor']],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        col1, col2 = st.columns(2, gap="large")
        with col1:
            # Conexão a Internet
            st.markdown("**Conexão à Internet nas IES**")
            conexao_counts = df_instituicoes_unicos['in_servico_internet'].value_counts().rename(index={
                1: 'Sim',
                2: 'Não'
            })
            conexao_data = pd.DataFrame({
                'Conexão à Internet': conexao_counts.index,
                'Quantidade': conexao_counts.values
            })

            fig = px.pie(
                conexao_data, 
                names='Conexão à Internet', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.Mint
            )
            st.plotly_chart(fig, use_container_width=True)      

        with col2:
            # Acesso a Biblioteca
            st.markdown("**Acesso à Biblioteca nas IES**")
            biblioteca_counts = df_instituicoes_unicos['in_repositorio_institucional'].value_counts().rename(index={
                1: 'Sim',
                2: 'Não'
            })
            biblioteca_data = pd.DataFrame({
                'Acesso à Biblioteca': biblioteca_counts.index,
                'Quantidade': biblioteca_counts.values
            })

            fig = px.pie(
                biblioteca_data, 
                names='Acesso à Biblioteca', 
                values='Quantidade',
                color_discrete_sequence=px.colors.sequential.Mint
            )
            st.plotly_chart(fig, use_container_width=True)                           




    with tab4:

        st.subheader("Sobre os Cursos Ofertados")
        st.markdown("<br>", unsafe_allow_html=True)

        # Use os dados filtrados para aplicar os filtros selecionados
        df_cursos = df_filtrado if 'df_filtrado' in locals() else df
        # Garantir que cada Curso seja considerado apenas uma vez por IES e Ano
        df_cursos_unicos = df_cursos.drop_duplicates(subset=['co_ies', 'co_curso', 'nu_ano_censo'])
        total_cursos = df_cursos_unicos['no_curso'].nunique()


        # Gráfico de Pizza com o total de vagas por modalidade de ensino tp_modalidade_ensino
        modalidade_counts = df_cursos_unicos['tp_modalidade_ensino'].value_counts().rename(index={
            1: 'Presencial',
            2: 'EAD'
        })
        modalidade_data = pd.DataFrame({
            'Modalidade de Ensino': modalidade_counts.index,
            'Quantidade': modalidade_counts.values
        })
        fig = px.pie(
            modalidade_data, 
            names='Modalidade de Ensino', 
            values='Quantidade',
            title="Distribuição de Cursos por Modalidade de Ensino",
            color_discrete_sequence=px.colors.sequential.Blugrn
        )
        st.plotly_chart(fig, use_container_width=True)


        st.divider()


        df_ing_conc = (
            df_metricas
            .groupby(['no_ies'], as_index=False)
            .agg(
                ingressantes=('qt_ing','sum'),
                concluintes=('qt_conc','sum')
            )
            .sort_values('ingressantes', ascending=False)
        )

        # Taxa de Ingresso por 
        # Agregar por IES + Curso + Ano (soma de vagas e ingressantes)
        df_cursos = (
            df_metricas
            .groupby(['co_ies','no_ies','no_curso','nu_ano_censo'], as_index=False)
            .agg(
                qt_vg_total=('qt_vg_total','sum'),
                qt_ing=('qt_ing','sum')
            )
        )

        # Calcular taxa de ingresso após agregar
        df_cursos['taxa_ingresso'] = np.where(
            df_cursos['qt_vg_total'] > 0,
            (df_cursos['qt_ing'] / df_cursos['qt_vg_total'] * 100).round(2),
            np.nan
        )

        # Ordenar por Nome da IES, Nome do Curso e Taxa de Ingresso
        df_cursos = df_cursos.sort_values(
            by=['no_ies', 'taxa_ingresso'],
            ascending=[True, False]   # ordena taxa de forma decrescente
        )

        # Mostrar tabela
        st.markdown(f"**Tabela de Cursos Ofertados - Taxa de Ingresso**")
        st.markdown("A tabela abaixo apresenta os cursos ofertados pelas IES, juntamente com o total de vagas, ingressantes e a taxa de ingresso (%) no ano de 2023, que representa a proporção de ingressantes em relação ao total de vagas oferecidas.")
        df_cursos_renomeado = df_cursos.rename(columns={
            'no_ies': 'Nome da IES',
            'no_curso': 'Nome do Curso',
            'qt_vg_total': 'Total de Vagas',
            'qt_ing': 'Total de Ingressantes',
            'taxa_ingresso': 'Taxa de Ingresso (%)'
        })
        st.dataframe(
            df_cursos_renomeado[['Nome da IES', 'Nome do Curso', 'Total de Vagas', 'Total de Ingressantes', 'Taxa de Ingresso (%)']],
            use_container_width=True
        )

else:
    st.warning("⚠️ Nenhum dado disponível para exibição. Verifique status do DataIESB.")