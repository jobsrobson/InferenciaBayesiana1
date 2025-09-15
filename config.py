"""
Configurações do dashboard
Autor: Robson Jobs
"""

import streamlit as st
from typing import Dict, Any

# Configurações gerais do dashboard
DASHBOARD_CONFIG = {
    'title': 'Dashboard - Inferência Bayesiana',
    'subtitle': 'Análise do Censo da Educação Superior 2023',
    'author': 'Robson Jobs',
    'version': '1.0.0',
    'description': 'Dashboard para análise bayesiana dos dados do Censo da Educação Superior 2023'
}

# Configurações do Streamlit
STREAMLIT_CONFIG = {
    'page_title': 'Dashboard - Inferência Bayesiana',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Configurações de cores e temas
COLOR_PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#17becf',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Configurações de visualização
VIZ_CONFIG = {
    'default_theme': 'plotly_white',
    'color_palette': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ],
    'default_height': 500,
    'default_width': 800
}

# Configurações dos modelos bayesianos
BAYESIAN_CONFIG = {
    'default_samples': 2000,
    'default_chains': 2,
    'default_tune': 1000,
    'default_cores': 2,
    'target_accept': 0.8,
    'max_treedepth': 10
}

# Configurações de dados
DATA_CONFIG = {
    'max_file_size_mb': 200,
    'supported_formats': ['csv', 'xlsx', 'xls'],
    'encoding_options': ['utf-8', 'latin-1', 'cp1252'],
    'separator_options': [',', ';', '\t', '|'],
    'sample_size': 10000  # Para preview dos dados
}

# Mensagens de erro e avisos
MESSAGES = {
    'no_data': '⚠️ Nenhum dado carregado. Use o painel lateral para carregar seus dados.',
    'loading_data': '⏳ Carregando dados...',
    'processing': '🔄 Processando...',
    'error_loading': '❌ Erro ao carregar dados',
    'success_loading': '✅ Dados carregados com sucesso',
    'model_running': '🚀 Executando modelo bayesiano...',
    'model_complete': '✅ Modelo executado com sucesso',
    'model_error': '❌ Erro na execução do modelo',
    'export_success': '📥 Dados exportados com sucesso',
    'invalid_data': '⚠️ Dados inválidos ou corrompidos'
}

# Configurações de exportação
EXPORT_CONFIG = {
    'csv_separator': ',',
    'csv_encoding': 'utf-8',
    'excel_engine': 'openpyxl',
    'include_index': False,
    'date_format': '%Y-%m-%d'
}

# Configurações de cache
CACHE_CONFIG = {
    'ttl': 3600,  # 1 hora
    'max_entries': 100,
    'allow_output_mutation': True
}

# URLs e links úteis
LINKS = {
    'documentation': 'https://docs.streamlit.io/',
    'pymc_docs': 'https://docs.pymc.io/',
    'arviz_docs': 'https://arviz-devs.github.io/arviz/',
    'census_data': 'https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior',
    'github_repo': 'https://github.com/jobsrobson/InferenciaBayesiana1'
}

# Configurações de segurança
SECURITY_CONFIG = {
    'max_upload_size': 200 * 1024 * 1024,  # 200MB
    'allowed_extensions': ['.csv', '.xlsx', '.xls'],
    'sanitize_inputs': True,
    'validate_data_types': True
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    'chunk_size': 10000,
    'lazy_loading': True,
    'use_multiprocessing': False,  # Pode causar problemas no Streamlit
    'memory_threshold_mb': 1000
}

# Textos da interface
UI_TEXTS = {
    'sidebar': {
        'navigation': '🧭 Navegação',
        'data_section': '📁 Dados',
        'upload_help': 'Faça upload dos dados do Censo da Educação Superior',
        'settings': '⚙️ Configurações'
    },
    'pages': {
        'home': '🏠 Início',
        'exploratory': '📊 Análise Exploratória',
        'models': '🔬 Modelos Bayesianos',
        'visualizations': '📈 Visualizações',
        'comparison': '🔍 Comparação de Modelos',
        'reports': '📋 Relatórios',
        'about': 'ℹ️ Sobre'
    },
    'buttons': {
        'load_data': '📂 Carregar Dados',
        'run_model': '🚀 Executar Modelo',
        'export_results': '📥 Exportar Resultados',
        'reset': '🔄 Reiniciar',
        'download': '💾 Download'
    }
}

# Configurações específicas por tipo de análise
ANALYSIS_CONFIG = {
    'exploratory': {
        'max_categories': 50,
        'correlation_threshold': 0.5,
        'outlier_threshold': 3,
        'missing_threshold': 0.5
    },
    'modeling': {
        'train_test_split': 0.8,
        'cv_folds': 5,
        'random_state': 42,
        'early_stopping': True
    },
    'visualization': {
        'max_points': 10000,
        'opacity': 0.7,
        'line_width': 2,
        'marker_size': 8
    }
}

def get_config(section: str = None) -> Dict[str, Any]:
    """
    Retorna configurações específicas ou todas
    
    Args:
        section: Seção específica da configuração
        
    Returns:
        Dicionário com configurações
    """
    configs = {
        'dashboard': DASHBOARD_CONFIG,
        'streamlit': STREAMLIT_CONFIG,
        'colors': COLOR_PALETTE,
        'viz': VIZ_CONFIG,
        'bayesian': BAYESIAN_CONFIG,
        'data': DATA_CONFIG,
        'messages': MESSAGES,
        'export': EXPORT_CONFIG,
        'cache': CACHE_CONFIG,
        'links': LINKS,
        'security': SECURITY_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'ui': UI_TEXTS,
        'analysis': ANALYSIS_CONFIG
    }
    
    if section:
        return configs.get(section, {})
    else:
        return configs

def set_streamlit_config():
    """Aplica configurações do Streamlit"""
    st.set_page_config(**STREAMLIT_CONFIG)

def get_color_palette():
    """Retorna paleta de cores"""
    return VIZ_CONFIG['color_palette']

def get_theme():
    """Retorna tema padrão"""
    return VIZ_CONFIG['default_theme']