"""
Funções utilitárias para o dashboard
Autor: Robson Jobs
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import pickle
from datetime import datetime
import re

class Utils:
    """Classe com funções utilitárias"""
    
    @staticmethod
    def format_number(number: Union[int, float], 
                     precision: int = 2, 
                     suffix: str = "") -> str:
        """
        Formata números para exibição
        
        Args:
            number: Número para formatar
            precision: Casas decimais
            suffix: Sufixo (ex: %, M, K)
            
        Returns:
            String formatada
        """
        if pd.isna(number):
            return "N/A"
        
        if abs(number) >= 1e9:
            return f"{number/1e9:.{precision}f}B{suffix}"
        elif abs(number) >= 1e6:
            return f"{number/1e6:.{precision}f}M{suffix}"
        elif abs(number) >= 1e3:
            return f"{number/1e3:.{precision}f}K{suffix}"
        else:
            return f"{number:.{precision}f}{suffix}"
    
    @staticmethod
    def calculate_summary_stats(data: pd.Series) -> Dict[str, Any]:
        """
        Calcula estatísticas resumidas de uma série
        
        Args:
            data: Série pandas
            
        Returns:
            Dicionário com estatísticas
        """
        if data.empty:
            return {}
        
        stats = {
            'count': len(data),
            'missing': data.isnull().sum(),
            'missing_pct': (data.isnull().sum() / len(data)) * 100
        }
        
        if data.dtype in ['int64', 'float64']:
            stats.update({
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std(),
                'min': data.min(),
                'max': data.max(),
                'q25': data.quantile(0.25),
                'q75': data.quantile(0.75),
                'skewness': data.skew(),
                'kurtosis': data.kurtosis()
            })
        else:
            stats.update({
                'unique': data.nunique(),
                'top_value': data.mode().iloc[0] if not data.mode().empty else None,
                'top_freq': data.value_counts().iloc[0] if not data.value_counts().empty else 0
            })
        
        return stats
    
    @staticmethod
    def detect_outliers(data: pd.Series, method: str = 'iqr') -> pd.Series:
        """
        Detecta outliers em uma série
        
        Args:
            data: Série pandas
            method: Método de detecção ('iqr', 'zscore')
            
        Returns:
            Série booleana com outliers
        """
        if data.dtype not in ['int64', 'float64']:
            return pd.Series([False] * len(data), index=data.index)
        
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (data < lower_bound) | (data > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((data - data.mean()) / data.std())
            return z_scores > 3
        
        else:
            raise ValueError("Método deve ser 'iqr' ou 'zscore'")
    
    @staticmethod
    def create_bins(data: pd.Series, n_bins: int = 10, method: str = 'equal_width') -> pd.Series:
        """
        Cria bins para uma variável contínua
        
        Args:
            data: Série pandas
            n_bins: Número de bins
            method: Método ('equal_width', 'equal_freq', 'kmeans')
            
        Returns:
            Série com bins
        """
        if method == 'equal_width':
            return pd.cut(data, bins=n_bins, duplicates='drop')
        elif method == 'equal_freq':
            return pd.qcut(data, q=n_bins, duplicates='drop')
        else:
            raise ValueError("Método deve ser 'equal_width' ou 'equal_freq'")
    
    @staticmethod
    def validate_columns(data: pd.DataFrame, required_cols: List[str]) -> Tuple[bool, List[str]]:
        """
        Valida se colunas obrigatórias existem no DataFrame
        
        Args:
            data: DataFrame para validar
            required_cols: Lista de colunas obrigatórias
            
        Returns:
            Tupla (é_válido, colunas_faltando)
        """
        missing_cols = [col for col in required_cols if col not in data.columns]
        return len(missing_cols) == 0, missing_cols
    
    @staticmethod
    def clean_column_names(data: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa nomes das colunas
        
        Args:
            data: DataFrame para limpar
            
        Returns:
            DataFrame com colunas limpas
        """
        data_clean = data.copy()
        data_clean.columns = (data_clean.columns
                             .str.lower()
                             .str.replace(' ', '_')
                             .str.replace('[^a-zA-Z0-9_]', '', regex=True))
        return data_clean
    
    @staticmethod
    def export_to_csv(data: pd.DataFrame, filename: str = None) -> str:
        """
        Exporta DataFrame para CSV
        
        Args:
            data: DataFrame para exportar
            filename: Nome do arquivo (opcional)
            
        Returns:
            String com dados CSV
        """
        if filename is None:
            filename = f"dados_exportados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return data.to_csv(index=False)
    
    @staticmethod
    def create_download_link(data: Union[pd.DataFrame, str], 
                           filename: str, 
                           link_text: str = "Download") -> None:
        """
        Cria link de download no Streamlit
        
        Args:
            data: Dados para download
            filename: Nome do arquivo
            link_text: Texto do link
        """
        if isinstance(data, pd.DataFrame):
            csv_data = data.to_csv(index=False)
            st.download_button(
                label=link_text,
                data=csv_data,
                file_name=filename,
                mime='text/csv'
            )
        elif isinstance(data, str):
            st.download_button(
                label=link_text,
                data=data,
                file_name=filename,
                mime='text/plain'
            )
    
    @staticmethod
    def save_session_state(state_dict: Dict[str, Any], filename: str = None) -> str:
        """
        Salva estado da sessão
        
        Args:
            state_dict: Dicionário com estado
            filename: Nome do arquivo
            
        Returns:
            Nome do arquivo salvo
        """
        if filename is None:
            filename = f"session_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Converter tipos não serializáveis
        clean_state = {}
        for key, value in state_dict.items():
            try:
                json.dumps(value)
                clean_state[key] = value
            except (TypeError, ValueError):
                clean_state[key] = str(value)
        
        with open(filename, 'w') as f:
            json.dump(clean_state, f, indent=2, default=str)
        
        return filename
    
    @staticmethod
    def load_session_state(filename: str) -> Dict[str, Any]:
        """
        Carrega estado da sessão
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Dicionário com estado carregado
        """
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar estado: {e}")
            return {}
    
    @staticmethod
    def progress_bar(current: int, total: int, text: str = "Progresso") -> None:
        """
        Exibe barra de progresso
        
        Args:
            current: Valor atual
            total: Valor total
            text: Texto da barra
        """
        progress = current / total if total > 0 else 0
        st.progress(progress, text=f"{text}: {current}/{total}")
    
    @staticmethod
    def display_metrics_grid(metrics: Dict[str, Any], cols: int = 4) -> None:
        """
        Exibe métricas em grade
        
        Args:
            metrics: Dicionário com métricas
            cols: Número de colunas
        """
        metric_items = list(metrics.items())
        rows = len(metric_items) // cols + (1 if len(metric_items) % cols else 0)
        
        for row in range(rows):
            columns = st.columns(cols)
            for col in range(cols):
                idx = row * cols + col
                if idx < len(metric_items):
                    key, value = metric_items[idx]
                    with columns[col]:
                        if isinstance(value, dict) and 'value' in value:
                            st.metric(
                                label=key,
                                value=Utils.format_number(value['value']),
                                delta=value.get('delta')
                            )
                        else:
                            st.metric(label=key, value=Utils.format_number(value))
    
    @staticmethod
    def filter_dataframe(data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Aplica filtros ao DataFrame
        
        Args:
            data: DataFrame original
            filters: Dicionário com filtros
            
        Returns:
            DataFrame filtrado
        """
        filtered_data = data.copy()
        
        for column, filter_config in filters.items():
            if column not in data.columns:
                continue
            
            filter_type = filter_config.get('type', 'range')
            
            if filter_type == 'range' and data[column].dtype in ['int64', 'float64']:
                min_val = filter_config.get('min', data[column].min())
                max_val = filter_config.get('max', data[column].max())
                filtered_data = filtered_data[
                    (filtered_data[column] >= min_val) & 
                    (filtered_data[column] <= max_val)
                ]
            
            elif filter_type == 'categorical':
                selected_values = filter_config.get('values', [])
                if selected_values:
                    filtered_data = filtered_data[filtered_data[column].isin(selected_values)]
        
        return filtered_data
    
    @staticmethod
    def generate_sample_data(n_rows: int = 1000) -> pd.DataFrame:
        """
        Gera dados de exemplo para testes
        
        Args:
            n_rows: Número de linhas
            
        Returns:
            DataFrame com dados de exemplo
        """
        np.random.seed(42)
        
        data = {
            'id': range(n_rows),
            'universidade': np.random.choice(['USP', 'UNICAMP', 'UFRJ', 'UFMG', 'PUC'], n_rows),
            'curso': np.random.choice(['Engenharia', 'Medicina', 'Direito', 'Economia', 'Psicologia'], n_rows),
            'regiao': np.random.choice(['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'], n_rows),
            'matriculas': np.random.randint(100, 5000, n_rows),
            'vagas': np.random.randint(50, 1000, n_rows),
            'taxa_evasao': np.random.uniform(0.05, 0.30, n_rows),
            'nota_enade': np.random.uniform(1.0, 5.0, n_rows),
            'ano': np.random.choice([2020, 2021, 2022, 2023], n_rows)
        }
        
        return pd.DataFrame(data)