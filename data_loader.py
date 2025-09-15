"""
Módulo para carregamento e pré-processamento de dados
Autor: Robson Jobs
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Dict, Any
import io

class DataLoader:
    """Classe para carregamento e validação de dados"""
    
    def __init__(self):
        self.data = None
        self.metadata = {}
    
    def load_csv(self, file_buffer, **kwargs) -> pd.DataFrame:
        """
        Carrega dados de um arquivo CSV
        
        Args:
            file_buffer: Buffer do arquivo CSV
            **kwargs: Argumentos adicionais para pd.read_csv
            
        Returns:
            DataFrame com os dados carregados
        """
        try:
            # Configurações padrão para leitura
            default_kwargs = {
                'encoding': 'utf-8',
                'sep': ',',
                'low_memory': False
            }
            default_kwargs.update(kwargs)
            
            # Carregar dados
            self.data = pd.read_csv(file_buffer, **default_kwargs)
            
            # Gerar metadata
            self._generate_metadata()
            
            return self.data
            
        except UnicodeDecodeError:
            # Tentar com encoding alternativo
            try:
                file_buffer.seek(0)
                self.data = pd.read_csv(file_buffer, encoding='latin-1', **kwargs)
                self._generate_metadata()
                return self.data
            except Exception as e:
                raise Exception(f"Erro ao decodificar arquivo: {e}")
                
        except Exception as e:
            raise Exception(f"Erro ao carregar CSV: {e}")
    
    def load_excel(self, file_buffer, sheet_name=0, **kwargs) -> pd.DataFrame:
        """
        Carrega dados de um arquivo Excel
        
        Args:
            file_buffer: Buffer do arquivo Excel
            sheet_name: Nome ou índice da planilha
            **kwargs: Argumentos adicionais para pd.read_excel
            
        Returns:
            DataFrame com os dados carregados
        """
        try:
            self.data = pd.read_excel(file_buffer, sheet_name=sheet_name, **kwargs)
            self._generate_metadata()
            return self.data
            
        except Exception as e:
            raise Exception(f"Erro ao carregar Excel: {e}")
    
    def _generate_metadata(self) -> None:
        """Gera metadata dos dados carregados"""
        if self.data is not None:
            self.metadata = {
                'shape': self.data.shape,
                'columns': list(self.data.columns),
                'dtypes': self.data.dtypes.to_dict(),
                'null_counts': self.data.isnull().sum().to_dict(),
                'memory_usage': self.data.memory_usage(deep=True).sum(),
                'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(self.data.select_dtypes(include=['object']).columns)
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo dos dados carregados
        
        Returns:
            Dicionário com informações resumidas
        """
        if self.data is None:
            return {}
        
        return {
            'registros': self.data.shape[0],
            'variaveis': self.data.shape[1],
            'memoria_mb': round(self.metadata['memory_usage'] / (1024**2), 2),
            'valores_nulos': sum(self.metadata['null_counts'].values()),
            'colunas_numericas': len(self.metadata['numeric_columns']),
            'colunas_categoricas': len(self.metadata['categorical_columns'])
        }
    
    def validate_data(self) -> Dict[str, Any]:
        """
        Valida a qualidade dos dados
        
        Returns:
            Dicionário com resultados da validação
        """
        if self.data is None:
            return {'status': 'error', 'message': 'Nenhum dado carregado'}
        
        issues = []
        warnings = []
        
        # Verificar dados nulos
        null_percentage = (self.data.isnull().sum() / len(self.data)) * 100
        high_null_cols = null_percentage[null_percentage > 50].index.tolist()
        
        if high_null_cols:
            warnings.append(f"Colunas com >50% valores nulos: {high_null_cols}")
        
        # Verificar duplicatas
        duplicates = self.data.duplicated().sum()
        if duplicates > 0:
            warnings.append(f"Encontradas {duplicates} linhas duplicadas")
        
        # Verificar colunas vazias
        empty_cols = [col for col in self.data.columns if self.data[col].isna().all()]
        if empty_cols:
            issues.append(f"Colunas completamente vazias: {empty_cols}")
        
        return {
            'status': 'warning' if warnings else 'success',
            'issues': issues,
            'warnings': warnings,
            'summary': self.get_summary()
        }
    
    def preprocess_data(self, operations: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Aplica pré-processamento aos dados
        
        Args:
            operations: Dicionário com operações a serem aplicadas
            
        Returns:
            DataFrame pré-processado
        """
        if self.data is None:
            raise ValueError("Nenhum dado carregado")
        
        processed_data = self.data.copy()
        
        # Operações padrão se nenhuma for especificada
        if operations is None:
            operations = {
                'remove_duplicates': True,
                'handle_nulls': 'drop',
                'standardize_columns': True
            }
        
        # Remover duplicatas
        if operations.get('remove_duplicates', False):
            processed_data = processed_data.drop_duplicates()
        
        # Tratar valores nulos
        null_handling = operations.get('handle_nulls', 'keep')
        if null_handling == 'drop':
            processed_data = processed_data.dropna()
        elif null_handling == 'fill_mean':
            numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
            processed_data[numeric_cols] = processed_data[numeric_cols].fillna(
                processed_data[numeric_cols].mean()
            )
        
        # Padronizar nomes das colunas
        if operations.get('standardize_columns', False):
            processed_data.columns = processed_data.columns.str.lower().str.replace(' ', '_')
        
        return processed_data
    
    def sample_data(self, n: int = 1000, random_state: int = 42) -> pd.DataFrame:
        """
        Retorna uma amostra dos dados
        
        Args:
            n: Número de registros da amostra
            random_state: Seed para reprodutibilidade
            
        Returns:
            DataFrame com amostra dos dados
        """
        if self.data is None:
            raise ValueError("Nenhum dado carregado")
        
        if n >= len(self.data):
            return self.data.copy()
        
        return self.data.sample(n=n, random_state=random_state)