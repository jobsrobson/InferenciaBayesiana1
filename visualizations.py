"""
Módulo para visualizações interativas
Autor: Robson Jobs
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
import seaborn as sns
import matplotlib.pyplot as plt

# Imports condicionais para visualizações bayesianas
try:
    import arviz as az
    ARVIZ_AVAILABLE = True
except ImportError:
    ARVIZ_AVAILABLE = False

class Visualizations:
    """Classe para criação de visualizações interativas"""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        self.theme = "plotly_white"
    
    def create_scatter_plot(self, 
                          data: pd.DataFrame,
                          x_col: str,
                          y_col: str,
                          color_col: Optional[str] = None,
                          size_col: Optional[str] = None,
                          title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico de dispersão interativo
        
        Args:
            data: DataFrame com os dados
            x_col: Coluna para eixo X
            y_col: Coluna para eixo Y
            color_col: Coluna para cores (opcional)
            size_col: Coluna para tamanhos (opcional)
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            title=title or f"{y_col} vs {x_col}",
            template=self.theme,
            hover_data=[col for col in data.columns if col not in [x_col, y_col]]
        )
        
        fig.update_layout(
            hovermode='closest',
            showlegend=True if color_col else False
        )
        
        return fig
    
    def create_histogram(self,
                        data: pd.DataFrame,
                        col: str,
                        bins: int = 30,
                        color_col: Optional[str] = None,
                        title: Optional[str] = None) -> go.Figure:
        """
        Cria histograma interativo
        
        Args:
            data: DataFrame com os dados
            col: Coluna para o histograma
            bins: Número de bins
            color_col: Coluna para separar por cores
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        fig = px.histogram(
            data,
            x=col,
            color=color_col,
            nbins=bins,
            title=title or f"Distribuição de {col}",
            template=self.theme,
            marginal="box"
        )
        
        fig.update_layout(
            bargap=0.1,
            showlegend=True if color_col else False
        )
        
        return fig
    
    def create_box_plot(self,
                       data: pd.DataFrame,
                       y_col: str,
                       x_col: Optional[str] = None,
                       title: Optional[str] = None) -> go.Figure:
        """
        Cria box plot interativo
        
        Args:
            data: DataFrame com os dados
            y_col: Coluna para valores
            x_col: Coluna para categorias (opcional)
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        fig = px.box(
            data,
            x=x_col,
            y=y_col,
            title=title or f"Box Plot de {y_col}",
            template=self.theme
        )
        
        fig.update_traces(
            boxpoints="outliers",
            jitter=0.3,
            pointpos=-1.8
        )
        
        return fig
    
    def create_correlation_heatmap(self,
                                  data: pd.DataFrame,
                                  columns: Optional[List[str]] = None,
                                  title: Optional[str] = None) -> go.Figure:
        """
        Cria mapa de calor de correlações
        
        Args:
            data: DataFrame com os dados
            columns: Colunas para calcular correlação
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        if columns is None:
            numeric_data = data.select_dtypes(include=[np.number])
        else:
            numeric_data = data[columns]
        
        corr_matrix = numeric_data.corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title=title or "Matriz de Correlação",
            template=self.theme,
            color_continuous_scale="RdBu_r"
        )
        
        fig.update_layout(
            width=600,
            height=600
        )
        
        return fig
    
    def create_time_series(self,
                          data: pd.DataFrame,
                          date_col: str,
                          value_col: str,
                          group_col: Optional[str] = None,
                          title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico de série temporal
        
        Args:
            data: DataFrame com os dados
            date_col: Coluna de datas
            value_col: Coluna de valores
            group_col: Coluna para agrupar séries
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        fig = px.line(
            data,
            x=date_col,
            y=value_col,
            color=group_col,
            title=title or f"Série Temporal de {value_col}",
            template=self.theme
        )
        
        fig.update_layout(
            hovermode='x unified',
            showlegend=True if group_col else False
        )
        
        return fig
    
    def create_bar_chart(self,
                        data: pd.DataFrame,
                        x_col: str,
                        y_col: str,
                        color_col: Optional[str] = None,
                        orientation: str = 'v',
                        title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico de barras
        
        Args:
            data: DataFrame com os dados
            x_col: Coluna para eixo X
            y_col: Coluna para eixo Y
            color_col: Coluna para cores
            orientation: Orientação ('v' ou 'h')
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            orientation=orientation,
            title=title or f"{y_col} por {x_col}",
            template=self.theme
        )
        
        fig.update_layout(
            showlegend=True if color_col else False
        )
        
        return fig
    
    def create_3d_scatter(self,
                         data: pd.DataFrame,
                         x_col: str,
                         y_col: str,
                         z_col: str,
                         color_col: Optional[str] = None,
                         title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico 3D de dispersão
        
        Args:
            data: DataFrame com os dados
            x_col: Coluna para eixo X
            y_col: Coluna para eixo Y
            z_col: Coluna para eixo Z
            color_col: Coluna para cores
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        fig = px.scatter_3d(
            data,
            x=x_col,
            y=y_col,
            z=z_col,
            color=color_col,
            title=title or f"Gráfico 3D: {x_col}, {y_col}, {z_col}",
            template=self.theme
        )
        
        return fig
    
    def create_distribution_comparison(self,
                                     data: pd.DataFrame,
                                     col: str,
                                     group_col: str,
                                     title: Optional[str] = None) -> go.Figure:
        """
        Compara distribuições entre grupos
        
        Args:
            data: DataFrame com os dados
            col: Coluna de valores
            group_col: Coluna de grupos
            title: Título do gráfico
            
        Returns:
            Figura plotly
        """
        fig = go.Figure()
        
        groups = data[group_col].unique()
        
        for group in groups:
            group_data = data[data[group_col] == group][col]
            
            fig.add_trace(go.Violin(
                y=group_data,
                name=str(group),
                box_visible=True,
                meanline_visible=True
            ))
        
        fig.update_layout(
            title=title or f"Distribuição de {col} por {group_col}",
            template=self.theme,
            yaxis_title=col,
            xaxis_title=group_col
        )
        
        return fig
    
    def create_posterior_plot(self, trace, var_names: List[str] = None) -> go.Figure:
        """
        Cria gráfico das distribuições posteriores
        
        Args:
            trace: Trace do modelo bayesiano
            var_names: Nomes das variáveis para plotar
            
        Returns:
            Figura plotly
        """
        if not ARVIZ_AVAILABLE:
            st.error("ArviZ não está disponível para visualizações bayesianas")
            return go.Figure()
        
        try:
            # Converter para matplotlib e depois para plotly
            az_plot = az.plot_posterior(trace, var_names=var_names)
            
            # Criar figura plotly equivalente
            fig = go.Figure()
            
            # Adicionar como imagem (temporário)
            fig.add_annotation(
                text="Visualização das distribuições posteriores",
                showarrow=False,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                font=dict(size=16)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Erro ao criar gráfico posterior: {e}")
            return go.Figure()
    
    def create_trace_plot(self, trace, var_names: List[str] = None) -> go.Figure:
        """
        Cria gráfico de trace das cadeias MCMC
        
        Args:
            trace: Trace do modelo bayesiano
            var_names: Nomes das variáveis para plotar
            
        Returns:
            Figura plotly
        """
        if not ARVIZ_AVAILABLE:
            st.error("ArviZ não está disponível para visualizações bayesianas")
            return go.Figure()
        
        try:
            fig = go.Figure()
            
            # Placeholder para trace plot
            fig.add_annotation(
                text="Gráfico de trace das cadeias MCMC",
                showarrow=False,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                font=dict(size=16)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Erro ao criar trace plot: {e}")
            return go.Figure()
    
    def create_dashboard_metrics(self, metrics: Dict[str, Any]) -> go.Figure:
        """
        Cria dashboard com métricas principais
        
        Args:
            metrics: Dicionário com métricas
            
        Returns:
            Figura plotly com dashboard
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=list(metrics.keys())[:4],
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for i, (key, value) in enumerate(list(metrics.items())[:4]):
            row, col = positions[i]
            
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=value,
                    title={"text": key},
                    gauge={"axis": {"range": [0, value * 1.5]}}
                ),
                row=row, col=col
            )
        
        fig.update_layout(height=400, title="Métricas do Dashboard")
        
        return fig