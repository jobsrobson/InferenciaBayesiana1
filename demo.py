"""
Script para demonstrar o uso do dashboard
Autor: Robson Jobs
"""

import pandas as pd
import numpy as np
from utils import Utils
from data_loader import DataLoader
from visualizations import Visualizations

def main():
    """Demonstra as funcionalidades do dashboard"""
    
    print("🎯 Demonstração do Dashboard de Inferência Bayesiana")
    print("=" * 50)
    
    # 1. Gerar dados de exemplo
    print("\n1. 📊 Gerando dados de exemplo...")
    sample_data = Utils.generate_sample_data(n_rows=1000)
    print(f"   ✅ Dados gerados: {sample_data.shape[0]} registros, {sample_data.shape[1]} variáveis")
    print(f"   📋 Colunas: {list(sample_data.columns)}")
    
    # 2. Carregar dados usando DataLoader
    print("\n2. 📁 Testando DataLoader...")
    # Salvar dados temporários
    sample_data.to_csv('/tmp/dados_exemplo.csv', index=False)
    
    loader = DataLoader()
    with open('/tmp/dados_exemplo.csv', 'rb') as f:
        loaded_data = loader.load_csv(f)
    
    print(f"   ✅ Dados carregados com sucesso: {loaded_data.shape}")
    
    # 3. Validar dados
    print("\n3. 🔍 Validando qualidade dos dados...")
    validation = loader.validate_data()
    print(f"   📊 Status: {validation['status']}")
    print(f"   📈 Resumo: {validation['summary']}")
    
    # 4. Estatísticas resumidas
    print("\n4. 📈 Calculando estatísticas...")
    stats = Utils.calculate_summary_stats(loaded_data['matriculas'])
    print(f"   🎯 Matrículas - Média: {stats['mean']:.2f}, Mediana: {stats['median']:.2f}")
    
    # 5. Detectar outliers
    print("\n5. 🎯 Detectando outliers...")
    outliers = Utils.detect_outliers(loaded_data['matriculas'])
    print(f"   ⚠️  Outliers encontrados: {outliers.sum()} ({(outliers.sum()/len(loaded_data)*100):.1f}%)")
    
    # 6. Criar visualizações
    print("\n6. 📊 Criando visualizações...")
    viz = Visualizations()
    
    # Gráfico de dispersão
    fig_scatter = viz.create_scatter_plot(
        loaded_data, 
        'matriculas', 
        'nota_enade',
        color_col='regiao',
        title='Matrículas vs Nota ENADE por Região'
    )
    print("   ✅ Gráfico de dispersão criado")
    
    # Histograma
    fig_hist = viz.create_histogram(
        loaded_data,
        'nota_enade',
        color_col='regiao',
        title='Distribuição das Notas ENADE'
    )
    print("   ✅ Histograma criado")
    
    # Matriz de correlação
    numeric_cols = loaded_data.select_dtypes(include=[np.number]).columns.tolist()
    fig_corr = viz.create_correlation_heatmap(
        loaded_data,
        columns=numeric_cols,
        title='Matriz de Correlação'
    )
    print("   ✅ Matriz de correlação criada")
    
    # 7. Filtrar dados
    print("\n7. 🔍 Testando filtros...")
    filters = {
        'matriculas': {'type': 'range', 'min': 500, 'max': 3000},
        'regiao': {'type': 'categorical', 'values': ['Sudeste', 'Sul']}
    }
    filtered_data = Utils.filter_dataframe(loaded_data, filters)
    print(f"   🎯 Dados filtrados: {len(filtered_data)} registros ({len(filtered_data)/len(loaded_data)*100:.1f}%)")
    
    # 8. Exportar resultados
    print("\n8. 💾 Exportando resultados...")
    csv_export = Utils.export_to_csv(filtered_data)
    print(f"   📄 CSV exportado: {len(csv_export)} caracteres")
    
    print("\n" + "=" * 50)
    print("🎉 Demonstração concluída com sucesso!")
    print("\n💡 Para usar o dashboard completo:")
    print("   streamlit run app.py")
    print("\n📚 Para mais informações, consulte o README.md")

if __name__ == "__main__":
    main()